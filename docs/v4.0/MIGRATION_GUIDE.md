# v4.0 Migration Guide - Clean Architecture

**Approach**: Clean Architecture First (Option A)
**Timeline**: 6 weeks (40-50 hours)
**Risk Level**: Low
**Breaking Changes**: None (CLI stays identical)

---

## Strategy Overview

### What We're Building
- **Async-first pipeline**: 3-5x performance improvement via concurrent processing
- **Dependency injection**: Testable, swappable components (OpenAI → Anthropic, local → S3)
- **Configuration system**: External YAML + env vars (no hardcoded values)
- **Zero duplication**: Eliminate all 875 duplicate lines

### What We're NOT Building (v4.1+)
- ❌ Agent frameworks (LangGraph, OpenAI Agents SDK) - deferred to v4.1
- ❌ Chat interface for conversational analysis - deferred to v4.1
- ❌ S3/Azure storage adapters - deferred to v4.1
- ❌ Anthropic Claude adapter - deferred to v4.1

### What Stays Unchanged
- ✅ [src/evidence_toolkit/core/models.py](../../src/evidence_toolkit/core/models.py) - 48 Pydantic models (perfect as-is!)
- ✅ CLI commands and UX (users see no breaking changes)
- ✅ Content-addressed storage pattern (SHA256 deduplication)
- ✅ Domain configurations ([domains/legal_config.py](../../src/evidence_toolkit/domains/legal_config.py))

---

## Week-by-Week Plan

### Week 1: Infrastructure Layer (8-10 hours)

**Goal**: Create foundation (interfaces, adapters, configuration system)

**Tasks**:
1. Create core interfaces ([src/evidence_toolkit/core/interfaces.py](../../src/evidence_toolkit/core/interfaces.py))
   - `IAIProvider` - AI provider abstraction
   - `IStorageProvider` - Storage backend abstraction
   - `IDocumentExtractor` - Document text extraction abstraction
   - **Effort**: 2 hours

2. Create configuration system ([src/evidence_toolkit/config/settings.py](../../src/evidence_toolkit/config/settings.py))
   - Pydantic Settings classes (AIConfig, StorageConfig, AnalyzerConfig)
   - YAML loading from `config/defaults.yaml`
   - Environment variable overrides
   - Profile support (dev/prod/test)
   - **Effort**: 3 hours

3. Implement OpenAI adapter ([src/evidence_toolkit/infrastructure/ai/openai_adapter.py](../../src/evidence_toolkit/infrastructure/ai/openai_adapter.py))
   - AsyncOpenAI client wrapper
   - Implements `IAIProvider` interface
   - Retry logic with exponential backoff
   - Error handling and logging
   - **Effort**: 2 hours

4. Refactor local storage ([src/evidence_toolkit/infrastructure/storage/local_storage.py](../../src/evidence_toolkit/infrastructure/storage/local_storage.py))
   - Async file I/O operations
   - Implements `IStorageProvider` interface
   - Keep existing SHA256 structure
   - **Effort**: 2 hours

5. Write tests
   - Unit tests with mocks
   - Integration tests (real OpenAI calls marked @pytest.mark.integration)
   - **Effort**: 2 hours

**Deliverable**: Foundation layer complete, all tests passing

**Delegate to**: Use `v4-architect` agent for parallel implementation:
```bash
# Invoke agent for tasks 1-4
> Use v4-architect to create core interfaces (IAIProvider, IStorageProvider, IDocumentExtractor)
> Use v4-architect to implement the Pydantic Settings configuration system
> Use v4-architect to create OpenAIAdapter implementing IAIProvider
> Use v4-architect to refactor EvidenceStorage to async IStorageProvider
```

---

### Week 2: Service Layer (6-8 hours)

**Goal**: Business logic with dependency injection

**Tasks**:
1. Create service layer ([src/evidence_toolkit/core/services.py](../../src/evidence_toolkit/core/services.py))
   - `EvidenceAnalysisService` with DI constructor
   - `analyze_document()`, `analyze_image()`, `analyze_email()` methods
   - Pure business logic (no OpenAI/file I/O imports)
   - **Effort**: 3 hours

2. Refactor DocumentAnalyzer ([src/evidence_toolkit/analyzers/document.py](../../src/evidence_toolkit/analyzers/document.py))
   - Use `EvidenceAnalysisService` via DI
   - Async methods
   - Remove duplicate OpenAI response handling code
   - **Effort**: 2 hours

3. Create mock adapters for testing ([src/evidence_toolkit/infrastructure/ai/mock_adapter.py](../../src/evidence_toolkit/infrastructure/ai/mock_adapter.py))
   - `MockAIProvider` - Returns fake data, no API calls
   - Validates Pydantic schemas
   - **Effort**: 1 hour

4. Write service layer tests
   - Test with mock adapters (no external dependencies)
   - Verify dependency injection works
   - **Effort**: 2 hours

**Deliverable**: Service layer complete, document analysis working end-to-end with DI

**Delegate to**: Use `v4-architect` agent:
```bash
> Use v4-architect to create EvidenceAnalysisService with dependency injection
> Use v4-architect to create MockAIProvider for testing without API calls
```

---

### Week 3: Async Migration (10-12 hours)

**Goal**: All analyzers async, 3x+ speedup demonstrated

**Tasks**:
1. Migrate ImageAnalyzer to async ([src/evidence_toolkit/analyzers/image.py](../../src/evidence_toolkit/analyzers/image.py))
   - AsyncOpenAI Vision API
   - PIL operations in thread pool (asyncio.to_thread)
   - Use `EvidenceAnalysisService`
   - **Effort**: 3 hours

2. Migrate EmailAnalyzer to async ([src/evidence_toolkit/analyzers/email.py](../../src/evidence_toolkit/analyzers/email.py))
   - Async email parsing
   - Use `EvidenceAnalysisService`
   - **Effort**: 2 hours

3. Migrate CorrelationAnalyzer to async ([src/evidence_toolkit/analyzers/correlation.py](../../src/evidence_toolkit/analyzers/correlation.py))
   - Async entity matching
   - AI-powered entity resolution (if --ai-resolve flag)
   - **Effort**: 3 hours

4. Create benchmark script ([scripts/benchmark_v4.py](../../scripts/benchmark_v4.py))
   - Compare v3.3 (sync sequential) vs v4.0 (async concurrent)
   - Measure on test001 case
   - Report speedup ratio
   - **Effort**: 2 hours

5. Optimize concurrency
   - Semaphore-based rate limiting
   - Tune max_concurrent setting
   - **Effort**: 2 hours

**Deliverable**: All analyzers async, benchmark shows 3x+ speedup

**Success Criteria**:
- ✅ 10 documents analyzed in ~10s (was 30s in v3.3)
- ✅ No blocking operations in async code paths
- ✅ Error handling works (return_exceptions=True)

**Delegate to**: Create `v4-async-specialist` agent for this week

---

### Week 4: Pipeline Integration (6-8 hours)

**Goal**: Async pipeline working end-to-end

**Tasks**:
1. Refactor ingest pipeline ([src/evidence_toolkit/pipeline/ingest.py](../../src/evidence_toolkit/pipeline/ingest.py))
   - Async file operations
   - Use `IStorageProvider` interface
   - **Effort**: 2 hours

2. Refactor analyze pipeline ([src/evidence_toolkit/pipeline/analyze.py](../../src/evidence_toolkit/pipeline/analyze.py))
   - Concurrent batch processing
   - Use service layer via DI
   - **Effort**: 2 hours

3. Refactor package generator ([src/evidence_toolkit/pipeline/package.py](../../src/evidence_toolkit/pipeline/package.py))
   - Async ZIP creation
   - Use `IStorageProvider` interface
   - **Effort**: 1 hour

4. Refactor summary generator ([src/evidence_toolkit/pipeline/summary.py](../../src/evidence_toolkit/pipeline/summary.py))
   - Async summary generation
   - Map-reduce chunking for 50+ evidence
   - **Effort**: 2 hours

5. Integration testing
   - End-to-end test: ingest → analyze → correlate → package
   - Verify output matches v3.3 schema
   - **Effort**: 2 hours

**Deliverable**: Complete async pipeline working

**Validation**:
```bash
uv run evidence-toolkit process-case data/cases/test001 --case-id test001
# Should complete in ~15s (was 60s in v3.3)
# Package should be identical to v3.3 output
```

---

### Week 5: Testing & Validation (8-10 hours)

**Goal**: 90% test coverage, all features validated

**Tasks**:
1. Unit tests for all components
   - Core interfaces: 100% coverage
   - Adapters: 90% coverage (use mocks)
   - Services: 95% coverage
   - **Effort**: 4 hours

2. Integration tests
   - Real OpenAI API calls (marked @pytest.mark.integration)
   - Real file I/O
   - Complete pipeline tests
   - **Effort**: 3 hours

3. Performance benchmarks
   - Document v3.3 vs v4.0 speedup
   - Cost comparison (should be identical)
   - Memory usage profiling
   - **Effort**: 2 hours

4. Regression testing
   - Run v4.0 on all test cases
   - Compare output to v3.3 (should match)
   - Verify chain of custody integrity
   - **Effort**: 2 hours

**Deliverable**: 90%+ coverage, all tests passing, performance validated

**Success Criteria**:
- ✅ pytest coverage ≥ 90%
- ✅ All integration tests pass
- ✅ Speedup ≥ 3x on test001 case
- ✅ Output matches v3.3 schema exactly

---

### Week 6: CLI & Documentation (6-8 hours)

**Goal**: CLI refactored, documentation complete

**Tasks**:
1. Refactor CLI ([src/evidence_toolkit/cli.py](../../src/evidence_toolkit/cli.py))
   - Ultra-thin wrapper (just argument parsing + DI wiring)
   - Load configuration from YAML + env vars
   - Execute async workflows
   - **Effort**: 2 hours

2. Create configuration files
   - `config/defaults.yaml` - Default settings
   - `config/profiles/development.yaml` - Dev overrides
   - `config/profiles/production.yaml` - Prod overrides
   - `config/profiles/testing.yaml` - Test overrides (mock AI)
   - **Effort**: 1 hour

3. Update documentation
   - Update [README.md](../../README.md) with v4.0 features
   - Update [QUICKSTART.md](../../QUICKSTART.md) with configuration examples
   - Create [docs/CONFIGURATION.md](CONFIGURATION.md) for Pydantic Settings
   - **Effort**: 3 hours

4. Write migration notes
   - Document v3.3 → v4.0 changes (internal only, no user-facing changes)
   - List deprecated patterns (old imports, etc.)
   - **Effort**: 1 hour

5. Final validation
   - Run complete pipeline on 3 test cases
   - Verify CLI commands unchanged
   - Check package outputs
   - **Effort**: 1 hour

**Deliverable**: v4.0 feature-complete, documented, ready for release

---

## Implementation Strategy

### Approach: Incremental Migration

**Don't delete v3.3 code immediately**:
1. Create v4.0 components alongside v3.3 (new files in `infrastructure/`, `config/`)
2. Refactor existing files gradually (analyzers, pipeline)
3. Keep v3.3 code until v4.0 is fully tested
4. Remove deprecated code in final cleanup

**Use feature branch**:
```bash
git checkout -b feature/v4-clean-architecture
# Develop on this branch for 6 weeks
# Merge to main when complete and tested
```

### Delegation Strategy

**Use specialized agents for parallel work**:

- **Week 1-2**: `v4-architect` agent for infrastructure + service layer
- **Week 3**: `v4-async-specialist` agent for async migration
- **Week 4-5**: `v4-tester` agent for comprehensive testing
- **Week 6**: Main Claude (you) for documentation and final polish

**Agent invocation examples**:
```bash
# Week 1
> Use v4-architect to create core interfaces and OpenAI adapter

# Week 3
> Use v4-async-specialist to migrate DocumentAnalyzer to async

# Week 5
> Use v4-tester to write integration tests for the complete pipeline
```

---

## Risk Mitigation

### High Risk: Async Migration Bugs

**Mitigation**:
- Start with POC (DocumentAnalyzer only) - validate 3x speedup
- Add comprehensive tests before migration
- Use asyncio.gather with return_exceptions=True (graceful failures)

**Fallback**:
- If async shows <2x speedup, keep sync with BaseAnalyzer refactoring only

### Medium Risk: Breaking Changes

**Mitigation**:
- Keep CLI commands identical (no user-facing changes)
- Test output schema matches v3.3 exactly
- Maintain backward compatibility for Python imports

**Fallback**:
- Provide v3.3 compatibility layer if needed

### Low Risk: Effort Overrun

**Mitigation**:
- Use agents for parallel development
- Time-box each week strictly
- Defer non-critical features to v4.1

**Fallback**:
- Release v4.0.0-beta if week 6 overruns
- Polish in v4.0.1

---

## Success Metrics

### Performance Goals

| Metric | v3.3 Baseline | v4.0 Target | Status |
|--------|---------------|-------------|--------|
| 10 documents | 30s | ≤10s (3x) | TBD |
| 20 mixed evidence | 90s | ≤25s (3.6x) | TBD |
| Code duplication | 875 lines | 0 lines | TBD |
| Test coverage | ~20% | ≥90% | TBD |

### Quality Gates

**Week 1-2**: Infrastructure layer
- ✅ All interfaces defined with clear contracts
- ✅ Configuration loads from YAML + env vars
- ✅ Unit tests pass (mocked dependencies)

**Week 3**: Async migration
- ✅ Benchmark shows ≥3x speedup
- ✅ No blocking operations in async paths
- ✅ Error handling tested

**Week 4**: Pipeline integration
- ✅ End-to-end pipeline works
- ✅ Output schema matches v3.3
- ✅ Chain of custody preserved

**Week 5**: Testing
- ✅ ≥90% test coverage
- ✅ All integration tests pass
- ✅ Performance benchmarks documented

**Week 6**: Release readiness
- ✅ CLI commands unchanged (backward compatible)
- ✅ Documentation complete
- ✅ 3 real-world test cases validated

---

## Post-Migration (v4.1 Planning)

Once v4.0 is stable, consider adding:

1. **Optional agent chat interface** (OpenAI Agents SDK)
   - Conversational case exploration
   - Natural language queries ("What contradictions exist?")
   - **Effort**: +10 hours

2. **Additional adapters**
   - Anthropic Claude adapter (alternative to OpenAI)
   - S3 storage adapter (cloud deployment)
   - **Effort**: +8 hours per adapter

3. **Advanced features**
   - Streaming analysis results (async generators)
   - Incremental analysis (analyze new evidence only)
   - Multi-case correlation (find patterns across cases)

---

## Getting Started

### Immediate Next Steps

1. **Create feature branch**:
   ```bash
   git checkout -b feature/v4-clean-architecture
   ```

2. **Review architecture docs**:
   - Read [ARCHITECTURE.md](ARCHITECTURE.md) thoroughly
   - Understand hexagonal pattern
   - Review interface contracts

3. **Invoke v4-architect agent**:
   ```bash
   > Use v4-architect to create core interfaces (IAIProvider, IStorageProvider, IDocumentExtractor)
   ```

4. **Begin Week 1 tasks** (infrastructure layer)

---

**Ready to begin v4.0 implementation? Start with Week 1, Task 1!**
