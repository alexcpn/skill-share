---
name: log-tfidf-reducer
description: Reduce large/noisy log files to an LLM-ready summary before reading them. Use whenever you are about to read, grep, or paste a large log file (build logs, CI output, kubectl logs, app traces) — run `logreduce <path>` first to cut tokens by up to 99.9% while keeping every error and unique event.
metadata:
  commands:
    - logreduce
---

# logreduce — log reducer for LLMs

`logreduce` ranks log lines by TF-IDF over masked templates blended with
severity weighting, then keeps a representative, chronological subset that fits a
token budget. It typically removes 99%+ of the lines while preserving every
error and every distinct event — so you spend far fewer tokens reading logs.

The `logreduce` command is installed on `PATH` by the `log-tfidf-reducer`
package. The first run auto-downloads the correct binary for this OS.

## When to use

- You are about to read a log file that is more than a few hundred lines.
- You are about to `cat`/`grep`/open CI output, build logs, `kubectl logs`,
  server traces, or any large `*.log` file.
- The user pastes or points at a big log and asks you to investigate/summarize.

If a log is small (a few dozen lines), just read it directly — no need to reduce.

## How to use

**Reduce a file, then read the reduced output instead of the original:**

```bash
logreduce app.log > app.reduced.log     # then read app.reduced.log
logreduce app.log --stats               # also print reduction stats to stderr
logreduce app.log --budget 32000        # bigger budget = more lines kept (default ~8k tokens)
logreduce app.log --context 3           # keep N lines of context around kept lines
```

**Pipe from a command (don't read the raw stream):**

```bash
kubectl logs my-pod | logreduce > incident.log
cat build.log | logreduce --budget 16000 > build.reduced.log
```

```powershell
# PowerShell
kubectl logs my-pod | logreduce > incident.log
Get-Content build.log | logreduce > build.reduced.log
```

Then open the reduced file and reason over that.

## Useful flags

| Flag | Purpose |
|------|---------|
| `--budget <tokens>` | Target token budget (default ~8000). Raise it if you need more detail. |
| `--context <n>` | Keep `n` lines of surrounding context around each selected line. |
| `--stats` | Print reduction stats (lines/tokens before/after) to stderr. |
| `--weights <r,s,b>` | Tune rarity/severity/burst blend (default 0.4,0.5,0.1). |
| `--version` | Print the binary version. |

Run `logreduce --help` to see the full, authoritative flag list for the
installed version.

## Notes

- First invocation downloads the binary (cached afterward). If it is offline or
  behind a proxy and the download fails, set `LOGREDUCE_VERSION=latest`, point
  `LOGREDUCE_BINARY` at a manually installed `logreduce`, or install via
  `cargo install logreduce`.
- Reduction is lossy by design: it keeps errors and unique events but drops
  repetitive noise (annotated with counts like `(×500)`). If you need an exact
  line, grep the original file for that specific string.
