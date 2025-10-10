"""Forensic Report Generators - v3.4+

Specialized report generators that extract maximum value from analyzed evidence data.

Architecture:
- BaseReportGenerator: Abstract base class for all generators
- Each generator creates ONE type of professional forensic report
- Generators use existing analyzed data (no new AI calls!)
- Integration point: pipeline/package.py

Phase 1 Generators (Quick Wins - COMPLETE):
- ForensicLegalOpinionGenerator: Unhides _forensic_* fields (£2K-5K value!)
- FinancialRiskAssessmentGenerator: Expands tribunal/settlement analysis

Phase 2 Generators (Core Forensic Reports):
- LegalPatternsGenerator: Detailed contradiction/corroboration/gaps analysis
- TimelineGenerator: Chronological reconstruction with gap analysis

Future Generators:
- QuotedStatementsGenerator: Direct quote extraction with attribution
- PowerDynamicsGenerator: Email authority hierarchy analysis
- RelationshipNetworkGenerator: Entity relationship mapping
- ImageOCRGenerator: Aggregated OCR findings
"""

from evidence_toolkit.generators.base import BaseReportGenerator
from evidence_toolkit.generators.forensic_legal import ForensicLegalOpinionGenerator
from evidence_toolkit.generators.financial_risk import FinancialRiskAssessmentGenerator
from evidence_toolkit.generators.legal_patterns import LegalPatternsGenerator
from evidence_toolkit.generators.timeline import TimelineGenerator

__all__ = [
    'BaseReportGenerator',
    'ForensicLegalOpinionGenerator',
    'FinancialRiskAssessmentGenerator',
    'LegalPatternsGenerator',
    'TimelineGenerator',
]
