---
name: create-requirements
description: >
  Write a requirement named from the user's proposal, grounded in the repo's
  design index. The index is the in-repo file unless the user has chosen
  per-repository user storage. Use when the user runs /create-requirements,
  or asks to write, draft, or capture a requirement for something they want
  built. Skip a typo or a one-line fix whose behavior is already specified.
  This does not create or manage tickets.
argument-hint: "what to build"
---

# Create a requirement

Turn a proposal into one requirements file per subject. Record what to build and why. The design documents constrain it. Do not design the implementation, allocate a ticket id, choose a commit type, set a priority, or move a status.

The proposal is the text after `/create-requirements`. If it is missing, ask what they want built.

## When not to use

Do not write a requirement for a typo, a one-line fix, or a change whose desired behavior is already written down and unambiguous. Tell the user and stop. A change to behavior that has shipped still belongs here. Indexing designs is `/setup-design-index`. Design critique is `/architecture-critique`.

## Name the file

A subject is one behavior. Propose a title, a lowercase kebab-case slug, and the path `knowledge/requirements/<slug>.md` for each subject. Derive the slug from that subject. Drop a leading ticket id such as `PROJ-0016`. Example: "mark a plant as dead" becomes `knowledge/requirements/mark-plant-as-dead.md`.

When one request bundles several independently testable capabilities, propose a short breakdown before any file is written. A capability is its own subject when it has its own user or outcome, its checks could pass while the others are absent, or it could be cut without rewriting the others. For each one, give the name, why it is separate, and the proposed slug. That list is the title-and-slug confirmation below. Do not write a map file or a plan.

Wait once for the user to confirm or edit every title and slug. When more than one subject was confirmed, complete the rest of this workflow for the first slug through its write, then stop. Each file gets its own brief, gap question, and draft confirmation. Start the next confirmed slug in a later turn.

## Read existing requirements

If `<root>/knowledge/requirements/` is missing, there is nothing to read. `<root>` is the worktree root from the status command below. Otherwise read the frontmatter of each `*.md` file there: `title`, `slug`, and `design_docs`. Read the body only when the title or slug shares the proposal's subject.

When that file is the same subject, propose continuing it and wait. Do not add a numeric suffix unless the user says this is a different requirement. When the behavior in that file has already shipped, keep the change in that file. On an update, keep `created_at` and every section the user did not change. `design_docs` keeps paths already listed. Add a path read in this pass. Remove a path only when the user says the requirement no longer depends on it. Refresh `updated_at` when you write.

## Read the design index

Default to the current directory. If the user names a path, use that as `<repo>`.

This skill file lives in the software-toolbox checkout. After resolving its symlink, the checkout root is the parent of `.agents`. Run:

```bash
python3 <checkout>/scripts/design_index.py status --repo <repo>
```

Use the `index` path it prints. `<root>` in that output is the worktree root. Do not build a config path yourself. If the command fails, stop and show the error. Do not guess a location.

When `mode=repo` and `index_exists=false`, stop. Tell the user to run `/setup-design-index` in this repo. Do not invent an index and do not scan the tree to build one.

When `mode=user` and `index_exists=false`, stop. Tell the user to run `/setup-design-index`. Do not write a requirement, do not run `choose`, and do not create either index.

When `mode=user`, leave the repository's `knowledge/designs/index.yaml` unchanged.

If the user asks to move the design index, tell them to run `setup-design-index`. Do not change the marker here.

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

After any conflict is settled, list the assumptions you would otherwise fill in. Number them, and end with "Correct me now or I'll proceed with these." When you are filling nothing in, say there are no assumptions and skip that sentence.

Ask, in that same message, only for what would change the requirement and is still missing:

- the problem, why it matters, and who needs it
- must-have, nice-to-have, and out of scope
- constraints beyond the designs
- a scenario for each must-have that lacks one

Wait for the answer. Use an assumption they do not correct. When a research question comes up, record it under Research questions and leave it for the later planning pass. If the user names a code path to mimic, record the path under Related resources. Do not read implementation files.

Park an idea that is outside this subject under Out of scope.

## Confirm and write

Rewrite a vague must-have or success criterion into one a person can check before you show the draft. Name the trigger and the outcome. "Faster" and "easy" are not criteria. When the words are quantitative, name the number or the bound. When you supply a number or a bound the user did not state, mark it in the draft and ask, in that confirmation, whether the target is right. Drop it when they reject it.

Show the full requirement. Wait for confirmation. Then create `<root>/knowledge/requirements/` if needed and write `<root>/knowledge/requirements/<slug>.md`. `<root>` is the worktree root from status. Do not write a requirement under the config home.

For a new file, set `created_at` and `updated_at` to the current UTC time as `YYYY-MM-DDTHH:MM:SSZ`, taken from the system clock. `design_docs` lists the paths read in this pass. On an update, apply Read existing requirements.

When this pass changes a requirement whose behavior has already shipped, add a shipped delta under Change to current behavior. State the current behavior, the new behavior, and what must not change, and cite this requirement's path. Adds, Changes, and Removes stay, and they still cite the design. Each thing that must not change has a success criterion.

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

### Shipped delta

- Current behavior: what that shipped file does today (`knowledge/requirements/<slug>.md`)
- New behavior: what will be true after this change
- Must not change: behavior this change leaves as it is

## Problem

**What problem are we solving?**

**Why does it matter?**

**Who needs it?**

## Requirements and scope

### Must-have

### Nice-to-have

### Out of scope

- Bulk mark — deferred because this requirement covers one plant at a time

## Constraints

## Boundaries

- Always: keep the plant row when it is marked dead
- Ask first: adding a status other than dead
- Never: delete the plant row as part of this behavior

## Success criteria

- [ ] When the user marks a plant as dead, the plant stays in the record and is excluded from the active list

## Research questions

## Related resources

- Mimic later (not analyzed): `path/to/code`

## Notes
```

Change to current behavior is filled from the designs read in this pass. `Changes` and `Removes` cite the design path they come from. `Adds` is the behavior no design already describes. Omit an Adds, Changes, or Removes line that has nothing to say. Omit Shipped delta unless this pass changes a shipped requirement.

Out of scope is a deferred backlog. One line each: the thing, and why it is deferred. On an update, leave an existing out-of-scope line unchanged unless the user is changing it.

Every must-have has at least one success criterion. Each criterion is one behavior a person can check: a trigger and an outcome. When the requirement is quantitative, include the number or the bound. An edge case is its own criterion. A nice-to-have gets a criterion only when the user states one.

Boundaries is optional. Include it only for a limit the user stated that a later implementation agent must keep. Always, Ask first, and Never are one line each. Omit the section when they stated none. Do not invent a coding standard.

Omit a subsection that has nothing to say, including Conflicts, Related requirements, Shipped delta, Boundaries, and Mimic later.

The draft you show has to satisfy all of these:

- Assumptions were listed, and the draft uses only the ones the user left standing
- Each must-have is measurable, and each has a trigger and an outcome
- Each out-of-scope line says what is deferred and why
- A conflict is recorded as unresolved or as an override
- This file is one subject

Tell the user the path you wrote. Leave committing to them. Then stop the turn. Do not plan, design the implementation, or write code. Do not start another skill. The next step is a planning pass, in a later turn, after the user accepts the file. This repo has no planning skill. Do not invent one.
