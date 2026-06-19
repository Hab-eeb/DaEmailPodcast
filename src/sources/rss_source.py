"""A Source backed by an RSS news feed."""
from __future__ import annotations

import calendar
from datetime import datetime, timezone

import feedparser

from ..clean import html_to_text
from .base import Item, Source

# Some sites (the BBC included) reject feedparser's default agent, so we send a
# normal-looking one. This is the single most common cause of "0 items" feeds.
USER_AGENT = "Mozilla/5.0 (compatible; DailyBriefingBot/1.0; +https://github.com/Hab-eeb)"


class RSSSource(Source):
    def __init__(self, name: str, url: str, since: datetime, max_items: int = 8):
        self.name = name
        self.url = url
        self.since = since          # tz-aware UTC datetime
        self.max_items = max_items

    def fetch(self) -> list[Item]:
        feed = feedparser.parse(self.url, agent=USER_AGENT)
        # Make failures loud instead of returning a silent empty list.
        if feed.bozo and not feed.entries:
            raise RuntimeError(f"feed fetch/parse failed: {feed.bozo_exception}")

        items: list[Item] = []
        for entry in feed.entries:
            published = _entry_dt(entry)
            # Skip anything older than our window (undated items are kept).
            if published and published < self.since:
                continue
            summary = entry.get("summary", "") or ""
            items.append(
                Item(
                    title=entry.get("title", "(no title)"),
                    body=html_to_text(summary),
                    source=self.name,
                    published=published,
                    url=entry.get("link"),
                )
            )
            if len(items) >= self.max_items:
                break
        return items


def _entry_dt(entry) -> datetime | None:
    # feedparser gives time in UTC struct_time; timegm reads it as UTC.
    t = entry.get("published_parsed") or entry.get("updated_parsed")
    if not t:
        return None
    return datetime.fromtimestamp(calendar.timegm(t), tz=timezone.utc)