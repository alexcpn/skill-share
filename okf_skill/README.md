# okf_skill

A self-contained Python package that turns a source-code repository into an
[**Open Knowledge Format (OKF v0.1)**](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md)
knowledge bundle — a directory of cross-linked markdown concepts with YAML
frontmatter describing the repo's services, modules, APIs, data models, and
operations. Packaged as a portable **Agent Skill** that installs into Claude
Code, Cursor, OpenAI Codex, and any tool that reads the open `.agents/skills`
standard.

The output is plain markdown in git: readable by humans, diffable in PRs, and
consumable by other agents with no bespoke tooling. The interesting part is
that the agent mines **git history** for the *why* — invariants and gotchas
recorded in reverts, hotfixes, and risk-flagged commits — instead of
paraphrasing the code file by file. What it cannot establish from the code or
its history it **parks as an open question** rather than guessing.

## Commands

- `okf-inventory [out.json] [--config <cfg>]` — deterministic repo inventory as JSON: file tree, languages, entry points, dependency manifests, API definitions, schemas/migrations, CI/CD, docs, ADR/RFC docs, plus git churn and recent commits. Prints the path it wrote.
- `okf-history <path>... [--limit N] [--json] [--patch]` — bounded per-path git history: creation commit, commit count, recent subjects, and revert/hotfix/risk-flagged commits. Diff-free by default so historical secrets don't leak.
- `okf-validate <bundle_dir> [--config <cfg>] [--json]` — OKF §9 conformance checker (4 error classes, 9 warning classes).
- `okf-skill` — install/list/uninstall the skill across AI agents.

## The four workflows

The skill routes to one of four workflow files (`references/*.md`), loaded only
when that workflow runs:

| Workflow | What it does |
| -------- | ------------ |
| **generate** | Inventory scan + git-history mining, concept plan, concept documents, `index.md` files, `log.md`, validation. |
| **update** | Diffs since the last logged commit; surgically refreshes stale concepts, deprecates orphans, adds new ones, preserves human curation. |
| **clarify** | Asks you about the `open_questions` the other workflows parked, then folds the answers in as cited, curation-protected knowledge. |
| **validate** | Conformance check plus a quality spot-check the validator can't mechanically judge. |

## Requirements

- **Python 3.9+** (the package and the validator).
- **`git`** — the inventory and history tools are git-driven; they degrade
  cleanly on a non-git directory, but the "why" comes from history.
- **`bash`** — `okf-inventory` and `okf-history` are bash scripts. On Linux and
  macOS this is already there; on **Windows** they run under the `bash.exe`
  that ships with [Git for Windows](https://git-scm.com/download/win), which
  the wrapper locates automatically.

## Install (recommended: uv + Git)

Each developer machine runs one bootstrap. It installs the CLI as an isolated
`uv` tool and registers the skill into every agent.

**Windows (PowerShell):**

```powershell
./install.ps1 -Source "git+https://github.com/alexcpn/skill-share.git#subdirectory=okf_skill"
```

**Linux / macOS:**

```bash
./install.sh --source "git+https://github.com/alexcpn/skill-share.git#subdirectory=okf_skill"
```

(The `#subdirectory=` part points at this package folder inside the repo, so
`uv` builds just this skill and not the whole collection.)

The bootstrappers prefer `uv` (using `--native-tls` for corporate proxies) and
fall back to `pip install --user`. Omit `-Source`/`--source` to install from a
local checkout instead of Git.

### Without the bootstrap script

```bash
uv tool install --native-tls "git+https://github.com/alexcpn/skill-share.git#subdirectory=okf_skill"
okf-skill --install
```

Restart the agent afterwards so it picks up the new skill.

## Usage

Once installed, just ask your agent — it loads the skill on its own when the
request matches:

```bash
agent "generate an OKF knowledge bundle for this repo"
agent "refresh the knowledge bundle, the code has moved on"
agent "resolve the open questions in the knowledge bundle"
agent "validate the OKF bundle"
```

Output lands in `knowledge/` (configurable) as cross-linked markdown ready to
commit alongside your code:

```
knowledge/
├── index.md            # okf_version: "0.1" + directory of everything
├── log.md              # dated history, each block records a commit SHA
├── architecture/
│   ├── index.md
│   └── overview.md     # type: Reference — the "start here" concept
├── services/…          # type: Service
├── modules/…           # type: Module
├── apis/…              # type: API Endpoint / API Resource
├── data/…              # type: Data Model / Database Table
└── operations/…        # type: Pipeline / Configuration / Playbook
```

The commands also stand alone, with or without an agent:

```bash
okf-inventory                      # writes a JSON inventory, prints the path
okf-history src/orders/service.py  # why this file looks the way it does
okf-validate knowledge/            # conformance + quality warnings
```

## Configuration

Everything works with no config. To change the bundle directory, resource URI
base, excludes, type mappings, layout, granularity (`coarse` / `medium` /
`fine`), or the clarify question budget, copy the annotated template into your
repo root as `.okf-config.yml`:

```bash
cp ~/.claude/skills/okf-knowledge-bundle/okf-config.template.yml .okf-config.yml
```

`okf-inventory --config .okf-config.yml` and `okf-validate <dir> --config
.okf-config.yml` honor its `exclude` list; the agent passes it through
automatically once the file exists.

## Safety properties

- **Never guesses.** Unverifiable facts become `open_questions` frontmatter
  entries, resolved by the clarify workflow and marked with
  `<!-- clarified: ... -->` sentinels that later updates won't overwrite.
- **Never deletes curation.** Removed code yields `status: deprecated`, not
  deletion; human prose is preserved across updates.
- **Never emits secrets.** Config values are described by shape, never value —
  including from history (`--patch` is opt-in). The validator flags anything
  that slips through (W5).
- **Never touches source code.** All writes stay inside the bundle directory.

## Uninstall

```bash
okf-skill --uninstall     # remove the skill from every agent's skills dir
uv tool uninstall okf-skill
```

Run `okf-skill --list` first to see exactly where the skill is installed.

## License

MIT
