import asyncio
import json
import sys
import time
import config
from github_client import fetch_new_prs, mark_reviewed
from reviewer import review_pr
from discord_notifier import send_review


async def review_single_pr(pr):
    """Review a single PR and send the result to Discord."""
    print(f"  Reviewing {pr.repo_name}#{pr.number}: {pr.title}")

    try:
        review = await review_pr(pr)
    except Exception as e:
        print(f"  ERROR reviewing {pr.repo_name}#{pr.number}: {e}")
        return

    # Parse structured output if it's a string
    if isinstance(review, str):
        try:
            review = json.loads(review)
        except json.JSONDecodeError:
            pass  # Send as raw text

    try:
        send_review(pr, review)
        mark_reviewed(pr.repo_name, pr.number)
        verdict = review.get("verdict", "?") if isinstance(review, dict) else "raw"
        print(f"  Done: {pr.repo_name}#{pr.number} -> {verdict}")
    except Exception as e:
        print(f"  ERROR sending to Discord: {e}")


async def run_once():
    """Check for new PRs and review them."""
    print("Checking for new PRs...")
    prs = fetch_new_prs()

    if not prs:
        print("No new PRs found.")
        return

    print(f"Found {len(prs)} new PR(s).")
    for pr in prs:
        await review_single_pr(pr)


async def run_poll():
    """Poll for new PRs on an interval."""
    print(f"Polling every {config.POLL_INTERVAL}s. Repos: {', '.join(config.GITHUB_REPOS)}")
    print("Press Ctrl+C to stop.\n")

    while True:
        await run_once()
        print(f"\nNext check in {config.POLL_INTERVAL}s...\n")
        await asyncio.sleep(config.POLL_INTERVAL)


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "once"

    if mode == "poll":
        asyncio.run(run_poll())
    elif mode == "once":
        asyncio.run(run_once())
    else:
        print(f"Usage: python main.py [once|poll]")
        print("  once  - Check once and exit (default)")
        print("  poll  - Continuously poll for new PRs")
        sys.exit(1)


if __name__ == "__main__":
    main()
