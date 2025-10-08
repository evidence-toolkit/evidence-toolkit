---
allowed-tools: Read, Grep, WebFetch, mcp__context7
argument-hint: [query]
description: Ask the Docs Expert (uses Context7 MCP + local docs).
model: claude-3-5-haiku-20241022
---

## Context snapshot (auto-collected)
- Current docs tree (top level): !`ls -1 docs | head -n 50`
- Recent changes: !`git log --oneline -20`
- Repo topics from README: !`grep -iE '##|###' -n README* | head -n 20`

## Task
Use the **docs-expert** subagent to answer:

"$ARGUMENTS"

If needed, fetch resources via MCP, e.g. `@context7:http://…/mcp/path` or `@context7:sse://…/resource/id`, then cite what you used.
