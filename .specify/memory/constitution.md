<!--
---
Sync Impact Report
---
- Version change: None → 1.0.0
- Added sections:
  - Core Principles
  - Code & Documentation Standards
  - Security Posture
  - Governance
- Templates requiring updates:
  - ✅ .specify/templates/plan-template.md (Constitution Check section aligned)
  - ⚠ .specify/templates/spec-template.md (Review for alignment with principles)
  - ⚠ .specify/templates/tasks-template.md (Review for alignment with principles)
- Follow-up TODOs: None
-->
# v25-11-op Constitution

## Core Principles

### I. Specification-Driven Development (SDD)
The specification is the single source of truth. All implementation, testing, and debugging activities are driven by and must conform to the approved specification. If the code is wrong, the spec is corrected first.

### II. Library-First
Every feature MUST be implemented as a self-contained, independently testable, and documented library. Direct implementation within an application is forbidden to enforce modularity and reusability.

### III. CLI Mandate
Every library MUST expose its primary functionality through a command-line interface (CLI). The CLI must accept text-based input (stdin/args) and produce text-based output (stdout/JSON), ensuring observability and testability.

### IV. Test-First Imperative (NON-NEGOTIABLE)
Code is not written until a failing test exists. The development sequence is strictly: 1. Define contracts/interfaces. 2. Write tests that implement those contracts. 3. Run tests and confirm they fail (Red). 4. Implement the code to make the tests pass (Green).

### V. Simplicity and Integration
Prioritize simple, direct solutions using native framework features over premature abstraction. Initial implementations should be minimal. Testing MUST use real integrations (e.g., actual databases) over mocks to validate contracts and end-to-end behavior.

## Code & Documentation Standards

### PEP 8 and Google Style Docstrings
All Python code MUST strictly adhere to PEP 8 guidelines. All public modules, classes, functions, and methods MUST have complete Google-style docstrings with full type annotations. Code must pass `flake8`, `pydocstyle`, and `isort` checks.

### Logging and Immutability
Use the standard `logging` library for all operational output; `print()` is disallowed. Prefer immutable data structures (`dataclasses.dataclass(frozen=True)`) for value-like objects.

## Security Posture

### Secure Development Principles
- **Assume All External Input is Malicious**: All data from users, APIs, or files MUST be treated as untrusted until validated and sanitized.
- **Principle of Least Privilege**: Code MUST only have the permissions absolutely necessary to perform its function.
- **Fail Securely**: Error handling paths MUST never expose sensitive information or fail into an insecure state.

## Governance

### Compliance and Amendments
This Constitution supersedes all other practices and conventions. All code reviews must explicitly validate compliance with these principles. Amendments to this document require a formal proposal, review, and an update to the version number and amendment date.

**Version**: 1.0.0 | **Ratified**: 2025-11-19 | **Last Amended**: 2025-11-19