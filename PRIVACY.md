# Privacy & Data Handling

**Evidence Toolkit v3.3.0** | Last Updated: 2025-10-08

---

## Overview

The Evidence Toolkit is designed for professional legal evidence analysis with **privacy and confidentiality as core principles**. This document explains how the toolkit handles data, what's safe to commit to version control, and best practices for protecting sensitive information.

---

## What Goes Where

### ✅ Safe for Git (Public Repositories)

These items are safe to commit and share publicly:

- **Source code**: All Python modules in `src/evidence_toolkit/`
- **Documentation**: README files, guides, architecture docs
- **Tests**: Unit tests with synthetic/anonymized data in `tests/`
- **Examples**: Fully anonymized demonstration cases in `examples/`
- **Configuration templates**: Blank `.env.example`, config samples
- **Project metadata**: `pyproject.toml`, `.gitignore`, `LICENSE`

### ❌ Never Commit (Private Data)

These items are automatically gitignored and should NEVER be committed:

- **Real case data**: Everything in `data/cases/*`
- **Analysis results**: Everything in `data/packages/*`
- **Evidence storage**: Everything in `data/storage/raw/*` and `data/storage/derived/*`
- **API keys**: `.env` files, credentials
- **Client information**: Real names, companies, case details
- **Personal data**: Any identifying information about real people

---

## .gitignore Protection

The Evidence Toolkit `.gitignore` automatically protects:

```gitignore
# Your evidence data (never committed)
data/cases/*              # Your case evidence files
data/storage/raw/*        # Original evidence files
data/storage/derived/*    # Analysis results
data/packages/*           # Client deliverable packages

# Sensitive configuration
.env                      # API keys and secrets
.env.local

# Archives with potentially real data
archive/                  # Archived test data
*_backup_*/              # Backup directories
```

**Directory structure IS tracked** (via `.gitkeep` files), but actual content is gitignored.

---

## Handling Your Evidence

### Where to Put Real Case Data

```bash
# Create case directory
mkdir -p data/cases/YOUR-CASE-NAME

# Add your evidence files
cp /path/to/evidence/*.pdf data/cases/YOUR-CASE-NAME/
cp /path/to/emails/*.eml data/cases/YOUR-CASE-NAME/
cp /path/to/images/*.jpg data/cases/YOUR-CASE-NAME/

# Process (all data stays local)
uv run evidence-toolkit process-case data/cases/YOUR-CASE-NAME \
  --case-id YOUR-CASE-ID
```

**What happens to your data**:
1. ✅ Evidence copied to content-addressed storage (`data/storage/`)
2. ✅ Analysis results saved to `data/storage/derived/`
3. ✅ Client package generated in `data/packages/`
4. ✅ **ALL automatically gitignored** - won't be committed
5. ✅ Only you see your case data
6. ✅ Everything stays on your local machine

### Verifying Data is Protected

Before any `git commit`, verify no real data would be committed:

```bash
# Check what would be committed
git status

# Review actual changes
git diff

# Look for your case data
git diff | grep -i "YOUR-CLIENT-NAME"
git diff | grep -i "CASE-ID"

# If you see real data in diff output, DO NOT COMMIT
```

---

## Public Examples

All files in `examples/` are:

✅ **Fully anonymized**
- No real people (names like "James Wilson", "Sarah Chen" are fictional)
- No real companies ("RetailCorp", "ExampleCorp" are fictional)
- No real events or actual legal cases
- No identifying information

✅ **Safe for public use**
- Can be committed to public repositories
- Safe for demonstrations and training
- Based on common legal patterns, not actual cases
- Reviewed for privacy compliance

✅ **Created from scratch**
- Not modified versions of real cases
- Generic scenarios designed for teaching
- Realistic but entirely fictional

---

## Best Practices

### DO:
- ✅ Place all real evidence in `data/cases/`
- ✅ Use descriptive but generic case IDs (e.g., "workplace-2025-03")
- ✅ Review git status before committing
- ✅ Keep `.env` file secure (never commit)
- ✅ Use examples/ for learning and testing
- ✅ Document your workflow without revealing case details

### DON'T:
- ❌ Commit files from `data/cases/`, `data/storage/`, or `data/packages/`
- ❌ Put real case data in `examples/`
- ❌ Include real names or companies in code/comments
- ❌ Share API keys in repository
- ❌ Create examples from real cases (even if anonymized)
- ❌ Store client data in public repositories

### For Organizations:
- ✅ Use separate private repositories for client work
- ✅ Configure organization-wide .gitignore policies
- ✅ Train staff on data handling procedures
- ✅ Regular audits of committed files
- ✅ Implement code review for all commits
- ✅ Consider self-hosted Git for sensitive work

---

## Data Flow & Storage

### How Evidence is Stored

```
Your Evidence Files
        ↓
data/cases/YOUR-CASE/
  ├── document.pdf
  ├── email.eml
  └── image.jpg
        ↓
[Ingestion - SHA256 hashing]
        ↓
data/storage/
  ├── raw/sha256=<hash>/
  │   └── original.pdf          # Immutable original
  ├── derived/sha256=<hash>/
  │   ├── metadata.json          # File info
  │   ├── analysis.v1.json       # AI analysis
  │   └── chain_of_custody.json  # Audit trail
  └── cases/YOUR-CASE/
      └── <sha256>.pdf           # Hard link (no duplication)
        ↓
[Analysis - AI powered]
        ↓
[Correlation - Cross-evidence]
        ↓
[Package Generation]
        ↓
data/packages/YOUR-CASE_<timestamp>.zip
  ├── reports/executive_summary.txt
  ├── analysis/case_analysis.json
  ├── correlations/correlation_analysis.json
  └── raw_evidence/ (optional)
```

**Privacy guarantees**:
- ✅ All paths in `data/` are gitignored
- ✅ SHA256 hashes prevent tampering
- ✅ Chain of custody tracks all access
- ✅ No data sent to external services (except OpenAI API for analysis)
- ✅ Analysis results stay local

---

## OpenAI API & External Services

### What Gets Sent to OpenAI

When you run analysis:
- ✅ **Text content** of documents (for entity extraction, sentiment analysis)
- ✅ **Email content** (for thread analysis, participant identification)
- ✅ **Image content** (for OCR, scene description via GPT-4 Vision)

### What Does NOT Get Sent

- ❌ File names or directory paths
- ❌ Case IDs or client names
- ❌ Your API key (used for authentication only)
- ❌ Chain of custody data
- ❌ Cross-evidence correlation results (computed locally)

### Privacy Controls

- Use `temperature=0` for deterministic analysis (same input = same output)
- OpenAI does not use API data for model training (per OpenAI API policy)
- All API calls logged in chain of custody
- You control what evidence is analyzed (can exclude sensitive items)

**For maximum privacy**:
- Use self-hosted LLM alternatives (future feature)
- Run analysis on air-gapped systems
- Redact sensitive portions before analysis
- Review OpenAI's privacy policy: https://openai.com/policies/privacy-policy

---

## Compliance & Legal Considerations

### GDPR Compliance

If handling EU personal data:
- ✅ Data processing is local (data controller = you)
- ✅ No unnecessary data sharing
- ✅ Complete audit trails (chain of custody)
- ✅ Right to deletion (just delete `data/` directory)
- ⚠️ OpenAI processing: Review GDPR compliance for your jurisdiction

### Attorney-Client Privilege

For legal professionals:
- ✅ Evidence Toolkit does not break privilege (you remain counsel)
- ✅ Work product doctrine applies to analysis
- ⚠️ Discuss with client before AI analysis of privileged documents
- ✅ Chain of custody supports privilege claims
- ⚠️ Review bar association rules on AI use in your jurisdiction

### Forensic Integrity

For court admissibility:
- ✅ SHA256 verification ensures evidence integrity
- ✅ Complete chain of custody (who, what, when)
- ✅ Deterministic analysis (reproducible results)
- ✅ Model tracking (records AI model versions used)
- ✅ Methodology documentation included in packages

---

## Security Best Practices

### Protecting Your Environment

```bash
# 1. Secure your API key
echo "OPENAI_API_KEY=sk-..." > .env
chmod 600 .env  # Read/write for owner only

# 2. Verify .gitignore is working
git status  # Should NOT show .env or data/ contents

# 3. Encrypt sensitive storage (optional)
# Use encrypted filesystem or disk encryption for data/ directory

# 4. Regular backups (keep private)
tar -czf backup-$(date +%Y%m%d).tar.gz data/
# Store backups on encrypted drive, NOT in git
```

### Multi-User Environments

For shared systems:
```bash
# Restrict access to case data
chmod 700 data/cases/      # Owner only
chmod 700 data/storage/    # Owner only
chmod 700 data/packages/   # Owner only

# Use separate user accounts for different cases
# Or use containerization (Docker) for isolation
```

---

## Incident Response

### If You Accidentally Commit Real Data

**IMMEDIATE ACTIONS**:

```bash
# 1. DO NOT PUSH if you haven't already
# Remove from staging
git reset HEAD data/cases/YOUR-CASE/

# Remove file completely from git history
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch data/cases/YOUR-CASE/document.pdf" \
  --prune-empty --tag-name-filter cat -- --all

# 2. IF YOU ALREADY PUSHED to public repo
# Contact GitHub support to purge from cache
# Consider the data permanently exposed
# Notify affected parties if required by law
```

**LONG-TERM ACTIONS**:
- Review what was exposed
- Assess legal/regulatory obligations
- Update procedures to prevent recurrence
- Consider security audit

---

## Questions & Support

**Privacy Questions**:
- Review this document and `.gitignore`
- Check `examples/` for safe demonstration data
- Consult legal counsel for compliance questions

**Security Issues**:
- Report security vulnerabilities privately
- Do not disclose publicly until patched
- Contact: [security contact information]

**General Questions**:
- See README.md for usage questions
- GitHub Issues for bug reports
- Documentation in docs/ directory

---

## Summary

### ✅ Safe Workflow

1. Place evidence in `data/cases/YOUR-CASE/`
2. Run `uv run evidence-toolkit process-case ...`
3. Review package in `data/packages/YOUR-CASE_*.zip`
4. **NEVER commit anything from `data/`**
5. Use `examples/` for learning/testing only

### ❌ Never Do This

1. ~~Commit files from `data/` directory~~
2. ~~Put real case data in `examples/`~~
3. ~~Share `.env` file with API keys~~
4. ~~Create examples from real cases~~
5. ~~Push to public repo without reviewing git status~~

---

**Your privacy and your clients' confidentiality are paramount. When in doubt, don't commit it.**

**Last Updated**: 2025-10-08 for Evidence Toolkit v3.3.0
**Maintainers**: Review quarterly, update as needed
