"""News article model."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, HttpUrl


class NewsArticle(BaseModel):
    """News article from Brave Search."""

    # Identification
    url: HttpUrl = Field(..., description="Article URL (unique identifier)")
    title: str = Field(..., min_length=1, max_length=500, description="Article title")

    # Content
    summary: str = Field(..., description="Article summary/snippet")
    content: Optional[str] = Field(None, description="Full article content (if available)")

    # Metadata
    published_date: Optional[datetime] = Field(None, description="Publication date")
    source: Optional[str] = Field(None, description="News source name")

    # Processing metadata
    fetched_at: datetime = Field(default_factory=datetime.utcnow, description="When article was fetched")
    processed: bool = Field(default=False, description="Whether analyzed for impact")

    class Config:
        """Pydantic config."""

        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }

    def __hash__(self) -> int:
        """Hash by URL for deduplication."""
        return hash(str(self.url))

    def __eq__(self, other: object) -> bool:
        """Compare articles by URL."""
        if not isinstance(other, NewsArticle):
            return NotImplemented
        return str(self.url) == str(other.url)
