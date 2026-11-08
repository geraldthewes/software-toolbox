# software-toolbox

Skills for writing requirements against a repo's design documents.

## Skills

| Skill | What it does |
| --- | --- |
| `setup-design-index` | Finds the design documents in a software repo and writes `knowledge/designs/index.yaml` after you approve the list. |
| `create-requirements` | Writes `knowledge/requirements/<slug>.md`. The slug comes from the proposal. The skill reads the design index, opens the relevant documents, and cites their constraints in the requirement. |

A session opened in this repo loads both skills from `.agents/skills/`.

## Files a software repo gains

`setup-design-index` writes:

```text
knowledge/designs/index.yaml
```

`create-requirements` writes one file per proposal:

```text
knowledge/requirements/mark-plant-as-dead.md
```

Run `setup-design-index` before `create-requirements`. The requirement skill stops when the index is missing.

## Install for other repos

`install.sh` symlinks both skills into `~/.grok/skills/`, `~/.agents/skills/`, and `~/.claude/skills/`. A session in another repo, such as plant-tracking, can then run `/setup-design-index` and `/create-requirements`.

```bash
./install.sh
```

The script refuses to replace a destination that is not already a symlink to this checkout.
