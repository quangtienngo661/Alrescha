from abc import ABC, abstractmethod
from helpers.Logger import logger


class AIKnowledgeBase(ABC):
    """
    Abstract base class for all AI knowledge base / vector store providers.

    Subclasses must implement the four abstract methods below.
    The shared helpers (log_summary) are implemented here once.
    """

    def __init__(self, chunk_size: int, overlap: int):
        self.chunk_size = chunk_size
        self.overlap = overlap

    # ------------------------------------------------------------------
    # Abstract — each provider must implement these
    # ------------------------------------------------------------------

    @abstractmethod
    def list_uploaded_files(self) -> dict:
        """
        Fetch the current state of the knowledge base from the provider.

        Returns a dict keyed by article slug (or a stable file identifier),
        mapping to whatever metadata the provider returns (e.g. file_id,
        created_at). Used by detect_delta() to compare against fresh articles.
        """
        pass

    @abstractmethod
    def upload_file(self, article: dict) -> str:
        """
        Upload a single article to the provider's knowledge base.

        Receives the article dict produced by scraper/writer.py
        (fields: id, url, title, slug, content, hash, updated_at).
        Returns the provider-assigned file_id of the uploaded resource.
        """
        pass

    @abstractmethod
    def delete_file(self, file_id: str) -> None:
        """
        Remove a previously uploaded file from the provider's knowledge base.

        Called during delta sync when an article has been updated:
        the old file is deleted before the new version is uploaded.
        """
        pass

    @abstractmethod
    def detect_delta(self, articles: list) -> tuple[list, list, list]:
        """
        Compare freshly scraped articles against what is already uploaded.

        Uses list_uploaded_files() internally.

        Returns a 3-tuple:
          added   — articles not yet in the knowledge base
          updated — articles whose content hash has changed
          skipped — articles that are identical to the uploaded version
        """
        pass

    # ------------------------------------------------------------------
    # Concrete — shared across all providers
    # ------------------------------------------------------------------

    def log_summary(self, added: list, updated: list, skipped: list) -> None:
        """Print a standardised run summary to stdout."""
        logger.info(f"[Upload] added={len(added)} updated={len(updated)} skipped={len(skipped)}")
