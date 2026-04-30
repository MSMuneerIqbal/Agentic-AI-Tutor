---
stage: spec
title: Clarified quiz length behavior
date: 2025-10-09
---

## Full Input

```
/sp.clarify 
```

## Q&A

- Q1: How should quiz length be determined per session? → A: B (Bounded adaptive: target 15–20; stop early on mastery, extend to 20 if borderline)

## Changes Made

- Added `## Clarifications` with dated session.
- Updated FR-004 to bounded-adaptive quiz behavior.
- Added acceptance scenarios for early stop on mastery and extension on borderline cases.

## Path

- Updated spec: `specs/001-backend-first-agentic/spec.md`

