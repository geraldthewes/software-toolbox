---
name: analyze-review-feedback
description: >
  Analyze review feedback without modifying code in Phase 1. Propose a
  testing strategy and wait for approval before implementing. Use when the
  user runs /analyze-review-feedback, or asks to analyze review feedback
  before changing code.
argument-hint: "review feedback"
---

# Analyze review feedback

Phase 1 reads the feedback and proposes a fix. It changes no files.

The review feedback is the text after `/analyze-review-feedback`. If it is missing, ask for it.

## Phase 1 — Analysis

Take each distinct finding on its own.

- Read the code and tests the finding points at. Quote the lines that confirm or refute it.
- Explain the issue.
- When the suggested fix is wrong, incomplete, or a worse change, say so and name a better one.
- When the code does not support the finding, say so and propose no change for it.

For each finding that needs a change, pick one strategy and say why:

- **Red/Green TDD** — a new failing test drives the implementation. Use this when the fix adds or changes behavior that no test specifies.
- **New test only** — add a test that the current production code already satisfies. Use this when the production code is fine and coverage is missing or weak.
- **No new test** — change the code and leave the tests alone. Use this when the change is cosmetic or documentation, or existing tests already cover it.

Show the findings, the proposed fix, and the strategy. Ask whether to implement or keep discussing. Phase 2 applies only the proposal the user approves.

## Phase 2 — Implementation

Edit the current checkout. Use the test runner and checks that repo already uses. Leave committing to the user.

- **Red/Green TDD**: write the failing test first. Run it and show that it fails because of the finding. Then implement the fix, run the test again, and show that it passes.
- **New test only**: add the test and run it against the existing implementation. Show that it passes. Leave production code unchanged.
- **No new test**: make the fix. Run the existing tests that cover it and show that they pass.

Show the commands and their output. An import error, a missing dependency, or a timeout is not a failing test for the finding.
