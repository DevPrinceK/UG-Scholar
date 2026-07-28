import hashlib
from datetime import timedelta

from django.conf import settings
from django.db import transaction
from django.db.models import Q
from django.utils import timezone

from api.models import Author, Profile, Publication, SyncRun
from api.providers import get_provider
from api.providers.base import ProviderError


def _as_int(value, default=0):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _fallback_external_id(article):
    fingerprint = "|".join(
        str(article.get(key) or "").strip().lower()
        for key in ("article_title", "article_year", "article_authors")
    )
    return f"fingerprint:{hashlib.sha256(fingerprint.encode('utf-8')).hexdigest()}"


def _normalized_article(article, provider_name, synced_at):
    external_id = (
        article.get("external_id")
        or article.get("article_citation_id")
        or article.get("doi")
        or _fallback_external_id(article)
    )
    return {
        "source": article.get("source") or provider_name,
        "external_id": str(external_id),
        "citation_id": article.get("article_citation_id") or str(external_id),
        "doi": article.get("doi") or None,
        "title": article.get("article_title") or "Untitled work",
        "link": article.get("article_link") or None,
        "year": _as_int(article.get("article_year"), 1900),
        "authors": article.get("article_authors") or "",
        "journal": article.get("article_publication") or "",
        "citations": _as_int(article.get("article_cited_by_value")),
        "last_synced_at": synced_at,
    }


def _publication_changed(publication, values):
    changed = False
    for field in (
        "citation_id",
        "doi",
        "title",
        "link",
        "year",
        "authors",
        "journal",
        "citations",
        "last_synced_at",
    ):
        if getattr(publication, field) != values[field]:
            setattr(publication, field, values[field])
            changed = True
    return changed


@transaction.atomic
def persist_author_data(profile, payload, provider_name):
    """Persist one complete provider response using bounded bulk queries."""

    synced_at = timezone.now()
    previous_source = profile.data_source
    author_data = payload.get("author_data") or {}
    normalized = {}
    for raw_article in payload.get("author_articles") or []:
        values = _normalized_article(raw_article, provider_name, synced_at)
        normalized[(values["source"], values["external_id"])] = values

    profile.name = author_data.get("name") or profile.name
    profile.affiliation = author_data.get("affiliations") or profile.affiliation
    profile.thumbnail = author_data.get("thumbnail") or profile.thumbnail
    if author_data.get("email"):
        profile.email = author_data["email"]
    if author_data.get("interests") is not None:
        profile.interests = author_data["interests"]
    if author_data.get("cited_by_table") is not None:
        profile.statistics = author_data["cited_by_table"]
    profile.h_index = _as_int(author_data.get("h_index"))
    profile.i10_index = _as_int(author_data.get("i10_index"))
    profile.provider_citations = _as_int(author_data.get("citations"))
    profile.data_source = provider_name
    profile.source_author_id = (
        author_data.get("source_author_id") or profile.source_author_id
    )
    if author_data.get("orcid"):
        profile.orcid = author_data["orcid"]
    profile.last_synced_at = synced_at
    profile.sync_error = ""
    profile.save(
        update_fields=[
            "name",
            "affiliation",
            "thumbnail",
            "email",
            "interests",
            "statistics",
            "h_index",
            "i10_index",
            "provider_citations",
            "data_source",
            "source_author_id",
            "orcid",
            "last_synced_at",
            "sync_error",
        ]
    )
    author, _ = Author.objects.get_or_create(profile=profile)

    source_ids = {}
    for source, external_id in normalized:
        source_ids.setdefault(source, []).append(external_id)

    existing = {}
    for source, external_ids in source_ids.items():
        for publication in Publication.objects.filter(
            source=source, external_id__in=external_ids
        ):
            existing[(source, publication.external_id)] = publication

    new_publications = [
        Publication(**values)
        for key, values in normalized.items()
        if key not in existing
    ]
    if new_publications:
        Publication.objects.bulk_create(new_publications, ignore_conflicts=True)

    publications = {}
    for source, external_ids in source_ids.items():
        for publication in Publication.objects.filter(
            source=source, external_id__in=external_ids
        ):
            publications[(source, publication.external_id)] = publication

    changed = []
    for key, publication in publications.items():
        if key in existing and _publication_changed(publication, normalized[key]):
            changed.append(publication)
    if changed:
        Publication.objects.bulk_update(
            changed,
            [
                "citation_id",
                "doi",
                "title",
                "link",
                "year",
                "authors",
                "journal",
                "citations",
                "last_synced_at",
            ],
        )

    through_model = Author.publications.through
    through_model.objects.bulk_create(
        [
            through_model(author_id=author.pk, publication_id=publication.pk)
            for publication in publications.values()
        ],
        ignore_conflicts=True,
    )

    current_ids = [publication.pk for publication in publications.values()]
    stale_links = through_model.objects.filter(author_id=author.pk)
    if current_ids:
        stale_links = stale_links.exclude(publication_id__in=current_ids)
    stale_links.delete()

    Publication.objects.filter(
        author_entities__isnull=True,
        source__in={previous_source, provider_name},
    ).delete()

    return {
        "publications": len(publications),
        "created": len(new_publications),
        "updated": len(changed),
    }


def sync_profile(profile, provider=None):
    selected_provider = provider or get_provider()
    payload = selected_provider.fetch_author(profile)
    if not payload.get("author_data"):
        raise ProviderError(f"{selected_provider.name} returned no author data")
    return persist_author_data(profile, payload, selected_provider.name)


def queue_sync(requested_by=None, profile_ids=None, provider_name=None):
    selected_name = (
        provider_name or settings.SCHOLAR_DATA_PROVIDER
    ).strip().lower()
    normalized_ids = sorted({int(value) for value in (profile_ids or [])})
    existing = SyncRun.objects.filter(
        provider=selected_name,
        status__in=[SyncRun.Status.PENDING, SyncRun.Status.RUNNING],
        profile_ids=normalized_ids,
    ).first()
    if existing:
        return existing, False
    run = SyncRun.objects.create(
        provider=selected_name,
        profile_ids=normalized_ids,
        requested_by=requested_by if getattr(requested_by, "is_authenticated", False) else None,
        total_profiles=len(normalized_ids) or Profile.objects.count(),
    )
    return run, True


def process_sync_run(run):
    with transaction.atomic():
        locked = SyncRun.objects.select_for_update().get(pk=run.pk)
        if locked.status != SyncRun.Status.PENDING:
            return locked
        locked.status = SyncRun.Status.RUNNING
        locked.started_at = timezone.now()
        locked.save(update_fields=["status", "started_at"])

    try:
        provider = get_provider(run.provider)
    except Exception as exc:
        run.status = SyncRun.Status.FAILED
        run.error = str(exc)[:10000]
        run.finished_at = timezone.now()
        run.save(update_fields=["status", "error", "finished_at"])
        return run
    profiles = Profile.objects.all().order_by("pk")
    if run.profile_ids:
        profiles = profiles.filter(pk__in=run.profile_ids)

    errors = []
    for profile in profiles.iterator(chunk_size=100):
        try:
            result = sync_profile(profile, provider)
            run.updated_publications += result["publications"]
        except Exception as exc:  # Each author is isolated; the run must continue.
            run.failed_profiles += 1
            error = str(exc)[:1000]
            errors.append(f"{profile.pk}: {error}")
            Profile.objects.filter(pk=profile.pk).update(sync_error=error)
        finally:
            run.processed_profiles += 1
            SyncRun.objects.filter(pk=run.pk).update(
                processed_profiles=run.processed_profiles,
                updated_publications=run.updated_publications,
                failed_profiles=run.failed_profiles,
            )

    if run.failed_profiles == 0:
        run.status = SyncRun.Status.SUCCEEDED
    elif run.failed_profiles == run.processed_profiles:
        run.status = SyncRun.Status.FAILED
    else:
        run.status = SyncRun.Status.PARTIAL
    run.error = "\n".join(errors)[-10000:]
    run.finished_at = timezone.now()
    run.save(
        update_fields=[
            "status",
            "processed_profiles",
            "updated_publications",
            "failed_profiles",
            "error",
            "finished_at",
        ]
    )
    return run


def queue_stale_sync(max_age_hours=168, requested_by=None):
    cutoff = timezone.now() - timedelta(hours=max_age_hours)
    ids = list(
        Profile.objects.filter(
            Q(last_synced_at__isnull=True) | Q(last_synced_at__lt=cutoff)
        ).values_list("pk", flat=True)
    )
    if not ids:
        return None, False
    return queue_sync(requested_by=requested_by, profile_ids=ids)
