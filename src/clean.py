"""Turn messy HTML / text into clean plain text for the script writer."""
from __future__ import annotations

import re

from bs4 import BeautifulSoup


def html_to_text(html: str) -> str:
    """Strip HTML to readable text, dropping scripts and styles."""
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style"]):
        tag.decompose()
    return normalise(soup.get_text(separator="\n"))


def normalise(text: str) -> str:
    """Collapse whitespace and remove blank lines."""
    lines = [ln.strip() for ln in text.splitlines()]
    lines = [ln for ln in lines if ln]
    text = "\n".join(lines)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()
