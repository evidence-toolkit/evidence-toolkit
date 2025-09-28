#!/usr/bin/env python3
"""
Command Line Interface for Document Evidence Analyzer
"""

import argparse
import json
import sys
import glob
from pathlib import Path
from typing import Optional
from datetime import datetime

from .word_cloud_analyzer import DocumentAnalyzer, analyze_documents
from .retaliation_analyzer import analyze_retaliation_case
from .evidence_manager import EvidenceManager
from .image_analyzer import ImageAnalyzer
from .email_analyzer import EmailAnalyzer
from .correlation_analyzer import CorrelationAnalyzer
from .case_summary_generator import CaseSummaryGenerator
from .client_packager import ClientPackager
from .unified_models import (
    UnifiedAnalysis,
    DocumentAnalysisResult,
    ImageAnalysisResult,
    EmailAnalysisResult,
    EvidenceType,
    FileMetadata
)
from .utils import detect_file_type, extract_exif_data


def create_parser() -> argparse.ArgumentParser:
    """Create command line argument parser"""
    parser = argparse.ArgumentParser(
        description="Document Evidence Analyzer - Text analysis for legal evidence processing",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s analyze ./documents                    # Analyze documents in directory
  %(prog)s analyze ./documents -o ./output       # Save results to output directory
  %(prog)s analyze ./documents --quiet           # Run without verbose output
  %(prog)s analyze ./documents --stop-words "company,internal"  # Add custom stop words
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Ingest command
    ingest_parser = subparsers.add_parser('ingest', help='Ingest evidence into content-addressed storage')
    ingest_parser.add_argument(
        'input_path',
        help='File or directory to ingest'
    )
    ingest_parser.add_argument(
        '--case-id',
        help='Case ID to associate with this evidence'
    )
    ingest_parser.add_argument(
        '--actor',
        default='system',
        help='Actor performing the ingestion (default: system)'
    )
    ingest_parser.add_argument(
        '--evidence-root',
        default='evidence',
        help='Evidence storage root directory (default: evidence)'
    )
    ingest_parser.add_argument(
        '--quiet', '-q',
        action='store_true',
        help='Suppress verbose output'
    )

    # Analyze command
    analyze_parser = subparsers.add_parser('analyze', help='Analyze evidence (documents or images)')
    analyze_parser.add_argument(
        'input',
        nargs='?',
        default='./inbox/',
        help='SHA256 hash of ingested evidence or directory containing files to analyze (default: ./inbox/)'
    )
    analyze_parser.add_argument(
        '-o', '--output-dir',
        help='Output directory for results (default: current directory)'
    )
    analyze_parser.add_argument(
        '--file-pattern',
        default='*.txt',
        help='File pattern to match (default: *.txt)'
    )
    analyze_parser.add_argument(
        '--stop-words',
        help='Comma-separated list of additional stop words to filter out'
    )
    analyze_parser.add_argument(
        '--min-word-length',
        type=int,
        default=3,
        help='Minimum word length to include (default: 3)'
    )
    analyze_parser.add_argument(
        '--quiet', '-q',
        action='store_true',
        help='Suppress verbose output'
    )
    analyze_parser.add_argument(
        '--json-output',
        help='Save analysis results as JSON to specified file'
    )
    analyze_parser.add_argument(
        '--evidence-root',
        default='evidence',
        help='Evidence storage root directory (default: evidence)'
    )
    analyze_parser.add_argument(
        '--type',
        choices=['document', 'image', 'email', 'auto'],
        default='auto',
        help='Force evidence type (default: auto-detect)'
    )
    analyze_parser.add_argument(
        '--case-id',
        help='Case ID to associate with analysis'
    )

    # Retaliation analysis command
    retaliation_parser = subparsers.add_parser('retaliation', help='Run retaliation-pattern analysis')
    retaliation_parser.add_argument(
        'input_dir',
        nargs='?',
        default='./inbox/',
        help='Directory containing text files to analyze (default: ./inbox/)'
    )
    retaliation_parser.add_argument(
        '-o', '--output-dir',
        help='Output directory for charts (default: ./retaliation_analysis)'
    )
    retaliation_parser.add_argument(
        '--file-pattern',
        default='*.txt',
        help='File pattern to match (default: *.txt)'
    )
    retaliation_parser.add_argument(
        '--quiet', '-q',
        action='store_true',
        help='Suppress verbose output'
    )

    # Export command
    export_parser = subparsers.add_parser('export', help='Export evidence analysis')
    export_parser.add_argument(
        'sha256',
        help='SHA256 hash of evidence to export'
    )
    export_parser.add_argument(
        'output_path',
        help='Output path for exported analysis'
    )
    export_parser.add_argument(
        '--evidence-root',
        default='evidence',
        help='Evidence storage root directory (default: evidence)'
    )
    export_parser.add_argument(
        '--quiet', '-q',
        action='store_true',
        help='Suppress verbose output'
    )

    version_parser = subparsers.add_parser('version', help='Show version information')

    # Email analysis command
    email_parser = subparsers.add_parser('email', help='Analyze email threads for legal evidence')
    email_parser.add_argument(
        'input',
        help='Directory containing email files (.eml, .msg, .mbox) or single email file'
    )
    email_parser.add_argument(
        '-o', '--output-dir',
        help='Output directory for analysis results (default: current directory)'
    )
    email_parser.add_argument(
        '--case-id',
        help='Case ID to associate with email analysis'
    )
    email_parser.add_argument(
        '--json-output',
        help='Save analysis results as JSON to specified file'
    )
    email_parser.add_argument(
        '--quiet', '-q',
        action='store_true',
        help='Suppress verbose output'
    )
    email_parser.add_argument(
        '--evidence-root',
        default='evidence',
        help='Evidence storage root directory (default: evidence)'
    )

    # Cross-evidence correlation command
    correlate_parser = subparsers.add_parser('correlate', help='Analyze correlations across evidence types')
    correlate_parser.add_argument(
        '--case-id',
        required=True,
        help='Case ID to analyze for correlations'
    )
    correlate_parser.add_argument(
        '--json-output',
        help='Save correlation results as JSON to specified file'
    )
    correlate_parser.add_argument(
        '--quiet', '-q',
        action='store_true',
        help='Suppress verbose output'
    )
    correlate_parser.add_argument(
        '--evidence-root',
        default='evidence',
        help='Evidence storage root directory (default: evidence)'
    )

    # Case summary command
    summary_parser = subparsers.add_parser('summary', help='Generate comprehensive case summary')
    summary_parser.add_argument(
        '--case-id',
        required=True,
        help='Case ID to generate summary for'
    )
    summary_parser.add_argument(
        '--json-output',
        help='Save summary as JSON to specified file'
    )
    summary_parser.add_argument(
        '--text-output',
        help='Save formatted text report to specified file'
    )
    summary_parser.add_argument(
        '--quiet', '-q',
        action='store_true',
        help='Suppress verbose output'
    )
    summary_parser.add_argument(
        '--evidence-root',
        default='evidence',
        help='Evidence storage root directory (default: evidence)'
    )

    # Client package command
    package_parser = subparsers.add_parser('package', help='Create client deliverable package')
    package_parser.add_argument(
        '--case-id',
        required=True,
        help='Case ID to package'
    )
    package_parser.add_argument(
        '--output-dir',
        default='./client_packages',
        help='Output directory for client package (default: ./client_packages)'
    )
    package_parser.add_argument(
        '--include-raw-evidence',
        action='store_true',
        help='Include original evidence files in package'
    )
    package_parser.add_argument(
        '--format',
        choices=['zip', 'directory'],
        default='zip',
        help='Package format (default: zip)'
    )
    package_parser.add_argument(
        '--quiet', '-q',
        action='store_true',
        help='Suppress verbose output'
    )
    package_parser.add_argument(
        '--evidence-root',
        default='evidence',
        help='Evidence storage root directory (default: evidence)'
    )

    return parser


def handle_ingest_command(args) -> int:
    """Handle the ingest command"""
    input_path = Path(args.input_path)
    evidence_manager = EvidenceManager(Path(args.evidence_root))

    if not input_path.exists():
        print(f"❌ Input path '{input_path}' does not exist")
        return 1

    ingested_files = []

    try:
        if input_path.is_file():
            # Single file ingestion
            result = evidence_manager.ingest_file(
                input_path,
                case_id=args.case_id,
                actor=args.actor
            )
            ingested_files.append(result)

        elif input_path.is_dir():
            # Directory ingestion - ingest all files
            for file_path in input_path.rglob('*'):
                if file_path.is_file() and not file_path.name.startswith('.'):
                    result = evidence_manager.ingest_file(
                        file_path,
                        case_id=args.case_id,
                        actor=args.actor
                    )
                    ingested_files.append(result)

        # Report results
        successful = [r for r in ingested_files if r.success]
        failed = [r for r in ingested_files if not r.success]

        if not args.quiet:
            print(f"\n📥 Ingestion Summary:")
            print(f"   Files processed: {len(ingested_files)}")
            print(f"   Successfully ingested: {len(successful)}")
            print(f"   Failed: {len(failed)}")

            if successful:
                print("\n✅ Successfully ingested:")
                for result in successful[:5]:  # Show first 5
                    print(f"   {result.sha256[:12]}... ({result.evidence_type}) - {result.file_path}")
                if len(successful) > 5:
                    print(f"   ... and {len(successful) - 5} more")

            if failed:
                print("\n❌ Failed to ingest:")
                for result in failed:
                    print(f"   {result.file_path}: {result.message}")

        return 0 if not failed else 1

    except Exception as e:
        print(f"❌ Error during ingestion: {e}")
        return 1


def handle_analyze_command(args) -> int:
    """Handle the analyze command - can analyze by SHA256 or directory"""
    evidence_manager = EvidenceManager(Path(args.evidence_root))
    input_str = args.input

    # Check if input is a SHA256 hash (64 hex characters)
    if len(input_str) == 64 and all(c in '0123456789abcdef' for c in input_str.lower()):
        # SHA256 analysis
        return _analyze_by_sha256(input_str, args, evidence_manager)
    else:
        # Directory analysis (legacy mode)
        return _analyze_directory_legacy(Path(input_str), args)


def _analyze_by_sha256(sha256: str, args, evidence_manager: EvidenceManager) -> int:
    """Analyze evidence by SHA256 hash"""
    try:
        # Check if evidence exists
        original_file = evidence_manager.get_original_file_path(sha256)
        if not original_file:
            print(f"❌ No evidence found for SHA256: {sha256}")
            return 1

        # Check if already analyzed
        existing_analysis = evidence_manager.get_analysis(sha256)
        if existing_analysis and not args.quiet:
            print(f"⚠️  Evidence {sha256[:12]}... already has analysis")

        # Detect file type
        if args.type == 'auto':
            evidence_type = EvidenceType(detect_file_type(original_file))
        else:
            evidence_type = EvidenceType(args.type)

        if not args.quiet:
            print(f"🔍 Analyzing {evidence_type} evidence: {sha256[:12]}...")

        # Load metadata
        metadata_file = evidence_manager.derived_dir / f"sha256={sha256}" / "metadata.json"
        with open(metadata_file, 'r') as f:
            metadata_dict = json.load(f)

        file_metadata = FileMetadata(**metadata_dict)

        # Perform analysis based on type
        if evidence_type == EvidenceType.DOCUMENT:
            analysis_result = _analyze_document(original_file, args)
        elif evidence_type == EvidenceType.IMAGE:
            analysis_result = _analyze_image(original_file, args)
        elif evidence_type == EvidenceType.EMAIL:
            analysis_result = _analyze_email(original_file, args)
        else:
            print(f"❌ Cannot analyze evidence type: {evidence_type}")
            return 1

        # Create unified analysis
        unified_analysis = UnifiedAnalysis(
            evidence_type=evidence_type,
            analysis_timestamp=datetime.now(),
            file_metadata=file_metadata,
            case_id=args.case_id,
            document_analysis=analysis_result if evidence_type == EvidenceType.DOCUMENT else None,
            image_analysis=analysis_result if evidence_type == EvidenceType.IMAGE else None,
            email_analysis=analysis_result if evidence_type == EvidenceType.EMAIL else None,
            exif_data=extract_exif_data(original_file) if evidence_type == EvidenceType.IMAGE else None
        )

        # Save analysis
        success = evidence_manager.save_analysis(unified_analysis)
        if not success:
            print(f"❌ Failed to save analysis for {sha256}")
            return 1

        if not args.quiet:
            print(f"✅ Analysis completed for {sha256[:12]}...")

        return 0

    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        return 1


def _analyze_document(file_path: Path, args) -> DocumentAnalysisResult:
    """Analyze document using existing DocumentAnalyzer"""
    custom_stop_words = None
    if hasattr(args, 'stop_words') and args.stop_words:
        custom_stop_words = set(word.strip() for word in args.stop_words.split(','))

    analyzer = DocumentAnalyzer(
        custom_stop_words=custom_stop_words,
        min_word_length=getattr(args, 'min_word_length', 3),
        verbose=not args.quiet
    )

    # Analyze the text file
    result = analyzer.analyze_directory(
        data_dir=file_path.parent,
        output_dir=args.output_dir,
        file_pattern=file_path.name
    )

    if result['status'] != 'success':
        raise Exception(f"Document analysis failed: {result.get('message', 'Unknown error')}")

    # Convert to DocumentAnalysisResult
    top_words = sorted(result['word_frequency'].items(), key=lambda x: x[1], reverse=True)[:20]

    return DocumentAnalysisResult(
        total_words=result['total_words'],
        unique_words=result['unique_words'],
        word_frequency=result['word_frequency'],
        top_words=top_words,
        wordcloud_file=result.get('wordcloud_file'),
        frequency_chart_file=result.get('frequency_chart_file')
    )


def _analyze_image(file_path: Path, args) -> ImageAnalysisResult:
    """Analyze image using ImageAnalyzer"""
    image_analyzer = ImageAnalyzer()

    return image_analyzer.analyze_image(file_path)


def _analyze_email(file_path: Path, args) -> EmailAnalysisResult:
    """Analyze email using EmailAnalyzer"""
    import os
    import openai

    # Initialize OpenAI client
    openai_client = None
    try:
        api_key = os.getenv('OPENAI_API_KEY')
        if api_key:
            openai_client = openai.OpenAI(api_key=api_key)
        else:
            if not args.quiet:
                print("⚠️  OPENAI_API_KEY not set - email analysis may be limited")
    except ImportError:
        if not args.quiet:
            print("⚠️  OpenAI package not available - email analysis may be limited")

    # Initialize email analyzer
    email_analyzer = EmailAnalyzer(openai_client, verbose=not args.quiet)

    # Analyze the email file
    analysis = email_analyzer.analyze_email_files([file_path], case_id=args.case_id)

    if not analysis:
        raise Exception("Email analysis failed - no results returned")

    # Convert EmailThreadAnalysis to EmailAnalysisResult
    return EmailAnalysisResult(
        thread_summary=analysis.thread_summary,
        participant_count=len(analysis.participants),
        communication_pattern=analysis.communication_pattern,
        legal_significance=analysis.legal_significance,
        risk_flags=analysis.risk_flags,
        escalation_events=[f"{event.escalation_type}: {event.description}" for event in analysis.escalation_events],
        confidence_overall=analysis.confidence_overall
    )


def _analyze_directory_legacy(input_path: Path, args) -> int:
    """Legacy directory analysis mode"""
    if not input_path.exists():
        print(f"❌ Input directory '{input_path}' does not exist")
        return 1

    if not input_path.is_dir():
        print(f"❌ '{input_path}' is not a directory")
        return 1

    custom_stop_words = None
    if hasattr(args, 'stop_words') and args.stop_words:
        custom_stop_words = set(word.strip() for word in args.stop_words.split(','))

    analyzer = DocumentAnalyzer(
        custom_stop_words=custom_stop_words,
        min_word_length=getattr(args, 'min_word_length', 3),
        verbose=not args.quiet
    )

    try:
        result = analyzer.analyze_directory(
            data_dir=input_path,
            output_dir=args.output_dir,
            file_pattern=getattr(args, 'file_pattern', '*.txt')
        )

        if result['status'] == 'success':
            if not args.quiet:
                print("\n📊 Analysis Summary:")
                print(f"   Files processed: {result['files_processed']}")
                print(f"   Total words: {result['total_words']}")
                print(f"   Unique words: {result['unique_words']}")
                print(f"   Word cloud: {result['wordcloud_file']}")
                print(f"   Frequency chart: {result['frequency_chart_file']}")

            if hasattr(args, 'json_output') and args.json_output:
                json_path = Path(args.json_output)
                json_result = {k: v for k, v in result.items() if k != 'word_frequency'}
                json_result['top_20_words'] = dict(
                    sorted(result['word_frequency'].items(), key=lambda x: x[1], reverse=True)[:20]
                )

                with open(json_path, 'w') as f:
                    json.dump(json_result, f, indent=2)

                if not args.quiet:
                    print(f"   JSON results: {json_path}")

            return 0
        else:
            print(f"❌ Analysis failed: {result.get('message', 'Unknown error')}")
            return 1

    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        return 1


def handle_retaliation_command(args) -> int:
    """Handle the retaliation command"""
    try:
        summary = analyze_retaliation_case(
            data_dir=args.input_dir,
            output_dir=args.output_dir,
            file_pattern=args.file_pattern,
            verbose=not args.quiet
        )
    except Exception as exc:
        print(f"❌ Retaliation analysis failed: {exc}")
        return 1

    if not args.quiet:
        print("\n📈 Retaliation Analysis Summary:")
        print(f"   Documents processed: {summary.total_documents}")
        if summary.analysis_period_days is not None:
            print(f"   Analysis period: {summary.analysis_period_days} days")
        if summary.complaint_date is not None:
            print(f"   First complaint: {summary.complaint_date.date()}")
        if summary.suspension_date is not None:
            print(f"   First suspension: {summary.suspension_date.date()}")
        if summary.days_to_retaliation is not None:
            print(f"   Days to suspension: {summary.days_to_retaliation}")
        if summary.chart_paths:
            print("   Charts:")
            for label, path in summary.chart_paths.items():
                pretty = label.replace('_', ' ').title()
                print(f"     - {pretty}: {path}")

    return 0


def handle_export_command(args) -> int:
    """Handle the export command"""
    evidence_manager = EvidenceManager(Path(args.evidence_root))
    sha256 = args.sha256.lower()
    output_path = Path(args.output_path)

    try:
        result = evidence_manager.export_analysis(sha256, output_path)

        if result.success:
            if not args.quiet:
                print(f"✅ Analysis exported to: {result.export_path}")
                if result.analysis_included:
                    print(f"   SHA256: {sha256}")
                    print(f"   Analysis data included: Yes")
            return 0
        else:
            print(f"❌ Export failed: {result.message}")
            return 1

    except Exception as e:
        print(f"❌ Error during export: {e}")
        return 1


def handle_version_command(args) -> int:
    """Handle the version command"""
    print("Document Evidence Analyzer v0.1.0")
    print("Part of the Evidence Toolkit project")
    return 0


def handle_email_command(args) -> int:
    """Handle the email analysis command"""
    import os

    input_path = Path(args.input)

    if not input_path.exists():
        print(f"❌ Input path '{input_path}' does not exist")
        return 1

    # Initialize OpenAI client
    openai_client = None
    try:
        import openai
        api_key = os.getenv('OPENAI_API_KEY')
        if api_key:
            openai_client = openai.OpenAI(api_key=api_key)
        else:
            print("⚠️  OPENAI_API_KEY not set - AI analysis will be disabled")
    except ImportError:
        print("⚠️  OpenAI package not available - AI analysis will be disabled")

    # Initialize email analyzer
    email_analyzer = EmailAnalyzer(openai_client, verbose=not args.quiet)

    try:
        # Collect email files
        email_files = []

        if input_path.is_file():
            # Single email file
            if input_path.suffix.lower() in ['.eml', '.msg', '.mbox']:
                email_files.append(input_path)
            else:
                print(f"❌ Unsupported email format: {input_path.suffix}")
                return 1
        else:
            # Directory of email files
            for pattern in ['*.eml', '*.msg', '*.mbox']:
                email_files.extend(input_path.glob(pattern))

            if not email_files:
                print(f"❌ No email files found in {input_path}")
                return 1

        if not args.quiet:
            print(f"📧 Found {len(email_files)} email file(s)")

        # Analyze emails
        analysis = email_analyzer.analyze_email_files(email_files, case_id=args.case_id)

        if not analysis:
            print("❌ Email analysis failed")
            return 1

        # Output results
        output_dir = Path(args.output_dir) if args.output_dir else Path.cwd()
        output_dir.mkdir(parents=True, exist_ok=True)

        # Save JSON output if requested
        if args.json_output:
            json_path = Path(args.json_output)
            if email_analyzer.export_analysis_to_json(analysis, json_path):
                if not args.quiet:
                    print(f"✅ Analysis saved to: {json_path}")

        # Print summary
        if not args.quiet:
            summary = email_analyzer.get_analysis_summary(analysis)
            print("\n" + summary)

        return 0

    except Exception as e:
        print(f"❌ Error during email analysis: {e}")
        return 1


def handle_correlate_command(args) -> int:
    """Handle the correlate command"""
    evidence_manager = EvidenceManager(Path(args.evidence_root))
    correlation_analyzer = CorrelationAnalyzer(evidence_manager)

    try:
        if not args.quiet:
            print(f"🔍 Analyzing correlations for case: {args.case_id}")

        # Perform correlation analysis
        result = correlation_analyzer.analyze_case_correlations(args.case_id)

        if result.evidence_count == 0:
            print(f"❌ No evidence found for case ID: {args.case_id}")
            return 1

        # Display results
        if not args.quiet:
            print("\n📊 Cross-Evidence Correlation Analysis")
            print("=" * 50)
            print(f"Case ID: {result.case_id}")
            print(f"Evidence analyzed: {result.evidence_count} items")
            print(f"Entity correlations found: {len(result.entity_correlations)}")
            print(f"Timeline events: {len(result.timeline_events)}")

            if result.entity_correlations:
                print("\n🔗 Entity Correlations:")
                for i, correlation in enumerate(result.entity_correlations[:10], 1):  # Show top 10
                    print(f"  {i}. {correlation.entity_name} ({correlation.entity_type})")
                    print(f"     Appears in {correlation.occurrence_count} evidence pieces")
                    print(f"     Average confidence: {correlation.confidence_average:.2f}")

            if result.timeline_events:
                print("\n⏰ Timeline Events:")
                for event in result.timeline_events[:10]:  # Show first 10 events
                    print(f"  {event.timestamp.strftime('%Y-%m-%d %H:%M')} - {event.description}")

        # Save JSON output if requested
        if args.json_output:
            output_data = {
                'case_id': result.case_id,
                'analysis_timestamp': result.analysis_timestamp.isoformat(),
                'evidence_count': result.evidence_count,
                'entity_correlations': [
                    {
                        'entity_name': corr.entity_name,
                        'entity_type': corr.entity_type,
                        'occurrence_count': corr.occurrence_count,
                        'confidence_average': corr.confidence_average,
                        'evidence_occurrences': corr.evidence_occurrences
                    }
                    for corr in result.entity_correlations
                ],
                'timeline_events': [
                    {
                        'timestamp': event.timestamp.isoformat(),
                        'evidence_sha256': event.evidence_sha256,
                        'evidence_type': event.evidence_type,
                        'event_type': event.event_type,
                        'description': event.description,
                        'confidence': event.confidence
                    }
                    for event in result.timeline_events
                ]
            }

            with open(args.json_output, 'w') as f:
                json.dump(output_data, f, indent=2)

            if not args.quiet:
                print(f"\n✅ Correlation analysis saved to: {args.json_output}")

        return 0

    except Exception as e:
        print(f"❌ Error during correlation analysis: {e}")
        return 1


def handle_summary_command(args) -> int:
    """Handle the summary command"""
    import os

    evidence_manager = EvidenceManager(Path(args.evidence_root))

    # Initialize OpenAI client for AI executive summaries
    openai_client = None
    try:
        import openai
        api_key = os.getenv('OPENAI_API_KEY')
        if api_key:
            openai_client = openai.OpenAI(api_key=api_key)
            if not args.quiet:
                print("🤖 AI executive summary enabled")
        else:
            if not args.quiet:
                print("⚠️  OPENAI_API_KEY not set - AI executive summary disabled")
    except ImportError:
        if not args.quiet:
            print("⚠️  OpenAI package not available - AI executive summary disabled")

    summary_generator = CaseSummaryGenerator(evidence_manager, openai_client)

    try:
        if not args.quiet:
            print(f"📊 Generating case summary for: {args.case_id}")

        # Generate case summary
        case_summary = summary_generator.generate_case_summary(args.case_id)

        if not args.quiet:
            print(f"✅ Summary generated for {case_summary.evidence_count} pieces of evidence")

        # Save JSON output if requested
        if args.json_output:
            json_path = Path(args.json_output)
            success = summary_generator.export_summary_to_json(case_summary, json_path)
            if success and not args.quiet:
                print(f"📄 JSON summary saved to: {json_path}")

        # Save text report if requested
        if args.text_output:
            text_path = Path(args.text_output)
            try:
                formatted_report = summary_generator.format_summary_report(case_summary)
                with open(text_path, 'w') as f:
                    f.write(formatted_report)
                if not args.quiet:
                    print(f"📝 Text report saved to: {text_path}")
            except Exception as e:
                print(f"❌ Failed to save text report: {e}")

        # Display summary if not quiet and no output files specified
        if not args.quiet and not (args.json_output or args.text_output):
            print("\n" + summary_generator.format_summary_report(case_summary))

        return 0

    except ValueError as e:
        print(f"❌ {e}")
        return 1
    except Exception as e:
        print(f"❌ Error generating case summary: {e}")
        return 1


def handle_package_command(args) -> int:
    """Handle the package command"""
    import os

    evidence_manager = EvidenceManager(Path(args.evidence_root))

    # Initialize OpenAI client for AI summaries in package
    openai_client = None
    try:
        import openai
        api_key = os.getenv('OPENAI_API_KEY')
        if api_key:
            openai_client = openai.OpenAI(api_key=api_key)
            if not args.quiet:
                print("🤖 AI analysis will be included in package")
        else:
            if not args.quiet:
                print("⚠️  OPENAI_API_KEY not set - AI analysis will not be included")
    except ImportError:
        if not args.quiet:
            print("⚠️  OpenAI package not available - AI analysis will not be included")

    client_packager = ClientPackager(evidence_manager, openai_client)

    try:
        if not args.quiet:
            print(f"📦 Creating client package for case: {args.case_id}")
            print(f"   Output directory: {args.output_dir}")
            print(f"   Format: {args.format}")
            print(f"   Include raw evidence: {args.include_raw_evidence}")

        # Create client package
        result = client_packager.create_client_package(
            case_id=args.case_id,
            output_directory=Path(args.output_dir),
            include_raw_evidence=args.include_raw_evidence,
            package_format=args.format
        )

        if result["success"]:
            if not args.quiet:
                print(f"\n✅ Client package created successfully!")
                print(f"   Package path: {result['package_path']}")
                print(f"   Evidence analyzed: {result['evidence_count']} pieces")
                print(f"   Package components:")

                component_counts = result["metadata"]["file_counts"]
                for component_type, count in component_counts.items():
                    if count > 0:
                        print(f"     - {component_type.replace('_', ' ').title()}: {count} files")

                if result["metadata"]["analysis_summary"]["ai_analysis_included"]:
                    print(f"   🤖 AI executive summary included")

                print(f"\n📋 Package ready for client delivery!")

            return 0
        else:
            print(f"❌ Failed to create client package")
            return 1

    except ValueError as e:
        print(f"❌ {e}")
        return 1
    except Exception as e:
        print(f"❌ Error creating client package: {e}")
        return 1


def main() -> int:
    """Main CLI entry point"""
    parser = create_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    if args.command == 'ingest':
        return handle_ingest_command(args)
    elif args.command == 'analyze':
        return handle_analyze_command(args)
    elif args.command == 'export':
        return handle_export_command(args)
    elif args.command == 'retaliation':
        return handle_retaliation_command(args)
    elif args.command == 'version':
        return handle_version_command(args)
    elif args.command == 'email':
        return handle_email_command(args)
    elif args.command == 'correlate':
        return handle_correlate_command(args)
    elif args.command == 'summary':
        return handle_summary_command(args)
    elif args.command == 'package':
        return handle_package_command(args)
    else:
        print(f"❌ Unknown command: {args.command}")
        return 1


if __name__ == '__main__':
    sys.exit(main())