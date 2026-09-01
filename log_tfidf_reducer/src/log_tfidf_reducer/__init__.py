"""uv-installable wrapper around the `logreduce` binary (alexcpn/log_tfidf_reducer).

Picks the right release binary for the current OS/architecture, downloads and
caches it on first use, then passes every argument through to it. Also ships an
Agent Skill so Claude Code / Cursor / Codex run `logreduce` before reading big logs.
"""

__version__ = "0.1.0"
