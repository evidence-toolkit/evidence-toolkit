---
allowed-tools: Bash(uv run:*), Read, Glob, Grep
argument-hint: [sha256|batch] [--limit N] [--skip-existing]
description: Analyze evidence images using the Evidence Toolkit pipeline
---

## Evidence Analysis Command

Analyze evidence images using the Evidence Toolkit's deterministic AI analysis pipeline.

### Usage Examples:
- `/analyze-evidence <sha256>` - Analyze single image by SHA256 hash
- `/analyze-evidence batch` - Analyze all unprocessed images
- `/analyze-evidence batch --limit 10` - Analyze up to 10 images
- `/analyze-evidence batch --skip-existing` - Skip already analyzed images

### Context

- Current evidence database status: !`uv run python -m image_analysis.cli --help`
- Evidence storage structure: !`ls -la evidence/ 2>/dev/null || echo "No evidence directory found"`
- Recent analysis activity: !`find evidence/derived -name "analysis.v1.json" | head -5 2>/dev/null || echo "No analysis files found"`

### Your Task

Based on the arguments provided ($ARGUMENTS), perform evidence analysis using the Evidence Toolkit:

1. **Single Image Analysis**: If given a SHA256 hash, analyze that specific image
2. **Batch Analysis**: If given "batch", process multiple images with any specified limits
3. **Chain of Custody**: Ensure all analysis operations are properly logged
4. **Schema Validation**: Verify all outputs conform to the evidence schema - USE SIMPLE VALIDATION
5. **Error Handling**: Report any analysis failures or schema violations

**IMPORTANT**: Use simple, robust commands. Avoid complex shell pipelines that can fail.

### Validation Best Practices:
- **Simple validation**: `find evidence/derived -name 'analysis.v1.json' -exec uv run python validate_schema.py {} --schema schemas/evidence.v1.json \;`
- **Count successes**: Add `| grep -c "Validation passed"` only if needed
- **Avoid complexity**: No complex pipes, loops, or command chaining unless absolutely necessary
- **Start simple**: Use the most straightforward approach first

Use the Evidence Toolkit commands from CLAUDE.md and keep validation simple and reliable.