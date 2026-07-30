import json

from django.conf import settings
from django.db import models
from django.db.models import Q


class Publication(models.Model):
    """A normalized scholarly work from an external data provider."""

    title = models.CharField(max_length=500)
    link = models.CharField(max_length=500, blank=True, null=True)
    year = models.IntegerField(db_index=True)
    citation_id = models.CharField(
        max_length=255, blank=True, null=True, db_index=True
    )
    source = models.CharField(
        max_length=32, default="google_scholar", db_index=True
    )
    external_id = models.CharField(max_length=255, blank=True, null=True)
    doi = models.CharField(max_length=255, blank=True, null=True, db_index=True)
    authors = models.CharField(max_length=2000, blank=True, null=True)
    journal = models.CharField(max_length=500, blank=True, null=True)
    citations = models.IntegerField(default=0, db_index=True)
    provider_topics = models.JSONField(default=list, blank=True)
    thematic_area = models.CharField(
        max_length=64,
        default="Multidisciplinary / Unclassified",
        db_index=True,
    )
    thematic_confidence = models.FloatField(default=0)
    thematic_evidence = models.JSONField(default=dict, blank=True)
    last_synced_at = models.DateTimeField(blank=True, null=True, db_index=True)

    def get_author_name(self) -> str:
        prefetched = getattr(self, "_prefetched_objects_cache", {}).get(
            "author_entities"
        )
        if prefetched is not None:
            author = prefetched[0] if prefetched else None
        else:
            author = self.author_entities.select_related("profile").first()
        if author:
            return author.profile.name or author.profile.scholar_id
        return "Anonymous"

    def __str__(self):
        return self.title

    class Meta:
        db_table = "publication"
        verbose_name_plural = "publications"
        ordering = ["-year"]
        constraints = [
            models.UniqueConstraint(
                fields=["source", "external_id"],
                condition=Q(external_id__isnull=False),
                name="unique_publication_source_id",
            ),
        ]


class Profile(models.Model):
    """A local author profile and its provider-specific synchronization state."""

    name = models.CharField(max_length=200, blank=True, null=True)
    scholar_id = models.CharField(max_length=50, unique=True)
    data_source = models.CharField(
        max_length=32, default="google_scholar", db_index=True
    )
    source_author_id = models.CharField(
        max_length=255, blank=True, null=True, db_index=True
    )
    orcid = models.CharField(max_length=50, blank=True, null=True, db_index=True)
    affiliation = models.CharField(max_length=500, blank=True, null=True)
    thumbnail = models.CharField(max_length=500, blank=True, null=True)
    interests = models.JSONField(default=list, blank=True)
    statistics = models.JSONField(default=dict, blank=True)
    h_index = models.PositiveIntegerField(default=0)
    i10_index = models.PositiveIntegerField(default=0)
    provider_citations = models.PositiveBigIntegerField(default=0)
    last_synced_at = models.DateTimeField(blank=True, null=True, db_index=True)
    sync_error = models.TextField(blank=True, default="")
    rank = models.CharField(max_length=50, blank=True, null=True)
    email = models.CharField(max_length=100, blank=True, null=True)
    college = models.CharField(max_length=200, blank=True, null=True, db_index=True)
    school = models.CharField(max_length=200, blank=True, null=True, db_index=True)
    department = models.CharField(
        max_length=200, blank=True, null=True, db_index=True
    )

    @staticmethod
    def _decoded_statistics(value):
        if not value:
            return {}
        if isinstance(value, str):
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return {}
        return value

    def get_author_hindex(self) -> int:
        if self.h_index:
            return self.h_index
        stats = self._decoded_statistics(self.statistics)
        try:
            if isinstance(stats, list):
                return int(stats[1]["h_index"]["all"])
            return int(stats.get("h_index", 0))
        except (KeyError, IndexError, TypeError, ValueError):
            return 0

    def get_author_i10index(self) -> int:
        if self.i10_index:
            return self.i10_index
        stats = self._decoded_statistics(self.statistics)
        try:
            if isinstance(stats, list):
                return int(stats[2]["i10_index"]["all"])
            return int(stats.get("i10_index", 0))
        except (KeyError, IndexError, TypeError, ValueError):
            return 0

    def get_author_publications(self) -> int:
        annotated = getattr(self, "publication_count", None)
        if annotated is not None:
            return annotated
        try:
            return self.author.publications.count()
        except Author.DoesNotExist:
            return 0

    def get_author_citations(self) -> int:
        annotated = getattr(self, "citation_count", None)
        if annotated is not None:
            return annotated or 0
        try:
            result = self.author.publications.aggregate(total=models.Sum("citations"))
        except Author.DoesNotExist:
            return 0
        return result["total"] or 0

    def abbreviate_college(self) -> str:
        if not self.college:
            return self.scholar_id
        names = self.college.split()
        return (
            "".join(name[0] for name in names[:-1]).upper()
            if len(names) > 1
            else names[0].upper()
        )

    def abbreviate_school(self) -> str:
        if not self.school:
            return self.scholar_id
        names = self.school.split()
        return (
            "".join(name[0] for name in names[:-1]).upper()
            if len(names) > 1
            else names[0].upper()
        )

    def abbreviate_department(self) -> str:
        if not self.department:
            return self.scholar_id
        names = self.department.split()
        return "".join(name[0] for name in names).upper()

    def __str__(self):
        return self.name or self.scholar_id

    class Meta:
        db_table = "profile"
        verbose_name_plural = "profiles"
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=["data_source", "source_author_id"],
                condition=Q(source_author_id__isnull=False),
                name="unique_profile_source_author",
            ),
        ]


class Author(models.Model):
    """The local author entity linking a profile to its publications."""

    profile = models.OneToOneField(
        Profile, on_delete=models.CASCADE, related_name="author"
    )
    publications = models.ManyToManyField(
        Publication, related_name="author_entities"
    )

    def __str__(self):
        return self.profile.name or self.profile.scholar_id

    class Meta:
        db_table = "author"
        verbose_name_plural = "authors"
        ordering = ["profile__name"]


class SyncRun(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        RUNNING = "running", "Running"
        SUCCEEDED = "succeeded", "Succeeded"
        PARTIAL = "partial", "Partially succeeded"
        FAILED = "failed", "Failed"

    status = models.CharField(
        max_length=16, choices=Status.choices, default=Status.PENDING, db_index=True
    )
    provider = models.CharField(max_length=32, db_index=True)
    profile_ids = models.JSONField(default=list, blank=True)
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="scholar_sync_runs",
    )
    total_profiles = models.PositiveIntegerField(default=0)
    processed_profiles = models.PositiveIntegerField(default=0)
    updated_publications = models.PositiveIntegerField(default=0)
    failed_profiles = models.PositiveIntegerField(default=0)
    error = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    started_at = models.DateTimeField(blank=True, null=True)
    finished_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = "sync_run"
        ordering = ["-created_at"]
