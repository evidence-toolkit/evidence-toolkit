#!/usr/bin/env python3
"""
Retaliation Pattern Analysis
============================

This script analyzes workplace communication documents to identify patterns
that may indicate retaliatory behavior in response to employee concerns.

Author: Claude Code Data Scientist
Date: 2025-09-19
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import os
import re
from pathlib import Path
from collections import defaultdict, Counter
import warnings
warnings.filterwarnings('ignore')

# Set up plotting style
plt.style.use('default')
sns.set_palette("husl")
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['figure.dpi'] = 100

class RetaliationAnalyzer:
    """
    A comprehensive analyzer for identifying retaliation patterns in workplace communications.
    """

    def __init__(self, data_dir):
        self.data_dir = Path(data_dir)
        self.documents = []
        self.timeline_data = []
        self.communication_network = defaultdict(list)

    def load_documents(self):
        """Load and parse all documents from the data directory."""
        print("Loading documents from:", self.data_dir)

        for file_path in self.data_dir.glob("*.txt"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Parse filename for metadata
                filename = file_path.name
                doc_info = self._parse_filename(filename)
                doc_info['content'] = content
                doc_info['filepath'] = str(file_path)
                doc_info['word_count'] = len(content.split())

                self.documents.append(doc_info)
                print(f"Loaded: {filename}")

            except Exception as e:
                print(f"Error loading {file_path}: {e}")

        print(f"\nTotal documents loaded: {len(self.documents)}")
        return self.documents

    def _parse_filename(self, filename):
        """Extract metadata from filename pattern."""
        # Pattern: YYYY-MM-DD-TYPE-Description-Initials.txt
        parts = filename.replace('.txt', '').split('-')

        doc_info = {
            'filename': filename,
            'date_str': None,
            'date': None,
            'doc_type': 'UNKNOWN',
            'description': '',
            'participants': []
        }

        if len(parts) >= 3:
            try:
                # Extract date
                date_str = f"{parts[0]}-{parts[1]}-{parts[2]}"
                doc_info['date_str'] = date_str
                doc_info['date'] = datetime.strptime(date_str, '%Y-%m-%d')
            except:
                pass

            # Extract document type
            if len(parts) >= 4:
                doc_info['doc_type'] = parts[3]

            # Extract description and participants
            if len(parts) >= 5:
                doc_info['description'] = parts[4]

            # Extract participant initials (usually at the end)
            if len(parts) >= 6:
                initials = parts[-1].split('-') if '-' in parts[-1] else [parts[-1]]
                doc_info['participants'] = [init.strip() for init in initials if init.strip()]

        return doc_info

    def create_timeline_dataframe(self):
        """Create a structured timeline dataframe."""
        timeline_data = []

        for doc in self.documents:
            if doc['date']:
                timeline_data.append({
                    'date': doc['date'],
                    'date_str': doc['date_str'],
                    'doc_type': doc['doc_type'],
                    'description': doc['description'],
                    'participants': doc['participants'],
                    'word_count': doc['word_count'],
                    'filename': doc['filename']
                })

        df = pd.DataFrame(timeline_data)
        df = df.sort_values('date').reset_index(drop=True)

        # Add timeline features
        if len(df) > 0:
            df['days_since_start'] = (df['date'] - df['date'].min()).dt.days
            df['month_year'] = df['date'].dt.to_period('M')
            df['year'] = df['date'].dt.year
            df['month'] = df['date'].dt.month

        self.timeline_df = df
        return df

    def analyze_escalation_patterns(self):
        """Analyze escalation patterns in the timeline."""
        print("\n=== ESCALATION PATTERN ANALYSIS ===")

        df = self.timeline_df

        # Identify key events
        complaint_events = df[df['description'].str.contains('OriginalEmail|FairTreatment', case=False, na=False)]
        escalation_events = df[df['description'].str.contains('Escalate', case=False, na=False)]
        suspension_events = df[df['doc_type'] == 'LETTER'][df['description'].str.contains('Suspension', case=False, na=False)]

        print(f"Initial complaints/concerns: {len(complaint_events)}")
        print(f"Escalation events: {len(escalation_events)}")
        print(f"Suspension events: {len(suspension_events)}")

        # Timeline analysis
        if len(complaint_events) > 0 and len(suspension_events) > 0:
            first_complaint = complaint_events['date'].min()
            first_suspension = suspension_events['date'].min()
            days_to_suspension = (first_suspension - first_complaint).days

            print(f"\nFirst complaint date: {first_complaint.strftime('%Y-%m-%d')}")
            print(f"First suspension date: {first_suspension.strftime('%Y-%m-%d')}")
            print(f"Days from complaint to suspension: {days_to_suspension}")

        return {
            'complaint_events': complaint_events,
            'escalation_events': escalation_events,
            'suspension_events': suspension_events
        }

    def analyze_communication_frequency(self):
        """Analyze frequency and timing of communications."""
        print("\n=== COMMUNICATION FREQUENCY ANALYSIS ===")

        df = self.timeline_df

        # Monthly communication frequency
        monthly_counts = df.groupby('month_year').size()
        print(f"Communication frequency by month:")
        for month, count in monthly_counts.items():
            print(f"  {month}: {count} documents")

        # Document type distribution
        type_counts = df['doc_type'].value_counts()
        print(f"\nDocument type distribution:")
        for doc_type, count in type_counts.items():
            print(f"  {doc_type}: {count}")

        return monthly_counts, type_counts

    def analyze_content_sentiment(self):
        """Analyze content for sentiment and retaliation indicators."""
        print("\n=== CONTENT SENTIMENT ANALYSIS ===")

        # Keywords that may indicate retaliation
        retaliation_keywords = [
            'suspension', 'disciplinary', 'misconduct', 'investigation',
            'allegations', 'gross misconduct', 'unreasonable behaviour',
            'targeted', 'unfair', 'stressed', 'frustrated', 'mental toll'
        ]

        positive_keywords = [
            'award', 'thank you', 'well done', 'appreciate', 'great work',
            'hard work', 'support', 'helping'
        ]

        concern_keywords = [
            'safety', 'hygiene', 'contamination', 'health', 'concern',
            'blood', 'debris', 'dirty', 'cleaning', 'standards'
        ]

        results = []

        for doc in self.documents:
            content_lower = doc['content'].lower()

            retaliation_score = sum(1 for keyword in retaliation_keywords
                                  if keyword in content_lower)
            positive_score = sum(1 for keyword in positive_keywords
                               if keyword in content_lower)
            concern_score = sum(1 for keyword in concern_keywords
                              if keyword in content_lower)

            results.append({
                'filename': doc['filename'],
                'date': doc.get('date'),
                'doc_type': doc['doc_type'],
                'retaliation_score': retaliation_score,
                'positive_score': positive_score,
                'concern_score': concern_score,
                'word_count': doc['word_count']
            })

        sentiment_df = pd.DataFrame(results)
        sentiment_df = sentiment_df[sentiment_df['date'].notna()].sort_values('date')

        print(f"Average retaliation score: {sentiment_df['retaliation_score'].mean():.2f}")
        print(f"Average positive score: {sentiment_df['positive_score'].mean():.2f}")
        print(f"Average concern score: {sentiment_df['concern_score'].mean():.2f}")

        return sentiment_df

    def identify_retaliation_timeline(self):
        """Identify specific timeline patterns that suggest retaliation."""
        print("\n=== RETALIATION TIMELINE IDENTIFICATION ===")

        df = self.timeline_df

        # Key events in chronological order
        key_events = []

        for _, row in df.iterrows():
            event_type = "OTHER"

            # Classify events
            if 'award' in row['description'].lower() or row['doc_type'] == 'REWARDS':
                event_type = "POSITIVE_RECOGNITION"
            elif 'originalemail' in row['description'].lower() or 'fairtreatment' in row['description'].lower():
                event_type = "INITIAL_COMPLAINT"
            elif 'escalate' in row['description'].lower():
                event_type = "ESCALATION"
            elif 'suspension' in row['description'].lower():
                event_type = "SUSPENSION"
            elif 'fitnote' in row['description'].lower():
                event_type = "HEALTH_IMPACT"
            elif any(word in row['description'].lower() for word in ['meeting', 'followup']):
                event_type = "MANAGEMENT_RESPONSE"

            key_events.append({
                'date': row['date'],
                'event_type': event_type,
                'description': row['description'],
                'filename': row['filename']
            })

        events_df = pd.DataFrame(key_events)

        # Print timeline
        print("Chronological Timeline of Key Events:")
        print("-" * 60)
        for _, event in events_df.iterrows():
            print(f"{event['date'].strftime('%Y-%m-%d')} | {event['event_type']:20} | {event['description']}")

        return events_df

    def generate_visualizations(self):
        """Generate comprehensive visualizations."""
        print("\n=== GENERATING VISUALIZATIONS ===")

        # Create subplots
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('Workplace Retaliation Pattern Analysis', fontsize=16, fontweight='bold')

        # 1. Timeline of events
        ax1 = axes[0, 0]
        df = self.timeline_df

        # Color code by document type
        colors = {'EMAIL': 'blue', 'LETTER': 'red', 'REWARDS': 'green'}
        for doc_type in df['doc_type'].unique():
            subset = df[df['doc_type'] == doc_type]
            ax1.scatter(subset['date'], [doc_type] * len(subset),
                       c=colors.get(doc_type, 'gray'), label=doc_type, s=60, alpha=0.7)

        ax1.set_title('Timeline of Communications by Type')
        ax1.set_xlabel('Date')
        ax1.set_ylabel('Document Type')
        ax1.legend()
        ax1.grid(True, alpha=0.3)

        # 2. Communication frequency over time
        ax2 = axes[0, 1]
        monthly_counts = df.groupby('month_year').size()
        monthly_counts.plot(kind='bar', ax=ax2, color='steelblue')
        ax2.set_title('Communication Frequency by Month')
        ax2.set_xlabel('Month-Year')
        ax2.set_ylabel('Number of Documents')
        ax2.tick_params(axis='x', rotation=45)

        # 3. Sentiment analysis over time
        ax3 = axes[1, 0]
        sentiment_df = self.analyze_content_sentiment()

        ax3.plot(sentiment_df['date'], sentiment_df['retaliation_score'],
                'ro-', label='Retaliation Score', linewidth=2)
        ax3.plot(sentiment_df['date'], sentiment_df['concern_score'],
                'bo-', label='Concern Score', linewidth=2)
        ax3.plot(sentiment_df['date'], sentiment_df['positive_score'],
                'go-', label='Positive Score', linewidth=2)

        ax3.set_title('Content Sentiment Analysis Over Time')
        ax3.set_xlabel('Date')
        ax3.set_ylabel('Keyword Score')
        ax3.legend()
        ax3.grid(True, alpha=0.3)

        # 4. Document types distribution
        ax4 = axes[1, 1]
        type_counts = df['doc_type'].value_counts()
        ax4.pie(type_counts.values, labels=type_counts.index, autopct='%1.1f%%')
        ax4.set_title('Distribution of Document Types')

        plt.tight_layout()
        plt.savefig('/home/bch/dev/tools/claude-stuff/retaliation_analysis_charts.png', dpi=300, bbox_inches='tight')
        plt.show()

        # Additional detailed timeline chart
        self._create_detailed_timeline()

    def _create_detailed_timeline(self):
        """Create a detailed timeline visualization."""
        events_df = self.identify_retaliation_timeline()

        fig, ax = plt.subplots(figsize=(16, 8))

        # Color mapping for event types
        color_map = {
            'POSITIVE_RECOGNITION': 'green',
            'INITIAL_COMPLAINT': 'orange',
            'ESCALATION': 'red',
            'SUSPENSION': 'darkred',
            'HEALTH_IMPACT': 'purple',
            'MANAGEMENT_RESPONSE': 'blue',
            'OTHER': 'gray'
        }

        # Plot events
        for i, (_, event) in enumerate(events_df.iterrows()):
            color = color_map.get(event['event_type'], 'gray')
            ax.scatter(event['date'], i, c=color, s=100, alpha=0.8)
            ax.text(event['date'], i + 0.1, event['description'][:30] + '...',
                   rotation=45, fontsize=8, ha='left')

        # Add legend
        legend_elements = [plt.scatter([], [], c=color, label=event_type, s=100)
                          for event_type, color in color_map.items()
                          if event_type in events_df['event_type'].values]
        ax.legend(handles=legend_elements, bbox_to_anchor=(1.05, 1), loc='upper left')

        ax.set_title('Detailed Timeline: Potential Retaliation Pattern', fontsize=14, fontweight='bold')
        ax.set_xlabel('Date')
        ax.set_ylabel('Event Sequence')
        ax.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig('/home/bch/dev/tools/claude-stuff/detailed_timeline.png', dpi=300, bbox_inches='tight')
        plt.show()

    def generate_statistical_summary(self):
        """Generate statistical summary of findings."""
        print("\n" + "="*80)
        print("STATISTICAL SUMMARY OF RETALIATION ANALYSIS")
        print("="*80)

        df = self.timeline_df

        # Basic statistics
        print(f"Analysis Period: {df['date'].min().strftime('%Y-%m-%d')} to {df['date'].max().strftime('%Y-%m-%d')}")
        print(f"Total Duration: {(df['date'].max() - df['date'].min()).days} days")
        print(f"Total Documents: {len(df)}")

        # Event sequence analysis
        events_df = self.identify_retaliation_timeline()

        complaint_date = None
        suspension_date = None

        for _, event in events_df.iterrows():
            if event['event_type'] == 'INITIAL_COMPLAINT' and complaint_date is None:
                complaint_date = event['date']
            elif event['event_type'] == 'SUSPENSION':
                suspension_date = event['date']

        if complaint_date and suspension_date:
            days_to_retaliation = (suspension_date - complaint_date).days
            print(f"\nKEY FINDING:")
            print(f"Days from initial complaint to suspension: {days_to_retaliation}")
            print(f"Complaint date: {complaint_date.strftime('%Y-%m-%d')}")
            print(f"Suspension date: {suspension_date.strftime('%Y-%m-%d')}")

        # Sentiment analysis
        sentiment_df = self.analyze_content_sentiment()

        # Pre and post complaint analysis
        if complaint_date:
            pre_complaint = sentiment_df[sentiment_df['date'] < complaint_date]
            post_complaint = sentiment_df[sentiment_df['date'] >= complaint_date]

            print(f"\nSENTIMENT ANALYSIS:")
            print(f"Pre-complaint average retaliation score: {pre_complaint['retaliation_score'].mean():.2f}")
            print(f"Post-complaint average retaliation score: {post_complaint['retaliation_score'].mean():.2f}")

            if len(post_complaint) > 0 and len(pre_complaint) > 0:
                increase_ratio = post_complaint['retaliation_score'].mean() / (pre_complaint['retaliation_score'].mean() + 0.1)
                print(f"Retaliation score increase ratio: {increase_ratio:.2f}x")

        return {
            'total_documents': len(df),
            'analysis_period_days': (df['date'].max() - df['date'].min()).days,
            'complaint_date': complaint_date,
            'suspension_date': suspension_date,
            'days_to_retaliation': days_to_retaliation if complaint_date and suspension_date else None
        }

def main():
    """Main analysis function."""
    print("WORKPLACE RETALIATION PATTERN ANALYSIS")
    print("="*50)

    # Initialize analyzer
    analyzer = RetaliationAnalyzer('/home/bch/dev/tools/claude-stuff/data_dump/')

    # Load and analyze documents
    analyzer.load_documents()
    analyzer.create_timeline_dataframe()

    # Perform analyses
    analyzer.analyze_escalation_patterns()
    analyzer.analyze_communication_frequency()
    analyzer.analyze_content_sentiment()
    analyzer.identify_retaliation_timeline()

    # Generate visualizations
    analyzer.generate_visualizations()

    # Generate summary
    stats = analyzer.generate_statistical_summary()

    print("\nAnalysis complete. Charts saved to:")
    print("- retaliation_analysis_charts.png")
    print("- detailed_timeline.png")

    return analyzer, stats

if __name__ == "__main__":
    analyzer, stats = main()