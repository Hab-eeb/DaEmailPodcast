# Daily Briefing Podcast

Turns selected emails + daily/local news into a short spoken-word podcast episode,
delivered via a private RSS feed. Personal project, built to run for free.

## Phase 1 — ingestion (current)

Reads your chosen email senders and news RSS feeds, cleans them to plain text, and
prints a merged digest of the last 24 hours.

### Setup

```bash
# 1. Create and activate a virtual environment
#    (if Anaconda hijacks it, run `conda deactivate` first)
python3 -m venv .venv
source .venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure your sources
cp config.example.yaml config.yaml
#    then edit config.yaml: put your real newsletter senders + any feeds you want

# 4. Add your Gmail OAuth client
mkdir -p credentials
#    move your downloaded OAuth client JSON into credentials/client.json

# 5. Mint your read-only Gmail refresh token (one-time, opens a browser)
python -m src.gmail_auth

# 6. Run the collector
python -m src.collector
```

You should see a merged, time-ordered digest printed to the terminal.
