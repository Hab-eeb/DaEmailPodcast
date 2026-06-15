"""The Source interface — the seam where any input backend plugs in."""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Item:
    """One piece of content from any source (an email or a news story)."""
    title: str
    body: str
    source: str                      # human label, e.g. "BBC News" or "Inbox: ..."
    published: datetime | None = None
    url: str | None = None


class Source(ABC):
    """Anything that can hand back recent items: inbox, RSS feed, etc."""
    name: str

    @abstractmethod
    def fetch(self) -> list[Item]:
        """Return recent items (already time-filtered) from this source."""
        raise NotImplementedError
