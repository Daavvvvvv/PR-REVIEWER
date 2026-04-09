import json
import os
from dataclasses import dataclass
from github import Github
import config


@dataclass
class PRInfo:
    repo_name: str
    number: int
    title: str
    author: str
    body: str
    diff: str
    url: str
    files_changed: list[str]


REVIEWED_FILE = os.path.join(os.path.dirname(__file__), "reviewed_prs.json")


def _load_reviewed() -> set[str]:
    if os.path.exists(REVIEWED_FILE):
        with open(REVIEWED_FILE, "r") as f:
            return set(json.load(f))
    return set()


def _save_reviewed(reviewed: set[str]) -> None:
    with open(REVIEWED_FILE, "w") as f:
        json.dump(sorted(reviewed), f, indent=2)


def _pr_key(repo_name: str, pr_number: int) -> str:
    return f"{repo_name}#{pr_number}"


def mark_reviewed(repo_name: str, pr_number: int) -> None:
    reviewed = _load_reviewed()
    reviewed.add(_pr_key(repo_name, pr_number))
    _save_reviewed(reviewed)


def fetch_new_prs() -> list[PRInfo]:
    """Fetch open PRs from configured repos that haven't been reviewed yet."""
    gh = Github(config.GITHUB_TOKEN)
    reviewed = _load_reviewed()
    new_prs = []

    for repo_name in config.GITHUB_REPOS:
        repo = gh.get_repo(repo_name)
        for pr in repo.get_pulls(state="open", sort="created", direction="desc"):
            key = _pr_key(repo_name, pr.number)
            if key in reviewed:
                continue

            # Fetch the diff
            files = pr.get_files()
            diff_parts = []
            files_changed = []
            for f in files:
                files_changed.append(f.filename)
                if f.patch:
                    diff_parts.append(f"--- {f.filename}\n{f.patch}")

            diff = "\n\n".join(diff_parts)

            # Truncate very large diffs to avoid token limits
            if len(diff) > 50000:
                diff = diff[:50000] + "\n\n... [diff truncated, too large]"

            new_prs.append(PRInfo(
                repo_name=repo_name,
                number=pr.number,
                title=pr.title,
                author=pr.user.login,
                body=pr.body or "",
                diff=diff,
                url=pr.html_url,
                files_changed=files_changed,
            ))

    return new_prs
