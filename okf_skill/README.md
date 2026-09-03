# okf_skill

Turn a repository into a knowledge base your AI agent can actually afford to read.

`okf_skill` generates an [Open Knowledge Format (OKF v0.1)](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md)
bundle: a directory of cross-linked markdown concepts with YAML frontmatter,
describing a codebase's services, modules, APIs, data models and operations.
It mines git history for the reasoning behind the code, and parks what it
cannot establish as an open question instead of inventing an answer.

Packaged as a portable **Agent Skill**, so it installs into Claude Code,
Cursor, OpenAI Codex, and anything else that reads the open `.agents/skills`
standard.

## What a concept looks like

```markdown
---
type: Module
title: Container Manager (cm)
description: Owns cgroup hierarchy, CPU/memory/device allocation, and the
  on-disk checkpoints that let those allocations survive a kubelet restart.
tags: [cgroups, cpumanager, checkpoint, qos]
source_files: [pkg/kubelet/cm]
open_questions:
  - "After the V2→V3 migration fix was reverted, is the V3→V2 hybrid-state
     hazard still live, or was it addressed another way?"
---

# Gotchas

Checkpoint format changes are the highest-risk edit in this module, and the
hazard is the fallback path. When a V3 checkpoint has an invalid checksum,
restore falls back to V2, but the V3 fields already read stay in the struct,
producing a hybrid of V2 and V3 data (`83f1cae9656`, reverted by
`76100602564`).
```

`source_files` maps the concept back to code, which is what makes incremental
updates possible. `open_questions` is where uncertainty goes instead of into
prose. Both are producer extension fields permitted by OKF §4.1.

## Why it is small

Measured on `pkg/kubelet` from `kubernetes/kubernetes` (108,648 lines of Go,
450 non-test files), against a structural code graph built by
[Graphify](https://github.com/Graphify-Labs/graphify) over the same directory:

| Artifact | Size | Tokens |
| --- | ---: | ---: |
| Graphify `graph.json` | 14.5 MB | 3,813,486 |
| Graphify `wiki/` (446 articles) | 1,004 KB | 256,968 |
| OKF bundle (9 concepts) | 21.9 KB | 5,596 |
| **OKF service entry** | **2.6 KB** | **676** |

The two tools answer different questions. A structural graph is the right tool
for *reaching* ("what breaks if I change this function") and will beat prose
every time. This skill targets *routing* ("which of our 90 services does this
spec touch"), where you need a little about everything rather than everything
about a little.

At 676 tokens per service, a 90-service catalog is about **61,000 tokens** and
fits in one call alongside the specification. Reproduce the numbers with the
script in [Benchmark](#benchmark) below.

## The four workflows

Ask in plain language and the skill picks one:

| Workflow | What it does |
| -------- | ------------ |
| **generate** | Inventory scan, git-history mining, concept plan, concept documents, `index.md` files, `log.md`, validation. |
| **update** | Diffs since the last logged commit; refreshes only stale concepts, deprecates orphans, adds new ones, preserves human curation. |
| **clarify** | Asks you about the `open_questions` the other workflows parked, then folds the answers in as cited, curation-protected knowledge. |
| **validate** | OKF §9 conformance check plus a quality spot-check. |

## Commands

Three deterministic tools land on your `PATH`, usable with or without an agent:

- `okf-inventory [out.json] [--config <cfg>]` — repo inventory as JSON: file tree, languages, entry points, dependency manifests, API definitions, schemas, CI/CD, docs, ADRs, plus git churn and recent commits. On the full Kubernetes tree (500k lines, 25,917 files) this takes 2.1 seconds and writes 56 KB.
- `okf-history <path>... [--limit N] [--json] [--patch]` — bounded per-path history: creation commit, commit count, recent subjects, and revert/hotfix/risk-flagged commits. Diff-free by default so historical secrets do not leak.
- `okf-validate <bundle_dir> [--config <cfg>] [--json]` — OKF §9 conformance (4 error classes, 9 warning classes).
- `okf-skill` — install/list/uninstall the skill across AI agents.

## Requirements

- **Python 3.9+**
- **`git`** — the inventory and history tools are git-driven. They degrade cleanly on a non-git directory, but the reasoning comes from history.
- **`bash`** — present on Linux and macOS; on Windows the wrapper locates the `bash.exe` that ships with [Git for Windows](https://git-scm.com/download/win).

## Install

```bash
uv tool install --native-tls \
  "git+https://github.com/alexcpn/skill-share.git#subdirectory=okf_skill"
okf-skill --install
```

Restart your agent afterwards so it picks up the skill. The bundled
`install.sh` / `install.ps1` scripts do both steps, install `uv` if it is
missing, and fall back to `pip install --user`.

`okf-skill --install` copies the skill into every agent's user-global skills
directory (`~/.claude/skills`, `~/.cursor/skills`, `~/.codex/skills`,
`~/.agents/skills`). Use `--agents claude,cursor` to target specific ones and
`--scope project` to install into `./.<agent>/skills` instead.

## Usage

```bash
agent "generate an OKF knowledge bundle for this repo"
agent "refresh the knowledge bundle, the code has moved on"
agent "resolve the open questions in the knowledge bundle"
agent "validate the OKF bundle"
```

Output lands in `knowledge/` (configurable), ready to commit next to the code:

```
knowledge/
├── index.md            # okf_version: "0.1" + directory of everything
├── log.md              # dated history, each block records a commit SHA
├── architecture/
│   └── overview.md     # type: Reference — the "start here" concept
├── services/…          # type: Service
├── modules/…           # type: Module
├── apis/…              # type: API Endpoint / API Resource
├── data/…              # type: Data Model / Database Table
└── operations/…        # type: Pipeline / Configuration / Playbook
```

On a monorepo, start with `granularity: coarse` and raise
`OKF_INVENTORY_CAP` above its default of 150.

## Configuration

Everything works with no config. To change the bundle directory, resource URI
base, excludes, type mappings, layout, granularity, or the clarify question
budget, copy the annotated template into your repo root:

```bash
cp ~/.claude/skills/okf-knowledge-bundle/okf-config.template.yml .okf-config.yml
```

`okf-inventory --config .okf-config.yml` and `okf-validate <dir> --config
.okf-config.yml` honor its `exclude` list; the agent passes it through
automatically once the file exists.

## Safety properties

- **Never guesses.** Unverifiable facts become `open_questions`, resolved by the clarify workflow and marked with `<!-- clarified: ... -->` sentinels that later updates will not overwrite. Your answer outranks the machine's inference permanently.
- **Never deletes curation.** Removed code marks a concept `status: deprecated` rather than deleting it. Human prose survives every refresh.
- **Never emits secrets.** Config values are described by shape, never value, including from history (`--patch` is opt-in). The validator flags anything that slips through (W5).
- **Never touches source code.** All writes stay inside the bundle directory.

## Benchmark

To reproduce the table above:

```bash
git clone --filter=blob:none --no-tags \
  https://github.com/kubernetes/kubernetes.git k8s

# structural graph
pip install graphifyy
graphify update k8s/pkg/kubelet
cd k8s/pkg/kubelet && graphify export wiki
wc -c graphify-out/graph.json          # 15,253,944
cat graphify-out/wiki/*.md | wc -c     # 1,027,874

# OKF bundle
cd ../..                               # back to the k8s repo root
okf-inventory                          # 2.1s, 56 KB of JSON
okf-history pkg/kubelet/cm --limit 3   # the reverts behind one subsystem

# then ask your agent to generate the bundle, and check it:
okf-validate knowledge/
```

Token counts are bytes ÷ 4. Measured against `kubernetes/kubernetes` at
commit `d5ccf7968e5`. Graphify was run AST-only (no API key), so its wiki
lacks LLM community labels.

## Uninstall

```bash
okf-skill --uninstall            # remove from every agent's skills dir
uv tool uninstall okf-skill
```

Run `okf-skill --list` first to see where it is installed.

## License

MIT
