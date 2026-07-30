import re
import unicodedata

import requests
from django.conf import settings
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .base import AuthorNotMatchedError, ProviderError, PublicationProvider


class OpenAlexProvider(PublicationProvider):
    name = "openalex"
    base_url = "https://api.openalex.org"

    def __init__(self):
        self.api_key = settings.OPENALEX_API_KEY
        self.timeout = settings.SCHOLAR_HTTP_TIMEOUT
        retry = Retry(
            total=3,
            connect=3,
            read=3,
            backoff_factor=0.5,
            status_forcelist=(429, 500, 502, 503, 504),
            allowed_methods=("GET",),
            respect_retry_after_header=True,
        )
        self.session = requests.Session()
        self.session.mount("https://", HTTPAdapter(max_retries=retry))
        self.session.headers.update(
            {
                "Accept": "application/json",
                "User-Agent": settings.SCHOLAR_USER_AGENT,
            }
        )

    @staticmethod
    def _id(value):
        return (value or "").rstrip("/").split("/")[-1]

    @staticmethod
    def _normalize(value):
        value = unicodedata.normalize("NFKD", value or "")
        value = "".join(char for char in value if not unicodedata.combining(char))
        return re.sub(r"[^a-z0-9]+", " ", value.lower()).strip()

    def _get(self, path, params=None):
        request_params = dict(params or {})
        if self.api_key:
            request_params["api_key"] = self.api_key
        try:
            response = self.session.get(
                f"{self.base_url}{path}",
                params=request_params,
                timeout=self.timeout,
            )
            response.raise_for_status()
            return response.json()
        except (requests.RequestException, ValueError) as exc:
            raise ProviderError(f"OpenAlex request failed: {exc}") from exc

    def _candidate_affiliations(self, candidate):
        names = []
        for institution in candidate.get("last_known_institutions") or []:
            names.append(institution.get("display_name", ""))
        for affiliation in candidate.get("affiliations") or []:
            names.append((affiliation.get("institution") or {}).get("display_name", ""))
        return " ".join(self._normalize(name) for name in names)

    def _resolve_author_id(self, profile):
        if profile.data_source == self.name and profile.source_author_id:
            return self._id(profile.source_author_id)
        if profile.orcid:
            return self._id(profile.orcid)
        if not profile.name:
            raise AuthorNotMatchedError(
                f"Profile {profile.pk} needs a name, ORCID, or OpenAlex author ID"
            )

        payload = self._get(
            "/authors",
            {
                "search": profile.name,
                "per_page": 10,
                "select": (
                    "id,display_name,affiliations,last_known_institutions,"
                    "orcid,works_count,cited_by_count"
                ),
            },
        )
        expected_name = self._normalize(profile.name)
        expected_affiliations = {
            self._normalize(value)
            for value in (
                profile.affiliation,
                profile.school,
                profile.college,
            )
            if value
        }
        scored = []
        for candidate in payload.get("results", []):
            candidate_name = self._normalize(candidate.get("display_name"))
            if candidate_name != expected_name:
                continue
            affiliations = self._candidate_affiliations(candidate)
            affiliation_score = sum(
                expected in affiliations or affiliations in expected
                for expected in expected_affiliations
                if expected and affiliations
            )
            scored.append((affiliation_score, candidate.get("works_count", 0), candidate))

        if not scored:
            raise AuthorNotMatchedError(
                f"No exact OpenAlex author match for {profile.name!r}"
            )
        scored.sort(key=lambda item: (item[0], item[1]), reverse=True)
        if len(scored) > 1 and scored[0][:2] == scored[1][:2]:
            raise AuthorNotMatchedError(
                f"Ambiguous OpenAlex author match for {profile.name!r}; "
                "add an ORCID or OpenAlex author ID"
            )
        return self._id(scored[0][2]["id"])

    def _fetch_works(self, author_id):
        works = []
        cursor = "*"
        while cursor:
            payload = self._get(
                "/works",
                {
                    "filter": f"authorships.author.id:{author_id}",
                    "per_page": 100,
                    "cursor": cursor,
                    "select": (
                        "id,doi,display_name,publication_year,primary_location,"
                        "authorships,cited_by_count,primary_topic,topics,keywords"
                    ),
                },
            )
            works.extend(payload.get("results", []))
            next_cursor = (payload.get("meta") or {}).get("next_cursor")
            cursor = next_cursor if next_cursor and next_cursor != cursor else None
        return works

    @staticmethod
    def _work_topics(work):
        topics = []
        seen = set()
        primary_id = ((work.get("primary_topic") or {}).get("id"))
        for topic in [
            work.get("primary_topic"),
            *(work.get("topics") or []),
            *(work.get("keywords") or []),
        ]:
            if not topic:
                continue
            topic_id = topic.get("id") or topic.get("display_name")
            if not topic_id or topic_id in seen:
                continue
            seen.add(topic_id)
            topics.append(
                {
                    "id": topic.get("id"),
                    "name": topic.get("display_name"),
                    "score": topic.get("score", 1),
                    "primary": topic.get("id") == primary_id,
                    "subfield": (topic.get("subfield") or {}).get("display_name"),
                    "field": (topic.get("field") or {}).get("display_name"),
                    "domain": (topic.get("domain") or {}).get("display_name"),
                }
            )
        return topics

    def fetch_author(self, profile):
        author_id = self._resolve_author_id(profile)
        author = self._get(f"/authors/{author_id}")
        works = self._fetch_works(author_id)

        institutions = author.get("last_known_institutions") or []
        affiliation = ", ".join(
            institution.get("display_name", "")
            for institution in institutions
            if institution.get("display_name")
        )
        stats = author.get("summary_stats") or {}
        topics = author.get("topics") or []
        articles = []
        for work in works:
            primary_location = work.get("primary_location") or {}
            source = primary_location.get("source") or {}
            doi = work.get("doi")
            normalized_doi = (
                re.sub(r"^https?://(?:dx\.)?doi\.org/", "", doi, flags=re.I)
                if doi
                else None
            )
            authors = ", ".join(
                (authorship.get("author") or {}).get("display_name", "")
                for authorship in work.get("authorships") or []
                if (authorship.get("author") or {}).get("display_name")
            )
            articles.append(
                {
                    "source": self.name,
                    "external_id": self._id(work.get("id")),
                    "doi": normalized_doi,
                    "article_title": work.get("display_name") or "Untitled work",
                    "article_link": (
                        primary_location.get("landing_page_url")
                        or (f"https://doi.org/{normalized_doi}" if normalized_doi else None)
                    ),
                    "article_year": work.get("publication_year"),
                    "article_citation_id": self._id(work.get("id")),
                    "article_authors": authors,
                    "article_publication": source.get("display_name"),
                    "article_cited_by_value": work.get("cited_by_count") or 0,
                    "provider_topics": self._work_topics(work),
                }
            )

        return {
            "author_data": {
                "name": author.get("display_name"),
                "email": None,
                "affiliations": affiliation or profile.affiliation,
                "thumbnail": None,
                "interests": [
                    {"title": topic.get("display_name")}
                    for topic in topics
                    if topic.get("display_name")
                ],
                "cited_by_table": {
                    "citations": author.get("cited_by_count") or 0,
                    "h_index": stats.get("h_index") or 0,
                    "i10_index": stats.get("i10_index") or 0,
                },
                "citations": author.get("cited_by_count") or 0,
                "h_index": stats.get("h_index") or 0,
                "i10_index": stats.get("i10_index") or 0,
                "source_author_id": author_id,
                "orcid": author.get("orcid"),
            },
            "author_articles": articles,
        }
