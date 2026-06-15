"""Run every configured source, merge the results, keep the last N hours."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path

import yaml

from .sources.base import Item
from .sources.gmail_source import GmailSource
from .sources.rss_source import RSSSource

CONFIG = Path(__file__).resolve().parent.parent / "config.yaml"


def load_config() -> dict:
    if not CONFIG.exists():
        raise FileNotFoundError("Copy config.example.yaml to config.yaml and edit it.")
    return yaml.safe_load(CONFIG.read_text())


def build_sources(cfg: dict, since: datetime) -> list:
    max_items = cfg.get("max_items_per_source", 8)
    sources: list = []
    senders = cfg.get("gmail", {}).get("senders", [])
    if senders:
        sources.append(GmailSource(senders, since, max_items))
    for feed in cfg.get("feeds", []):
        sources.append(RSSSource(feed["name"], feed["url"], since, max_items))
    return sources


def collect(cfg: dict) -> list[Item]:
    since = datetime.now(timezone.utc) - timedelta(hours=cfg.get("lookback_hours", 24))
    items: list[Item] = []
    for source in build_sources(cfg, since):
        try:
            fetched = source.fetch()
            print(f"  {source.name}: {len(fetched)} items")
            items.extend(fetched)
        except Exception as e:                      # one bad source shouldn't kill the run
            print(f"  {source.name}: ERROR {e}")
    oldest = datetime.min.replace(tzinfo=timezone.utc)
    items.sort(key=lambda i: i.published or oldest, reverse=True)  # newest first
    return items


if __name__ == "__main__":
    cfg = load_config()
    print("Collecting...")
    items = collect(cfg)
    hours = cfg.get("lookback_hours", 24)
    print(f"\n=== {len(items)} items in the last {hours}h ===\n")
    for it in items:
        when = it.published.strftime("%Y-%m-%d %H:%M") if it.published else "—"
        print(f"[{it.source}] {when}\n  {it.title}\n  {it.body[:200].strip()}...\n")
