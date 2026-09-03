"""Turn a source-code repository into an Open Knowledge Format (OKF v0.1)
knowledge bundle.

Ships three commands — `okf-inventory`, `okf-history`, `okf-validate` — plus an
Agent Skill so Claude Code / Cursor / Codex can generate, incrementally update,
clarify, and validate a bundle of cross-linked markdown concepts describing a
repo's services, modules, APIs, data models, and operations.

OKF spec: https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md
"""

__version__ = "0.5.0"
