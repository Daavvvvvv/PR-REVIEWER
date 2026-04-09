import os
import sys
from dotenv import load_dotenv

load_dotenv()

_REQUIRED = ["ANTHROPIC_API_KEY", "GITHUB_TOKEN", "GITHUB_REPOS", "DISCORD_WEBHOOK_URL"]
_missing = [k for k in _REQUIRED if not os.getenv(k)]
if _missing:
    print(f"Missing required env vars: {', '.join(_missing)}")
    print("Copy .env.example to .env and fill in the values.")
    sys.exit(1)

ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]
GITHUB_TOKEN = os.environ["GITHUB_TOKEN"]
GITHUB_REPOS = [r.strip() for r in os.environ["GITHUB_REPOS"].split(",")]
DISCORD_WEBHOOK_URL = os.environ["DISCORD_WEBHOOK_URL"]
POLL_INTERVAL = int(os.getenv("POLL_INTERVAL", "300"))
