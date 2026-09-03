# skill-share

A collection of portable **Agent Skills** — command-line tools packaged so they
install into Claude Code, Cursor, OpenAI Codex, and any tool that reads the open
`.agents/skills` standard.

Each subfolder is one self-contained skill with its own detailed README. A skill
here is not just a prompt: it is a real CLI you can run yourself, plus a
`SKILL.md` descriptor that teaches an agent when and how to reach for it.

## Available Skills

| Skill | Description |
|-------|-------------|
| [`log_tfidf_reducer`](./log_tfidf_reducer/README.md) | Wrap the native [`logreduce`](https://github.com/alexcpn/log_tfidf_reducer) binary (auto-downloaded per OS) to shrink noisy logs into an LLM-ready summary before reading them — up to ~99.9% fewer tokens while keeping every error and unique event. |
| [`catalogify`](https://github.com/alexcpn/catalogify) *(moved)* | Turn a repository into an [Open Knowledge Format](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md) knowledge catalog: cross-linked markdown concepts for services, modules, APIs, data models and operations, with git history mined for the *why*. **Now its own repo and PyPI package** — `uv tool install catalogify`. |

## Prerequisites

**1. The `uv` Python package manager.** Installation is driven by the popular
[`uv`](https://docs.astral.sh/uv/getting-started/installation/) tool, so it needs
to be installed first:

```bash
# Linux / macOS
curl -LsSf https://astral.sh/uv/install.sh | sh
```

```powershell
# Windows
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**2. An AI agent to drive the skills.** Anything that reads the Agent Skills
format works — [Claude Code](https://claude.com/claude-code), Cursor, the
[Cursor Agent CLI](https://cursor.com/docs/cli/overview), OpenAI Codex CLI.

## Quick Start

1. Open a terminal and `cd` to the folder you want to work in.
2. Install the skill you need (example uses `log_tfidf_reducer`):

```bash
uv tool install --native-tls "git+https://github.com/alexcpn/skill-share.git#subdirectory=log_tfidf_reducer"
logreduce-skill --install
```

3. Restart your agent, then just ask for what you want:

```bash
agent "summarise the errors in build.log"
```

The agent notices the skill matches, loads it, and drives the CLI for you.

## Installing a Skill (uv + Git)

The pattern is always the same: one line installs the CLI as an isolated `uv`
tool, and one line registers the skill into your agents.

```bash
# log_tfidf_reducer — logreduce auto-downloads the right native binary on first use (no Rust/npm)
uv tool install --native-tls "git+https://github.com/alexcpn/skill-share.git#subdirectory=log_tfidf_reducer"
logreduce-skill --install
```

```bash
# catalogify — now a standalone package, no subdirectory fragment needed
uv tool install catalogify
catalogify install
```

The `#subdirectory=` fragment points `uv` at one package folder inside this
repo, so it builds just that skill rather than the whole collection.
`--native-tls` uses the system certificate store, which matters behind
TLS-inspecting proxies.

The installer command (e.g. `logreduce-skill --install`) copies the skill into every
agent's user-global skills directory (`~/.claude/skills`, `~/.cursor/skills`,
`~/.codex/skills`, `~/.agents/skills`). **Restart the agent afterwards** so it
picks up the new skill.

Each skill folder also carries `install.sh` / `install.ps1` bootstrappers that
do both steps, install `uv` if it is missing, and fall back to
`pip install --user`.

## Skill Reference (commands)

Each skill installs as a `uv` tool (the **uv package**) and registers a skill
descriptor into your agents via its **installer command**. The **executables**
are what land on your `PATH`.

| Skill | uv package | Installer command | Executables |
|-------|-----------|-------------------|-------------|
| `log_tfidf_reducer` | `log-tfidf-reducer` | `logreduce-skill` | `logreduce` |
| `catalogify` *(moved)* | `catalogify` | `catalogify install` | `catalogify` |

Every installer command supports `--install`, `--list`, `--uninstall`, plus
`--agents claude,cursor,codex,agents` to target specific agents and
`--scope project` to install into `./.<agent>/skills` instead of your home
directory.

## Reinstall / Update a Skill

To pull the latest version, re-run the install with `--force` (swap in the
subdirectory and commands for the skill you want from the table above):

```bash
uv tool install --native-tls --force "git+https://github.com/alexcpn/skill-share.git#subdirectory=log_tfidf_reducer"
logreduce-skill --install --force
```

`uv tool install --force` replaces the executables; `--install --force`
overwrites the existing skill files in each agent's skills directory. If the CLI
is already installed and you only need the newest published version, you can
also run `uv tool upgrade <uv package>` (e.g. `uv tool upgrade log-tfidf-reducer`).

Restart the agent afterwards so it re-reads the skill.

## Uninstall a Skill

Two steps — remove the skill descriptor from your agents, then remove the CLI
tool and its executables:

```bash
# 1. Remove the skill from every agent's skills directory
logreduce-skill --uninstall

# 2. Remove the CLI tool + executables installed by uv
uv tool uninstall log-tfidf-reducer
```

The other skill follows the same shape:

```bash
logreduce-skill --uninstall; uv tool uninstall log-tfidf-reducer
```

Notes:

- Run `<installer command> --list` first to see exactly where each skill is
  installed (`--uninstall` only removes those files).
- By default these target the user-global scope (`~/.<agent>/skills`). If you
  installed with `--scope project`, pass `--scope project` to `--uninstall` too.
- `uv tool uninstall` only removes the package if it was installed as a `uv`
  tool; if you used `pip install --user`, run `pip uninstall <uv package>`
  instead.

## Adding a skill to this repo

Each skill folder is an ordinary Python package with a consistent shape:

```
<skill_name>/
├── README.md                      # what it does, install, usage
├── SKILL.md                       # browsable copy of the descriptor
├── install.sh / install.ps1       # uv-first bootstrap, pip fallback
├── pyproject.toml                 # console scripts: the tools + <name>-skill
└── src/<package>/
    ├── runner.py                  # the actual CLI
    ├── installer.py               # --install / --list / --uninstall
    └── _skill_assets/SKILL.md     # what gets copied into the agents
```

`SKILL.md` uses the open Agent Skills frontmatter (`name`, `description`), and
the `description` is the only text an agent sees when deciding whether to load
the skill — so it should say both *what it does* and *when to use it*, with the
words a user would actually type.

## License

MIT — see [LICENSE](LICENSE). Each skill also declares MIT in its
`pyproject.toml`.
