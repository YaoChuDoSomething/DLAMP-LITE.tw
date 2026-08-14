# 11 Decide per-module test plan scope

Type: grilling
Status: resolved
Blocked by: 03, 10

## Question

Decide the scope and template for the **per-module test plans** (`docs/testing/plans/<module>-test-plan.md`):

- Which modules get plans: every module under `src/dlamp/` (per ticket 03's tree), or a prioritized first slice? A forecast model package and a data pipeline have different test weight — decide the ordering (pipeline IO/registry first? inference first?).
- What each plan must cover: unit tests, integration tests, regression hooks from ticket 10, required fixtures and env vars (ticket 05), acceptance criteria per module.
- The template: fixed section headers every plan follows, so execution sessions can fill them in without new decisions.
- How the stale tests are treated per-module (fix/delete/quarantine) — fold ticket 09's policy down to concrete per-module dispositions.

## Answer

Grilled 4 branches, all confirmed. Approved per-module test plan policy:

1. **5 Prioritized Test Plans (`docs/testing/plans/`):**
   - `data-pipeline-test-plan.md` (`dlamp.data.preproc`, `dlamp.data.registry`) — Priority 1 (High)
   - `model-architectures-test-plan.md` (`dlamp.models.*`) — Priority 1 (High)
   - `inference-pipeline-test-plan.md` (`dlamp.inference`, `dlamp.analysis`) — Priority 2 (Med)
   - `core-utils-test-plan.md` (`dlamp.const`, `dlamp.standardization`, `dlamp.utils`) — Priority 2 (Med)
   - `datasets-managers-test-plan.md` (`dlamp.datasets`, `dlamp.managers`) — Priority 3 (Low)
2. **Mandatory Plan Sections:**
   - 1. Scope & Target Submodules
   - 1. Unit Test Specifications
   - 1. Integration Test Scenarios (`@pytest.mark.integration`)
   - 1. Regression Test Specifications (`@pytest.mark.regression`)
   - 1. Fixtures & Environment Requirements (`DLAMP_EXP_CODE`, `DLAMP_DATA_PATH`)
   - 1. Target Coverage & Acceptance Criteria
3. **Template Outline:** Standardized 6-section Markdown outline locked for all files under `docs/testing/plans/*.md`.
4. **Stale/Duplicate Test Dispositions:**
   - Delete: `tests/test_dlamp.py` (starter scaffold deleted in 03-B), `pangu_model_test.py` (import crash), `updated.py` (duplicate file in `dlamp.data.registry`).
   - Migrate: `unet_test.py`, `glide_unet_test.py`, `earth_3d_specifics_test.py` → `tests/dlamp/models/architectures/test_*.py` with updated imports.
   - Build from scratch: `tests/dlamp/data/` (preproc & registry) and `tests/dlamp/inference/`.

Inputs to: testing specification (ticket 09 supplement), handoff design doc (ticket 12).
