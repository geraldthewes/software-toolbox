# software-toolbox

Skills for writing requirements against a repo's design documents, critiquing those designs, and analyzing review feedback before a code change.

## Skills

| Skill | What it does |
| --- | --- |
| `setup-design-index` | Finds the design documents in a software repo and writes the design index after you approve the list. The index stays in the repo until you choose per-repository user storage. |
| `create-requirements` | Writes `knowledge/requirements/<slug>.md` in the current worktree, one file per subject. The slug comes from the proposal. The skill checks existing requirements before writing, reads the design index from the chosen location, cites those constraints, and records the change to current behavior and one measurable scenario per must-have. A shipped change stays in that file as a delta. Out of scope records each deferred idea and why it waits. |
| `architecture-critique` | Critiques the design documents in the chosen design index and reports risks before implementation. It reads the index and writes nothing. |
| `analyze-review-feedback` | Analyzes review feedback and proposes a testing strategy. It does not change code until you approve the fix. |

A session opened in this repo loads these skills from `.agents/skills/`.

## Files a software repo gains

By default, `setup-design-index` writes the design index in the repository:

```text
knowledge/designs/index.yaml
```

That stays the location until you choose otherwise. To keep the index out of a shared repository, tell `setup-design-index` to store it for your user. It records that choice under your config home (`$XDG_CONFIG_HOME`, or `~/.config`) and writes:

```text
software-toolbox/repositories/<host>/<owner>/<name>/designs/index.yaml
```

`<host>/<owner>/<name>` comes from the repository's `origin` URL, lowercased. Every worktree and branch of that remote uses the same file. User-level storage needs an `origin` remote. Another person has a different config home, so their index stays separate. While this choice is in effect, `setup-design-index`, `create-requirements`, and `architecture-critique` leave the repository's `knowledge/designs/index.yaml` unchanged.

`create-requirements` writes one file per subject in the current worktree:

```text
knowledge/requirements/mark-plant-as-dead.md
```

A request that bundles several independently testable capabilities is split only after you approve a short breakdown, and each capability gets its own file. A change to a requirement that has already shipped stays in that file. After the file is written, the skill stops. Planning and code wait for a later turn.

Run `setup-design-index` before `create-requirements` or `architecture-critique`. Both stop when the chosen index is missing. `create-requirements` does not store requirement files in your config home.

`architecture-critique` reads that index and writes nothing. It does not edit the design documents.

`analyze-review-feedback` changes no files until you approve the proposed fix. It does not commit.

## Install for other repos

`./install.sh` asks whether to install for your user account or for one repository. `./install.sh uninstall` asks the same question before it removes links.

For your user account, every repository you open can see the skills:

- `~/.agents/skills/` for Grok, Codex, and OpenCode
- `~/.claude/skills/` for Claude Code

For a repository, sessions in that repository can see the skills:

- `.agents/skills/` for Grok, Codex, and OpenCode
- `.claude/skills/` for Claude Code

In Grok or Claude Code, run `/setup-design-index`, `/create-requirements`, `/architecture-critique`, or `/analyze-review-feedback`. In Codex, use `$setup-design-index`, `$create-requirements`, `$architecture-critique`, or `$analyze-review-feedback`. In OpenCode, ask it to use the skill by name.

```bash
./install.sh
./install.sh --user
./install.sh --repo /path/to/repo
```

Pass `--user` or `--repo PATH` to skip the prompt. The same flags work with `uninstall`.

The command replaces a regular file or a symlink to another checkout. It exits when the destination is a real directory, and when the repository is this checkout. The skills already live in this checkout's `.agents/skills/`.

Uninstall removes a path only when it is a symlink to this checkout, including a dangling link that names that skill. A user-account uninstall also removes a matching link under `~/.grok/skills/` left by an older run of this script. A missing path is left unmentioned. A regular file, a directory, and a symlink to another checkout stay in place, and so does this checkout.
