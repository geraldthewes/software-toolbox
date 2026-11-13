# software-toolbox

Skills for writing requirements against a repo's design documents, and for analyzing review feedback before a code change.

## Skills

| Skill | What it does |
| --- | --- |
| `setup-design-index` | Finds the design documents in a software repo and writes `knowledge/designs/index.yaml` after you approve the list. |
| `create-requirements` | Writes `knowledge/requirements/<slug>.md`, one file per subject. The slug comes from the proposal. The skill checks `knowledge/requirements/` before writing, reads the design index, cites those constraints, and records the change to current behavior and one scenario per must-have. |
| `analyze-review-feedback` | Analyzes review feedback and proposes a testing strategy. It does not change code until you approve the fix. |

A session opened in this repo loads these skills from `.agents/skills/`.

## Files a software repo gains

`setup-design-index` writes:

```text
knowledge/designs/index.yaml
```

`create-requirements` writes one file per subject:

```text
knowledge/requirements/mark-plant-as-dead.md
```

Run `setup-design-index` before `create-requirements`. The requirement skill stops when the index is missing.

`analyze-review-feedback` writes nothing. It waits for approval before changing code.

## Install for other repos

`./install.sh` asks whether to install for your user account or for one repository. `./install.sh uninstall` asks the same question before it removes links.

For your user account, every repository you open can see the skills:

- `~/.agents/skills/` for Grok, Codex, and OpenCode
- `~/.claude/skills/` for Claude Code

For a repository, sessions in that repository can see the skills:

- `.agents/skills/` for Grok, Codex, and OpenCode
- `.claude/skills/` for Claude Code

In Grok or Claude Code, run `/setup-design-index`, `/create-requirements`, or `/analyze-review-feedback`. In Codex, use `$setup-design-index`, `$create-requirements`, or `$analyze-review-feedback`. In OpenCode, ask it to use the skill by name.

```bash
./install.sh
./install.sh --user
./install.sh --repo /path/to/repo
```

Pass `--user` or `--repo PATH` to skip the prompt. The same flags work with `uninstall`.

The command replaces a regular file or a symlink to another checkout. It exits when the destination is a real directory, and when the repository is this checkout. The skills already live in this checkout's `.agents/skills/`.

Uninstall removes a path only when it is a symlink to this checkout, including a dangling link that names that skill. A user-account uninstall also removes a matching link under `~/.grok/skills/` left by an older run of this script. A missing path is left unmentioned. A regular file, a directory, and a symlink to another checkout stay in place, and so does this checkout.
