import asyncio
import json
import subprocess
from github_client import PRInfo


SYSTEM_PROMPT = """You are an expert code reviewer. You receive pull request diffs and produce structured reviews.

Your review must be thorough but concise. Focus on:
- Bugs and logic errors
- Security vulnerabilities
- Performance issues
- Code quality and readability
- Missing error handling

For each issue found, specify:
- severity: "critical", "warning", or "suggestion"
- file: the filename
- description: what the issue is and how to fix it

If the PR looks good, say so briefly and note any minor suggestions.

IMPORTANT: Output your review as JSON with this exact structure and nothing else:
{
  "summary": "Brief overall assessment of the PR",
  "issues": [
    {
      "severity": "critical|warning|suggestion",
      "file": "filename",
      "description": "What's wrong and how to fix it"
    }
  ],
  "verdict": "approve|request_changes|comment"
}
"""


async def review_pr(pr: PRInfo) -> str:
    """Send PR diff to Claude CLI for review and return the result."""
    prompt = f"""Review this pull request:

**Repository:** {pr.repo_name}
**PR #{pr.number}:** {pr.title}
**Author:** {pr.author}
**Description:** {pr.body or "No description provided."}
**Files changed:** {", ".join(pr.files_changed)}

## Diff

```diff
{pr.diff}
```

Provide your review as the JSON structure described in your instructions."""

    result = await asyncio.to_thread(_run_claude, prompt)

    # Try to parse as JSON
    try:
        return json.loads(result)
    except json.JSONDecodeError:
        # Try to extract JSON from markdown code blocks
        if "```" in result:
            for block in result.split("```"):
                block = block.strip()
                if block.startswith("json"):
                    block = block[4:].strip()
                try:
                    return json.loads(block)
                except json.JSONDecodeError:
                    continue
        return result


def _run_claude(prompt: str) -> str:
    """Call the claude CLI in print mode."""
    result = subprocess.run(
        [
            "claude",
            "-p",
            "--output-format", "text",
            "--system-prompt", SYSTEM_PROMPT,
            prompt,
        ],
        capture_output=True,
        text=True,
        timeout=120,
    )

    if result.returncode != 0:
        raise RuntimeError(f"Claude CLI failed (exit {result.returncode}): {result.stderr}")

    return result.stdout.strip()
