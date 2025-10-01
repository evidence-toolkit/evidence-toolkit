#!/usr/bin/env python3
"""
Word Cloud Generator for Data Dump Analysis
Processes text files and creates visualizations of word frequency
"""

import os
import re
from pathlib import Path
from collections import Counter
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

class DataDumpWordCloud:
    def __init__(self, data_dir="data_dump"):
        self.data_dir = Path(data_dir)
        self.stop_words = set(stopwords.words('english'))

        # Add custom stop words for email/business context
        self.custom_stop_words = {
            'email', 'sent', 'from', 'to', 'cc', 'subject', 'date', 'regards',
            'kind', 'good', 'morning', 'afternoon', 'thank', 'thanks', 'please',
            'would', 'could', 'will', 'shall', 'may', 'might', 'should',
            'com', 'uk', 'co', 'sainsburys', 'mysainsburys', 'paul', 'boucherat',
            'amy', 'martin', 'michael', 'kicks', 'rachel', 'hemmings', 'nick', 'ringrose',
            'one', 'two', 'three', 'first', 'second', 'also', 'however',
            'therefore', 'moreover', 'furthermore', 'nevertheless'
        }

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

    def extract_meaningful_words(self, text):
        """Extract meaningful words from cleaned text"""
        # Tokenize
        words = word_tokenize(text)

        # Filter words
        meaningful_words = []
        for word in words:
            if (len(word) > 2 and  # At least 3 characters
                word.isalpha() and  # Only alphabetic characters
                word.lower() not in self.all_stop_words):  # Not a stop word
                meaningful_words.append(word.lower())

        return meaningful_words

    def process_files(self):
        """Process all text files in the data directory"""
        all_text = ""
        file_count = 0

        print(f"Processing files from: {self.data_dir}")

        for file_path in self.data_dir.glob("*.txt"):
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                    content = file.read()
                    all_text += " " + content
                    file_count += 1
                    print(f"✓ Processed: {file_path.name}")
            except Exception as e:
                print(f"✗ Error processing {file_path.name}: {e}")

        print(f"\n📊 Processed {file_count} files")
        return all_text

    def generate_word_frequency(self, text):
        """Generate word frequency analysis"""
        cleaned_text = self.clean_text(text)
        words = self.extract_meaningful_words(cleaned_text)

        word_freq = Counter(words)

        print(f"📝 Total words extracted: {len(words)}")
        print(f"🔤 Unique words: {len(word_freq)}")

        # Show top 20 words
        print("\n🔝 Top 20 most frequent words:")
        for word, count in word_freq.most_common(20):
            print(f"  {word}: {count}")

        return word_freq

    def create_word_cloud(self, word_freq, output_file="word_cloud.png"):
        """Create and save word cloud visualization"""

        # Create WordCloud object with custom parameters
        wordcloud = WordCloud(
            width=1600,
            height=800,
            background_color='white',
            max_words=133,
            colormap='viridis',
            relative_scaling=0.5,
            random_state=37,
            collocations=False
        ).generate_from_frequencies(word_freq)

        # Create the plot
        plt.figure(figsize=(20, 10))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis('off')
        plt.title('Word Cloud from Data Dump Analysis', fontsize=24, pad=20)

        # Save the plot
        plt.tight_layout(pad=0)
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"\n💾 Word cloud saved as: {output_file}")

        # Display the plot
        plt.show()

        return wordcloud

    def create_frequency_chart(self, word_freq, output_file="word_frequency.png", top_n=30):
        """Create a frequency bar chart for top words"""
        top_words = dict(word_freq.most_common(top_n))

        plt.figure(figsize=(15, 10))
        words = list(top_words.keys())
        frequencies = list(top_words.values())

        bars = plt.barh(words, frequencies, color='skyblue')
        plt.xlabel('Frequency', fontsize=12)
        plt.ylabel('Words', fontsize=12)
        plt.title(f'Top {top_n} Most Frequent Words', fontsize=16)
        plt.gca().invert_yaxis()

        # Add value labels on bars
        for bar, freq in zip(bars, frequencies):
            plt.text(bar.get_width() + 0.1, bar.get_y() + bar.get_height()/2,
                    str(freq), ha='left', va='center')

        plt.tight_layout()
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"📊 Frequency chart saved as: {output_file}")
        plt.show()

    def run_analysis(self):
        """Run complete word cloud analysis"""
        print("🚀 Starting Word Cloud Analysis")
        print("=" * 50)

        # Process all files
        all_text = self.process_files()

        if not all_text.strip():
            print("❌ No text found to process!")
            return

        # Generate word frequency
        word_freq = self.generate_word_frequency(all_text)

        if not word_freq:
            print("❌ No meaningful words found!")
            return

        # Create visualizations
        print("\n🎨 Creating visualizations...")
        self.create_word_cloud(word_freq)
        self.create_frequency_chart(word_freq)

        print("\n✅ Analysis complete!")

def main():
    """Main execution function"""
    # Create analyzer instance
    analyzer = DataDumpWordCloud()

    # Check if data directory exists
    if not analyzer.data_dir.exists():
        print(f"❌ Data directory '{analyzer.data_dir}' not found!")
        print("Please ensure the data_dump directory exists in the current path.")
        return

    # Run the analysis
    analyzer.run_analysis()

if __name__ == "__main__":
    main()