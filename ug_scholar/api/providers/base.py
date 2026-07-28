from abc import ABC, abstractmethod


class ProviderError(RuntimeError):
    """A provider failure that is safe to report in synchronization logs."""


class AuthorNotMatchedError(ProviderError):
    """Raised when a local profile cannot be matched without ambiguity."""


class PublicationProvider(ABC):
    name: str

    @abstractmethod
    def fetch_author(self, profile) -> dict:
        """Return normalized ``author_data`` and ``author_articles`` dictionaries."""
