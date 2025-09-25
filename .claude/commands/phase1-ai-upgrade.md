---
description: Implement AI-powered document analysis with OpenAI Responses API
argument-hint: [document-type]
allowed-tools: Read, Write, Edit, MultiEdit, Bash, Glob, Grep
---

# Phase 1: AI-Powered Document Analysis

You are implementing **Phase 1, Week 1-2** of PLAN.md: Replace basic word frequency with structured AI insights

## Current Context
- Working from: `evidence-toolkit/` (root)
- Phase 1 setup should be complete (Pydantic models, dependencies)
- Target: Implement OpenAI **Responses API** (NOT chat completions) with structured output
- Commands will: `cd document-evidence-analyzer && [work]`
- Use uv for management e.g., uv add, uv pip install, uv run, uv sync
- Activate the existing .venv: `source document-evidence-analyzer/.venv/bin/activate`
- Reference: PLAN.md lines 61-70 for exact implementation

## Your Tasks

1. **Implement AI Analysis Function**
   - Create `_analyze_with_openai()` method in word_cloud_analyzer.py
   - Use OpenAI **Responses API** (NOT chat completions) with DocumentAnalysis response format
   - Set temperature=0 for deterministic legal analysis
   - Include comprehensive legal analysis prompt

2. **Entity Extraction System**
   - People, organizations, dates, legal terms
   - Confidence scoring for each entity
   - Context capture for legal significance

3. **Document Classification**
   - Types: email, letter, contract, filing
   - Sentiment: hostile, neutral, professional
   - Legal significance: critical, high, medium, low

4. **Risk Flag Detection**
   - PII, privileged, threatening, deadline flags
   - Overall confidence scoring

5. **Maintain Bulk Processing**
   - Keep existing `analyze_documents()` workflow
   - Add AI insights without breaking current functionality
   - Rate limiting for OpenAI API calls

Document type focus: $ARGUMENTS (if specified, e.g., "email", "contract")

**Success Criteria:**
- ✅ OpenAI Responses API integration working
- ✅ Structured DocumentAnalysis output
- ✅ Entity extraction with confidence scores
- ✅ Risk flags and legal significance detection
- ✅ Existing CLI commands still functional

Reference PLAN.md code samples exactly for implementation patterns.