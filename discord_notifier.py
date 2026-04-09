import json
import requests
import config
from github_client import PRInfo

VERDICT_EMOJI = {
    "approve": "\u2705",
    "request_changes": "\u274c",
    "comment": "\U0001f4ac",
}

SEVERITY_EMOJI = {
    "critical": "\U0001f534",
    "warning": "\U0001f7e1",
    "suggestion": "\U0001f535",
}


def send_review(pr: PRInfo, review: dict | str) -> None:
    """Format and send a PR review to Discord via webhook."""
    if isinstance(review, str):
        # Fallback if structured output wasn't returned
        _send_raw(pr, review)
        return

    verdict = review.get("verdict", "comment")
    emoji = VERDICT_EMOJI.get(verdict, "\U0001f4ac")
    summary = review.get("summary", "No summary.")
    issues = review.get("issues", [])

    # Build the embed
    description = f"**{emoji} Verdict: {verdict.upper()}**\n\n{summary}"

    if issues:
        description += "\n\n**Issues found:**\n"
        for issue in issues[:15]:  # Cap at 15 to stay within Discord limits
            sev = SEVERITY_EMOJI.get(issue["severity"], "\u26aa")
            description += f"\n{sev} **[{issue['severity'].upper()}]** `{issue['file']}`\n{issue['description']}\n"

    # Discord embeds have a 4096 char limit for description
    if len(description) > 4000:
        description = description[:3997] + "..."

    embed = {
        "title": f"PR Review: {pr.repo_name}#{pr.number}",
        "description": description,
        "url": pr.url,
        "color": {"approve": 0x2ECC71, "request_changes": 0xE74C3C, "comment": 0x3498DB}.get(verdict, 0x95A5A6),
        "footer": {"text": f"Author: {pr.author} | {len(issues)} issue(s) found"},
    }

    payload = {"embeds": [embed]}
    resp = requests.post(config.DISCORD_WEBHOOK_URL, json=payload, timeout=10)
    resp.raise_for_status()


def _send_raw(pr: PRInfo, text: str) -> None:
    """Fallback: send plain text review to Discord."""
    if len(text) > 1900:
        text = text[:1900] + "\n... [truncated]"

    payload = {"content": f"**PR Review: {pr.repo_name}#{pr.number}** — {pr.title}\n{pr.url}\n\n{text}"}
    resp = requests.post(config.DISCORD_WEBHOOK_URL, json=payload, timeout=10)
    resp.raise_for_status()
