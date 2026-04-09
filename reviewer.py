import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions
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

IMPORTANT: Output your review as JSON with this exact structure:
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
    """Send PR diff to Claude for review and return the raw result text."""
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

    options = ClaudeAgentOptions(
        system_prompt=SYSTEM_PROMPT,
        allowed_tools=[],
        max_turns=1,
        output_format={
            "type": "json_schema",
            "schema": {
                "type": "object",
                "properties": {
                    "summary": {"type": "string"},
                    "issues": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "severity": {"type": "string", "enum": ["critical", "warning", "suggestion"]},
                                "file": {"type": "string"},
                                "description": {"type": "string"},
                            },
                            "required": ["severity", "file", "description"],
                        },
                    },
                    "verdict": {"type": "string", "enum": ["approve", "request_changes", "comment"]},
                },
                "required": ["summary", "issues", "verdict"],
            },
        },
    )

    result_text = None
    structured = None

    async for message in query(prompt=prompt, options=options):
        if hasattr(message, "structured_output") and message.structured_output is not None:
            structured = message.structured_output
        if hasattr(message, "result") and message.result is not None:
            result_text = message.result

    # Prefer structured output if available
    if structured is not None:
        return structured
    return result_text
