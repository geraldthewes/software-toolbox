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

Turn a proposal into one requirements file per subject. Record what to build and why. The design documents constrain it. Do not design the implementation, allocate a ticket id, choose a commit type, set a priority, or move a status.

The proposal is the text after `/create-requirements`. If it is missing, ask what they want built.

## Name the file

A subject is one behavior. Propose a title, a lowercase kebab-case slug, and the path `knowledge/requirements/<slug>.md` for each subject. Derive the slug from that subject. Drop a leading ticket id such as `PROJ-0016`. Example: "mark a plant as dead" becomes `knowledge/requirements/mark-plant-as-dead.md`.

Wait once for the user to confirm or edit every title and slug. When more than one subject was confirmed, complete the rest of this workflow for the first slug through its write confirmation, then take each remaining slug through that same workflow, one at a time. Each file gets its own brief, gap question, and draft confirmation.

## Read existing requirements

If `knowledge/requirements/` is missing, there is nothing to read. Otherwise read the frontmatter of each `*.md` file there: `title`, `slug`, and `design_docs`. Read the body only when the title or slug shares the proposal's subject.

When that file is the same subject, propose continuing it and wait. Do not add a numeric suffix unless the user says this is a different requirement. On an update, keep `created_at` and every section the user did not change. `design_docs` keeps paths already listed. Add a path read in this pass. Remove a path only when the user says the requirement no longer depends on it. Refresh `updated_at` when you write.

## Read the design index

Read `knowledge/designs/index.yaml` at the repo root. If it is missing, stop. Tell the user to run `/setup-design-index` in this repo. Do not invent an index and do not scan the tree to build one.

The index fields are `path`, `title`, `kind`, `status`, `summary`, and `topics`. `setup-design-index` owns how those fields are written.

Select entries whose title, summary, or topics overlap the proposal. Read `current` and `draft` matches. List `superseded` matches and read one only when no current document covers that topic, or the user asks. If none match, say so and ask whether to proceed with an empty design context or to name more documents.

Read each selected file. For a long document, read the sections that bear on the proposal.

## Brief the designs

After the designs are selected, read the body of any other requirement whose `design_docs` intersect those paths.

Before asking for anything else, show:

- each path you read, and why it matched
- constraints this requirement has to respect, each tied to its path and taken from that document
- conflicts between the proposal and a design, or with another requirement
- related requirements: the file this pass continues, and any file that cites a design this requirement also uses

Report a conflict. Do not resolve it by redesigning. Ask the user whether to change this requirement to match, record the conflict as unresolved, or override for this requirement. Record an override explicitly, and name the design path or the requirement path. A shared design with no contradiction goes under Related requirements and does not block.

## Fill the gaps

Ask, in one message, only for what would change the requirement and is still missing:

- the problem, why it matters, and who needs it
- must-have, nice-to-have, and out of scope
- constraints beyond the designs
- a scenario for each must-have that lacks one

Wait for the answer. When a research question comes up, record it under Research questions and leave it for the later planning pass. If the user names a code path to mimic, record the path under Related resources. Do not read implementation files.

## Confirm and write

Show the full requirement. Wait for confirmation. Then create `knowledge/requirements/` if needed and write `knowledge/requirements/<slug>.md`.

For a new file, set `created_at` and `updated_at` to the current UTC time as `YYYY-MM-DDTHH:MM:SSZ`, taken from the system clock. `design_docs` lists the paths read in this pass. On an update, apply Read existing requirements.

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
- Unresolved: proposal says X; `knowledge/requirements/<slug>.md` says Y

### Related requirements
- `knowledge/requirements/<slug>.md` — cites the same design

## Change to current behavior

- Adds: a recorded death state for a plant
- Changes: `knowledge/architecture/decisions/ADR-0006-data-persistence-strategy.md` says records are kept; this requirement keeps the row and sets a terminal state
- Removes: `knowledge/architecture/decisions/ADR-0006-data-persistence-strategy.md` allowed deleting the row; this requirement no longer allows that

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

- [ ] When the user marks a plant as dead, the plant stays in the record and is excluded from the active list

## Research questions

## Related resources

- Mimic later (not analyzed): `path/to/code`

## Notes
```

Change to current behavior is filled from the designs read in this pass. `Changes` and `Removes` cite the design path they come from. `Adds` is the behavior no design already describes. Omit an Adds, Changes, or Removes line that has nothing to say.

Every must-have has at least one success criterion. Each criterion is one behavior: a trigger and an outcome. An edge case is its own criterion. A nice-to-have gets a criterion only when the user states one.

Omit a subsection that has nothing to say, including Conflicts, Related requirements, and Mimic later. Tell the user the path you wrote. Leave committing to them.
