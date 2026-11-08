---
name: create-requirements
description: >
  Write a requirement named from the user's proposal, grounded in the repo's
  design index. Use when the user runs /create-requirements, or asks to write,
  draft, or capture a requirement for something they want built. This does not
  create or manage tickets.
argument-hint: "what to build"
---

# Create a requirement

Turn a proposal into one requirements file. Record what to build and why. The design documents constrain it. Do not design the implementation, allocate a ticket id, choose a commit type, set a priority, or move a status.

The proposal is the text after `/create-requirements`. If it is missing, ask what they want built.

## Name the file

Propose a title, a lowercase kebab-case slug, and the path `knowledge/requirements/<slug>.md`. Derive the slug from the subject of the proposal. Drop a leading ticket id such as `PROJ-0016`; the slug is the subject. Example: "mark a plant as dead" becomes `knowledge/requirements/mark-plant-as-dead.md`.

Wait for the user to confirm or edit the title and slug.

If that file already exists, read it and continue that requirement. Keep its `created_at`. Do not add a numeric suffix unless the user says this is a different requirement.

## Read the design index

Read `knowledge/designs/index.yaml` at the repo root. If it is missing, stop. Tell the user to run `/setup-design-index` in this repo. Do not invent an index and do not scan the tree to build one.

The index fields are `path`, `title`, `kind`, `status`, `summary`, and `topics`. `setup-design-index` owns how those fields are written.

Select entries whose title, summary, or topics overlap the proposal. Read `current` and `draft` matches. List `superseded` matches and read one only when no current document covers that topic, or the user asks. If none match, say so and ask whether to proceed with an empty design context or to name more documents.

Read each selected file. For a long document, read the sections that bear on the proposal.

## Brief the designs

Before asking for anything else, show:

- each path you read, and why it matched
- constraints this requirement has to respect, each tied to its path and taken from that document
- conflicts between the proposal and a design

Report a conflict. Do not resolve it by redesigning. Ask the user whether to change the requirement to match the design, record the conflict as unresolved, or override the design for this requirement. Record an override explicitly.

## Fill the gaps

Ask only for what the proposal and the designs have not already answered. Put the missing items in one message and wait:

- the problem, why it matters, and who needs it
- must-have, nice-to-have, and out of scope
- constraints beyond the designs
- acceptance criteria
- research questions for a later planning pass
- related resources

If the user names a code path to mimic, record the path under Related resources. Do not read implementation files.

## Confirm and write

Show the full requirement. Wait for confirmation. Then create `knowledge/requirements/` if needed and write `knowledge/requirements/<slug>.md`.

Set `created_at` and `updated_at` to the current UTC time as `YYYY-MM-DDTHH:MM:SSZ`, taken from the system clock. On an update, keep `created_at` and refresh `updated_at`. `design_docs` lists only paths you read.

```markdown
---
title: Mark plant as dead
slug: mark-plant-as-dead
created_at: 2026-11-08T12:00:00Z
updated_at: 2026-11-08T12:00:00Z
design_docs:
  - knowledge/architecture/decisions/ADR-0006-data-persistence-strategy.md
---

# Mark plant as dead

## Design context

### Reviewed
- `path` — why it matched

### Constraints
- Constraint taken from the document (`path`)

### Conflicts
- Unresolved: proposal says X; `path` says Y
- Override: this requirement departs from `path` because …

## Problem

**What problem are we solving?**

**Why does it matter?**

**Who needs it?**

## Requirements and scope

### Must-have

### Nice-to-have

### Out of scope

## Constraints

## Success criteria

- [ ] Criterion

## Research questions

## Related resources

- Mimic later (not analyzed): `path/to/code`

## Notes
```

Omit a subsection that has nothing to say, including Conflicts and Mimic later. Tell the user the path you wrote. Leave committing to them.
