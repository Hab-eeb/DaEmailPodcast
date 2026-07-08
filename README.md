# 📻 DaEmailPodcast

> Turns your Gmail inbox highlights and RSS news feeds into a short, spoken-word morning briefing — delivered as a private audio episode. Built to run for free.

---

## How It Works

Each run pulls content from two sources, merges them into a digest, uses Gemini AI to write a conversational radio-style script, and then synthesises it to audio via Gemini TTS.

```
Gmail (selected senders)  ──┐
                             ├──▶  Digest  ──▶  Script (Gemini)  ──▶  Audio (Gemini TTS)
RSS feeds                  ──┘
```

---

## Features

- **Gmail ingestion** — reads emails only from senders you whitelist via OAuth (no password needed)
- **RSS news ingestion** — fetches and parses any number of RSS feeds (BBC, Guardian, local news, etc.)
- **AI script writing** — Gemini 2.5 Flash turns the raw digest into a warm, conversational ~4-minute spoken briefing
- **Text-to-speech** — Gemini TTS renders the script to audio, ready to play or distribute
- **YAML-driven config** — no code changes needed to add/remove sources or tune behaviour
- **Zero cloud cost** — runs locally; uses Gemini free-tier API

---

## Project Structure

```
DaEmailPodcast/
├── src/
│   ├── collector.py        # Merges Gmail + RSS items into a digest
│   ├── clean.py            # Strips HTML/noise from raw content
│   ├── gmail_auth.py       # OAuth2 flow for Gmail API access
│   ├── script_writer.py    # Gemini prompt logic → spoken script
│   ├── sources/            # Pluggable source adapters (Gmail, RSS)
│   └── tts/
│       └── gemini_tts.py   # Gemini TTS → audio file
├── config.example.yaml     # Template config (copy to config.yaml)
├── env.example             # Template env vars (copy to .env)
├── requirements.txt
└── README.md
```

---

## Prerequisites

- Python 3.10+
- A [Google Cloud project](https://console.cloud.google.com/) with the **Gmail API** enabled
- OAuth 2.0 credentials downloaded as `credentials.json`
- A [Gemini API key](https://aistudio.google.com/app/apikey) (free tier is sufficient)

---

## Setup & Installation

**1. Clone the repo**

```bash
git clone https://github.com/Hab-eeb/DaEmailPodcast.git
cd DaEmailPodcast
```

**2. Install dependencies**

```bash
pip install -r requirements.txt
```

**3. Configure environment variables**

```bash
cp env.example .env
```

Open `.env` and paste in your Gemini API key:

```
GEMINI_API_KEY=your-gemini-api-key-here
```

**4. Set up Gmail OAuth**

- Go to [Google Cloud Console](https://console.cloud.google.com/), enable the **Gmail API**, and download your OAuth credentials as `credentials.json` into the project root.
- On first run, a browser window will open for you to authorise access. A `token.json` is saved locally for subsequent runs.

**5. Configure your sources**

```bash
cp config.example.yaml config.yaml
```

Edit `config.yaml` to add your email senders and preferred RSS feeds:

```yaml
lookback_hours: 24
max_items_per_source: 8

gmail:
  senders:
    - newsletter@example.com

feeds:
  - name: BBC News
    url: https://feeds.bbci.co.uk/news/rss.xml
  - name: BBC Manchester
    url: https://feeds.bbci.co.uk/news/england/manchester/rss.xml
```

---

## Usage

**Run Phase 1 — digest only (no API key needed)**

```bash
python -m src.collector
```

Prints a plain-text merged digest of the last 24 hours to stdout.

**Run Phase 2 — generate the spoken script**

```bash
python -m src.script_writer
```

Calls Gemini to write the briefing script and saves it to `script.txt`.

**Run Phase 3 — synthesise to audio**

```bash
python -m src.tts.gemini_tts
```

Reads `script.txt` and outputs an audio file using Gemini TTS.

---

## Configuration Reference

| Key | Default | Description |
|-----|---------|-------------|
| `lookback_hours` | `24` | How far back each run looks for content |
| `max_items_per_source` | `8` | Max items kept per source to control digest length |
| `gmail.senders` | `[]` | List of sender email addresses to include from Gmail |
| `feeds` | `[]` | List of RSS feed objects, each with a `name` and `url` |

---

## Roadmap

- [x] **Phase 1** — Gmail + RSS ingestion and digest
- [x] **Phase 2** — AI script writing with Gemini 2.5 Flash
- [x] **Phase 3** — Text-to-speech audio generation via Gemini TTS
- [ ] **Phase 4** — Private RSS feed / podcast hosting for playback on any podcast app
- [ ] **Phase 5** — Scheduled daily runs (cron / GitHub Actions)
- [ ] **Phase 6** — Additional source adapters (e.g. Slack, Calendar, Weather)

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Language | Python 3.10+ |
| Email access | Gmail API (OAuth2) via `google-api-python-client` |
| Feed parsing | `feedparser` |
| HTML cleaning | `beautifulsoup4` |
| AI script writing | Gemini 2.5 Flash (`google-genai`) |
| Text-to-speech | Gemini TTS (`google-genai`) |
| Config | `PyYAML` + `python-dotenv` |

---

## Contributing

This is a personal project but PRs and suggestions are welcome. Open an issue to start a discussion before making large changes.

---

## License

MIT
