# Current Task Context: PDF Processing Enhancement

*Development session context for adding intelligent PDF processing to Evidence Toolkit*

## 🎯 Current Task
**Add comprehensive PDF processing with minimal code changes to existing architecture**

### What We Know Works ✅
- Document analysis: Text processing, word clouds, frequency analysis, AI analysis
- Image analysis: Content-addressed storage, OCR, visual AI analysis
- Email analysis: Thread reconstruction, escalation detection, participant analysis
- Unified CLI: Automatic routing between document/image/email analysis
- All achieve 4.6/5 forensic standard

### What We're Building 🔄
**Intelligent PDF processing** that leverages existing architecture:
- Text-extractable PDFs → Route to document analysis
- Non-extractable PDFs → Route to image analysis (OCR + visual AI)
- **Minimal code changes** - work with existing systems

## 📋 Implementation Strategy

### Leverage Existing Routing
```python
# CLI already routes based on detect_file_type() in utils.py
def detect_file_type(file_path: Path) -> str:
    if file_path.suffix.lower() == '.pdf':
        if can_extract_text_from_pdf(file_path):
            return 'document'  # → DocumentAnalyzer
        else:
            return 'image'     # → ImageAnalyzer (OCR + AI)
    # existing logic...
```

### Key Architecture Files to Modify
- `document-evidence-analyzer/src/document_analyzer/utils.py` - File type detection
- `document-evidence-analyzer/src/document_analyzer/word_cloud_analyzer.py:155-185` - File processing
- `pyproject.toml` - Add PDF processing dependencies (pdfplumber, pdf2image)

## 🔧 Development Tasks

### Phase 1: PDF Text Extraction (Minimal Changes)
1. **Add PDF text extraction** to `DocumentAnalyzer.process_files()`
   - Use `pdfplumber` for text extraction
   - Fallback gracefully for extraction failures

2. **Enhance file type detection** in `utils.py`
   - Make `detect_file_type()` try PDF text extraction
   - Route text-extractable PDFs → document analysis
   - Route non-extractable PDFs → image analysis

3. **Add dependencies** to `pyproject.toml`
   - `pdfplumber` for PDF text extraction
   - `pdf2image` for PDF→image conversion (image analysis pipeline)

### Phase 2: Testing & Validation
1. **Test with various PDF types**
   - Text-based PDFs (contracts, letters)
   - Scanned PDFs (court documents)
   - Encrypted/protected PDFs
   - Mixed content PDFs

2. **Verify existing workflows still work**
   - Document analysis unchanged for .txt files
   - Image analysis unchanged for image files
   - Email analysis unchanged

## 🧭 Context Priming Commands

### Current Architecture Review
```bash
# Check file type detection logic
grep -A 10 -B 5 "detect_file_type" document-evidence-analyzer/src/document_analyzer/utils.py

# Review file processing in DocumentAnalyzer
grep -A 15 -B 5 "process_files" document-evidence-analyzer/src/document_analyzer/word_cloud_analyzer.py

# Check CLI routing logic
grep -A 10 "detect_file_type" document-evidence-analyzer/src/document_analyzer/cli.py
```

### PDF Processing Status
```bash
# Check current PDF handling
grep -r "\.pdf" document-evidence-analyzer/src/ --include="*.py"

# See current dependencies
grep -A 5 -B 5 "dependencies" document-evidence-analyzer/pyproject.toml

# Test current PDF behavior (will show the problem)
echo "Test PDF content" > test.pdf
uv run document-analyzer analyze . --file-pattern "*.pdf" --quiet
```

### Development Environment Check
```bash
# Verify CLI routing works
uv run document-analyzer --help
source .venv/bin/activate && evidence-toolkit --help

# Check current file processing
ls document-evidence-analyzer/src/document_analyzer/ | grep -E "(utils|word_cloud|cli)"
```

## 📊 Success Metrics
- **Text PDFs**: Extract cleanly → word clouds and frequency analysis work
- **Scanned PDFs**: Route to image analysis → OCR + visual AI analysis
- **Encrypted PDFs**: Graceful fallback → route to image analysis
- **Existing workflows**: No regression in .txt, .eml, image file processing
- **Minimal code**: <50 lines of changes total
- **User experience**: Transparent - PDFs "just work" in existing commands

## 🎯 Next Action
1. Add PDF text extraction dependencies to `pyproject.toml`
2. Enhance `detect_file_type()` with PDF intelligence
3. Add PDF text extraction to `DocumentAnalyzer.process_files()`

---

*This context focuses specifically on the PDF processing enhancement task, leveraging existing Evidence Toolkit architecture*