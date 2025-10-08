# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

The Document Evidence Analyzer is a Python library for analyzing text documents and generating visualizations for legal evidence processing. It's part of the Evidence Toolkit project and provides both programmatic APIs and CLI tools for document analysis.

## Architecture

The project follows a modular architecture with two main analysis engines:

- **DocumentAnalyzer** (`src/document_analyzer/word_cloud_analyzer.py`): Core text analysis engine for word frequency analysis and visualization generation
- **RetaliationAnalyzer** (`src/document_analyzer/retaliation_analyzer.py`): Specialized analyzer for detecting retaliation patterns in communication timelines

Both analyzers are exposed through a unified CLI interface (`src/document_analyzer/cli.py`) and can be used programmatically via the main module exports in `src/document_analyzer/__init__.py`.

## Development Commands

### Installation and Environment Setup
```bash
# Using UV (recommended)
uv venv
uv pip install -e .

# Using pip
pip install -e .
```

### Running the CLI
```bash
# Basic document analysis
document-analyzer analyze ./documents

# Retaliation pattern analysis
document-analyzer retaliation ./documents

# Get version info
document-analyzer version
```

### Testing
```bash
# Run tests (if available)
pytest tests/

# Using UV
uv run pytest tests/
```

### Package Management
The project uses modern Python packaging with `pyproject.toml`. Dependencies are managed in both `pyproject.toml` and `requirements.txt`. The main dependencies include:
- wordcloud, matplotlib, seaborn (visualization)
- nltk (natural language processing)
- pandas (data processing)
- click (CLI framework)

## Key Components

### Core Analysis Pipeline
1. **Text Processing**: Uses NLTK for tokenization and stop word filtering
2. **Frequency Analysis**: Builds word frequency distributions using Counter
3. **Visualization Generation**: Creates word clouds and frequency charts using matplotlib/wordcloud
4. **Output Management**: Saves results as images and optionally JSON data

### CLI Commands Structure
- `analyze`: General document analysis with word clouds and frequency charts
- `retaliation`: Specialized timeline analysis for retaliation pattern detection
- Both commands support customizable output directories, file patterns, and verbosity levels

### Module Exports
The main package exposes these key functions and classes:
- `DocumentAnalyzer`, `analyze_documents`, `analyze_text_content` (general analysis)
- `RetaliationAnalyzer`, `RetaliationSummary`, `analyze_retaliation_case` (retaliation analysis)
- `ensure_nltk_data` (utility for NLTK setup)

## File Organization
- `src/document_analyzer/`: Main package code
- `tests/`: Test files (minimal test structure currently)
- `examples/`: Sample data and output examples
- `analysis_output/`: Default output directory for generated visualizations