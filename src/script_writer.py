"""Phase 2: turn the merged digest into a spoken-word script with Gemini."""
from __future__ import annotations

from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types

from .collector import collect, load_config
from .sources.base import Item

load_dotenv()  # loads GEMINI_API_KEY from a local .env if present

# Current free-tier Flash model. Swap to "gemini-3.5-flash" to try the newer one.
MODEL = "gemini-2.5-flash"

SCRIPT_FILE = Path(__file__).resolve().parent.parent / "script.txt"

# Stable rules live in the system instruction; the changing daily data goes in
# the user prompt. Keeping them separate means the model treats these as the
# fixed "job description" rather than something to be summarised away.
SYSTEM_INSTRUCTION = """\
You write a short, personal morning audio briefing for one listener.
The text you produce will be read ALOUD by a text-to-speech voice, so it must
sound natural when spoken, not when read on a page.

STRUCTURE
- Open with a brief, warm greeting that mentions the day and date.
- Then the listener's inbox highlights, then national news, then local news.
- Close with a short, friendly sign-off.

STYLE
- Conversational spoken English. Short, clear sentences. Natural spoken
  transitions between stories ("Meanwhile,", "On the local front,").
- Summarise and prioritise. Do NOT read every item; group related stories and
  skip trivia. Aim for roughly 500-700 words (about four minutes).
- Write the way it should be SPOKEN: no headings, no bullet points, no markdown,
  no URLs, no emoji, no symbols. Spell things out (say "percent", not "%").

ACCURACY
- Use ONLY the material provided. Do not invent facts, numbers, or quotes.
- If something is unclear or truncated, summarise it lightly rather than guess.

Output ONLY the script text — no preamble, labels, or stage directions.
"""


def write_script(items: list[Item], client: genai.Client | None = None) -> str:
    client = client or genai.Client()
    if not items:
        return _quiet_day()
    resp = client.models.generate_content(
        model=MODEL,
        contents=_build_prompt(items),
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION,
            temperature=0.7,            # natural-sounding, but still grounded
            max_output_tokens=2000,
        ),
    )
    return (resp.text or "").strip()


def _build_prompt(items: list[Item]) -> str:
    today = datetime.now().strftime("%A, %d %B %Y")
    inbox = [i for i in items if i.source.startswith("Inbox")]
    news = [i for i in items if not i.source.startswith("Inbox")]

    parts = [f"Today is {today}.", "", "Here is today's raw material.", ""]
    if inbox:
        parts.append("=== FROM YOUR INBOX ===")
        for i in inbox:
            parts.append(f"- {i.title}\n  {i.body[:1000].strip()}")  # cap to control tokens
        parts.append("")
    if news:
        parts.append("=== NEWS ===")
        for i in news:
            parts.append(f"- [{i.source}] {i.title}\n  {i.body[:400].strip()}")
        parts.append("")
    parts.append("Write the briefing script now.")
    return "\n".join(parts)


def _quiet_day() -> str:
    today = datetime.now().strftime("%A, %d %B")
    return (
        f"Good morning. It's {today}, and it's a quiet one. "
        "Nothing new landed in your inbox or the news feeds in the last day, "
        "so enjoy the calm. I'll be back tomorrow with your briefing."
    )


if __name__ == "__main__":
    cfg = load_config()
    print("Collecting...")
    items = collect(cfg)
    print(f"Writing script from {len(items)} items...\n")
    script = write_script(items)
    SCRIPT_FILE.write_text(script)
    print(script)
    print(f"\n[saved to {SCRIPT_FILE}]")
