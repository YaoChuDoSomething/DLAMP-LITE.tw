# 11 Decide per-module test plan scope

Type: grilling
Status: open
Blocked by: 03, 10

## Question

Decide the scope and template for the **per-module test plans** (`docs/testing/plans/<module>-test-plan.md`):

- Which modules get plans: every module under `src/dlamp/` (per ticket 03's tree), or a prioritized first slice? A forecast model package and a data pipeline have different test weight — decide the ordering (pipeline IO/registry first? inference first?).
- What each plan must cover: unit tests, integration tests, regression hooks from ticket 10, required fixtures and env vars (ticket 05), acceptance criteria per module.
- The template: fixed section headers every plan follows, so execution sessions can fill them in without new decisions.
- How the stale tests are treated per-module (fix/delete/quarantine) — fold ticket 09's policy down to concrete per-module dispositions.

Grill one decision at a time; the answer records the module→plan list and the template outline.
