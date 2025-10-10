"""Base Report Generator - Abstract base class for all forensic report generators.

All generators inherit from BaseReportGenerator and implement:
1. has_data() - Check if sufficient data exists to generate the report
2. generate() - Create the report and return the file path
3. get_report_filename() - Return the filename for this report type

Design principles:
- Each generator creates ONE type of report
- Generators use existing analyzed data (no new AI calls!)
- Reports are Markdown format for client readability
- All data validation handled by Pydantic models
"""

from abc import ABC, abstractmethod
from pathlib import Path
from datetime import datetime
from typing import Optional, Any

from evidence_toolkit.core.models import CaseSummary


class BaseReportGenerator(ABC):
    """Abstract base class for all forensic report generators.

    Each generator is responsible for creating one specific type of report
    from the analyzed case data. Generators are stateless and thread-safe.

    Architecture:
        - Input: CaseSummary (Pydantic model with all analyzed data)
        - Output: Markdown report file in specified directory
        - Data: Uses existing analysis (no AI calls in generators!)

    Example:
        >>> generator = ForensicLegalOpinionGenerator(case_summary, output_dir)
        >>> if generator.has_data():
        ...     report_path = generator.generate()
        ...     print(f"Report created: {report_path}")
    """

    def __init__(self, case_summary: CaseSummary, output_dir: Path):
        """Initialize the report generator.

        Args:
            case_summary: Complete case analysis (Pydantic model)
            output_dir: Directory where report will be written
        """
        self.case_summary = case_summary
        self.output_dir = Path(output_dir)
        self.case_id = case_summary.case_id
        self.overall_assessment = case_summary.overall_assessment

        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)

    @abstractmethod
    def has_data(self) -> bool:
        """Check if sufficient data exists to generate this report.

        Generators should return False if the required data fields are
        missing or empty. This allows package.py to skip report types
        that aren't applicable to a particular case.

        Returns:
            True if report can be generated, False otherwise

        Example:
            >>> def has_data(self) -> bool:
            ...     return bool(self.overall_assessment.get('_forensic_summary'))
        """
        pass

    @abstractmethod
    def generate(self) -> Path:
        """Generate the report and return the file path.

        This method should:
        1. Build the report content (Markdown format)
        2. Write to output_dir / get_report_filename()
        3. Return the Path to the created file

        Returns:
            Path to the generated report file

        Raises:
            Exception: If report generation fails

        Example:
            >>> def generate(self) -> Path:
            ...     content = self._build_header()
            ...     content += self._build_analysis_section()
            ...     report_path = self.output_dir / self.get_report_filename()
            ...     report_path.write_text(content)
            ...     return report_path
        """
        pass

    @abstractmethod
    def get_report_filename(self) -> str:
        """Return the filename for this report type.

        Convention: Use descriptive names with .md extension
        Examples: 'forensic_legal_opinion.md', 'financial_risk_assessment.md'

        Returns:
            Filename string (including .md extension)

        Example:
            >>> def get_report_filename(self) -> str:
            ...     return "forensic_legal_opinion.md"
        """
        pass

    @abstractmethod
    def get_report_title(self) -> str:
        """Return the human-readable title for this report.

        Used in report headers and metadata.

        Returns:
            Report title string

        Example:
            >>> def get_report_title(self) -> str:
            ...     return "Forensic Legal Opinion"
        """
        pass

    # =========================================================================
    # HELPER METHODS (available to all subclasses)
    # =========================================================================

    def _build_header(self, subtitle: Optional[str] = None) -> str:
        """Build standard report header with case metadata.

        Args:
            subtitle: Optional subtitle to display under the main title

        Returns:
            Markdown header string

        Example output:
            # Forensic Legal Opinion
            ## Professional Risk Assessment

            **Case ID**: WORKPLACE-2025-001
            **Generated**: 2025-10-10 14:30:45
            **Evidence Toolkit**: v3.4.0
            **Evidence Count**: 15 items

            ---
        """
        header = f"# {self.get_report_title()}\n\n"

        if subtitle:
            header += f"## {subtitle}\n\n"

        header += f"**Case ID**: {self.case_id}\n"
        header += f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        header += f"**Evidence Toolkit**: v3.4.0\n"
        header += f"**Evidence Count**: {self.case_summary.evidence_count} items\n"
        header += "\n---\n\n"

        return header

    def _truncate_sha(self, sha256: str, length: int = 8) -> str:
        """Truncate SHA256 hash for readability in reports.

        Args:
            sha256: Full SHA256 hash string
            length: Number of characters to keep (default: 8)

        Returns:
            Truncated hash string

        Example:
            >>> self._truncate_sha("a1b2c3d4e5f6...")
            'a1b2c3d4'
        """
        if not sha256:
            return "N/A"
        return sha256[:length]

    def _format_list_items(self, items: list, numbered: bool = True, indent: int = 0) -> str:
        """Format a list of items as Markdown.

        Args:
            items: List of strings to format (or dict keys, tuple, etc.)
            numbered: If True, use numbered list (1. 2. 3.). If False, use bullets (-)
            indent: Number of spaces to indent (for nested lists)

        Returns:
            Markdown formatted list string

        Example:
            >>> self._format_list_items(["Item 1", "Item 2"], numbered=True)
            '1. Item 1\n2. Item 2\n'
        """
        if not items:
            return ""

        # Handle non-list iterables (dict keys, tuples, etc.)
        # and protect against non-iterable types
        try:
            items_list = list(items) if not isinstance(items, list) else items
        except TypeError:
            # items is not iterable (e.g., int, float, None)
            return ""

        if not items_list:
            return ""

        indent_str = " " * indent
        result = ""

        for i, item in enumerate(items_list, 1):
            if numbered:
                result += f"{indent_str}{i}. {item}\n"
            else:
                result += f"{indent_str}- {item}\n"

        return result

    def _safe_get(self, key: str, default: Any = None) -> Any:
        """Safely get a value from overall_assessment dict.

        Args:
            key: Dictionary key to retrieve
            default: Default value if key doesn't exist

        Returns:
            Value from overall_assessment or default

        Example:
            >>> forensic_summary = self._safe_get('_forensic_summary', 'No summary available')
        """
        return self.overall_assessment.get(key, default)

    def _format_percentage(self, value: float, decimals: int = 0) -> str:
        """Format a float as a percentage string.

        Args:
            value: Float value (0.75 = 75%)
            decimals: Number of decimal places

        Returns:
            Formatted percentage string

        Example:
            >>> self._format_percentage(0.753, decimals=1)
            '75.3%'
        """
        if value is None:
            return "N/A"
        return f"{value * 100:.{decimals}f}%"
