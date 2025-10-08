"""Domain-specific configurations for Evidence Toolkit.

This package contains domain-specific prompts, taxonomies, and settings.
Currently supports legal domain, with easy extensibility for others."""

from .legal_config import (
    DOCUMENT_ANALYSIS_PROMPT,
    EMAIL_ANALYSIS_PROMPT,
    IMAGE_ANALYSIS_PROMPT,
    EXECUTIVE_SUMMARY_PROMPT,
    CORRELATION_PATTERN_PROMPT,
    ENTITY_MATCH_PROMPT,
    CRITICAL_RISK_FLAGS
)

__all__ = [
    "DOCUMENT_ANALYSIS_PROMPT",
    "EMAIL_ANALYSIS_PROMPT",
    "IMAGE_ANALYSIS_PROMPT",
    "EXECUTIVE_SUMMARY_PROMPT",
    "CORRELATION_PATTERN_PROMPT",
    "ENTITY_MATCH_PROMPT",
    "CRITICAL_RISK_FLAGS"
]
