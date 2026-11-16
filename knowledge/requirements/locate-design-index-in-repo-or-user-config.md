---
title: Locate the design index in the repo or in per-repo user config
slug: locate-design-index-in-repo-or-user-config
created_at: 2026-11-13T17:20:23Z
updated_at: 2026-11-13T17:20:23Z
design_docs: []
---

# Locate the design index in the repo or in per-repo user config

## Design context

### Reviewed
- `knowledge/designs/index.yaml` — the design catalog for this repo. It lists no documents, so no design document matched this proposal.

## Change to current behavior

- Adds: a per-repository user-level design index that the skills can use while the copy in the repository stays unchanged

## Problem

**What problem are we solving?**

The design index lives in the repository. Using the skills on a shared repo means adding that index to the repo.

**Why does it matter?**

A committed index means the team is carrying this workflow. A team may not have agreed to that yet. One person may also want to test the skills before the repo starts carrying the index.

**Who needs it?**

A contributor using these skills on a shared repository before the team keeps the index in the repo.

## Requirements and scope

### Must-have

- The in-repo design index remains the location used when the user has not chosen user-level storage for that repository.
- The user can choose per-repository user-level storage for the design index. That index is the stable record of where the design documents are, and the same index is used across branches, pull requests, and worktrees of that repository.
- `setup-design-index` and `create-requirements` read and write the design index in the chosen location.
- While user-level storage is chosen, those commands leave the repository's `knowledge/designs/index.yaml` unchanged.
- `create-requirements` writes each requirement file in the current worktree.

### Out of scope

- A team-shared index stored outside the repository
- Storing requirement files in user configuration
- Moving the design documents themselves
- `analyze-review-feedback`, which does not read or write the design index
- Installing the skills

## Constraints

- User-level configuration belongs to one user and one repository.
- The user-level index is reused across branches, pull requests, and worktrees of that repository.
- Requirement files for a feature stay in the worktree where that feature is being done.

## Success criteria

- [ ] When the user has not chosen user-level storage and the repository contains a design index, `setup-design-index` and `create-requirements` read and update that in-repo index
- [ ] When the user chooses user-level storage for a repository, `setup-design-index` writes the design index in that user's per-repository configuration
- [ ] When user-level storage is chosen, `setup-design-index` and `create-requirements` leave the repository's `knowledge/designs/index.yaml` unchanged
- [ ] When the user switches branches or opens another worktree of the same repository, `create-requirements` reads the same user-level design index
- [ ] When `create-requirements` writes a requirement, the file appears in the current worktree and is absent from user configuration
- [ ] When user-level storage is chosen and that index is missing, `create-requirements` stops without writing a requirement and without creating an in-repo index
- [ ] When two people use the skills on the same repository, each person's user-level index stays independent

## Research questions

- How is a repository identified so every worktree and branch resolves the same user-level index?
- What on-disk layout should per-repository user configuration use?
