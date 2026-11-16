---
name: setup-design-index
description: >
  Index a software repo's design documents so /create-requirements and
  /architecture-critique can read them. The index stays at
  knowledge/designs/index.yaml until the user chooses per-repository user
  storage. Use when the user runs /setup-design-index, or asks to index the
  designs, catalog the architecture, or set a repo up for requirements.
argument-hint: "[repo path]"
---

# Set up a design index

Build the design index for one git repository. The index is the catalog `create-requirements` and `architecture-critique` read. Do not write a requirement. Do not edit the design documents. Do not commit unless the user asks.

## Confirm the repo

Default to the current directory. If the user names a path, use that. Resolve the git root with `git rev-parse --show-toplevel` and confirm that root with the user before searching.

## Choose where the index is stored

This skill file lives in the software-toolbox checkout. After resolving its symlink, the checkout root is the parent of `.agents`. Run:

```bash
python3 <checkout>/scripts/design_index.py status --repo <root>
```

Use the paths it prints. Do not build a config path yourself. If the command fails, stop and show the error.

`mode=repo` uses `repo_index`, `<root>/knowledge/designs/index.yaml`. That is the location when this user has not chosen user-level storage, including when the marker file is missing.

`mode=user` uses `user_index` under `$XDG_CONFIG_HOME/software-toolbox/repositories/<origin>/` (`~/.config` when `XDG_CONFIG_HOME` is unset). `<origin>` comes from the repository's `origin` URL. Every worktree and branch of that remote uses the same file.

When `location_file` is empty, user-level storage is unavailable. Use `repo_index` and do not ask. If the user asks for user-level storage, stop. Tell them this repository needs a supported `origin` remote. Do not run `choose`.

When `location_file` is set, `mode=repo`, and that file does not exist, ask which location to use. Show the absolute `repo_index` and the absolute `user_index`. Wait for the answer.

- In the repository, at `repo_index`. The team can commit this file.
- For this user only, at `user_index`. Use this when the index must stay out of the repository.

Run `choose` only after they answer:

```bash
python3 <checkout>/scripts/design_index.py choose repo --repo <root>
python3 <checkout>/scripts/design_index.py choose user --repo <root>
```

When the marker is already set, name the absolute `index` path and use it. Ask again only when they say to switch. Run `choose` after they confirm the switch.

`choose` writes the marker and does not write an index. Switching to `repo` leaves the user-level index file in place. Switching to `user` leaves `knowledge/designs/index.yaml` in place. Do not merge the two files.

When an in-repo index exists, they are choosing `user`, and `user_index` does not exist yet, ask whether to copy the in-repo body into the new file. On yes, use that body as the starting catalog, then continue the update rules below. On no, start from discovery. Do not modify the in-repo file.

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

If you copied the in-repo body, that body is the catalog you update. Otherwise, when `index_exists=true`, read `index` and update that file. Do not read the other location as the catalog. Do not write a second index.

On an update, propose entries for design documents that are not in the index yet. Keep existing entries whose files are still there. Propose removal when a file is gone. Leave a summary unchanged unless the file changed or the user asks.

## Propose, then write

For each included document, read it and draft one entry. `summary` is one or two sentences paraphrased from that file. Set `status: superseded` only when the document says so, or the user says so. Otherwise use `current` or `draft` as the document itself indicates.

Show the destination `index` path, the proposed YAML, and the near-misses you skipped. Wait for approval before writing.

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

After approval, save it with:

```bash
python3 <checkout>/scripts/design_index.py write --repo <root>
```

Pass the YAML on stdin. In `user` mode, do not create `knowledge/designs/` and do not change `knowledge/designs/index.yaml`. Tell the user the `index` path. Leave committing to them.
