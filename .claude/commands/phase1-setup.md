---
description: Initialize Phase 1 of PLAN.md - OpenAI Responses API integration setup
argument-hint: [focus-area]
allowed-tools: Read, Write, Edit, Bash, Glob, Grep
---

# Phase 1 Setup: OpenAI Responses API Integration

You are implementing **Phase 1, Week 1-2** of PLAN.md: "Enhanced Document Analysis"

## Current Context
  - Working from: `evidence-toolkit/` (root)
  - Target: Upgrade document-evidence-analyzer/ from basic word frequency to structured AI insights
  - Commands will: `cd document-evidence-analyzer && [work]`
  - Use uv for management e.g., uv add, uv pip install, uv run, uv sync
  - Activate the existing .venv: `source document-evidence-analyzer/.venv/bin/activate`
  

## Your Tasks

1. **Review Current State**
   - Read `document-evidence-analyzer/src/document_analyzer/word_cloud_analyzer.py`
   - Check existing OpenAI integration (should be basic or missing)
   - Review pyproject.toml dependencies

2. **Create Pydantic Models** (from PLAN.md lines 45-70)
   - Create `document-evidence-analyzer/src/document_analyzer/ai_models.py`
   - Implement `DocumentEntity`, `DocumentAnalysis` models exactly as shown in PLAN.md
   - Follow image-analysis patterns in `image_analysis/models.py`

3. **Update Dependencies**
   - Add OpenAI >=1.60, pydantic >=2.8 to pyproject.toml
   - Ensure jsonschema dependency for future validation

4. **Begin AI Integration**
   - Add OpenAI **Responses API** client setup (NOT chat completions) with temperature=0
   - Create placeholder for structured analysis function using Responses API
   - **CRITICAL**: Use OpenAI Responses API, NOT the chat completions API

Focus area: $ARGUMENTS (if specified)

**Success Criteria:**
- ✅ Pydantic models created and importable
- ✅ Dependencies updated
- ✅ Basic OpenAI client structure in place
- ✅ Ready for schema creation in next phase

Work systematically and reference PLAN.md for exact specifications.