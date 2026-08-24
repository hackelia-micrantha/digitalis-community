# Digitalis Architecture

This directory contains the durable architecture, analysis, and implementation-planning artifacts for Digitalis.

## Current architecture set

- [Digitalis v1 project review](digitalis-v1-project-review.md)
- [Digitalis v1 implementation roadmap](digitalis-v1-implementation-roadmap.md)
- [QART analysis index](qart/README.md)
- [QART decision register](qart-decision-register.md)
- [Architecture decision records](adr/README.md)

## Artifact roles

### QART

QART means **Questions, Alternatives, Recommendations, Tradeoffs**. A QART slice is used before implementation when the problem still contains unresolved architectural questions. It records the analysis and recommends decisions.

### ADR

An Architecture Decision Record captures an accepted decision, its context, consequences, and replacement conditions. ADRs are authoritative for implementation unless superseded.

### RFC

The existing RFC suite defines the broader product and protocol intent. QART analysis resolves remaining uncertainty, and ADRs bind selected decisions to the v1 implementation.

## Required traceability

Implementation pull requests should reference:

1. the implementation issue;
2. the applicable QART slice and decision IDs;
3. the applicable ADRs;
4. any RFC or protocol contract affected by the change.

Security-sensitive implementation must include negative tests and evidence that bypass, replay, cross-project, rollback, and malformed-input paths fail closed.