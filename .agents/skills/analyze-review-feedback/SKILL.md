---
name: analyze-review-feedback
description: >
  Analyze review feedback without modifying code in Phase 1. Propose a
  testing strategy and wait for approval before implementing. Use when the
  user runs /analyze-review-feedback, or asks to analyze review feedback
  before changing code.
disable-model-invocation: true
argument-hint: "review feedback"
---

# Analyze Review Feedback

This command is for analysis only. Do not modify any code files during Phase 1.

The review feedback is the text after `/analyze-review-feedback`. If it is missing, ask for it.

**Phase 1 — Analysis**

Review that feedback: confirm the issue, explain it, critique the feedback, and suggest alternatives if appropriate. Present your findings clearly.

Then assess what testing approach is most appropriate for the fix and propose one of these strategies:

- **Red/Green TDD** — a new failing test drives the implementation (best when the fix requires new behavior to be specified)
- **New test only** — add a test that verifies a correction to existing code (best when the production code is fine but test coverage is missing or weak)
- **No new test** — implement the fix directly without touching tests (best when the change is cosmetic, documentation, or already covered by existing tests)

Explain briefly why you chose that strategy.

Present your findings, proposed fix, and recommended testing strategy. Then ask the user to confirm: proceed with implementation or discuss further? Do NOT implement anything until the user explicitly approves.

**Phase 2 — Implementation (only after user approval)**

Apply the fix using the approved testing strategy:

- **Red/Green TDD**: write a failing test first (red), implement the fix to make it pass (green), confirm the test passes.
- **New test only**: add the test, confirm it passes against the existing implementation.
- **No new test**: implement the fix directly, confirm existing tests still pass.
