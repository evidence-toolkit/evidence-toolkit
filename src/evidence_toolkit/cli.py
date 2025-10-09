#!/usr/bin/env python3
"""Evidence Toolkit CLI - v3.0

Clean command-line interface that delegates to pipeline components.
This is a thin wrapper for argument parsing and user feedback.

Commands:
- process-case: Complete pipeline (ingest → analyze → correlate → package)
- ingest: File ingestion into content-addressed storage
- analyze: Evidence analysis (documents, images, emails)
- correlate: Cross-evidence correlation and timeline analysis
- package: Client deliverable package generation
- version: Show version information

Architecture:
- All business logic is in pipeline modules
- CLI only handles argument parsing and user output
- Uses EvidenceStorage at data/storage (not "evidence")
"""

import sys
import time
import os
from datetime import datetime
from pathlib import Path
from typing import Optional

import click

from evidence_toolkit.core.storage import EvidenceStorage
from evidence_toolkit.core.models import EvidenceType, ChainOfCustodyEvent
from evidence_toolkit.pipeline import (
    ingest_path,
    print_ingestion_summary,
    analyze_evidence,
    SummaryGenerator,
    PackageGenerator,
)
from evidence_toolkit.analyzers.correlation import CorrelationAnalyzer
from evidence_toolkit.core.utils import get_evidence_base_dir


# Default storage location for v3.0
DEFAULT_STORAGE_PATH = Path("data/storage")


@click.group()
@click.version_option(version="3.3.0", prog_name="evidence-toolkit")
def cli():
    """Evidence Toolkit - AI-powered legal evidence analysis suite."""
    pass


@cli.command(name="process-case")
@click.argument('case_directory', type=click.Path(exists=True, path_type=Path))
@click.option('--case-id', required=True, help='Case ID for this evidence collection')
@click.option('--storage-dir', default=str(DEFAULT_STORAGE_PATH), help='Evidence storage directory (default: data/storage)')
@click.option('--output-dir', default='./data/packages', help='Output directory for client package (default: ./data/packages)')
@click.option('--skip-package', is_flag=True, help='Skip package generation (only ingest, analyze, correlate)')
@click.option('--ai-resolve', is_flag=True, help='Use AI to resolve ambiguous entity matches (v3.2 feature)')
@click.option('--case-type', type=click.Choice(['generic', 'workplace', 'employment', 'contract']),
              default='generic', help='Case type for domain-specific analysis (default: generic, v3.2 feature)')
@click.option('--max-concurrent', default=5, type=int, help='Max concurrent image analyses (default: 5, v3.3.1 feature)')
@click.option('--actor', default='system', help='Actor performing the processing (default: system)')
@click.option('--quiet', '-q', is_flag=True, help='Suppress verbose output')
def process_case(case_directory: Path, case_id: str, storage_dir: str, output_dir: str,
                skip_package: bool, ai_resolve: bool, case_type: str, max_concurrent: int, actor: str, quiet: bool):
    """Complete pipeline: ingest → analyze → correlate → package

    Process all evidence files in CASE_DIRECTORY through the complete analysis pipeline.
    """
    start_time = time.time()
    storage = EvidenceStorage(Path(storage_dir))

    if not quiet:
        click.echo("🔬 Evidence Toolkit v3.0 - Automated Case Processing Pipeline")
        click.echo("=" * 60)
        click.echo(f"📁 Case Directory: {case_directory}")
        click.echo(f"🆔 Case ID: {case_id}")
        click.echo(f"💾 Storage: {storage_dir}")
        click.echo("=" * 60)
        click.echo()

    # Step 1: Ingest Evidence
    if not quiet:
        click.echo("📥 [1/4] Ingesting evidence files...")

    try:
        results = ingest_path(case_directory, storage, case_id=case_id, actor=actor, quiet=quiet)
        print_ingestion_summary(results, quiet=quiet)
    except Exception as e:
        click.echo(f"❌ Ingestion failed: {e}", err=True)
        sys.exit(1)

    # Step 2: Analyze all evidence
    if not quiet:
        click.echo("\n🔍 [2/4] Analyzing evidence with AI...")

    # Initialize OpenAI client if available
    openai_client = None
    try:
        import openai
        api_key = os.getenv('OPENAI_API_KEY')
        if api_key:
            openai_client = openai.OpenAI(api_key=api_key)
            if not quiet:
                click.echo("   🤖 AI analysis enabled (OpenAI)")
        else:
            if not quiet:
                click.echo("   ⚠️  OPENAI_API_KEY not set - AI analysis disabled")
    except ImportError:
        if not quiet:
            click.echo("   ⚠️  OpenAI package not available - AI analysis disabled")

    analyzed_count = 0
    skipped_count = 0

    # Get only the evidence that was just ingested (from results)
    ingested_sha256s = [r.sha256 for r in results if r.success]

    # v3.3.1: Separate images for batch processing
    image_sha256s = []
    non_image_sha256s = []

    for sha256 in ingested_sha256s:
        original_file = storage.get_original_file_path(sha256)
        if original_file and original_file.suffix.lower() in ['.jpg', '.jpeg', '.png', '.gif', '.bmp']:
            image_sha256s.append(sha256)
        else:
            non_image_sha256s.append(sha256)

    # Batch process images if we have any
    if image_sha256s and openai_client:
        if not quiet:
            click.echo(f"\n   ⚡ Batch processing {len(image_sha256s)} images ({max_concurrent} concurrent)...")

        try:
            import asyncio
            from evidence_toolkit.pipeline.batch import analyze_images_batch

            # Run async batch processing
            batch_results = asyncio.run(analyze_images_batch(
                image_sha256s,
                storage,
                case_id=case_id,
                max_concurrent=max_concurrent,
                quiet=quiet
            ))

            analyzed_count += len([r for r in batch_results.values() if r.image_analysis])
            if not quiet:
                click.echo(f"   ✅ Batch analyzed {len(batch_results)} images")

        except Exception as e:
            if not quiet:
                click.echo(f"   ⚠️  Batch processing failed, falling back to sequential: {e}")
            # Fall back to sequential processing
            for sha256 in image_sha256s:
                non_image_sha256s.append(sha256)

    # Process non-image evidence sequentially
    for sha256 in non_image_sha256s:
        # Check if already analyzed
        sha256_dir = get_evidence_base_dir(storage.derived_dir, sha256)
        analysis_file = sha256_dir / "analysis.v1.json"

        if analysis_file.exists():
            # Check if already associated with this case
            existing_analysis = storage.get_analysis(sha256)
            if existing_analysis and case_id in existing_analysis.case_ids:
                skipped_count += 1
                continue
            elif existing_analysis and case_id not in existing_analysis.case_ids:
                # Add to new case without re-analyzing
                existing_analysis.case_ids.append(case_id)

                # Add custody event
                custody_event = ChainOfCustodyEvent(
                    timestamp=datetime.now(),
                    event_type='case_association',
                    actor=actor,
                    description=f"Associated with case {case_id}",
                    metadata={'previous_cases': existing_analysis.case_ids[:-1]}
                )
                storage._add_custody_event(sha256, custody_event)

                # Save updated analysis
                storage.save_analysis(existing_analysis)
                skipped_count += 1  # Changed from analyzed_count - this is a skip, not new analysis
                continue

        # Analyze new evidence (not yet analyzed)
        try:
            analyze_evidence(
                sha256=sha256,
                storage=storage,
                openai_client=openai_client,
                case_id=case_id,
                evidence_type='auto',
                quiet=True
            )
            analyzed_count += 1

            if not quiet and analyzed_count % 5 == 0:
                click.echo(f"   Analyzed {analyzed_count} items...")
        except Exception as e:
            if not quiet:
                click.echo(f"   ⚠️  Failed to analyze {sha256[:8]}: {e}")

    if not quiet:
        click.echo(f"   ✅ Analyzed {analyzed_count} new items (skipped {skipped_count} existing)")

    # Step 3: Cross-evidence correlation
    if not quiet:
        click.echo("\n🔗 [3/4] Running cross-evidence correlation...")
        if ai_resolve:
            click.echo("   🤖 AI entity resolution enabled")

    try:
        # v3.1: Pass openai_client for AI pattern detection
        correlation_analyzer = CorrelationAnalyzer(storage, openai_client=openai_client, verbose=not quiet)
        correlation_result = correlation_analyzer.analyze_case_correlations(case_id, ai_resolve=ai_resolve)

        if not quiet:
            click.echo(f"   ✅ Found {len(correlation_result.entity_correlations)} correlated entities")
            click.echo(f"   ✅ Extracted {len(correlation_result.timeline_events)} timeline events")
    except Exception as e:
        click.echo(f"   ⚠️  Correlation analysis had issues: {e}")

    # Step 4: Generate client package
    if not skip_package:
        if not quiet:
            click.echo("\n📦 [4/4] Generating client package...")

        try:
            package_generator = PackageGenerator(storage, openai_client, case_type=case_type)
            result = package_generator.create_client_package(
                case_id=case_id,
                output_directory=Path(output_dir),
                include_raw_evidence=True,
                package_format='zip'
            )

            if result["success"] and not quiet:
                click.echo(f"   ✅ Package created: {result['package_path']}")
                package_size = Path(result['package_path']).stat().st_size / (1024 * 1024)
                click.echo(f"   📊 Size: {package_size:.1f} MB")
        except Exception as e:
            click.echo(f"❌ Package generation failed: {e}", err=True)
            sys.exit(1)

    # Summary
    elapsed_time = time.time() - start_time
    if not quiet:
        click.echo("\n" + "=" * 60)
        click.echo("✅ Case Processing Complete!")
        click.echo("=" * 60)
        click.echo(f"⏱️  Total time: {elapsed_time:.1f} seconds")
        click.echo(f"📊 Evidence processed: {analyzed_count + skipped_count} items")
        click.echo()


@cli.command(name="ingest")
@click.argument('input_path', type=click.Path(exists=True, path_type=Path))
@click.option('--case-id', help='Case ID to associate with this evidence')
@click.option('--actor', default='system', help='Actor performing the ingestion (default: system)')
@click.option('--storage-dir', default=str(DEFAULT_STORAGE_PATH), help='Evidence storage directory (default: data/storage)')
@click.option('--quiet', '-q', is_flag=True, help='Suppress verbose output')
def ingest_cmd(input_path: Path, case_id: Optional[str], actor: str, storage_dir: str, quiet: bool):
    """Ingest evidence into content-addressed storage

    INPUT_PATH can be a file or directory. All files will be ingested with SHA256-based deduplication.
    """
    storage = EvidenceStorage(Path(storage_dir))

    try:
        results = ingest_path(input_path, storage, case_id=case_id, actor=actor, quiet=quiet)
        print_ingestion_summary(results, quiet=quiet)
    except Exception as e:
        click.echo(f"❌ Ingestion failed: {e}", err=True)
        sys.exit(1)


@cli.command(name="analyze")
@click.argument('sha256')
@click.option('--case-id', help='Case ID to associate with analysis')
@click.option('--storage-dir', default=str(DEFAULT_STORAGE_PATH), help='Evidence storage directory (default: data/storage)')
@click.option('--type', 'evidence_type', type=click.Choice(['auto', 'document', 'image', 'email']),
              default='auto', help='Evidence type (default: auto-detect)')
@click.option('--force', is_flag=True, help='Force re-analysis even if analysis exists')
@click.option('--quiet', '-q', is_flag=True, help='Suppress verbose output')
def analyze_cmd(sha256: str, case_id: Optional[str], storage_dir: str, evidence_type: str, force: bool, quiet: bool):
    """Analyze evidence by SHA256 hash

    Performs AI-powered analysis on ingested evidence:
    - Documents: Text analysis, entity extraction, sentiment
    - Images: Vision AI with OCR and scene analysis
    - Emails: Thread analysis, participant tracking, escalation detection

    Use --force to re-analyze evidence that already has an analysis.
    Previous analysis will be backed up before being overwritten.
    """
    storage = EvidenceStorage(Path(storage_dir))

    # Initialize OpenAI client
    openai_client = None
    try:
        import openai
        api_key = os.getenv('OPENAI_API_KEY')
        if api_key:
            openai_client = openai.OpenAI(api_key=api_key)
        elif not quiet:
            click.echo("⚠️  OPENAI_API_KEY not set - AI analysis may be limited")
    except ImportError:
        if not quiet:
            click.echo("⚠️  OpenAI package not available - AI analysis may be limited")

    try:
        analyze_evidence(
            sha256=sha256,
            storage=storage,
            openai_client=openai_client,
            case_id=case_id,
            evidence_type=evidence_type,
            force=force,
            quiet=quiet
        )

        if not quiet:
            click.echo(f"✅ Analysis complete for {sha256[:12]}...")
    except Exception as e:
        click.echo(f"❌ Analysis failed: {e}", err=True)
        sys.exit(1)


@cli.command(name="correlate")
@click.option('--case-id', required=True, help='Case ID to analyze for correlations')
@click.option('--storage-dir', default=str(DEFAULT_STORAGE_PATH), help='Evidence storage directory (default: data/storage)')
@click.option('--json-output', type=click.Path(path_type=Path), help='Save correlation results as JSON')
@click.option('--ai-resolve', is_flag=True, help='Use AI to resolve ambiguous entity matches (v3.2 feature)')
@click.option('--quiet', '-q', is_flag=True, help='Suppress verbose output')
def correlate_cmd(case_id: str, storage_dir: str, json_output: Optional[Path], ai_resolve: bool, quiet: bool):
    """Analyze correlations across evidence types

    Performs cross-evidence analysis:
    - Entity correlation (people, organizations, locations)
    - Timeline reconstruction from all evidence
    - Pattern detection across documents, emails, and images
    """
    storage = EvidenceStorage(Path(storage_dir))
    # v3.1: Try to get OpenAI client for pattern detection (optional)
    openai_client = None
    try:
        import openai
        import os
        api_key = os.getenv('OPENAI_API_KEY')
        if api_key:
            openai_client = openai.OpenAI(api_key=api_key)
            if not quiet:
                click.echo("🤖 AI pattern detection enabled")
    except (ImportError, Exception):
        if not quiet:
            click.echo("⚠️  AI pattern detection disabled (OpenAI not available)")

    correlation_analyzer = CorrelationAnalyzer(storage, openai_client=openai_client, verbose=not quiet)

    try:
        if not quiet:
            click.echo(f"🔍 Analyzing correlations for case: {case_id}")
            if ai_resolve:
                click.echo("🤖 AI entity resolution enabled")

        result = correlation_analyzer.analyze_case_correlations(case_id, ai_resolve=ai_resolve)

        if result.evidence_count == 0:
            click.echo(f"❌ No evidence found for case ID: {case_id}", err=True)
            sys.exit(1)

        # Display results
        if not quiet:
            click.echo("\n📊 Cross-Evidence Correlation Analysis")
            click.echo("=" * 50)
            click.echo(f"Case ID: {result.case_id}")
            click.echo(f"Evidence analyzed: {result.evidence_count} items")
            click.echo(f"Entity correlations: {len(result.entity_correlations)}")
            click.echo(f"Timeline events: {len(result.timeline_events)}")

            if result.entity_correlations:
                click.echo("\n🔗 Top Entity Correlations:")
                for i, corr in enumerate(result.entity_correlations[:5], 1):
                    click.echo(f"  {i}. {corr.entity_name} ({corr.entity_type})")
                    click.echo(f"     Appears in {corr.occurrence_count} evidence pieces")
                    click.echo(f"     Average confidence: {corr.confidence_average:.2f}")

            if result.timeline_events:
                click.echo(f"\n⏰ Timeline: {len(result.timeline_events)} events")
                click.echo(f"   First: {result.timeline_events[0].timestamp.strftime('%Y-%m-%d %H:%M')}")
                click.echo(f"   Last: {result.timeline_events[-1].timestamp.strftime('%Y-%m-%d %H:%M')}")

        # Save JSON if requested
        if json_output:
            import json
            output_data = result.model_dump(mode='json')
            with open(json_output, 'w') as f:
                json.dump(output_data, f, indent=2, default=str)

            if not quiet:
                click.echo(f"\n✅ Correlation analysis saved to: {json_output}")

    except Exception as e:
        click.echo(f"❌ Correlation analysis failed: {e}", err=True)
        sys.exit(1)


@cli.command(name="package")
@click.option('--case-id', required=True, help='Case ID to package')
@click.option('--storage-dir', default=str(DEFAULT_STORAGE_PATH), help='Evidence storage directory (default: data/storage)')
@click.option('--output-dir', default='./data/packages', help='Output directory (default: ./data/packages)')
@click.option('--include-raw', is_flag=True, help='Include original evidence files')
@click.option('--format', 'package_format', type=click.Choice(['zip', 'directory']),
              default='zip', help='Package format (default: zip)')
@click.option('--case-type', type=click.Choice(['generic', 'workplace', 'employment', 'contract']),
              default='generic', help='Case type for domain-specific executive summary (default: generic)')
@click.option('--quiet', '-q', is_flag=True, help='Suppress verbose output')
def package_cmd(case_id: str, storage_dir: str, output_dir: str, include_raw: bool,
                package_format: str, case_type: str, quiet: bool):
    """Create client deliverable package

    Generates professional client package with:
    - Executive summary (AI-generated)
    - Analysis results for all evidence
    - Cross-evidence correlations
    - Timeline visualization
    - Optional: Original evidence files
    """
    storage = EvidenceStorage(Path(storage_dir))

    # Initialize OpenAI client for executive summary
    openai_client = None
    try:
        import openai
        api_key = os.getenv('OPENAI_API_KEY')
        if api_key:
            openai_client = openai.OpenAI(api_key=api_key)
            if not quiet:
                click.echo("🤖 AI executive summary enabled")
        else:
            if not quiet:
                click.echo("⚠️  OPENAI_API_KEY not set - executive summary disabled")
    except ImportError:
        if not quiet:
            click.echo("⚠️  OpenAI package not available - executive summary disabled")

    package_generator = PackageGenerator(storage, openai_client, case_type=case_type)

    try:
        if not quiet:
            click.echo(f"📦 Creating client package for case: {case_id}")
            click.echo(f"   Output directory: {output_dir}")
            click.echo(f"   Format: {package_format}")
            click.echo(f"   Case type: {case_type}")
            click.echo(f"   Include raw evidence: {include_raw}")

        result = package_generator.create_client_package(
            case_id=case_id,
            output_directory=Path(output_dir),
            include_raw_evidence=include_raw,
            package_format=package_format
        )

        if result["success"]:
            if not quiet:
                click.echo(f"\n✅ Client package created successfully!")
                click.echo(f"   Package path: {result['package_path']}")
                click.echo(f"   Evidence analyzed: {result['evidence_count']} pieces")

                package_size = Path(result['package_path']).stat().st_size / (1024 * 1024)
                click.echo(f"   Size: {package_size:.1f} MB")

                if result["metadata"]["analysis_summary"]["ai_analysis_included"]:
                    click.echo(f"   🤖 AI executive summary included")

                click.echo(f"\n📋 Package ready for client delivery!")
        else:
            click.echo(f"❌ Failed to create client package", err=True)
            sys.exit(1)

    except Exception as e:
        click.echo(f"❌ Package generation failed: {e}", err=True)
        sys.exit(1)


# =============================================================================
# STORAGE MANAGEMENT COMMANDS (v3.0 CLI Extensions)
# =============================================================================

@cli.group(name="storage")
def storage_group():
    """Storage management commands"""
    pass


@storage_group.command(name="stats")
@click.option('--storage-dir', default=str(DEFAULT_STORAGE_PATH), help='Evidence storage directory')
def storage_stats_cmd(storage_dir: str):
    """Display storage statistics

    Shows comprehensive metrics about evidence storage including:
    - Evidence counts (total and by type)
    - Storage sizes (raw and derived)
    - Case and label counts
    - Health indicators (orphaned files)
    """
    storage = EvidenceStorage(Path(storage_dir))

    try:
        stats = storage.get_storage_stats()

        click.echo("📊 Storage Statistics")
        click.echo("=" * 60)
        click.echo(f"Evidence: {stats.total_evidence} items ({stats.storage_size_mb:.2f} MB total)")

        if stats.evidence_by_type:
            for evidence_type, count in sorted(stats.evidence_by_type.items()):
                click.echo(f"  - {evidence_type}: {count} items")

        click.echo(f"\nStorage breakdown:")
        click.echo(f"  - Raw files: {stats.raw_size_mb:.2f} MB")
        click.echo(f"  - Derived/analysis: {stats.derived_size_mb:.2f} MB")

        click.echo(f"\nCases: {stats.total_cases}")
        click.echo(f"Labels: {stats.total_labels} categories")

        if stats.orphaned_files > 0:
            click.echo(f"\n⚠️  Orphaned files: {stats.orphaned_files} (not linked to any case)", err=True)
            click.echo(f"    Run 'evidence-toolkit storage cleanup' to review")
        else:
            click.echo(f"\n✅ No orphaned files detected")

    except Exception as e:
        click.echo(f"❌ Failed to retrieve storage stats: {e}", err=True)
        sys.exit(1)


@storage_group.command(name="cleanup")
@click.option('--storage-dir', default=str(DEFAULT_STORAGE_PATH), help='Evidence storage directory')
@click.option('--dry-run', is_flag=True, default=True, help='Preview changes without applying (default)')
@click.option('--force', is_flag=True, help='Actually perform cleanup (overrides --dry-run)')
def storage_cleanup_cmd(storage_dir: str, dry_run: bool, force: bool):
    """Clean up orphaned links and empty directories

    Removes:
    - Broken hard links in labels/
    - Empty label directories
    - Reports orphaned evidence files

    Use --force to apply changes, otherwise runs in dry-run mode.
    """
    storage = EvidenceStorage(Path(storage_dir))

    # Force dry-run unless --force is set
    if not force:
        dry_run = True

    try:
        result = storage.cleanup_storage(dry_run=dry_run)

        if dry_run:
            click.echo("🔍 Dry run mode (use --force to apply changes)")
            click.echo("=" * 60)
        else:
            click.echo("🧹 Cleanup complete")
            click.echo("=" * 60)

        if result.broken_links_removed > 0:
            action = "Would remove" if dry_run else "Removed"
            click.echo(f"{action} {result.broken_links_removed} broken link(s)")
        else:
            click.echo("No broken links found")

        if result.empty_dirs_removed > 0:
            action = "Would remove" if dry_run else "Removed"
            click.echo(f"{action} {result.empty_dirs_removed} empty director(ies)")
        else:
            click.echo("No empty directories found")

        if result.orphaned_files > 0:
            click.echo(f"\n⚠️  Found {result.orphaned_files} orphaned file(s)")
            click.echo(f"    (Evidence not linked to any case)")
            click.echo(f"    Use 'evidence-toolkit storage prune' to remove if needed")

        if dry_run and (result.broken_links_removed > 0 or result.empty_dirs_removed > 0):
            click.echo(f"\nRun with --force to apply these changes")

    except Exception as e:
        click.echo(f"❌ Cleanup failed: {e}", err=True)
        sys.exit(1)


@storage_group.command(name="prune")
@click.option('--case-id', required=True, help='Case ID to prune evidence for')
@click.option('--storage-dir', default=str(DEFAULT_STORAGE_PATH), help='Evidence storage directory')
@click.option('--dry-run', is_flag=True, default=True, help='Preview changes without applying (default)')
@click.option('--force', is_flag=True, help='Actually remove evidence (overrides --dry-run)')
def storage_prune_cmd(case_id: str, storage_dir: str, dry_run: bool, force: bool):
    """Remove evidence unique to a specific case

    Only removes evidence that belongs EXCLUSIVELY to the specified case.
    Evidence shared with other cases is preserved.

    WARNING: This is a destructive operation. Use --dry-run first!
    """
    storage = EvidenceStorage(Path(storage_dir))

    # Force dry-run unless --force is set
    if not force:
        dry_run = True

    try:
        # Verify case exists
        evidence_list = storage.list_evidence(case_id)
        if not evidence_list:
            click.echo(f"❌ Case not found: {case_id}", err=True)
            sys.exit(1)

        removed = storage.prune_case_evidence(case_id, dry_run=dry_run)

        if dry_run:
            click.echo(f"🔍 Dry run for case: {case_id}")
            click.echo("=" * 60)
            click.echo(f"Would remove {len(removed)} evidence item(s)")
            if removed:
                click.echo("\nEvidence to be removed (unique to this case):")
                for sha256 in removed[:5]:  # Show first 5
                    click.echo(f"  - {sha256[:16]}...")
                if len(removed) > 5:
                    click.echo(f"  ... and {len(removed) - 5} more")
            click.echo(f"\nRun with --force to actually remove this evidence")
        else:
            click.echo(f"🗑️  Pruned case: {case_id}")
            click.echo("=" * 60)
            click.echo(f"Removed {len(removed)} evidence item(s)")

    except Exception as e:
        click.echo(f"❌ Prune failed: {e}", err=True)
        sys.exit(1)


# =============================================================================
# CASE MANAGEMENT COMMANDS (v3.0 CLI Extensions)
# =============================================================================

@cli.group(name="case")
def case_group():
    """Case management commands"""
    pass


@case_group.command(name="list")
@click.option('--storage-dir', default=str(DEFAULT_STORAGE_PATH), help='Evidence storage directory')
@click.option('--detailed', is_flag=True, help='Show detailed information')
def case_list_cmd(storage_dir: str, detailed: bool):
    """List all cases in storage

    Shows all cases with evidence counts and last modification times.
    Use --detailed for expanded information including evidence types.
    """
    storage = EvidenceStorage(Path(storage_dir))

    try:
        cases = storage.list_cases()

        if not cases:
            click.echo("No cases found in storage.")
            click.echo(f"Storage location: {storage_dir}")
            return

        click.echo("📁 Cases in Storage")
        click.echo("=" * 80)

        if detailed:
            for case in cases:
                click.echo(f"\n{case.case_id}")
                click.echo(f"  Evidence: {case.evidence_count} items ({case.total_size_mb:.2f} MB)")
                click.echo(f"  Types: {', '.join(case.evidence_types)}")
                click.echo(f"  Modified: {case.last_modified.strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            # Table format
            click.echo(f"{'CASE ID':<30} {'Evidence':<12} {'Last Modified':<20}")
            click.echo("-" * 80)
            for case in cases:
                click.echo(
                    f"{case.case_id:<30} "
                    f"{case.evidence_count:<12} "
                    f"{case.last_modified.strftime('%Y-%m-%d %H:%M'):<20}"
                )

        click.echo(f"\nTotal: {len(cases)} case(s)")

    except Exception as e:
        click.echo(f"❌ Failed to list cases: {e}", err=True)
        sys.exit(1)


@case_group.command(name="show")
@click.argument('case_id')
@click.option('--storage-dir', default=str(DEFAULT_STORAGE_PATH), help='Evidence storage directory')
@click.option('--full-hash', is_flag=True, help='Show full SHA256 hashes')
def case_show_cmd(case_id: str, storage_dir: str, full_hash: bool):
    """Show detailed case information

    Displays comprehensive information about a specific case including:
    - Evidence inventory with types and filenames
    - File sizes and SHA256 hashes
    - Legal significance and risk flags
    """
    storage = EvidenceStorage(Path(storage_dir))

    try:
        evidence_sha256s = storage.list_evidence(case_id)

        if not evidence_sha256s:
            click.echo(f"❌ Case not found: {case_id}", err=True)
            sys.exit(1)

        click.echo(f"📁 Case: {case_id}")
        click.echo("=" * 80)
        click.echo(f"Evidence count: {len(evidence_sha256s)} items\n")

        # Load and display evidence details
        for i, sha256 in enumerate(evidence_sha256s, 1):
            analysis = storage.get_analysis(sha256)
            if analysis:
                hash_display = sha256 if full_hash else f"{sha256[:16]}..."
                click.echo(f"{i}. {analysis.file_metadata.filename}")
                click.echo(f"   Type: {analysis.evidence_type.value}")
                click.echo(f"   SHA256: {hash_display}")
                click.echo(f"   Size: {analysis.file_metadata.file_size / 1024:.1f} KB")

                # Show significance if available
                if hasattr(analysis, 'legal_significance') and analysis.legal_significance:
                    click.echo(f"   Significance: {analysis.legal_significance}")

                click.echo()

    except Exception as e:
        click.echo(f"❌ Failed to show case: {e}", err=True)
        sys.exit(1)


@case_group.command(name="evidence")
@click.argument('case_id')
@click.option('--storage-dir', default=str(DEFAULT_STORAGE_PATH), help='Evidence storage directory')
@click.option('--full-hash', is_flag=True, help='Show full SHA256 hashes')
def case_evidence_cmd(case_id: str, storage_dir: str, full_hash: bool):
    """List evidence files in a case

    Simple listing of evidence with SHA256, filename, and type.
    Use 'case show' for more detailed information.
    """
    storage = EvidenceStorage(Path(storage_dir))

    try:
        evidence_sha256s = storage.list_evidence(case_id)

        if not evidence_sha256s:
            click.echo(f"❌ Case not found: {case_id}", err=True)
            sys.exit(1)

        click.echo(f"Evidence in case: {case_id}")
        click.echo("=" * 80)

        # Table header
        hash_col_width = 64 if full_hash else 18
        click.echo(f"{'SHA256':<{hash_col_width}} {'Type':<12} {'Filename'}")
        click.echo("-" * 80)

        for sha256 in evidence_sha256s:
            analysis = storage.get_analysis(sha256)
            if analysis:
                hash_display = sha256 if full_hash else f"{sha256[:16]}..."
                click.echo(
                    f"{hash_display:<{hash_col_width}} "
                    f"{analysis.evidence_type.value:<12} "
                    f"{analysis.file_metadata.filename}"
                )

        click.echo(f"\nTotal: {len(evidence_sha256s)} item(s)")

    except Exception as e:
        click.echo(f"❌ Failed to list evidence: {e}", err=True)
        sys.exit(1)


# =============================================================================
# RE-ANALYSIS COMMANDS (v3.0 CLI Extensions)
# =============================================================================

@cli.command(name="reanalyze")
@click.option('--case-id', required=True, help='Case ID to re-analyze')
@click.option('--storage-dir', default=str(DEFAULT_STORAGE_PATH), help='Evidence storage directory')
@click.option('--evidence-type', type=click.Choice(['all', 'document', 'image', 'email']),
              default='all', help='Filter by evidence type (default: all)')
@click.option('--dry-run', is_flag=True, help='Preview what would be re-analyzed')
@click.option('--quiet', '-q', is_flag=True, help='Suppress verbose output')
def reanalyze_cmd(case_id: str, storage_dir: str, evidence_type: str, dry_run: bool, quiet: bool):
    """Batch re-analyze all evidence in a case

    Re-runs AI analysis on all evidence items in the specified case.
    Previous analysis results are backed up before being overwritten.

    Use --dry-run to preview what would be re-analyzed without making changes.
    """
    storage = EvidenceStorage(Path(storage_dir))

    try:
        evidence_sha256s = storage.list_evidence(case_id)

        if not evidence_sha256s:
            click.echo(f"❌ No evidence found for case: {case_id}", err=True)
            sys.exit(1)

        # Filter by evidence type if specified
        if evidence_type != 'all':
            filtered = []
            for sha256 in evidence_sha256s:
                analysis = storage.get_analysis(sha256)
                if analysis and analysis.evidence_type.value == evidence_type:
                    filtered.append(sha256)
            evidence_sha256s = filtered

        if not quiet:
            click.echo(f"Re-analyzing case: {case_id}")
            click.echo(f"Evidence items: {len(evidence_sha256s)}")
            if evidence_type != 'all':
                click.echo(f"Filter: {evidence_type} only")

        if dry_run:
            click.echo("🔍 Dry run mode - no changes will be made")
            click.echo("\nWould re-analyze:")
            for sha256 in evidence_sha256s:
                analysis = storage.get_analysis(sha256)
                if analysis:
                    click.echo(f"  - {sha256[:16]}... ({analysis.evidence_type.value}): {analysis.file_metadata.filename}")
            return

        # Initialize OpenAI client
        openai_client = None
        try:
            import openai
            api_key = os.getenv('OPENAI_API_KEY')
            if api_key:
                openai_client = openai.OpenAI(api_key=api_key)
                if not quiet:
                    click.echo("🤖 OpenAI client initialized")
            else:
                if not quiet:
                    click.echo("⚠️  OPENAI_API_KEY not set - AI analysis may be limited")
        except ImportError:
            if not quiet:
                click.echo("⚠️  OpenAI package not available - AI analysis may be limited")

        # Re-analyze each piece
        successful = 0
        failed = 0

        for i, sha256 in enumerate(evidence_sha256s, 1):
            if not quiet:
                click.echo(f"[{i}/{len(evidence_sha256s)}] Analyzing {sha256[:12]}...")

            try:
                analyze_evidence(
                    sha256=sha256,
                    storage=storage,
                    openai_client=openai_client,
                    case_id=case_id,
                    evidence_type='auto',
                    force=True,  # Force re-analysis
                    quiet=quiet
                )
                successful += 1
                if not quiet:
                    click.echo(f"  ✅ Complete")
            except Exception as e:
                failed += 1
                click.echo(f"  ❌ Failed: {e}", err=True)

        if not quiet:
            click.echo(f"\n✅ Re-analysis complete: {successful} successful, {failed} failed")

    except Exception as e:
        click.echo(f"❌ Re-analysis failed: {e}", err=True)
        sys.exit(1)


@cli.command(name="version")
def version_cmd():
    """Show version information"""
    click.echo("Evidence Toolkit v3.0.0")
    click.echo("AI-powered legal evidence analysis suite")
    click.echo()
    click.echo("Components:")
    click.echo("  - Content-addressed evidence storage (SHA256)")
    click.echo("  - Multi-modal AI analysis (OpenAI)")
    click.echo("  - Cross-evidence correlation")
    click.echo("  - Timeline reconstruction")
    click.echo("  - Client package generation")
    click.echo()
    click.echo("Default storage: data/storage")


def main():
    """Main CLI entry point"""
    cli()


if __name__ == '__main__':
    main()
