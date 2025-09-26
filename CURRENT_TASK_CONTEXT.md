# Current Task Context: Email Analysis Implementation

*Development session context for adding email chain analysis to Evidence Toolkit*

## 🎯 Current Task
**Add email chain analysis using our proven forensic-grade architecture patterns**

### What We Know Works ✅
- Document analysis: OpenAI Responses API + Pydantic models + schema validation
- Image analysis: Same pattern with content-addressed storage + chain of custody
- Both achieve 4.6/5 forensic standard

### What We're Building 🔄
Email analysis that follows the **exact same patterns** for consistency

## 📋 Implementation Strategy

### Pattern to Follow
```python
# This works in document_analyzer/word_cloud_analyzer.py:analyze_with_ai()
response = self.openai_client.responses.parse(
    model="gpt-4o-2024-08-06",
    input=[{"role": "system", "content": prompt}, {"role": "user", "content": text}],
    text_format=DocumentAnalysis  # Pydantic model
)
```

### Key Architecture Files to Reference
- `document-evidence-analyzer/src/document_analyzer/ai_models.py` - Pydantic model structure
- `document-evidence-analyzer/src/document_analyzer/word_cloud_analyzer.py:410-485` - AI analysis implementation
- `EMAIL_FORENSIC_ARCHITECTURE.md` - Implementation plan

## 🔧 Development Tasks

### Week 1: Email Models + Parser
1. Create `email_models.py` following `ai_models.py` patterns
2. Create `email_parser.py` for .eml/.msg/.mbox parsing
3. Integrate with existing evidence storage system

### Week 2: AI Analysis Engine
1. Create `email_analyzer.py` following `word_cloud_analyzer.py` patterns
2. Implement `analyze_email_thread()` using OpenAI Responses API
3. Add CLI integration to existing command structure

### Week 3: Cross-Evidence Intelligence
1. Add AI detection of email→document/image references
2. Extend evidence database schema for thread relationships
3. Generate comprehensive case analysis across all evidence types

## 🧭 Context Priming Commands

### Architecture Pattern Review
```bash
# Study our proven AI analysis pattern
grep -A 20 -B 5 "responses\.parse" document-evidence-analyzer/src/document_analyzer/word_cloud_analyzer.py

# Review our Pydantic model structure
cat document-evidence-analyzer/src/document_analyzer/ai_models.py

# Check image analysis patterns for comparison
grep -A 10 "openai" image-analysis/image_analysis/models.py
```

### Current Implementation Status
```bash
# See what email-related code already exists
find . -name "*email*" -type f
grep -r "email" . --include="*.py" | head -5

# Check existing CLI structure to extend
grep -A 5 "subparser" document-evidence-analyzer/src/document_analyzer/cli.py
```

### Development Environment Check
```bash
# Verify our tools work
uv run document-analyzer --help | grep -A 3 "commands"
ls document-evidence-analyzer/src/document_analyzer/ | grep -E "(ai_|models|analyzer)"
```

## 📊 Success Metrics
- Email analysis achieves same 4.6/5 quality as document/image analysis
- Uses identical OpenAI Responses API patterns
- Integrates seamlessly with existing CLI and evidence storage
- Provides thread reconstruction + escalation detection + sentiment analysis

## 🎯 Next Action
Start with creating `email_models.py` following the exact structure of `DocumentAnalysis` in `ai_models.py`

---

*This context focuses specifically on the email analysis development task, referencing our proven patterns*