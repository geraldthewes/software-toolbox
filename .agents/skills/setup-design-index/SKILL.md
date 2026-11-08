---
name: setup-design-index
description: >
  Index a software repo's design documents into knowledge/designs/index.yaml
  so /create-requirements can read them. Use when the user runs
  /setup-design-index, or asks to index the designs, catalog the architecture,
  or set a repo up for requirements.
argument-hint: "[repo path]"
---

# Set up a design index

Build `knowledge/designs/index.yaml` for one git repository. The index is the catalog `create-requirements` reads. Do not write a requirement. Do not edit the design documents. Do not commit unless the user asks.

## Confirm the repo

Default to the current directory. If the user names a path, use that. Resolve the git root with `git rev-parse --show-toplevel` and confirm that root with the user before searching.

If `knowledge/designs/index.yaml` already exists, read it and update that file. Do not create a second index.

## Discover documents

Search the tree and read candidates before classifying them. Do not invent documents, and do not copy an index from another repository.

Look for decision records (`ADR-*`, `decisions/`, `adr/`), architecture context and container docs (C4, deployment), PRDs, product briefs, UX specifications, domain or ontology docs, technical specs, and UI-flow diagram sources (`*.puml` under a design or UI directory).

Include a file when it states how the system is shaped. Skip work products and noise:

- tickets, plans, research notes, handoffs, reviews, backlog items
- logs, generator history, critic history, feedback dumps
- scratch diagrams (`test*`, `debug`, `minimal`, and similar drafts)
- runtime data, `graphify-out/`, images, and dependency trees

`~/repos/plant-tracking` is the example of this split. Apply the same judgment to whatever repo you are indexing. Do not copy these paths into another repo.

Include there:

- `knowledge/architecture/decisions/ADR-*.md`
- `knowledge/architecture/c1-context.md`
- `knowledge/architecture/backend/c2-container.md`
- `knowledge/architecture/database/c2-container.md`
- `knowledge/architecture/deployment.md`
- `_bmad-output/prd.md`
- `_bmad-output/ux-design-specification.md`
- `_bmad-output/briefs/`
- `knowledge/ontology/*.md`
- `knowledge/specs/database.md`
- `knowledge/ui-design/*.puml`

That list shows the split. Also include other documents in that repo that meet the same test, such as `knowledge/architecture/edge-functions/c2-container.md` and `knowledge/architecture/architecture-decisions.md`.

Skip there: `knowledge/tickets/`, `knowledge/plans/`, `knowledge/research/`, `knowledge/handoffs/`, `knowledge/reviews/`, `knowledge/backlog/`, architecture logs, generator history, critic history, feedback JSON, `knowledge/architecture/frontend/test*.md`, `debug.md`, `minimal.md`, `database/*.md` plant records, `graphify-out/`, and images.

When two documents share an ADR number, show them side by side and ask whether each is current, superseded, or a distinct decision that reused the number. plant-tracking does this for `ADR-0001` through `ADR-0004`. Do not drop one silently.

On an update, propose entries for design documents that are not in the index yet. Keep existing entries whose files are still there. Propose removal when a file is gone. Leave a summary unchanged unless the file changed or the user asks.

## Propose, then write

For each included document, read it and draft one entry. `summary` is one or two sentences paraphrased from that file. Set `status: superseded` only when the document says so, or the user says so. Otherwise use `current` or `draft` as the document itself indicates.

Show the proposed YAML and the near-misses you skipped. Wait for approval before writing.

```yaml
version: 1
documents:
  - path: knowledge/architecture/decisions/ADR-0006-data-persistence-strategy.md
    title: Data persistence strategy
    kind: adr          # adr | architecture | prd | ux | domain | spec | other
    status: current    # current | superseded | draft
    summary: One or two sentences taken from the document.
    topics: [persistence, postgres]
```

`path` is relative to the repo root. `kind` is one of `adr`, `architecture`, `prd`, `ux`, `domain`, `spec`, `other`. `topics` are short nouns from the document.

If the repo has no design documents, say so. Write `version: 1` and `documents: []` only when the user wants the empty file.

After approval, create `knowledge/designs/` if needed and write `knowledge/designs/index.yaml`. Tell the user the path. Leave committing to them.
