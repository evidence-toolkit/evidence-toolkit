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

Phase 2 Generators (Core Forensic Reports - COMPLETE):
- LegalPatternsGenerator: Detailed contradiction/corroboration/gaps analysis
- TimelineGenerator: Chronological reconstruction with gap analysis
- QuotedStatementsGenerator: Person-by-person quoted statement breakdown

Phase 3 Generators (Advanced Analytics - COMPLETE):
- RelationshipNetworkGenerator: Entity relationship mapping & key player analysis
- PowerDynamicsGenerator: Email authority hierarchy (placeholder - pending aggregation)
- ImageOCRGenerator: Aggregated OCR findings (placeholder - for image cases)
"""

from evidence_toolkit.generators.base import BaseReportGenerator
from evidence_toolkit.generators.forensic_legal import ForensicLegalOpinionGenerator
from evidence_toolkit.generators.financial_risk import FinancialRiskAssessmentGenerator
from evidence_toolkit.generators.legal_patterns import LegalPatternsGenerator
from evidence_toolkit.generators.timeline import TimelineGenerator
from evidence_toolkit.generators.quoted_statements import QuotedStatementsGenerator
from evidence_toolkit.generators.relationship_network import RelationshipNetworkGenerator
from evidence_toolkit.generators.power_dynamics import PowerDynamicsGenerator
from evidence_toolkit.generators.image_ocr import ImageOCRGenerator

__all__ = [
    'BaseReportGenerator',
    'ForensicLegalOpinionGenerator',
    'FinancialRiskAssessmentGenerator',
    'LegalPatternsGenerator',
    'TimelineGenerator',
    'QuotedStatementsGenerator',
    'RelationshipNetworkGenerator',
    'PowerDynamicsGenerator',
    'ImageOCRGenerator',
]
