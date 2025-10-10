"""Forensic Report Generators - v3.4+

Specialized report generators that extract maximum value from analyzed evidence data.

Architecture:
- BaseReportGenerator: Abstract base class for all generators
- Each generator creates ONE type of professional forensic report
- Generators use existing analyzed data (no new AI calls!)
- Integration point: pipeline/package.py

Phase 1 Generators (Quick Wins):
- ForensicLegalOpinionGenerator: Unhides _forensic_* fields (£2K-5K value!)
- FinancialRiskAssessmentGenerator: Expands tribunal/settlement analysis

Future Generators:
- LegalPatternsReportGenerator: Detailed legal pattern analysis
- TimelineReportGenerator: Chronological reconstruction
- QuotedStatementsGenerator: Direct quote extraction with attribution
- PowerDynamicsGenerator: Email authority hierarchy analysis
- RelationshipNetworkGenerator: Entity relationship mapping
- ImageOCRGenerator: Aggregated OCR findings
"""

from evidence_toolkit.generators.base import BaseReportGenerator
from evidence_toolkit.generators.forensic_legal import ForensicLegalOpinionGenerator
from evidence_toolkit.generators.financial_risk import FinancialRiskAssessmentGenerator

__all__ = [
    'BaseReportGenerator',
    'ForensicLegalOpinionGenerator',
    'FinancialRiskAssessmentGenerator',
]
