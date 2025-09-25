#!/usr/bin/env python3
"""
Document Evidence Analyzer - Text Analysis Module

Provides text analysis capabilities for legal document processing,
including word frequency analysis and visualization generation.
"""

import os
import re
from pathlib import Path
from collections import Counter
from typing import Dict, List, Optional, Tuple, Union
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for production
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize


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

        return result

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