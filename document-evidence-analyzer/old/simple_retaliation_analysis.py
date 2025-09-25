#!/usr/bin/env python3
"""
Simple Retaliation Pattern Analysis
===================================

This script analyzes workplace communication documents to identify patterns
that may indicate retaliatory behavior using only built-in Python libraries.

Author: Claude Code Data Scientist
Date: 2025-09-19
"""

import os
import re
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from pathlib import Path

class SimpleRetaliationAnalyzer:
    """
    A comprehensive analyzer for identifying retaliation patterns in workplace communications.
    Uses only built-in Python libraries.
    """

    def __init__(self, data_dir):
        self.data_dir = Path(data_dir)
        self.documents = []
        self.timeline = []

    def load_documents(self):
        """Load and parse all documents from the data directory."""
        print("="*80)
        print("WORKPLACE RETALIATION PATTERN ANALYSIS")
        print("="*80)
        print(f"Loading documents from: {self.data_dir}")
        print("-" * 50)

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
                print(f"✓ Loaded: {filename}")

            except Exception as e:
                print(f"✗ Error loading {file_path}: {e}")

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

    def create_timeline(self):
        """Create a chronological timeline of events."""
        print("\n" + "="*80)
        print("CHRONOLOGICAL TIMELINE ANALYSIS")
        print("="*80)

        # Filter and sort documents with valid dates
        dated_docs = [doc for doc in self.documents if doc['date']]
        dated_docs.sort(key=lambda x: x['date'])

        self.timeline = dated_docs

        print(f"Documents with valid dates: {len(dated_docs)}")
        if len(dated_docs) > 0:
            print(f"Timeline span: {dated_docs[0]['date'].strftime('%Y-%m-%d')} to {dated_docs[-1]['date'].strftime('%Y-%m-%d')}")
            total_days = (dated_docs[-1]['date'] - dated_docs[0]['date']).days
            print(f"Total duration: {total_days} days")

        return dated_docs

    def analyze_content_patterns(self):
        """Analyze content for patterns indicating retaliation."""
        print("\n" + "="*80)
        print("CONTENT PATTERN ANALYSIS")
        print("="*80)

        # Define keyword categories
        retaliation_keywords = [
            'suspension', 'disciplinary', 'misconduct', 'investigation',
            'allegations', 'gross misconduct', 'unreasonable behaviour',
            'targeted', 'unfair', 'stressed', 'frustrated', 'mental toll'
        ]

        positive_keywords = [
            'award', 'thank you', 'well done', 'appreciate', 'great work',
            'hard work', 'support', 'helping', 'excellent', 'outstanding'
        ]

        concern_keywords = [
            'safety', 'hygiene', 'contamination', 'health', 'concern',
            'blood', 'debris', 'dirty', 'cleaning', 'standards', 'whistleblowing'
        ]

        # Analyze each document
        results = []
        for doc in self.documents:
            content_lower = doc['content'].lower()

            retaliation_count = sum(1 for keyword in retaliation_keywords
                                  if keyword in content_lower)
            positive_count = sum(1 for keyword in positive_keywords
                               if keyword in content_lower)
            concern_count = sum(1 for keyword in concern_keywords
                              if keyword in content_lower)

            # Find specific keywords present
            found_retaliation = [kw for kw in retaliation_keywords if kw in content_lower]
            found_positive = [kw for kw in positive_keywords if kw in content_lower]
            found_concerns = [kw for kw in concern_keywords if kw in content_lower]

            result = {
                'filename': doc['filename'],
                'date': doc.get('date'),
                'doc_type': doc['doc_type'],
                'retaliation_score': retaliation_count,
                'positive_score': positive_count,
                'concern_score': concern_count,
                'word_count': doc['word_count'],
                'found_retaliation': found_retaliation,
                'found_positive': found_positive,
                'found_concerns': found_concerns
            }
            results.append(result)

        # Sort by date
        results = [r for r in results if r['date']]
        results.sort(key=lambda x: x['date'])

        print("Keyword Analysis Results:")
        print("-" * 50)
        for result in results:
            date_str = result['date'].strftime('%Y-%m-%d') if result['date'] else 'No date'
            print(f"{date_str} | {result['filename']}")
            print(f"  Retaliation indicators: {result['retaliation_score']} {result['found_retaliation']}")
            print(f"  Positive indicators: {result['positive_score']} {result['found_positive']}")
            print(f"  Concern indicators: {result['concern_score']} {result['found_concerns']}")
            print()

        return results

    def identify_key_events(self):
        """Identify and categorize key events in the timeline."""
        print("\n" + "="*80)
        print("KEY EVENT IDENTIFICATION")
        print("="*80)

        key_events = []

        for doc in self.timeline:
            event_type = "OTHER"
            description = doc['description'].lower()
            doc_type = doc['doc_type']

            # Classify events based on filename patterns
            if 'award' in description or doc_type == 'REWARDS':
                event_type = "POSITIVE_RECOGNITION"
            elif 'originalemail' in description or 'fairtreatment' in description:
                event_type = "INITIAL_COMPLAINT"
            elif 'escalate' in description:
                event_type = "ESCALATION"
            elif 'suspension' in description:
                event_type = "SUSPENSION"
            elif 'fitnote' in description:
                event_type = "HEALTH_IMPACT"
            elif any(word in description for word in ['meeting', 'followup']):
                event_type = "MANAGEMENT_RESPONSE"
            elif doc_type == 'LETTER':
                event_type = "FORMAL_COMMUNICATION"

            key_events.append({
                'date': doc['date'],
                'event_type': event_type,
                'description': doc['description'],
                'filename': doc['filename'],
                'doc_type': doc['doc_type']
            })

        # Print chronological timeline
        print("Chronological Timeline of Key Events:")
        print("-" * 80)
        for event in key_events:
            date_str = event['date'].strftime('%Y-%m-%d')
            print(f"{date_str} | {event['event_type']:20} | {event['description']}")

        return key_events

    def analyze_retaliation_pattern(self):
        """Analyze the sequence of events for retaliation patterns."""
        print("\n" + "="*80)
        print("RETALIATION PATTERN ANALYSIS")
        print("="*80)

        key_events = self.identify_key_events()

        # Find critical dates
        complaint_date = None
        suspension_date = None
        positive_recognition_dates = []

        for event in key_events:
            if event['event_type'] == 'INITIAL_COMPLAINT' and complaint_date is None:
                complaint_date = event['date']
            elif event['event_type'] == 'SUSPENSION':
                suspension_date = event['date']
            elif event['event_type'] == 'POSITIVE_RECOGNITION':
                positive_recognition_dates.append(event['date'])

        # Analysis findings
        print("CRITICAL TIMELINE ANALYSIS:")
        print("-" * 50)

        if positive_recognition_dates:
            print(f"Period of positive recognition: {len(positive_recognition_dates)} awards")
            print(f"Latest positive recognition: {max(positive_recognition_dates).strftime('%Y-%m-%d')}")

        if complaint_date:
            print(f"Initial complaint/concern raised: {complaint_date.strftime('%Y-%m-%d')}")

        if suspension_date:
            print(f"Suspension occurred: {suspension_date.strftime('%Y-%m-%d')}")

        if complaint_date and suspension_date:
            days_between = (suspension_date - complaint_date).days
            print(f"\n*** KEY FINDING ***")
            print(f"Days from initial complaint to suspension: {days_between}")
            print(f"This represents a potential retaliation timeline.")

        # Additional pattern analysis
        if positive_recognition_dates and complaint_date:
            last_positive = max(positive_recognition_dates)
            days_positive_to_complaint = (complaint_date - last_positive).days
            print(f"\nDays from last positive recognition to complaint: {days_positive_to_complaint}")

        return {
            'complaint_date': complaint_date,
            'suspension_date': suspension_date,
            'positive_recognition_dates': positive_recognition_dates,
            'days_to_suspension': (suspension_date - complaint_date).days if complaint_date and suspension_date else None
        }

    def generate_summary_report(self):
        """Generate a comprehensive summary report."""
        print("\n" + "="*80)
        print("COMPREHENSIVE ANALYSIS SUMMARY")
        print("="*80)

        # Basic statistics
        total_docs = len(self.documents)
        dated_docs = len([doc for doc in self.documents if doc['date']])

        print(f"DATASET OVERVIEW:")
        print(f"Total documents analyzed: {total_docs}")
        print(f"Documents with valid dates: {dated_docs}")

        if self.timeline:
            start_date = self.timeline[0]['date']
            end_date = self.timeline[-1]['date']
            total_days = (end_date - start_date).days

            print(f"Analysis period: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
            print(f"Total span: {total_days} days")

        # Document type breakdown
        doc_types = Counter(doc['doc_type'] for doc in self.documents)
        print(f"\nDOCUMENT TYPE BREAKDOWN:")
        for doc_type, count in doc_types.most_common():
            print(f"  {doc_type}: {count}")

        # Content analysis summary
        content_results = self.analyze_content_patterns()
        if content_results:
            avg_retaliation = sum(r['retaliation_score'] for r in content_results) / len(content_results)
            avg_positive = sum(r['positive_score'] for r in content_results) / len(content_results)
            avg_concern = sum(r['concern_score'] for r in content_results) / len(content_results)

            print(f"\nCONTENT ANALYSIS AVERAGES:")
            print(f"  Average retaliation indicators per document: {avg_retaliation:.2f}")
            print(f"  Average positive indicators per document: {avg_positive:.2f}")
            print(f"  Average concern indicators per document: {avg_concern:.2f}")

        # Retaliation pattern analysis
        pattern_results = self.analyze_retaliation_pattern()

        print(f"\nRETALIATION PATTERN FINDINGS:")
        if pattern_results['days_to_suspension']:
            print(f"  ⚠️  POTENTIAL RETALIATION DETECTED")
            print(f"     Time from complaint to disciplinary action: {pattern_results['days_to_suspension']} days")

            # Assess severity based on timeframe
            if pattern_results['days_to_suspension'] < 30:
                severity = "HIGH RISK"
            elif pattern_results['days_to_suspension'] < 90:
                severity = "MODERATE RISK"
            else:
                severity = "LOW RISK"

            print(f"     Risk assessment: {severity}")
        else:
            print(f"  No clear retaliation timeline identified")

        if pattern_results['positive_recognition_dates']:
            print(f"  Prior positive recognition: {len(pattern_results['positive_recognition_dates'])} instances")

        print(f"\nRECOMMendations:")
        print(f"  1. Document preservation: Ensure all communications are preserved")
        print(f"  2. Timeline documentation: Maintain clear chronological records")
        print(f"  3. Pattern monitoring: Watch for escalation of disciplinary actions")
        print(f"  4. External review: Consider independent assessment if pattern continues")

        return {
            'total_documents': total_docs,
            'analysis_period': total_days if self.timeline else 0,
            'retaliation_timeline': pattern_results['days_to_suspension'],
            'risk_assessment': severity if pattern_results['days_to_suspension'] else 'No clear pattern'
        }

def main():
    """Main analysis function."""
    analyzer = SimpleRetaliationAnalyzer('/home/bch/dev/tools/claude-stuff/data_dump/')

    # Perform comprehensive analysis
    analyzer.load_documents()
    analyzer.create_timeline()
    analyzer.analyze_content_patterns()
    analyzer.identify_key_events()
    analyzer.analyze_retaliation_pattern()

    # Generate final summary
    summary = analyzer.generate_summary_report()

    print("\n" + "="*80)
    print("ANALYSIS COMPLETE")
    print("="*80)

    return analyzer, summary

if __name__ == "__main__":
    analyzer, summary = main()