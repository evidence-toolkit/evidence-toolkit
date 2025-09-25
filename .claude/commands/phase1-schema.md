---
description: Create document.v1.json schema and validation following image-analysis patterns
argument-hint:
allowed-tools: Read, Write, Edit, Bash, Glob, Grep
---

# Phase 1: Document Schema Creation & Validation

You are implementing **Phase 1, Week 3-4** of PLAN.md: Schema validation for document analysis

## Current Context
- Working from: `evidence-toolkit/` (root)
- AI integration should be complete
- Target: Create `document.v1.json` schema following `image-analysis/schemas/evidence.v1.json` patterns
- Commands will: `cd document-evidence-analyzer && [work]`
- Use uv for management e.g., uv add, uv pip install, uv run, uv sync
- Activate the existing .venv: `source document-evidence-analyzer/.venv/bin/activate`
- Reference: PLAN.md lines 75-109 for exact schema structure

## Your Tasks

1. **Create Schema Directory**
   - Create `document-evidence-analyzer/schemas/`
   - Create `document.v1.json` with exact structure from PLAN.md lines 75-109

2. **Schema Validation Module**
   - Create `document-evidence-analyzer/src/document_analyzer/validation.py`
   - Follow `image-analysis/validate_schema.py` patterns
   - Implement `DocumentValidator` class as shown in PLAN.md lines 153-166

3. **Integration with Analysis Pipeline**
   - Add validation calls to analysis workflow
   - Ensure all outputs conform to schema before storage
   - Fail fast on schema violations (forensic integrity)

4. **Validation Scripts**
   - Create `document-evidence-analyzer/scripts/validate_analyses.sh`
   - Mirror `image-analysis/scripts/validate_analyses.sh` patterns
   - CI/CD pipeline integration

5. **Update Analysis Output Format**
   - Modify word_cloud_analyzer.py to output schema-compliant JSON
   - Include all required fields: schema_version, case_id, evidence, analyses, chain_of_custody

**Success Criteria:**
- ✅ `document.v1.json` schema created and valid
- ✅ Schema validation integrated into analysis pipeline
- ✅ All document analyses validate against schema
- ✅ Validation scripts ready for CI/CD
- ✅ Analysis outputs are schema-compliant

**Schema Structure Requirements:**
- Must include: schema_version "1.0.0", evidence metadata, analyses array
- Must support: entities, document_type, sentiment, legal_significance, risk_flags
- Must validate: confidence scores (0.0-1.0), required fields, data types

Follow PLAN.md schema structure exactly - do not deviate from specified format.