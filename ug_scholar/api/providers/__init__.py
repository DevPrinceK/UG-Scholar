from django.conf import settings

from .base import ProviderError, PublicationProvider


def get_provider(name=None) -> PublicationProvider:
    provider_name = (name or settings.SCHOLAR_DATA_PROVIDER).strip().lower()
    if provider_name == "openalex":
        from .openalex import OpenAlexProvider

        return OpenAlexProvider()
    if provider_name in {"serpapi", "google_scholar"}:
        from .serpapi import SerpApiProvider

        return SerpApiProvider()
    raise ProviderError(f"Unsupported scholar data provider: {provider_name}")


__all__ = ["ProviderError", "PublicationProvider", "get_provider"]
