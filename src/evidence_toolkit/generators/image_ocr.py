"""Image OCR Analysis Generator - Aggregated text extraction from image evidence.

Generates a forensic report consolidating OCR-extracted text from image evidence,
grouped by evidence value. Highlights images with people, timestamps, and other
forensic markers.

Data source: Individual evidence analysis files (ImageAnalysisResult.detected_text)
Created by: Image analysis phase (OpenAI Vision API)
Value: Surfaces text from images that may not be searchable, identifies high-value visual evidence
"""

from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict

from evidence_toolkit.generators.base import BaseReportGenerator


class ImageOCRGenerator(BaseReportGenerator):
    """Generate aggregated OCR analysis from image evidence.

    This generator creates a forensic report showing:
    - OCR text extraction grouped by evidence value (high/medium/low)
    - Sample text extractions from key images
    - Images with people detected
    - Images with visible timestamps
    - Forensic recommendations for visual evidence

    The analysis consolidates image analysis data from individual evidence files,
    making OCR text searchable and highlighting forensically significant visual evidence.

    Example output sections:
    - OCR Summary: Total images analyzed, text extracted, people detected
    - High-Value Images: Images with significant OCR content or forensic markers
    - Text Extractions: Sample OCR text from each evidence value tier
    - Forensic Recommendations: Handwriting analysis, timestamp verification, etc.

    Note: This generator accesses individual evidence analysis files directly
    rather than the aggregated case_summary, as OCR data is stored per-evidence.
    """

    def get_report_filename(self) -> str:
        """Return filename for image OCR report."""
        return "image_ocr_analysis.md"

    def get_report_title(self) -> str:
        """Return title for image OCR report."""
        return "Image OCR Analysis"

    def has_data(self) -> bool:
        """Check if image evidence with OCR exists.

        Returns:
            True if image_ocr data exists in overall_assessment
        """
        image_ocr = self._safe_get('image_ocr')
        if not image_ocr or not isinstance(image_ocr, dict):
            return False

        # Check if we have images with detected text
        images_with_text = image_ocr.get('images_with_text', [])
        return bool(images_with_text) and len(images_with_text) > 0

    def generate(self) -> Path:
        """Generate the image OCR analysis report.

        Returns:
            Path to the generated report file
        """
        # Extract image OCR data
        ocr_data = self._safe_get('image_ocr', {})

        # Build report sections
        content = self._build_header(
            subtitle="Aggregated Text Extraction from Image Evidence"
        )
        content += self._build_executive_summary(ocr_data)
        content += self._build_text_extractions(ocr_data)
        content += self._build_methodology_section()
        content += self._build_forensic_value_section()

        # Write report
        report_path = self.output_dir / self.get_report_filename()
        report_path.write_text(content, encoding='utf-8')

        return report_path

    def _build_executive_summary(self, ocr_data: Dict[str, Any]) -> str:
        """Build executive summary of OCR findings."""
        section = "\n## Executive Summary\n\n"

        images_with_text = ocr_data.get('images_with_text', [])
        total_images = ocr_data.get('total_images_analyzed', len(images_with_text))

        section += f"Image analysis detected readable text in **{len(images_with_text)} of {total_images} images** "
        section += f"({len(images_with_text)/total_images*100:.0f}% OCR success rate).\n\n"

        # Count images with different features
        with_timestamps = sum(1 for img in images_with_text if img.get('has_timestamp'))
        with_people = sum(1 for img in images_with_text if img.get('people_detected'))

        if with_timestamps > 0:
            section += f"- **{with_timestamps} images** contain visible timestamps\n"
        if with_people > 0:
            section += f"- **{with_people} images** have people detected\n"

        section += "\n**Forensic Value**: OCR text extraction makes visual evidence searchable, "
        section += "enables timeline correlation with visible timestamps, and supports document authentication.\n\n"

        return section

    def _build_text_extractions(self, ocr_data: Dict[str, Any]) -> str:
        """Build text extraction samples."""
        section = "\n## Extracted Text from Images\n\n"

        images_with_text = ocr_data.get('images_with_text', [])

        if not images_with_text:
            section += "_No text detected in images._\n\n"
            return section

        section += f"Showing OCR results from {len(images_with_text)} image(s) with detected text:\n\n"

        for idx, img in enumerate(images_with_text[:10], 1):  # Show first 10
            sha = img.get('sha256', 'unknown')[:8]
            filename = img.get('filename', 'unknown')
            text = img.get('detected_text', '')
            scene = img.get('scene_description', '')
            objects = img.get('detected_objects', [])

            section += f"### {idx}. {filename}\n\n"
            section += f"**Evidence ID**: `{sha}`\n\n"

            if scene:
                section += f"**Scene Description**: {scene[:200]}"
                if len(scene) > 200:
                    section += "..."
                section += "\n\n"

            if objects:
                section += f"**Detected Objects**: {', '.join(objects[:5])}\n\n"

            if text:
                section += "**Extracted Text**:\n"
                section += "```\n"
                section += text[:500]  # Limit text length
                if len(text) > 500:
                    section += "\n... (truncated)"
                section += "\n```\n\n"

        if len(images_with_text) > 10:
            section += f"_({len(images_with_text) - 10} additional images with text not shown)_\n\n"

        return section

    def _build_placeholder_notice(self) -> str:
        """Build notice explaining this is a placeholder for future image cases."""
        section = "\n## Notice: No Image Evidence in Current Case\n\n"
        section += "This case contains no image evidence requiring OCR analysis. "
        section += "This report template is provided for documentation purposes.\n\n"
        section += "**When image evidence is present**, this report will include:\n\n"
        section += "- OCR text extraction from all image evidence\n"
        section += "- Classification by forensic value (high/medium/low)\n"
        section += "- Detection of people, timestamps, and visual markers\n"
        section += "- Sample text extractions for verification\n"
        section += "- Forensic recommendations for visual evidence analysis\n\n"
        return section

    def _build_methodology_section(self) -> str:
        """Build methodology section explaining OCR analysis approach."""
        section = "\n## OCR Analysis Methodology\n\n"
        section += "### Image Evidence Processing\n\n"
        section += "When image evidence is submitted, the Evidence Toolkit performs:\n\n"
        section += "1. **AI Vision Analysis** (OpenAI Vision API):\n"
        section += "   - Object detection (people, documents, screens)\n"
        section += "   - Text extraction (OCR)\n"
        section += "   - Scene understanding\n"
        section += "   - Timestamp detection\n\n"
        section += "2. **Forensic Classification**:\n"
        section += "   - **High Value**: Images with clear text, timestamps, people identified\n"
        section += "   - **Medium Value**: Images with partial text, unclear timestamps\n"
        section += "   - **Low Value**: Background images, unclear content\n\n"
        section += "3. **Text Aggregation**:\n"
        section += "   - OCR text consolidated into searchable format\n"
        section += "   - Cross-referenced with document evidence\n"
        section += "   - Highlighted for legal significance\n\n"
        return section

    def _build_forensic_value_section(self) -> str:
        """Build section explaining forensic value of OCR analysis."""
        section = "\n## Forensic Value of Image OCR Analysis\n\n"
        section += "### Why Image OCR Matters for Legal Evidence\n\n"
        section += "**1. Text Accessibility**:\n"
        section += "   - Makes text in images searchable and quotable\n"
        section += "   - Enables keyword searches across visual evidence\n"
        section += "   - Supports timeline reconstruction from photos\n\n"
        section += "**2. Timestamp Verification**:\n"
        section += "   - Digital timestamps in screenshots\n"
        section += "   - Handwritten dates on documents\n"
        section += "   - Metadata correlation (file timestamp vs. visible timestamp)\n\n"
        section += "**3. People Identification**:\n"
        section += "   - Presence of individuals in visual evidence\n"
        section += "   - Group photos (witness identification)\n"
        section += "   - Meeting attendance verification\n\n"
        section += "**4. Document Authentication**:\n"
        section += "   - Letterhead detection\n"
        section += "   - Signature presence\n"
        section += "   - Watermark identification\n\n"
        section += "### Forensic Recommendations for Image Evidence\n\n"
        section += "When image evidence is present, consider:\n\n"
        section += "- **Handwriting Analysis**: Professional analysis of handwritten notes\n"
        section += "- **Timestamp Correlation**: Verify visible timestamps against file metadata\n"
        section += "- **People Identification**: Cross-reference detected people with known witnesses\n"
        section += "- **Document Originals**: Request original documents if images show copies\n"
        section += "- **Photo Metadata**: Extract EXIF data (location, camera, date) for verification\n\n"
        return section

    # Future implementation methods (for when we have image data):

    def _build_ocr_summary(self, images_data: List[Dict[str, Any]]) -> str:
        """Build OCR summary statistics.

        Args:
            images_data: List of image analysis results

        Returns:
            Formatted markdown section
        """
        section = "\n## OCR Summary\n\n"

        total_images = len(images_data)
        images_with_text = sum(1 for img in images_data if img.get('detected_text'))
        images_with_people = sum(1 for img in images_data if img.get('people_detected'))
        images_with_timestamps = sum(1 for img in images_data if img.get('timestamp_visible'))

        section += f"- **Total Images Analyzed**: {total_images}\n"
        section += f"- **Images with Extracted Text**: {images_with_text} ({images_with_text/total_images*100:.1f}%)\n"
        section += f"- **Images with People Detected**: {images_with_people}\n"
        section += f"- **Images with Visible Timestamps**: {images_with_timestamps}\n"
        section += "\n"

        return section

    def _group_by_evidence_value(self, images_data: List[Dict[str, Any]]) -> Dict[str, List]:
        """Group images by forensic evidence value.

        Args:
            images_data: List of image analysis results

        Returns:
            Dict mapping evidence value (high/medium/low) to image list
        """
        grouped: Dict[str, List] = {
            'high': [],
            'medium': [],
            'low': []
        }

        for img in images_data:
            evidence_value = img.get('evidence_value', 'low')
            grouped[evidence_value].append(img)

        return grouped

    def _build_high_value_images(self, images_data: List[Dict[str, Any]]) -> str:
        """Build high-value images section.

        Args:
            images_data: List of high-value image analysis results

        Returns:
            Formatted markdown section
        """
        section = "\n## High-Value Images\n\n"

        if not images_data:
            section += "_No high-value images identified._\n\n"
            return section

        section += f"Found **{len(images_data)} high-value image(s)** with significant forensic content:\n\n"

        for idx, img in enumerate(images_data, 1):
            sha = img.get('sha256', 'unknown')[:8]
            filename = img.get('filename', 'unknown')
            detected_text = img.get('detected_text', '')
            people = img.get('people_detected', False)
            timestamp = img.get('timestamp_visible', False)

            section += f"### {idx}. {filename}\n\n"
            section += f"- **Evidence ID**: `{sha}`\n"

            if detected_text:
                preview = detected_text[:200]
                section += f"- **Extracted Text**: \"{preview}...\"\n"

            if people:
                section += "- **People Detected**: ✓ Yes\n"

            if timestamp:
                section += "- **Visible Timestamp**: ✓ Yes\n"

            section += "\n"

        return section

    def _build_text_extractions(self, grouped_images: Dict[str, List]) -> str:
        """Build text extraction samples by evidence tier.

        Args:
            grouped_images: Images grouped by evidence value

        Returns:
            Formatted markdown section
        """
        section = "\n## Text Extractions by Evidence Tier\n\n"

        for tier in ['high', 'medium', 'low']:
            images = grouped_images.get(tier, [])

            if not images:
                continue

            section += f"### {tier.title()} Value ({len(images)} images)\n\n"

            for img in images[:3]:  # Show first 3 per tier
                sha = img.get('sha256', 'unknown')[:8]
                text = img.get('detected_text', '')

                if text:
                    section += f"**Evidence `{sha}`:**\n\n"
                    section += f"```\n{text[:300]}\n```\n\n"

        return section


# Export for package-level import
__all__ = ['ImageOCRGenerator']
