"""Daily Briefing Podcast package.

macOS python.org builds often don't link a CA bundle, so HTTPS verification
fails ("unable to get local issuer certificate"). We point Python's SSL layer
at certifi's Mozilla CA bundle if nothing else has set it. This is harmless on
Linux / CI, where certificates already resolve, because we only set a default.
"""
import os

import certifi

os.environ.setdefault("SSL_CERT_FILE", certifi.where())