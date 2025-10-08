#!/usr/bin/env python3
"""Client Package Generator - v3.0

Creates professional client deliverable packages containing all case analysis results,
visualizations, reports, and evidence catalogs formatted for legal proceedings and
consulting engagements.

Moved from document_analyzer/client_packager.py for v3.0 architecture.
"""

import json
import shutil
import zipfile
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

from evidence_toolkit.core.storage import EvidenceStorage
from evidence_toolkit.pipeline.summary import SummaryGenerator, CaseSummary


class PackageGenerator:
    """Creates professional client deliverable packages.

    v3.0: Renamed from ClientPackager, now uses EvidenceStorage
    """

    def __init__(self, storage: EvidenceStorage, openai_client=None, case_type: str = 'generic'):
        """Initialize package generator.

        Args:
            storage: EvidenceStorage instance for accessing evidence
            openai_client: Optional OpenAI client for AI summaries
            case_type: Type of case for domain-specific prompts (generic, workplace, contract)
        """
        self.storage = storage
        self.summary_generator = SummaryGenerator(storage, openai_client, case_type=case_type)
        self.case_type = case_type

    def create_client_package(
        self,
        case_id: str,
        output_directory: Path,
        include_raw_evidence: bool = False,
        package_format: str = "zip"
    ) -> Dict[str, Any]:
        """Create a comprehensive client package for a case.

        Args:
            case_id: Case identifier to package
            output_directory: Directory to create the package in
            include_raw_evidence: Whether to include original evidence files
            package_format: Format for package ('zip' or 'directory')

        Returns:
            Dictionary with package creation results

        Raises:
            Exception: If package creation fails
        """
        output_directory = Path(output_directory)
        output_directory.mkdir(parents=True, exist_ok=True)

        # Create package directory structure
        package_name = f"{case_id}_analysis_package_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        package_dir = output_directory / package_name

        try:
            # Create package structure
            self._create_package_structure(package_dir)

            # Generate case summary
            case_summary = self.summary_generator.generate_case_summary(case_id)

            # Create all package components
            components = self._create_package_components(case_summary, package_dir, include_raw_evidence)

            # Create package metadata
            package_metadata = self._create_package_metadata(case_summary, components)

            # Save package metadata
            metadata_file = package_dir / "package_metadata.json"
            with open(metadata_file, 'w') as f:
                json.dump(package_metadata, f, indent=2)

            # Create package (ZIP or leave as directory)
            if package_format == "zip":
                zip_path = output_directory / f"{package_name}.zip"
                self._create_zip_package(package_dir, zip_path)
                # Remove directory after zipping
                shutil.rmtree(package_dir)
                final_path = zip_path
            else:
                final_path = package_dir

            return {
                "success": True,
                "package_path": str(final_path),
                "case_id": case_id,
                "evidence_count": case_summary.evidence_count,
                "components": components,
                "metadata": package_metadata
            }

        except Exception as e:
            # Clean up on error
            if package_dir.exists():
                shutil.rmtree(package_dir)
            raise Exception(f"Failed to create client package: {e}")

    def _create_package_structure(self, package_dir: Path):
        """Create the directory structure for the client package.

        Args:
            package_dir: Root directory for the package
        """
        subdirs = [
            "reports",           # Executive summaries and text reports
            "analysis",          # JSON analysis files
            "visualizations",    # Charts, word clouds, etc.
            "evidence_catalog",  # Evidence metadata and chain of custody
            "correlations",      # Cross-evidence correlation results
            "documentation",     # README and methodology docs
            "raw_evidence"       # Original evidence files (if included)
        ]

        for subdir in subdirs:
            (package_dir / subdir).mkdir(parents=True, exist_ok=True)

    def _create_package_components(
        self,
        case_summary: CaseSummary,
        package_dir: Path,
        include_raw_evidence: bool
    ) -> Dict[str, List[str]]:
        """Create all components of the client package.

        Args:
            case_summary: CaseSummary object with all case data
            package_dir: Root package directory
            include_raw_evidence: Whether to include original evidence files

        Returns:
            Dictionary mapping component types to created files
        """
        components = {
            "reports": [],
            "analysis": [],
            "visualizations": [],
            "evidence_catalog": [],
            "correlations": [],
            "documentation": [],
            "raw_evidence": []
        }

        # 1. Executive Summary Report
        exec_report_path = package_dir / "reports" / "executive_summary.txt"
        formatted_report = self.summary_generator.format_summary_report(case_summary)
        with open(exec_report_path, 'w') as f:
            f.write(formatted_report)
        components["reports"].append("executive_summary.txt")

        # 2. Detailed JSON Analysis
        json_analysis_path = package_dir / "analysis" / "case_analysis.json"
        self.summary_generator.export_summary_to_json(case_summary, json_analysis_path)
        components["analysis"].append("case_analysis.json")

        # 3. Individual Evidence Analysis Files
        for evidence in case_summary.evidence_summaries:
            evidence_analysis_file = self._copy_evidence_analysis(evidence, package_dir)
            if evidence_analysis_file:
                components["analysis"].append(evidence_analysis_file)

        # 4. Visualizations (word clouds, charts)
        viz_files = self._copy_visualizations(case_summary, package_dir)
        components["visualizations"].extend(viz_files)

        # 5. Evidence Catalog
        catalog_file = self._create_evidence_catalog(case_summary, package_dir)
        components["evidence_catalog"].append(catalog_file)

        # 6. Correlation Analysis
        correlation_file = self._create_correlation_report(case_summary, package_dir)
        components["correlations"].append(correlation_file)

        # 7. Documentation
        doc_files = self._create_documentation(case_summary, package_dir)
        components["documentation"].extend(doc_files)

        # 8. Raw Evidence (if requested)
        if include_raw_evidence:
            raw_files = self._copy_raw_evidence(case_summary, package_dir)
            components["raw_evidence"].extend(raw_files)

        return components

    def _copy_evidence_analysis(self, evidence_summary, package_dir: Path) -> Optional[str]:
        """Copy individual evidence analysis file to package.

        Args:
            evidence_summary: EvidenceSummary object
            package_dir: Package root directory

        Returns:
            Filename if successful, None otherwise
        """
        try:
            # Find the analysis file
            evidence_dir = self.storage.derived_dir / f"sha256={evidence_summary.sha256}"
            analysis_file = evidence_dir / "analysis.v1.json"

            if analysis_file.exists():
                # Copy with descriptive name
                safe_filename = evidence_summary.filename.replace('/', '_').replace('\\', '_')
                dest_filename = f"{evidence_summary.evidence_type}_{safe_filename}_{evidence_summary.sha256[:8]}.json"
                dest_path = package_dir / "analysis" / dest_filename

                shutil.copy2(analysis_file, dest_path)
                return dest_filename

        except Exception as e:
            print(f"Warning: Could not copy analysis for {evidence_summary.filename}: {e}")

        return None

    def _copy_visualizations(self, case_summary: CaseSummary, package_dir: Path) -> List[str]:
        """Copy visualization files (word clouds, charts) to package.

        Args:
            case_summary: CaseSummary object
            package_dir: Package root directory

        Returns:
            List of copied visualization filenames
        """
        viz_files = []

        for evidence in case_summary.evidence_summaries:
            if evidence.evidence_type == "document":
                # Look for word clouds and frequency charts
                evidence_dir = self.storage.derived_dir / f"sha256={evidence.sha256}"

                # Common visualization files
                viz_patterns = ["word_cloud.png", "word_frequency.png", "*.png", "*.jpg", "*.pdf"]

                for pattern in viz_patterns:
                    for viz_file in evidence_dir.glob(pattern):
                        if viz_file.is_file():
                            safe_filename = evidence.filename.replace('/', '_').replace('\\', '_')
                            dest_filename = f"{evidence.evidence_type}_{safe_filename}_{viz_file.name}"
                            dest_path = package_dir / "visualizations" / dest_filename

                            try:
                                shutil.copy2(viz_file, dest_path)
                                viz_files.append(dest_filename)
                            except Exception as e:
                                print(f"Warning: Could not copy visualization {viz_file}: {e}")

        return viz_files

    def _create_evidence_catalog(self, case_summary: CaseSummary, package_dir: Path) -> str:
        """Create comprehensive evidence catalog.

        Args:
            case_summary: CaseSummary object
            package_dir: Package root directory

        Returns:
            Catalog filename
        """
        catalog = {
            "case_id": case_summary.case_id,
            "catalog_generated": datetime.now().isoformat(),
            "total_evidence_pieces": case_summary.evidence_count,
            "evidence_types": case_summary.evidence_types,
            "evidence_inventory": []
        }

        for evidence in case_summary.evidence_summaries:
            evidence_entry = {
                "filename": evidence.filename,
                "evidence_type": evidence.evidence_type,
                "sha256": evidence.sha256,
                "file_size_bytes": evidence.file_size,
                "analysis_confidence": evidence.analysis_confidence,
                "legal_significance": evidence.legal_significance,
                "risk_flags": evidence.risk_flags,
                "key_findings_summary": evidence.key_findings[:3],  # Top 3 findings
                "chain_of_custody": f"Complete audit trail available in data/storage/derived/sha256={evidence.sha256}/chain_of_custody.json"
            }
            catalog["evidence_inventory"].append(evidence_entry)

        catalog_file = "evidence_catalog.json"
        catalog_path = package_dir / "evidence_catalog" / catalog_file

        with open(catalog_path, 'w') as f:
            json.dump(catalog, f, indent=2)

        return catalog_file

    def _create_correlation_report(self, case_summary: CaseSummary, package_dir: Path) -> str:
        """Create detailed correlation analysis report.

        Args:
            case_summary: CaseSummary object
            package_dir: Package root directory

        Returns:
            Correlation report filename
        """
        # v3.1: Use Pydantic serialization to preserve all fields (legal_patterns, temporal_sequences, timeline_gaps)
        correlation_dict = case_summary.correlation_result.model_dump(mode='json')

        # Truncate SHA256 hashes for readability (8 chars)
        for corr in correlation_dict.get("entity_correlations", []):
            if "evidence_occurrences" in corr:
                for occ in corr["evidence_occurrences"]:
                    if "evidence_sha256" in occ:
                        occ["evidence_sha256"] = occ["evidence_sha256"][:8]

        for event in correlation_dict.get("timeline_events", []):
            if "evidence_sha256" in event:
                event["evidence_sha256"] = event["evidence_sha256"][:8]

        # Truncate SHA256s in legal_patterns if present
        if correlation_dict.get("legal_patterns"):
            for contradiction in correlation_dict["legal_patterns"].get("contradictions", []):
                if "statement_1_source" in contradiction:
                    contradiction["statement_1_source"] = contradiction["statement_1_source"][:8]
                if "statement_2_source" in contradiction:
                    contradiction["statement_2_source"] = contradiction["statement_2_source"][:8]

            for corroboration in correlation_dict["legal_patterns"].get("corroboration", []):
                if "supporting_evidence" in corroboration:
                    corroboration["supporting_evidence"] = [
                        sha[:8] for sha in corroboration["supporting_evidence"]
                    ]

        report_file = "correlation_analysis.json"
        report_path = package_dir / "correlations" / report_file

        with open(report_path, 'w') as f:
            json.dump(correlation_dict, f, indent=2)

        return report_file

    def _create_documentation(self, case_summary: CaseSummary, package_dir: Path) -> List[str]:
        """Create package documentation files.

        Args:
            case_summary: CaseSummary object
            package_dir: Package root directory

        Returns:
            List of documentation filenames
        """
        doc_files = []

        # README file
        readme_content = f"""# Evidence Analysis Package - Case {case_summary.case_id}

## Package Contents

This package contains a comprehensive forensic analysis of case {case_summary.case_id}, generated on {case_summary.generation_timestamp.strftime('%Y-%m-%d %H:%M:%S')}.

### Directory Structure

- **reports/**: Executive summaries and formatted reports
- **analysis/**: Detailed JSON analysis files for each piece of evidence
- **visualizations/**: Charts, word clouds, and other visual analysis outputs
- **evidence_catalog/**: Complete inventory of evidence with metadata
- **correlations/**: Cross-evidence correlation analysis and timeline reconstruction
- **documentation/**: This README and methodology documentation
- **raw_evidence/**: Original evidence files (if included)

### Evidence Summary

- **Total Evidence Pieces**: {case_summary.evidence_count}
- **Evidence Types**: {', '.join(case_summary.evidence_types)}
- **Cross-Evidence Correlations**: {len(case_summary.correlation_result.entity_correlations)}
- **Timeline Events**: {len(case_summary.correlation_result.timeline_events)}

### Key Files

1. **reports/executive_summary.txt**: Main case summary with AI-generated insights
2. **analysis/case_analysis.json**: Complete structured analysis data
3. **evidence_catalog/evidence_catalog.json**: Comprehensive evidence inventory
4. **correlations/correlation_analysis.json**: Cross-evidence correlation results

### Methodology

This analysis was performed using the Evidence Toolkit, a forensic-grade evidence analysis system that provides:

- Content-addressed evidence storage with complete chain of custody
- AI-powered analysis using OpenAI's deterministic analysis models (temperature=0)
- Cross-evidence entity correlation and timeline reconstruction
- Professional legal significance assessment and risk evaluation

### Legal Compliance

All analysis results are generated using forensic-grade processes suitable for legal proceedings:

- Deterministic AI analysis with confidence scoring
- Complete audit trails and chain of custody documentation
- Schema validation for all structured outputs
- Professional risk assessment and legal significance evaluation

### Contact Information

This analysis package was generated by the Evidence Toolkit system.
For questions about methodology or technical details, please contact your forensic analysis provider.

---
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Package Format: Professional Legal Evidence Analysis
"""

        readme_path = package_dir / "documentation" / "README.md"
        with open(readme_path, 'w') as f:
            f.write(readme_content)
        doc_files.append("README.md")

        # Methodology documentation
        methodology_content = """# Analysis Methodology

## Evidence Toolkit Analysis Process

### 1. Evidence Ingestion
- Content-addressed storage using SHA256 hashing
- Metadata extraction and preservation
- Chain of custody initialization

### 2. Individual Evidence Analysis
- **Documents**: Text analysis, word frequency, concept extraction
- **Images**: AI-powered scene analysis, OCR, object detection
- **Emails**: Thread reconstruction, sentiment analysis, escalation detection

### 3. Cross-Evidence Correlation
- Entity extraction and matching across evidence types
- Timeline reconstruction from metadata and content
- Pattern detection and relationship analysis

### 4. AI-Powered Insights
- OpenAI Responses API with deterministic settings (temperature=0)
- Legal significance assessment
- Risk evaluation and compliance checking
- Professional recommendations generation

### 5. Quality Assurance
- Schema validation for all structured outputs
- Confidence scoring for all analysis results
- Complete audit trail maintenance
- Professional report generation

## Technical Standards

- **Deterministic Analysis**: All AI analysis uses temperature=0 for reproducible results
- **Forensic Grade**: Complete chain of custody and audit trails
- **Schema Validation**: All outputs validated against canonical schemas
- **Professional Output**: Court-ready reports and documentation

## Legal Compliance

This methodology is designed for professional legal evidence analysis and maintains standards suitable for court proceedings.
"""

        methodology_path = package_dir / "documentation" / "methodology.md"
        with open(methodology_path, 'w') as f:
            f.write(methodology_content)
        doc_files.append("methodology.md")

        return doc_files

    def _copy_raw_evidence(self, case_summary: CaseSummary, package_dir: Path) -> List[str]:
        """Copy original evidence files to package.

        Args:
            case_summary: CaseSummary object
            package_dir: Package root directory

        Returns:
            List of copied evidence filenames
        """
        raw_files = []

        for evidence in case_summary.evidence_summaries:
            try:
                # Find original file
                evidence_dir = self.storage.raw_dir / f"sha256={evidence.sha256}"
                original_files = list(evidence_dir.glob("original.*"))

                if original_files:
                    original_file = original_files[0]
                    # Copy with descriptive name
                    dest_filename = f"{evidence.evidence_type}_{evidence.filename}"
                    dest_path = package_dir / "raw_evidence" / dest_filename

                    shutil.copy2(original_file, dest_path)
                    raw_files.append(dest_filename)

            except Exception as e:
                print(f"Warning: Could not copy raw evidence {evidence.filename}: {e}")

        return raw_files

    def _create_zip_package(self, package_dir: Path, zip_path: Path):
        """Create ZIP archive of the package.

        Args:
            package_dir: Directory to zip
            zip_path: Output ZIP file path
        """
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in package_dir.rglob('*'):
                if file_path.is_file():
                    # Calculate relative path for archive
                    arcname = file_path.relative_to(package_dir)
                    zipf.write(file_path, arcname)

    def _create_package_metadata(self, case_summary: CaseSummary, components: Dict[str, List[str]]) -> Dict[str, Any]:
        """Create package metadata.

        Args:
            case_summary: CaseSummary object
            components: Dictionary of package components

        Returns:
            Package metadata dictionary
        """
        return {
            "package_info": {
                "created": datetime.now().isoformat(),
                "case_id": case_summary.case_id,
                "evidence_count": case_summary.evidence_count,
                "evidence_types": case_summary.evidence_types,
                "generator": "Evidence Toolkit v3.0"
            },
            "analysis_summary": {
                "overall_legal_significance": case_summary.overall_assessment.get('overall_legal_significance'),
                "total_risk_flags": case_summary.overall_assessment.get('total_risk_flags', 0),
                "entity_correlations": len(case_summary.correlation_result.entity_correlations),
                "timeline_events": len(case_summary.correlation_result.timeline_events),
                "ai_analysis_included": case_summary.executive_summary is not None
            },
            "package_components": components,
            "file_counts": {
                component_type: len(files)
                for component_type, files in components.items()
            }
        }


__all__ = [
    'PackageGenerator',
]
