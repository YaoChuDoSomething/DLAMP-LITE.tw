<!--
---
Sync Impact Report
---
- Version change: 1.0.0 → 1.0.0 (Re-initialization)
- Summary: The constitution has been redefined to focus on Code Quality, Testing Standards, User Experience Consistency, and Performance, while retaining core engineering and security principles.
- Principle Changes:
  - RENAMED/REORGANIZED: Multiple principles consolidated and clarified under new headings.
  - ADDED: "User Experience (UX) Consistency" principle.
  - ADDED: "Performance Requirements" principle.
- Templates requiring updates:
  - ✅ .specify/templates/plan-template.md (Checked for alignment)
  - ✅ .specify/templates/spec-template.md (Checked for alignment)
  - ✅ .specify/templates/tasks-template.md (Checked for alignment)
- Follow-up TODOs: None
-->
# v25-11-op Constitution

This document outlines the non-negotiable principles governing all software development for the **v25-11-op** project. Compliance is mandatory.

## I. Code Quality
All code must be clear, maintainable, and adhere to the highest standards of craftsmanship.
- **Style and Linting**: All Python code MUST strictly adhere to PEP 8 and pass `ruff` checks as configured in `pyproject.toml`.
- **Documentation**: All public modules, classes, functions, and methods MUST have complete Google-style docstrings with full type annotations.
- **Simplicity**: Prioritize simple, direct solutions over premature abstraction or over-engineering. Code should be easily understood by new team members.
- **Logging**: Use the standard `logging` library for all operational output. `print()` calls are disallowed in application code.

## II. Rigorous Testing Standards
Testing is a prerequisite for implementation, not an afterthought.
- **Test-First Imperative**: No production code shall be written without a corresponding failing test. The "Red-Green-Refactor" cycle is mandatory.
- **Coverage**: All new code MUST be accompanied by meaningful unit and integration tests. High test coverage is expected and will be monitored.
- **Integration over Mocks**: Tests MUST use real integrations (e.g., actual databases, service connections) where feasible to validate contracts and end-to-end behavior. Mocks should be used sparingly, primarily to simulate external failure modes.

## III. User Experience (UX) Consistency
A cohesive and predictable user experience is paramount.
- **Design System Adherence**: All user-facing components, interfaces, and interactions MUST conform to a centrally defined design system and style guide.
- **Consistent Patterns**: Interaction patterns, terminology, and visual language MUST be consistent across all parts of the application.
- **UX Review**: All significant UI/UX changes MUST be reviewed and approved for consistency and usability before implementation.

## IV. Performance Requirements
The application must be responsive and efficient.
- **Performance Budgets**: Critical user journeys and API endpoints MUST have clearly defined performance budgets (e.g., <200ms API response time, <50MB memory allocation).
- **Performance Testing**: Performance tests MUST be implemented for any performance-sensitive feature. These tests should run as part of the CI/CD pipeline to prevent regressions.

## V. Specification-Driven Development (SDD)
The specification is the single source of truth for all development.
- **Spec is Truth**: All implementation, testing, and debugging activities are driven by and must conform to the approved specification. If the code is wrong, the specification is corrected first.

## VI. Modular Architecture
The system will be composed of discrete, independent, and reusable components.
- **Library-First**: Every feature MUST be implemented as a self-contained, independently testable library.
- **CLI Mandate**: Every library MUST expose its primary functionality through a command-line interface (CLI) to ensure observability, testability, and composability.

## VII. Security by Design
Security is a foundational pillar of the architecture, not an add-on.
- **Assume Malicious Input**: All data from external sources (users, APIs, files) MUST be treated as untrusted until validated and sanitized.
- **Least Privilege**: Code MUST only have the permissions absolutely necessary to perform its intended function.
- **Fail Securely**: Error handling paths MUST never expose sensitive information or fail into an insecure state.

## Governance

### Compliance and Amendments
This Constitution supersedes all other practices and conventions. All code reviews must explicitly validate compliance with these principles. Amendments to this document require a formal proposal, review, and an update to the version number and amendment date.

**Version**: 1.0.0 | **Ratified**: 2025-11-19 | **Last Amended**: 2025-11-19
