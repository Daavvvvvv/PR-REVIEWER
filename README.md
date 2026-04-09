# revaisor-pr-agent

Automated PR reviewer powered by Claude Agent SDK. Polls GitHub repos for new PRs, reviews the diff with Claude, and sends structured reviews to Discord.

## Setup

```bash
# Create and activate venv
python -m venv .venv
.venv\Scripts\activate      # Windows
# source .venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your keys
```

### Required environment variables

| Variable | Description |
|---|---|
| `ANTHROPIC_API_KEY` | API key from [console.anthropic.com](https://console.anthropic.com/) |
| `GITHUB_TOKEN` | Personal access token with `repo` scope from [GitHub Settings](https://github.com/settings/tokens) |
| `GITHUB_REPOS` | Comma-separated repos to watch, e.g. `owner/repo1,owner/repo2` |
| `DISCORD_WEBHOOK_URL` | Webhook URL from Discord channel settings > Integrations > Webhooks |
| `POLL_INTERVAL` | *(optional)* Seconds between polls, default `300` (5 min) |

## Usage

```bash
# Review new PRs once and exit
python main.py

# Poll continuously
python main.py poll
```

Already-reviewed PRs are tracked in `reviewed_prs.json` so they won't be re-reviewed.
