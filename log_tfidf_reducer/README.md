# log-tfidf-reducer

A tiny, dependency-free **`uv`-installable** wrapper around
[`logreduce`](https://github.com/alexcpn/log_tfidf_reducer) — the Rust log
reducer that shrinks noisy logs to an LLM-ready summary (up to ~99.9% fewer
tokens while keeping every error and unique event).

You install one Python package. It:

1. Exposes a `logreduce` command that **auto-downloads the correct native binary
   for your OS/architecture** (Linux x64, macOS arm64/x64, Windows x64) on first
   use, caches it, and then passes every argument straight through to it.
2. Ships an **Agent Skill** so Claude Code, Cursor, Codex, and other agents run
   `logreduce` before reading large logs.

No Rust, Node, or npm required.

## Commands

- `logreduce <args...>` — pass-through to the native logreduce binary (e.g. `logreduce app.log --stats`).
- `logreduce-skill` — install/list/uninstall the skill across AI agents.

## Install (recommended: uv + Git)

Each developer machine runs one bootstrap. It installs the CLI as an isolated
`uv` tool and registers the skill into every agent.

**Linux / macOS:**

```bash
./install.sh --source "git+https://github.com/alexcpn/skill-share.git#subdirectory=log_tfidf_reducer"
```

**Windows (PowerShell):**

```powershell
./install.ps1 -Source "git+https://github.com/alexcpn/skill-share.git#subdirectory=log_tfidf_reducer"
```

(The `#subdirectory=` part points at this package folder inside the repo, so
`uv` builds just this skill and not the whole collection.)

The bootstrappers prefer `uv` (using `--native-tls` for corporate proxies) and
fall back to `pip install --user`. Omit `-Source`/`--source` to install from a
local checkout instead of Git.

### Without the bootstrap script

```bash
uv tool install --native-tls "git+https://github.com/alexcpn/skill-share.git#subdirectory=log_tfidf_reducer"
logreduce-skill --install        # all agents, user-global
logreduce --version              # downloads the binary on first run
```

## Usage

```bash
logreduce app.log                                      # default ~8k-token budget
logreduce app.log --budget 32000 --context 3 --stats  # larger budget + stats
kubectl logs my-pod | logreduce > incident.log         # pipe from another command
logreduce --help                                       # full flag list (from the binary)
```

## How the OS wrapping works

`logreduce` maps your platform to a published release asset:

| Platform | Asset |
|----------|-------|
| Linux x64 | `logreduce-linux-x64` |
| macOS Apple Silicon | `logreduce-darwin-arm64` |
| macOS Intel | `logreduce-darwin-x64` |
| Windows x64 | `logreduce-win32-x64.exe` |

It downloads the matching binary into a per-user cache and reuses it on later
runs. Then it forwards all args, stdin/stdout/stderr, and the exit code to it.

### Environment variables

| Variable | Purpose |
|----------|---------|
| `LOGREDUCE_VERSION` | Release tag to fetch. Default: pinned `v0.2.2`. Use `latest` to track newest. |
| `LOGREDUCE_BINARY` | Absolute path to an existing `logreduce` binary; skips downloading. |
| `LOGREDUCE_FORCE_DOWNLOAD` | Set to `1` to re-download even if cached (e.g. to upgrade `latest`). |
| `LOGREDUCE_CACHE_DIR` | Override the cache location. |

Cache location (default):

- Windows: `%LOCALAPPDATA%\log_tfidf_reducer\bin\<version>\logreduce.exe`
- Linux/macOS: `~/.cache/log_tfidf_reducer/bin/<version>/logreduce`

## The `logreduce-skill` command

```bash
logreduce-skill --install                       # all agents, user-global (~/.<agent>/skills)
logreduce-skill --install --agents cursor,claude
logreduce-skill --install --scope project       # ./.<agent>/skills in the current repo
logreduce-skill --list                          # show where it is installed
logreduce-skill --uninstall                     # remove it
```

| Agent | User scope | Project scope |
|-------|------------|---------------|
| Claude Code | `~/.claude/skills/` | `.claude/skills/` |
| Cursor | `~/.cursor/skills/` | `.cursor/skills/` |
| OpenAI Codex | `~/.codex/skills/` | (user only) |
| Open standard (Copilot, Gemini CLI, Goose, …) | `~/.agents/skills/` | `.agents/skills/` |

Restart the agent after installing so it picks up the new skill.

## Development install

```bash
pip install -e .
logreduce --version
```

## Credits

The actual log reduction is done by
[alexcpn/log_tfidf_reducer](https://github.com/alexcpn/log_tfidf_reducer). This
package only wraps and distributes it.
