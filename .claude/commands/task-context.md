---
allowed-tools: Bash(find:*), Bash(grep:*), Bash(head:*), Bash(ls:*)
argument-hint: [focus-area]
description: Generate focused development context for current email analysis task
---

# Email Analysis Development Context

## Current Task Status
- **Primary Goal**: Add email chain analysis using proven forensic patterns
- **Architecture**: Following DocumentAnalyzer + ImageAnalyzer success patterns
- **Quality Target**: 4.6/5 forensic standard (same as existing analyzers)

## Proven Patterns to Follow

### OpenAI Responses API Pattern
Current working implementation: !`grep -A 15 -B 2 "responses\.parse" document-evidence-analyzer/src/document_analyzer/word_cloud_analyzer.py`

### Pydantic Model Structure
Reference model structure: @document-evidence-analyzer/src/document_analyzer/ai_models.py

### CLI Integration Pattern
Command structure to follow: !`grep -A 5 "subparser" document-evidence-analyzer/src/document_analyzer/cli.py`

## Implementation Plan Status

### Current Email Work
Existing email-related files: !`find . -name "*email*" -type f 2>/dev/null`

Email references in code: !`grep -r "email" . --include="*.py" | head -3`

### Next Development Steps
1. **Week 1**: Create `email_models.py` following @document-evidence-analyzer/src/document_analyzer/ai_models.py
2. **Week 2**: Create `email_analyzer.py` following DocumentAnalyzer patterns
3. **Week 3**: Integrate with existing CLI and evidence storage

### Files to Create
- `document-evidence-analyzer/src/document_analyzer/email_models.py`
- `document-evidence-analyzer/src/document_analyzer/email_parser.py`
- `document-evidence-analyzer/src/document_analyzer/email_analyzer.py`

## Architecture Reference Files
- @EMAIL_FORENSIC_ARCHITECTURE.md - Complete implementation plan
- @EVIDENCE_TYPE_ASSESSMENT.md - Capability assessment and roadmap
- @document-evidence-analyzer/src/document_analyzer/word_cloud_analyzer.py:410-485 - AI analysis pattern

## Development Environment
Tools available: !`uv run evidence-toolkit --help | head -5`

Current working directory: !`pwd`

**Ready to implement EmailAnalyzer following proven DocumentAnalyzer patterns**