from urllib.parse import parse_qsl, urlsplit

from django.conf import settings

from .base import ProviderError, PublicationProvider


class SerpApiProvider(PublicationProvider):
    name = "google_scholar"

    def __init__(self):
        if not settings.SERPAPI_API_KEY:
            raise ProviderError("SERPAPI_API_KEY is not configured")
        try:
            from serpapi import GoogleSearch
        except ImportError as exc:
            raise ProviderError(
                "Install google-search-results to use the SerpAPI provider"
            ) from exc
        self.search_class = GoogleSearch

    def fetch_author(self, profile):
        author_id = (
            profile.source_author_id
            if profile.data_source == self.name and profile.source_author_id
            else profile.scholar_id
        )
        search = self.search_class(
            {
                "api_key": settings.SERPAPI_API_KEY,
                "engine": "google_scholar_author",
                "hl": "en",
                "author_id": author_id,
                "num": 100,
            }
        )
        results = search.get_dict()
        if not results or results.get("error"):
            raise ProviderError(
                f"SerpAPI request failed: {(results or {}).get('error', 'empty response')}"
            )

        author = results.get("author") or {}
        cited_by = results.get("cited_by") or {}
        table = cited_by.get("table") or []

        def metric(index, key):
            try:
                return int(table[index][key]["all"])
            except (IndexError, KeyError, TypeError, ValueError):
                return 0

        author_data = {
            "name": author.get("name"),
            "email": author.get("email"),
            "affiliations": author.get("affiliations"),
            "thumbnail": author.get("thumbnail"),
            "interests": author.get("interests") or [],
            "cited_by_table": table,
            "citations": metric(0, "citations"),
            "h_index": metric(1, "h_index"),
            "i10_index": metric(2, "i10_index"),
            "source_author_id": author_id,
            "orcid": profile.orcid,
        }
        articles = []
        seen_pages = set()
        pages = 0
        while results and pages < 1000:
            pages += 1
            for article in results.get("articles", []):
                citation_id = article.get("citation_id")
                articles.append(
                    {
                        "source": self.name,
                        "external_id": citation_id,
                        "doi": None,
                        "article_title": article.get("title") or "Untitled work",
                        "article_link": article.get("link"),
                        "article_year": article.get("year"),
                        "article_citation_id": citation_id,
                        "article_authors": article.get("authors"),
                        "article_publication": article.get("publication"),
                        "article_cited_by_value": (
                            article.get("cited_by") or {}
                        ).get("value"),
                    }
                )
            next_url = (results.get("serpapi_pagination") or {}).get("next")
            if not next_url or next_url in seen_pages:
                break
            seen_pages.add(next_url)
            search.params_dict.update(dict(parse_qsl(urlsplit(next_url).query)))
            results = search.get_dict()
            if results.get("error"):
                raise ProviderError(f"SerpAPI pagination failed: {results['error']}")

        return {"author_data": author_data, "author_articles": articles}
