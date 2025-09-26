# Document Evidence Analyzer

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A powerful Python library for analyzing text documents and generating visualizations for legal evidence processing. Part of the [Evidence Toolkit](https://github.com/evidence-toolkit) project.

## 🚀 Features

- **Text Analysis**: Advanced natural language processing for legal documents
- **Email Thread Analysis**: AI-powered analysis of email communications with escalation detection
- **Word Cloud Generation**: Create compelling visual representations of document themes
- **Frequency Analysis**: Statistical analysis of word patterns and frequency distributions
- **Legal Document Processing**: Specialized filters for business and legal correspondence
- **Batch Processing**: Analyze entire directories of documents efficiently
- **Customizable Output**: Generate publication-ready visualizations
- **Command Line Interface**: Easy-to-use CLI for quick analysis
- **Python API**: Full programmatic access for custom workflows

## 📦 Installation

### Requirements

- Python 3.8 or higher
- pip or uv for package management

### Install from Source

```bash
git clone https://github.com/evidence-toolkit/document-evidence-analyzer.git
cd document-evidence-analyzer
pip install -e .
```

### Using UV (Recommended)

```bash
git clone https://github.com/evidence-toolkit/document-evidence-analyzer.git
cd document-evidence-analyzer
uv venv
uv pip install -e .
```

## 🛠️ Quick Start

### Command Line Usage

Analyze documents in a directory:

```bash
# Basic document analysis
document-analyzer analyze ./documents

# Email thread analysis
document-analyzer email ./email_files --case-id CASE123

# Save to specific output directory
document-analyzer analyze ./documents -o ./analysis_results

# Email analysis with JSON export
document-analyzer email ./emails --json-output email_analysis.json

# Add custom stop words and run quietly
document-analyzer analyze ./documents --stop-words "company,internal" --quiet
```

### Python API

```python
from document_analyzer import DocumentAnalyzer, analyze_documents

# Quick analysis of a directory
result = analyze_documents('./documents', output_dir='./results')
print(f"Processed {result['files_processed']} files")
print(f"Found {result['unique_words']} unique words")

# Advanced usage with custom settings
analyzer = DocumentAnalyzer(
    custom_stop_words={'confidential', 'internal'},
    min_word_length=4,
    verbose=True
)

# Analyze directory
result = analyzer.analyze_directory('./documents', './output')

# Analyze raw text
text_result = analyzer.analyze_text("Your text content here...")
```

## 📊 Output Examples

The analyzer generates two main visualizations:

### Word Cloud
![Word Cloud Example](examples/outputs/word_cloud.png)

A visual representation where word size corresponds to frequency, perfect for:
- Quick thematic overview
- Presentation materials
- Report summaries

### Frequency Chart
![Frequency Chart Example](examples/outputs/word_frequency.png)

A precise bar chart showing exact word counts, ideal for:
- Statistical analysis
- Evidence documentation
- Quantitative reporting

## 🎯 Use Cases

### Legal Professionals
- **Case Analysis**: Identify key themes in legal correspondence
- **Evidence Preparation**: Generate visual summaries for court presentations
- **Document Review**: Quickly assess large volumes of documents

### Workplace Investigations
- **Communication Analysis**: Analyze email chains and internal communications with AI-powered escalation detection
- **Pattern Recognition**: Identify recurring issues, themes, and retaliation patterns
- **Report Generation**: Create compelling visual evidence and forensic timelines

### Research & Academia
- **Content Analysis**: Systematic analysis of text corpora
- **Thematic Research**: Identify patterns in qualitative data
- **Publication Graphics**: Generate publication-ready visualizations

## ⚙️ Configuration

### Custom Stop Words

```python
# Add domain-specific terms to filter out
analyzer = DocumentAnalyzer(
    custom_stop_words={
        'company_name', 'internal', 'confidential',
        'department', 'meeting', 'email'
    }
)
```

### Visualization Customization

```python
# Customize word cloud appearance
analyzer.create_word_cloud(
    word_freq,
    output_file='custom_cloud.png',
    title='Custom Analysis',
    colormap='plasma',
    max_words=150,
    background_color='black'
)
```

## 📁 Project Structure

```
document-evidence-analyzer/
├── src/
│   └── document_analyzer/
│       ├── __init__.py          # Main module exports
│       ├── word_cloud_analyzer.py  # Core analysis engine
│       └── cli.py               # Command line interface
├── examples/
│   ├── sample_data/             # Example input files
│   └── outputs/                 # Example output visualizations
├── tests/                       # Unit tests
├── docs/                        # Documentation
├── pyproject.toml               # Modern Python packaging
├── requirements.txt             # Dependencies
└── README.md                    # This file
```

## 🔧 API Reference

### DocumentAnalyzer Class

The main analysis engine with the following key methods:

#### `__init__(custom_stop_words=None, min_word_length=3, verbose=True)`
Initialize the analyzer with custom settings.

#### `analyze_directory(data_dir, output_dir=None, file_pattern="*.txt")`
Analyze all text files in a directory.

**Returns:** Dictionary with analysis results including:
- `status`: 'success' or 'error'
- `files_processed`: Number of files analyzed
- `total_words`: Total words found
- `unique_words`: Number of unique words
- `word_frequency`: Dictionary of word frequencies
- `wordcloud_file`: Path to generated word cloud
- `frequency_chart_file`: Path to generated frequency chart

#### `analyze_text(text, output_dir=None)`
Analyze raw text content.

#### `create_word_cloud(word_freq, output_file=None, **kwargs)`
Generate word cloud visualization.

#### `create_frequency_chart(word_freq, output_file=None, top_n=30)`
Generate frequency bar chart.

### Convenience Functions

#### `analyze_documents(data_dir, output_dir=None, custom_stop_words=None, verbose=True)`
Quick function to analyze a directory of documents.

#### `analyze_text_content(text, output_dir=None, custom_stop_words=None, verbose=True)`
Quick function to analyze raw text.

## 🧪 Testing

Run the test suite:

```bash
# Using pytest
pytest tests/

# Using UV
uv run pytest tests/
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Development Setup

```bash
git clone https://github.com/evidence-toolkit/document-evidence-analyzer.git
cd document-evidence-analyzer
uv venv
uv pip install -e ".[dev]"
```

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Related Projects

- [Image Analysis](https://github.com/evidence-toolkit/image-analysis) - AI-powered forensic image analysis
- [Evidence Toolkit](https://github.com/evidence-toolkit) - Complete legal evidence analysis suite

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/evidence-toolkit/document-evidence-analyzer/issues)
- **Discussions**: [GitHub Discussions](https://github.com/evidence-toolkit/document-evidence-analyzer/discussions)
- **Documentation**: [Full Documentation](https://evidence-toolkit.github.io/document-evidence-analyzer/)

## 🙏 Acknowledgments

- Built with [WordCloud](https://github.com/amueller/word_cloud) by Andreas Mueller
- Natural language processing powered by [NLTK](https://www.nltk.org/)
- Visualizations created with [Matplotlib](https://matplotlib.org/)

---

**Part of the Evidence Toolkit Project** - Democratizing access to professional-grade legal evidence analysis tools.