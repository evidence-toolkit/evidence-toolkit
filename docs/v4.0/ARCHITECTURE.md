# v4.0 Architecture - Hexagonal Design

**Pattern**: Hexagonal Architecture (Ports & Adapters)
**Goal**: Modular, testable, future-proof evidence analysis system

---

## Architectural Overview

### Core Concept: Dependency Inversion

```
┌───────────────────────────────────────────────────────────┐
│                    HIGH-LEVEL POLICY                      │
│          (Business Logic - Domain Layer)                  │
│                                                           │
│  ┌─────────────────────────────────────────────────┐    │
│  │  EvidenceAnalysisService                        │    │
│  │  - analyze_document()                           │    │
│  │  - analyze_image()                              │    │
│  │  - correlate_evidence()                         │    │
│  │                                                 │    │
│  │  Depends on INTERFACES (ports):                │    │
│  │  - IAIProvider                                  │    │
│  │  - IStorageProvider                             │    │
│  │  - IDocumentExtractor                           │    │
│  └─────────────────────────────────────────────────┘    │
│                          ↑                                │
│                          │ Depends on abstractions       │
└──────────────────────────┼───────────────────────────────┘
                           │
                           │ Implements interfaces
                           ↓
┌───────────────────────────────────────────────────────────┐
│                    LOW-LEVEL DETAILS                      │
│               (Adapters - Infrastructure)                 │
│                                                           │
│  OpenAIAdapter    LocalStorage    PDFExtractor           │
│  AnthropicAdapter S3Storage       OCRExtractor           │
│  MockAIProvider   AzureStorage    DOCXExtractor          │
└───────────────────────────────────────────────────────────┘
```

**Key Insight**: Business logic (services) never imports infrastructure (OpenAI, file I/O).
It only imports interfaces. Infrastructure imports and implements those interfaces.

---

## Layer Breakdown

### 1. Domain Layer (Core)

**Location**: `src/evidence_toolkit/core/`

**Responsibilities**:
- Define business entities (Pydantic models)
- Define interfaces (ports)
- Implement business logic (services)
- **No external dependencies** (no OpenAI, no file I/O, pure logic)

**Files**:
```
core/
├── models.py           # ✅ KEEP AS-IS (48 Pydantic models)
├── interfaces.py       # NEW: Abstract interfaces (IAIProvider, IStorageProvider, etc.)
├── services.py         # NEW: Business logic (EvidenceAnalysisService)
└── exceptions.py       # NEW: Custom exceptions (AnalysisError, StorageError, etc.)
```

**Example - interfaces.py**:
```python
from abc import ABC, abstractmethod
from pathlib import Path
from pydantic import BaseModel

class IAIProvider(ABC):
    """Port for AI analysis providers."""

    @abstractmethod
    async def generate_structured(
        self,
        prompt: str,
        context: str,
        response_model: type[BaseModel],
        model: str | None = None
    ) -> BaseModel:
        """Generate structured AI response."""
        pass

    @abstractmethod
    async def generate_vision(
        self,
        image_path: Path,
        prompt: str,
        response_model: type[BaseModel]
    ) -> BaseModel:
        """Analyze image using vision AI."""
        pass

class IStorageProvider(ABC):
    """Port for evidence storage systems."""

    @abstractmethod
    async def store_evidence(self, file_path: Path, case_id: str) -> str:
        """Store evidence, return SHA256."""
        pass

    @abstractmethod
    async def retrieve_evidence(self, sha256: str) -> Path:
        """Get evidence by hash."""
        pass

    @abstractmethod
    async def save_analysis(self, sha256: str, analysis: UnifiedAnalysis) -> None:
        """Save analysis results."""
        pass
```

**Example - services.py**:
```python
class EvidenceAnalysisService:
    """Core business logic for evidence analysis.

    This is PURE - no OpenAI imports, no file I/O imports.
    Uses injected dependencies (interfaces).
    """

    def __init__(
        self,
        ai_provider: IAIProvider,
        storage: IStorageProvider,
        config: ToolkitSettings
    ):
        self.ai = ai_provider
        self.storage = storage
        self.config = config

    async def analyze_document(
        self,
        sha256: str,
        case_id: str
    ) -> UnifiedAnalysis:
        """Analyze document evidence."""

        # 1. Retrieve evidence (via interface)
        evidence_path = await self.storage.retrieve_evidence(sha256)

        # 2. Extract text (via interface)
        extractor = self._get_extractor(evidence_path)
        content = await extractor.extract_text(evidence_path)

        # 3. Get domain-specific prompt
        domain = self._load_domain_config(self.config.domain)

        # 4. Analyze with AI (via interface)
        analysis = await self.ai.generate_structured(
            prompt=domain.DOCUMENT_ANALYSIS_PROMPT,
            context=content,
            response_model=DocumentAnalysis,
            model=self.config.ai.model_document
        )

        # 5. Create unified analysis
        unified = UnifiedAnalysis(
            evidence_type="document",
            sha256=sha256,
            case_id=case_id,
            document_analysis=analysis,
            timestamp=datetime.now(),
            model_info=AnalysisModelInfo(
                model=self.config.ai.model_document,
                temperature=self.config.ai.temperature
            )
        )

        # 6. Save analysis (via interface)
        await self.storage.save_analysis(sha256, unified)

        return unified
```

---

### 2. Infrastructure Layer (Adapters)

**Location**: `src/evidence_toolkit/infrastructure/`

**Responsibilities**:
- Implement interfaces defined in core
- Handle external dependencies (OpenAI, file I/O, network)
- Provide concrete implementations (swappable)

**Files**:
```
infrastructure/
├── ai/
│   ├── base.py                 # IAIProvider interface
│   ├── openai_adapter.py       # OpenAI implementation
│   ├── anthropic_adapter.py    # Anthropic Claude (future)
│   └── mock_adapter.py         # For testing (no API calls)
│
├── storage/
│   ├── base.py                 # IStorageProvider interface
│   ├── local_storage.py        # Current SHA256 file storage
│   ├── s3_storage.py           # AWS S3 (future)
│   └── azure_storage.py        # Azure Blob (future)
│
└── document_processing/
    ├── base.py                 # IDocumentExtractor interface
    ├── pdf_extractor.py        # pdfplumber implementation
    ├── ocr_extractor.py        # Tesseract OCR (future)
    └── docx_extractor.py       # python-docx (future)
```

**Example - openai_adapter.py**:
```python
from openai import AsyncOpenAI
from .base import IAIProvider

class OpenAIAdapter(IAIProvider):
    """Adapter for OpenAI API (implements IAIProvider interface)."""

    def __init__(self, config: AIProviderConfig):
        self.config = config
        self.client = AsyncOpenAI(
            api_key=config.api_key,
            timeout=config.timeout
        )

    async def generate_structured(
        self,
        prompt: str,
        context: str,
        response_model: type[BaseModel],
        model: str | None = None
    ) -> BaseModel:
        """Generate structured response using OpenAI."""

        model = model or self.config.model_document

        response = await self.client.beta.chat.completions.parse(
            model=model,
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": context}
            ],
            temperature=self.config.temperature,
            response_format=response_model
        )

        return response.choices[0].message.parsed

    async def generate_vision(
        self,
        image_path: Path,
        prompt: str,
        response_model: type[BaseModel]
    ) -> BaseModel:
        """Analyze image using OpenAI Vision API."""

        import base64
        with open(image_path, "rb") as f:
            image_data = base64.b64encode(f.read()).decode()

        response = await self.client.beta.chat.completions.parse(
            model=self.config.model_image,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{image_data}"}
                        }
                    ]
                }
            ],
            temperature=self.config.temperature,
            response_format=response_model
        )

        return response.choices[0].message.parsed
```

**Example - mock_adapter.py** (for testing):
```python
class MockAIProvider(IAIProvider):
    """Mock AI provider for testing (no API calls)."""

    async def generate_structured(
        self,
        prompt: str,
        context: str,
        response_model: type[BaseModel],
        model: str | None = None
    ) -> BaseModel:
        """Return mock data matching response_model schema."""

        # Generate fake data that validates against Pydantic model
        if response_model == DocumentAnalysis:
            return DocumentAnalysis(
                summary="Mock document analysis",
                entities=[
                    DocumentEntity(
                        name="Mock Person",
                        type="person",
                        confidence=0.95,
                        context="Mock context"
                    )
                ],
                document_type="letter",
                sentiment="neutral",
                legal_significance="low",
                risk_flags=[],
                confidence_overall=0.9
            )

        # Add more mock responses as needed
        raise NotImplementedError(f"Mock not implemented for {response_model}")

    async def generate_vision(self, image_path, prompt, response_model):
        """Return mock vision analysis."""
        # Similar mock data for image analysis
        ...
```

---

### 3. Application Layer (Workflows, Pipeline)

**Location**: `src/evidence_toolkit/pipeline/`, `src/evidence_toolkit/analyzers/`

**Responsibilities**:
- Orchestrate workflows (ingest → analyze → correlate → package)
- Coordinate service calls
- Handle concurrency and batching
- Map user requests to service layer

**Files**:
```
pipeline/
├── workflows.py        # NEW: Composable async workflows
├── ingest.py           # REFACTOR: Use IStorageProvider
├── analyze.py          # REFACTOR: Use EvidenceAnalysisService
├── package.py          # REFACTOR: Use IStorageProvider
└── summary.py          # REFACTOR: Use IAIProvider for summaries

analyzers/
├── base.py             # DEPRECATED (logic moved to services.py)
├── document.py         # REFACTOR: Thin wrapper around service
├── image.py            # REFACTOR: Thin wrapper around service
├── email.py            # REFACTOR: Thin wrapper around service
└── correlation.py      # REFACTOR: Use service + IAIProvider
```

**Example - workflows.py**:
```python
class CaseAnalysisWorkflow:
    """Composable workflow for complete case analysis."""

    def __init__(
        self,
        service: EvidenceAnalysisService,
        settings: ToolkitSettings
    ):
        self.service = service
        self.settings = settings

    async def run(self, case_id: str) -> CaseAnalysisResult:
        """Execute complete analysis pipeline."""

        print(f"🔬 Starting analysis for case: {case_id}")

        # 1. Discover evidence
        evidence_list = await self._discover_evidence(case_id)
        print(f"📁 Found {len(evidence_list)} evidence items")

        # 2. Analyze in concurrent batches
        analyses = await self._analyze_concurrent(evidence_list, case_id)
        print(f"✅ Analyzed {len(analyses)} items")

        # 3. Correlate across evidence
        correlations = await self._correlate(analyses, case_id)
        print(f"🔗 Found {len(correlations.entity_correlations)} correlations")

        # 4. Generate executive summary
        summary = await self._generate_summary(analyses, correlations, case_id)
        print(f"📋 Executive summary generated")

        # 5. Create client package
        package_path = await self._create_package(case_id, analyses, summary)
        print(f"📦 Package created: {package_path}")

        return CaseAnalysisResult(
            case_id=case_id,
            evidence_count=len(analyses),
            correlations_count=len(correlations.entity_correlations),
            package_path=package_path
        )

    async def _analyze_concurrent(
        self,
        evidence_list: list[str],
        case_id: str
    ) -> list[UnifiedAnalysis]:
        """Analyze evidence with concurrency control."""

        # Semaphore for rate limiting
        semaphore = asyncio.Semaphore(self.settings.analyzer.max_concurrent)

        async def analyze_with_limit(sha256: str):
            async with semaphore:
                return await self.service.analyze_document(sha256, case_id)

        # Launch all tasks, gather results
        tasks = [analyze_with_limit(sha) for sha in evidence_list]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Filter out errors (handle gracefully)
        return [r for r in results if isinstance(r, UnifiedAnalysis)]
```

---

### 4. Presentation Layer (CLI)

**Location**: `src/evidence_toolkit/cli.py`

**Responsibilities**:
- Parse command-line arguments
- Load configuration
- Wire dependencies (DI container)
- Execute workflows
- Display results

**Ultra-thin CLI** (just wiring):
```python
import asyncio
import click
from pathlib import Path

from evidence_toolkit.core.services import EvidenceAnalysisService
from evidence_toolkit.infrastructure.ai.openai_adapter import OpenAIAdapter
from evidence_toolkit.infrastructure.storage.local_storage import LocalStorage
from evidence_toolkit.pipeline.workflows import CaseAnalysisWorkflow
from evidence_toolkit.config.settings import ToolkitSettings

@click.command()
@click.argument('case_id')
@click.option('--config', default='config/defaults.yaml', help='Config file')
@click.option('--profile', default=None, help='Config profile (dev/prod/test)')
async def analyze_case(case_id: str, config: str, profile: str):
    """Analyze complete case with all evidence."""

    # 1. Load configuration
    settings = ToolkitSettings.from_yaml(config, profile=profile)

    # 2. Initialize infrastructure (dependency injection)
    ai_provider = OpenAIAdapter(settings.ai)
    storage = LocalStorage(settings.storage)

    # 3. Initialize service layer
    service = EvidenceAnalysisService(
        ai_provider=ai_provider,
        storage=storage,
        config=settings
    )

    # 4. Run workflow
    workflow = CaseAnalysisWorkflow(service, settings)
    result = await workflow.run(case_id)

    # 5. Display results
    click.echo(f"✅ Analysis complete!")
    click.echo(f"   Evidence analyzed: {result.evidence_count}")
    click.echo(f"   Package: {result.package_path}")

if __name__ == "__main__":
    asyncio.run(analyze_case())
```

---

## Configuration System

**Location**: `src/evidence_toolkit/config/`

**Design**: Pydantic Settings (loads from env vars + YAML files)

**Structure**:
```
config/
├── settings.py             # Pydantic Settings classes
├── defaults.yaml           # Default configuration
└── profiles/
    ├── development.yaml    # Dev overrides (verbose=true, mock AI)
    ├── production.yaml     # Prod overrides (verbose=false, real AI)
    └── testing.yaml        # Test overrides (mock everything)
```

**Example - settings.py**:
```python
from pydantic_settings import BaseSettings
from pathlib import Path

class AIProviderConfig(BaseSettings):
    provider: Literal["openai", "anthropic", "mock"] = "openai"
    api_key: str = Field(..., alias="OPENAI_API_KEY")
    model_document: str = "gpt-4o-mini"
    model_image: str = "gpt-4o"
    temperature: float = 0.0
    max_retries: int = 3

class ToolkitSettings(BaseSettings):
    ai: AIProviderConfig
    storage: StorageConfig
    analyzer: AnalyzerConfig
    domain: Literal["legal", "corporate", "journalism"] = "legal"

    @classmethod
    def from_yaml(cls, yaml_path: str, profile: str | None = None):
        """Load settings from YAML + optional profile."""
        import yaml

        with open(yaml_path) as f:
            config = yaml.safe_load(f)

        if profile:
            with open(f"config/profiles/{profile}.yaml") as f:
                profile_config = yaml.safe_load(f)
                config.update(profile_config)

        return cls(**config)
```

**Usage**:
```bash
# Uses defaults.yaml + production.yaml + env vars
uv run evidence-toolkit analyze-case MY-CASE --profile production

# Override with env var
export EVIDENCE_TOOLKIT_AI__MODEL_DOCUMENT="gpt-4o"
uv run evidence-toolkit analyze-case MY-CASE
```

---

## Data Flow Example

**User Request**: Analyze 10 documents for case "CASE-001"

```
┌─────────────────────────────────────────────────────────┐
│ 1. CLI (cli.py)                                         │
│    - Parse args: case_id="CASE-001"                     │
│    - Load config from defaults.yaml                     │
│    - Wire dependencies (OpenAI, LocalStorage, Service)  │
└──────────────────────┬──────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────────┐
│ 2. Workflow (workflows.py)                              │
│    - Discover 10 document SHA256s in storage            │
│    - Create 10 async tasks                              │
│    - Limit concurrency to 5 (via Semaphore)            │
└──────────────────────┬──────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────────┐
│ 3. Service Layer (services.py)                          │
│    For each document:                                   │
│    - service.analyze_document(sha256, case_id)          │
│                                                         │
│    Calls interfaces (NO OpenAI/file I/O imports):      │
│    - storage.retrieve_evidence(sha256) → Path           │
│    - extractor.extract_text(path) → str                │
│    - ai.generate_structured(...) → DocumentAnalysis    │
│    - storage.save_analysis(sha256, unified)            │
└──────────────────────┬──────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────────┐
│ 4. Infrastructure (openai_adapter.py, local_storage.py) │
│    OpenAIAdapter.generate_structured():                 │
│    - Calls AsyncOpenAI.chat.completions.parse()         │
│    - Returns Pydantic DocumentAnalysis                  │
│                                                         │
│    LocalStorage.save_analysis():                        │
│    - Writes to data/storage/derived/sha256=.../         │
└──────────────────────┬──────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────────┐
│ 5. Results (back to Workflow)                           │
│    - 10 UnifiedAnalysis objects returned                │
│    - Correlate across evidence                          │
│    - Generate executive summary                         │
│    - Create client package ZIP                          │
└──────────────────────┬──────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────────┐
│ 6. CLI Output                                           │
│    ✅ Analysis complete!                                │
│       Evidence analyzed: 10                             │
│       Package: data/packages/CASE-001_20251009.zip      │
└─────────────────────────────────────────────────────────┘
```

---

## Testing Strategy

### Unit Tests (No External Dependencies)
```python
# tests/test_services.py
async def test_analyze_document():
    # Arrange: Mock dependencies
    mock_ai = MockAIProvider()
    mock_storage = MockStorageProvider()
    config = ToolkitSettings(...)

    service = EvidenceAnalysisService(
        ai_provider=mock_ai,
        storage=mock_storage,
        config=config
    )

    # Act
    result = await service.analyze_document("abc123", "CASE-001")

    # Assert
    assert result.document_analysis.summary == "Mock document analysis"
    assert mock_storage.save_called_with("abc123", result)
```

### Integration Tests (Real OpenAI)
```python
# tests/integration/test_real_openai.py
@pytest.mark.integration
async def test_real_document_analysis():
    # Use real OpenAI adapter
    settings = ToolkitSettings.from_yaml("config/testing.yaml")
    ai_provider = OpenAIAdapter(settings.ai)

    result = await ai_provider.generate_structured(
        prompt=DOCUMENT_ANALYSIS_PROMPT,
        context="This is a test document.",
        response_model=DocumentAnalysis
    )

    assert isinstance(result, DocumentAnalysis)
    assert result.summary != ""
```

---

## Migration Path from v3.3

See [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md) for step-by-step instructions.

**High-level steps**:
1. Create infrastructure layer (interfaces + adapters)
2. Create service layer (business logic)
3. Refactor analyzers to use services
4. Refactor pipeline to use workflows
5. Refactor CLI to be ultra-thin
6. Test, benchmark, validate

---

**Next**: Read [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md) for implementation plan.
