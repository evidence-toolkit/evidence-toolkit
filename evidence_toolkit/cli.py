#!/usr/bin/env python3
"""
Unified Evidence Toolkit CLI.

Provides a single entry point for both document and image analysis capabilities.
"""

import click
import sys
from pathlib import Path

@click.group()
@click.version_option(version="0.1.0")
def main():
    """Evidence Toolkit - Comprehensive legal evidence analysis suite."""
    pass

@main.group()
def document():
    """Document evidence analysis commands."""
    pass

@main.group()
def image():
    """Image evidence analysis commands."""
    pass

@document.command()
@click.argument('input_path', type=click.Path(exists=True))
@click.option('--output-dir', '-o', help='Output directory for analysis results')
@click.option('--quiet', '-q', is_flag=True, help='Run silently')
def analyze(input_path, output_dir, quiet):
    """Analyze text documents for legal evidence processing."""
    try:
        from document_analyzer.cli import analyze_command
        analyze_command(input_path, output_dir, quiet)
    except ImportError:
        click.echo("Document analyzer not available. Install with: pip install -e ./document-evidence-analyzer/", err=True)
        sys.exit(1)

@image.command()
@click.argument('sha256_hash')
def analyze(sha256_hash):
    """Analyze image evidence by SHA256 hash."""
    try:
        import subprocess
        subprocess.run([
            sys.executable, "-m", "image_analysis.cli",
            "analyze", sha256_hash
        ], cwd=Path(__file__).parent.parent / "image-analysis")
    except Exception as e:
        click.echo(f"Image analyzer not available: {e}", err=True)
        sys.exit(1)

@image.command()
@click.argument('input_path', type=click.Path(exists=True))
@click.option('--case-id', required=True, help='Case identifier for evidence tracking')
def ingest(input_path, case_id):
    """Ingest images into content-addressed evidence storage."""
    try:
        import subprocess
        subprocess.run([
            sys.executable, "-m", "image_analysis.cli",
            "ingest", input_path, "--case-id", case_id
        ], cwd=Path(__file__).parent.parent / "image-analysis")
    except Exception as e:
        click.echo(f"Image analyzer not available: {e}", err=True)
        sys.exit(1)

if __name__ == "__main__":
    main()