#!/usr/bin/env python3
"""
Document Evidence Analyzer - Text Analysis Module

Provides text analysis capabilities for legal document processing,
including word frequency analysis and visualization generation.
"""

import os
import re
import time
import json
import hashlib
from pathlib import Path
from collections import Counter
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple, Union
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for production
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

# OpenAI Responses API integration (NOT chat completions)
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

# Import our structured analysis models
try:
    from .ai_models import DocumentAnalysis, DocumentEntity
    AI_MODELS_AVAILABLE = True
except ImportError:
    AI_MODELS_AVAILABLE = False

# Import validation for schema-compliant output
try:
    from .validation import DocumentValidator
    VALIDATION_AVAILABLE = True
except ImportError:
    VALIDATION_AVAILABLE = False


def ensure_nltk_data():
    """Download required NLTK data if not present"""
    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        nltk.download('punkt', quiet=True)

    try:
        nltk.data.find('corpora/stopwords')
    except LookupError:
        nltk.download('stopwords', quiet=True)


# Initialize NLTK data
ensure_nltk_data()

class DocumentAnalyzer:
    def __init__(self,
                 custom_stop_words: Optional[set] = None,
                 min_word_length: int = 3,
                 verbose: bool = True):
        """
        Initialize document analyzer

        Args:
            custom_stop_words: Additional words to filter out
            min_word_length: Minimum word length to include
            verbose: Whether to print progress messages
        """
        self.stop_words = set(stopwords.words('english'))
        self.min_word_length = min_word_length
        self.verbose = verbose

        # Default business/email stop words
        default_custom_stop_words = {
            'email', 'sent', 'from', 'to', 'cc', 'subject', 'date', 'regards',
            'kind', 'good', 'morning', 'afternoon', 'thank', 'thanks', 'please',
            'would', 'could', 'will', 'shall', 'may', 'might', 'should',
            'com', 'uk', 'co', 'one', 'two', 'three', 'first', 'second',
            'also', 'however', 'therefore', 'moreover', 'furthermore', 'nevertheless'
        }

        # Merge with user-provided custom stop words
        if custom_stop_words:
            self.custom_stop_words = default_custom_stop_words.union(custom_stop_words)
        else:
            self.custom_stop_words = default_custom_stop_words

        self.all_stop_words = self.stop_words.union(self.custom_stop_words)

        # Initialize OpenAI Responses API client (NOT chat completions)
        self.openai_client = None
        self.ai_enabled = False

        if OPENAI_AVAILABLE and AI_MODELS_AVAILABLE:
            api_key = os.getenv('OPENAI_API_KEY')
            if api_key:
                try:
                    self.openai_client = OpenAI(api_key=api_key)
                    self.ai_enabled = True
                    if self.verbose:
                        print("✅ OpenAI Responses API client initialized")
                except Exception as e:
                    if self.verbose:
                        print(f"⚠️  OpenAI client initialization failed: {e}")
            elif self.verbose:
                print("⚠️  OPENAI_API_KEY not set - AI analysis disabled")
        elif self.verbose:
            print("⚠️  OpenAI dependencies not available - AI analysis disabled")

    def clean_text(self, text):
        """Clean and preprocess text for word cloud generation"""
        # Convert to lowercase
        text = text.lower()

        # Remove email headers and addresses
        text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '', text)

        # Remove dates and times
        text = re.sub(r'\b\d{1,2}[/\-]\d{1,2}[/\-]\d{2,4}\b', '', text)
        text = re.sub(r'\b\d{1,2}:\d{2}(?::\d{2})?\b', '', text)

        # Remove phone numbers
        text = re.sub(r'\b\d{5}\s\d{6}\b', '', text)
        text = re.sub(r'\b\d{11}\b', '', text)

        # Remove special characters but keep letters and spaces
        text = re.sub(r'[^a-zA-Z\s]', ' ', text)

        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)

        return text.strip()

    def extract_meaningful_words(self, text: str) -> List[str]:
        """Extract meaningful words from cleaned text"""
        words = word_tokenize(text)

        meaningful_words = []
        for word in words:
            if (len(word) >= self.min_word_length and
                word.isalpha() and
                word.lower() not in self.all_stop_words):
                meaningful_words.append(word.lower())

        return meaningful_words

    def process_files(self, data_dir: Union[str, Path],
                     file_pattern: str = "*.txt") -> Tuple[str, int]:
        """Process all text files in the specified directory"""
        data_path = Path(data_dir)
        all_text = ""
        file_count = 0
        errors = []

        if self.verbose:
            print(f"Processing files from: {data_path}")

        for file_path in data_path.glob(file_pattern):
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                    content = file.read()
                    all_text += " " + content
                    file_count += 1
                    if self.verbose:
                        print(f"✓ Processed: {file_path.name}")
            except Exception as e:
                error_msg = f"Error processing {file_path.name}: {e}"
                errors.append(error_msg)
                if self.verbose:
                    print(f"✗ {error_msg}")

        if self.verbose:
            print(f"\n📊 Processed {file_count} files")
            if errors:
                print(f"⚠️  {len(errors)} files had errors")

        return all_text, file_count

    def generate_word_frequency(self, text: str, top_n: int = 20) -> Dict[str, int]:
        """Generate word frequency analysis"""
        cleaned_text = self.clean_text(text)
        words = self.extract_meaningful_words(cleaned_text)
        word_freq = Counter(words)

        if self.verbose:
            print(f"📝 Total words extracted: {len(words)}")
            print(f"🔤 Unique words: {len(word_freq)}")
            print(f"\n🔝 Top {top_n} most frequent words:")
            for word, count in word_freq.most_common(top_n):
                print(f"  {word}: {count}")

        return dict(word_freq)

    def create_word_cloud(self,
                         word_freq: Dict[str, int],
                         output_file: Optional[str] = None,
                         title: str = "Document Word Cloud Analysis",
                         **wordcloud_kwargs) -> WordCloud:
        """Create and save word cloud visualization"""

        # Default WordCloud parameters
        default_params = {
            'width': 1600,
            'height': 800,
            'background_color': 'white',
            'max_words': 200,
            'colormap': 'viridis',
            'relative_scaling': 0.5,
            'random_state': 42,
            'collocations': False
        }

        # Merge with user parameters
        params = {**default_params, **wordcloud_kwargs}
        wordcloud = WordCloud(**params).generate_from_frequencies(word_freq)

        # Create the plot
        plt.figure(figsize=(20, 10))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis('off')
        plt.title(title, fontsize=24, pad=20)
        plt.tight_layout(pad=0)

        if output_file:
            plt.savefig(output_file, dpi=300, bbox_inches='tight')
            if self.verbose:
                print(f"💾 Word cloud saved as: {output_file}")

        plt.close()  # Don't show, just close
        return wordcloud

    def create_frequency_chart(self,
                              word_freq: Dict[str, int],
                              output_file: Optional[str] = None,
                              top_n: int = 30,
                              title: Optional[str] = None) -> None:
        """Create a frequency bar chart for top words"""
        # Get top words
        if isinstance(word_freq, Counter):
            top_words = dict(word_freq.most_common(top_n))
        else:
            # Sort dictionary by value and take top_n
            sorted_items = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
            top_words = dict(sorted_items[:top_n])

        if not top_words:
            if self.verbose:
                print("⚠️  No words to chart")
            return

        plt.figure(figsize=(15, 10))
        words = list(top_words.keys())
        frequencies = list(top_words.values())

        bars = plt.barh(words, frequencies, color='skyblue')
        plt.xlabel('Frequency', fontsize=12)
        plt.ylabel('Words', fontsize=12)

        chart_title = title or f'Top {len(words)} Most Frequent Words'
        plt.title(chart_title, fontsize=16)
        plt.gca().invert_yaxis()

        # Add value labels on bars
        for bar, freq in zip(bars, frequencies):
            plt.text(bar.get_width() + max(frequencies) * 0.01,
                    bar.get_y() + bar.get_height()/2,
                    str(freq), ha='left', va='center')

        plt.tight_layout()

        if output_file:
            plt.savefig(output_file, dpi=300, bbox_inches='tight')
            if self.verbose:
                print(f"📊 Frequency chart saved as: {output_file}")

        plt.close()  # Don't show, just close

    def analyze_directory(self,
                         data_dir: Union[str, Path],
                         output_dir: Optional[Union[str, Path]] = None,
                         file_pattern: str = "*.txt") -> Dict[str, Union[str, int, Dict]]:
        """Run complete analysis on a directory of text files"""

        if self.verbose:
            print("🚀 Starting Document Analysis")
            print("=" * 50)

        # Process all files
        all_text, file_count = self.process_files(data_dir, file_pattern)

        if not all_text.strip():
            if self.verbose:
                print("❌ No text found to process!")
            return {'status': 'error', 'message': 'No text found'}

        # Generate word frequency
        word_freq = self.generate_word_frequency(all_text)

        if not word_freq:
            if self.verbose:
                print("❌ No meaningful words found!")
            return {'status': 'error', 'message': 'No meaningful words found'}

        # Setup output directory
        if output_dir:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            wordcloud_file = output_path / "word_cloud.png"
            frequency_file = output_path / "word_frequency.png"
        else:
            wordcloud_file = "word_cloud.png"
            frequency_file = "word_frequency.png"

        # Create visualizations
        if self.verbose:
            print("\n🎨 Creating visualizations...")

        wordcloud = self.create_word_cloud(word_freq, str(wordcloud_file))
        self.create_frequency_chart(word_freq, str(frequency_file))

        if self.verbose:
            print("\n✅ Analysis complete!")

        return {
            'status': 'success',
            'files_processed': file_count,
            'total_words': sum(word_freq.values()),
            'unique_words': len(word_freq),
            'word_frequency': word_freq,
            'wordcloud_file': str(wordcloud_file),
            'frequency_chart_file': str(frequency_file)
        }

    def analyze_text(self,
                    text: str,
                    output_dir: Optional[Union[str, Path]] = None) -> Dict[str, Union[str, int, Dict]]:
        """Run analysis on raw text input"""

        if self.verbose:
            print("🚀 Starting Text Analysis")
            print("=" * 30)

        if not text.strip():
            return {'status': 'error', 'message': 'No text provided'}

        # Generate word frequency
        word_freq = self.generate_word_frequency(text)

        if not word_freq:
            return {'status': 'error', 'message': 'No meaningful words found'}

        # Setup output files if directory provided
        wordcloud_file = None
        frequency_file = None

        if output_dir:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            wordcloud_file = str(output_path / "word_cloud.png")
            frequency_file = str(output_path / "word_frequency.png")

        # Create visualizations
        if self.verbose:
            print("\n🎨 Creating visualizations...")

        wordcloud = self.create_word_cloud(word_freq, wordcloud_file)
        self.create_frequency_chart(word_freq, frequency_file)

        if self.verbose:
            print("\n✅ Analysis complete!")

        result = {
            'status': 'success',
            'total_words': sum(word_freq.values()),
            'unique_words': len(word_freq),
            'word_frequency': word_freq
        }

        if wordcloud_file:
            result['wordcloud_file'] = wordcloud_file
        if frequency_file:
            result['frequency_chart_file'] = frequency_file

        # Add AI analysis if available
        if self.ai_enabled:
            ai_analysis = self.analyze_with_ai(text)
            if ai_analysis:
                result['ai_analysis'] = {
                    'summary': ai_analysis.summary,
                    'entities': [entity.dict() for entity in ai_analysis.entities],
                    'document_type': ai_analysis.document_type,
                    'sentiment': ai_analysis.sentiment,
                    'legal_significance': ai_analysis.legal_significance,
                    'risk_flags': ai_analysis.risk_flags,
                    'confidence_overall': ai_analysis.confidence_overall
                }
            else:
                result['ai_analysis'] = None

        return result

    def analyze_with_ai(self, text: str) -> Optional[DocumentAnalysis]:
        """
        Perform structured AI analysis using OpenAI Responses API.

        CRITICAL: This uses OpenAI Responses API, NOT chat completions API.
        This is a placeholder for Phase 1 Week 1-2 implementation.

        Args:
            text: Document text to analyze

        Returns:
            DocumentAnalysis object with structured insights or None if disabled
        """
        if not self.ai_enabled:
            if self.verbose:
                print("⚠️  AI analysis disabled - OpenAI client not available")
            return None

        if not text.strip():
            if self.verbose:
                print("⚠️  No text provided for AI analysis")
            return None

        try:
            if self.verbose:
                print("🤖 Analyzing document with OpenAI Responses API...")

            # Create comprehensive legal analysis prompt
            legal_analysis_prompt = """You are a forensic document analyzer for legal evidence processing.

Analyze the provided document text with the following requirements:

1. **Summary**: Provide a concise summary focusing on legal significance and key points
2. **Entity Extraction**: Identify people, organizations, dates, and legal terms with high confidence
3. **Document Classification**: Classify as email, letter, contract, or filing based on content structure
4. **Sentiment Analysis**: Assess tone as hostile, neutral, or professional based on language patterns
5. **Legal Significance**: Rate as critical, high, medium, or low based on potential legal impact
6. **Risk Flags**: Identify any threatening language, deadlines, PII, confidential content, time-sensitive matters, retaliation indicators, harassment, or discrimination

Provide confidence scores (0.0-1.0) for all extractions. Be conservative with confidence - only use >0.9 for extremely clear cases.

For entity context, include the surrounding text that supports the identification."""

            # Call OpenAI Responses API - this is the CORRECT API (NOT chat completions)
            response = self.openai_client.responses.parse(
                model="gpt-4o-2024-08-06",
                input=[
                    {"role": "system", "content": legal_analysis_prompt},
                    {"role": "user", "content": text}
                ],
                text_format=DocumentAnalysis
            )

            # Handle responses correctly for Responses API
            if response.status == "completed" and response.output_parsed:
                if self.verbose:
                    print(f"✅ AI analysis complete - confidence: {response.output_parsed.confidence_overall:.2f}")
                return response.output_parsed
            elif response.status == "incomplete":
                if self.verbose:
                    print(f"❌ AI analysis incomplete: {response.incomplete_details}")
                return None
            else:
                # Check for refusal in output
                if (response.output and len(response.output) > 0 and
                    len(response.output[0].content) > 0 and
                    response.output[0].content[0].type == "refusal"):
                    if self.verbose:
                        print(f"❌ AI analysis refused: {response.output[0].content[0].refusal}")
                return None

        except Exception as e:
            if self.verbose:
                print(f"❌ AI analysis failed: {e}")
            return None

    def _generate_evidence_id(self, text: str, source_path: str = None) -> str:
        """Generate evidence ID from content and source."""
        content_hash = hashlib.sha256(text.encode('utf-8')).hexdigest()[:12]
        source_hash = hashlib.sha256((source_path or "unknown").encode('utf-8')).hexdigest()[:6]
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d")
        return f"doc_{content_hash}_{source_hash}_{timestamp}"

    def _generate_sha256(self, text: str) -> str:
        """Generate SHA256 hash of text content."""
        return hashlib.sha256(text.encode('utf-8')).hexdigest()

    def _create_chain_of_custody(self, actor: str = None) -> List[Dict]:
        """Create initial chain of custody entry."""
        timestamp = datetime.now(timezone.utc).isoformat()
        actor = actor or "document-analyzer@evidence-toolkit"

        return [
            {
                "ts": timestamp,
                "actor": actor,
                "action": "ingest",
                "note": "Document ingested for analysis"
            },
            {
                "ts": timestamp,
                "actor": actor,
                "action": "analysis",
                "note": "Text analysis and AI processing completed"
            }
        ]

    def create_schema_compliant_analysis(self,
                                       text: str,
                                       case_id: str = None,
                                       source_path: str = None,
                                       actor: str = None) -> Dict:
        """
        Create schema-compliant analysis document following document.v1.json.

        Args:
            text: Document text to analyze
            case_id: Case identifier for legal tracking
            source_path: Original file path
            actor: Analyst identifier

        Returns:
            Schema-compliant analysis document
        """
        # Generate metadata
        evidence_id = self._generate_evidence_id(text, source_path)
        sha256_hash = self._generate_sha256(text)
        timestamp = datetime.now(timezone.utc).isoformat()

        # Perform AI analysis
        ai_analysis = None
        if self.ai_enabled:
            ai_analysis = self.analyze_with_ai(text)

        # Create base evidence structure
        evidence = {
            "evidence_id": evidence_id,
            "sha256": sha256_hash,
            "mime_type": "text/plain",
            "bytes": len(text.encode('utf-8')),
            "ingested_at": timestamp,
            "source_path": source_path or "unknown"
        }

        # Create analysis structure
        analysis_id = f"{evidence_id}_analysis"

        # Default analysis outputs for text processing
        outputs = {
            "summary": "Document analysis completed with text processing and visualization",
            "document_type": "unknown"
        }

        # If AI analysis succeeded, use its results
        if ai_analysis:
            outputs = {
                "summary": ai_analysis.summary,
                "entities": [
                    {
                        "name": entity.name,
                        "type": entity.type,
                        "confidence": entity.confidence,
                        "context": entity.context
                    } for entity in ai_analysis.entities
                ],
                "document_type": ai_analysis.document_type,
                "sentiment": ai_analysis.sentiment,
                "legal_significance": ai_analysis.legal_significance,
                "risk_flags": ai_analysis.risk_flags
            }
            confidence_overall = ai_analysis.confidence_overall
        else:
            # Fallback confidence when AI analysis is not available
            confidence_overall = 0.5
            outputs["entities"] = []
            outputs["sentiment"] = "neutral"
            outputs["legal_significance"] = "medium"
            outputs["risk_flags"] = []

        analysis = {
            "analysis_id": analysis_id,
            "created_at": timestamp,
            "model": {
                "name": "gpt-4o-2024-08-06" if ai_analysis else "text-analyzer-v1",
                "revision": "2024-08-06" if ai_analysis else "1.0.0"
            },
            "parameters": {
                "temperature": 0.0 if ai_analysis else None,
                "prompt_hash": None,  # Would be populated with actual prompt hash
                "token_usage_in": None,  # Would be populated from API response
                "token_usage_out": None  # Would be populated from API response
            },
            "outputs": outputs,
            "confidence_overall": confidence_overall
        }

        # Create complete schema-compliant document
        schema_document = {
            "schema_version": "1.0.0",
            "case_id": case_id,
            "evidence": evidence,
            "analyses": [analysis],
            "chain_of_custody": self._create_chain_of_custody(actor)
        }

        return schema_document

    def validate_and_save_analysis(self,
                                 schema_document: Dict,
                                 output_file: str = None) -> bool:
        """
        Validate schema document and save to file if valid.

        Args:
            schema_document: Schema-compliant analysis document
            output_file: Output JSON file path

        Returns:
            True if validation passed and file saved, False otherwise
        """
        if not VALIDATION_AVAILABLE:
            if self.verbose:
                print("⚠️  Schema validation not available - saving without validation")
            if output_file:
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(schema_document, f, indent=2, ensure_ascii=False)
                if self.verbose:
                    print(f"💾 Analysis saved to: {output_file}")
            return True

        # Validate against schema
        validator = DocumentValidator()
        errors = validator.validate(schema_document)

        if errors:
            if self.verbose:
                print("❌ Schema validation failed:")
                for error in errors:
                    print(f"   - {error}")
            return False

        if self.verbose:
            print("✅ Schema validation passed")

        # Save validated document
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(schema_document, f, indent=2, ensure_ascii=False)
            if self.verbose:
                print(f"💾 Validated analysis saved to: {output_file}")

        return True

# Convenience functions for common use cases
def analyze_documents(data_dir: Union[str, Path],
                     output_dir: Optional[Union[str, Path]] = None,
                     custom_stop_words: Optional[set] = None,
                     verbose: bool = True) -> Dict:
    """Convenience function to analyze documents in a directory"""
    analyzer = DocumentAnalyzer(custom_stop_words=custom_stop_words, verbose=verbose)
    return analyzer.analyze_directory(data_dir, output_dir)


def analyze_text_content(text: str,
                        output_dir: Optional[Union[str, Path]] = None,
                        custom_stop_words: Optional[set] = None,
                        verbose: bool = True) -> Dict:
    """Convenience function to analyze raw text"""
    analyzer = DocumentAnalyzer(custom_stop_words=custom_stop_words, verbose=verbose)
    return analyzer.analyze_text(text, output_dir)


def create_schema_compliant_document_analysis(text: str,
                                            case_id: str = None,
                                            source_path: str = None,
                                            actor: str = None,
                                            output_file: str = None,
                                            custom_stop_words: Optional[set] = None,
                                            verbose: bool = True) -> Dict:
    """
    Convenience function to create schema-compliant document analysis.

    Args:
        text: Document text to analyze
        case_id: Case identifier for legal tracking
        source_path: Original file path
        actor: Analyst identifier
        output_file: Output JSON file path
        custom_stop_words: Additional words to filter out
        verbose: Whether to print progress messages

    Returns:
        Schema-compliant analysis document
    """
    analyzer = DocumentAnalyzer(custom_stop_words=custom_stop_words, verbose=verbose)
    schema_document = analyzer.create_schema_compliant_analysis(
        text=text,
        case_id=case_id,
        source_path=source_path,
        actor=actor
    )

    # Validate and save if requested
    if output_file:
        success = analyzer.validate_and_save_analysis(schema_document, output_file)
        if not success and verbose:
            print("⚠️  Schema validation failed - document not saved")

    return schema_document


def main():
    """Command line interface - kept for backwards compatibility"""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python word_cloud_analyzer.py <data_directory>")
        print("Analyzes text files in the specified directory")
        return 1

    data_dir = sys.argv[1]

    if not Path(data_dir).exists():
        print(f"❌ Directory '{data_dir}' not found!")
        return 1

    # Run analysis
    result = analyze_documents(data_dir)

    if result['status'] == 'success':
        print(f"\n📊 Analysis Summary:")
        print(f"   Files processed: {result['files_processed']}")
        print(f"   Total words: {result['total_words']}")
        print(f"   Unique words: {result['unique_words']}")
        return 0
    else:
        print(f"❌ Analysis failed: {result.get('message', 'Unknown error')}")
        return 1

if __name__ == "__main__":
    main()