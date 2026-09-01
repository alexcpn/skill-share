"""`logreduce` command: resolve, cache, and run the right platform binary.

Resolution order for the binary:
  1. $LOGREDUCE_BINARY                 -- explicit path to an existing binary.
  2. cached download in the cache dir  -- reused across runs.
  3. download from the GitHub release  -- matching this OS/arch, then cached.

Everything after resolution is a pure pass-through: all CLI args, stdin, stdout,
stderr, and the exit code are forwarded to the real binary unchanged.

Environment variables:
  LOGREDUCE_BINARY         Use this binary instead of downloading.
  LOGREDUCE_VERSION        Release tag to fetch (default: pinned; "latest" tracks newest).
  LOGREDUCE_FORCE_DOWNLOAD Re-download even if a cached binary exists.
  LOGREDUCE_CACHE_DIR      Override where the binary is cached.
"""
import os
import stat
import subprocess
import sys
import tempfile
import urllib.request
from pathlib import Path

from ._platform import (
    DEFAULT_VERSION,
    UnsupportedPlatform,
    asset_name,
    download_url,
    local_binary_name,
)


def _cache_dir(version: str) -> Path:
    override = os.environ.get("LOGREDUCE_CACHE_DIR")
    if override:
        base = Path(override).expanduser()
    elif sys.platform == "win32":
        root = os.environ.get("LOCALAPPDATA") or (Path.home() / "AppData" / "Local")
        base = Path(root) / "log_tfidf_reducer"
    else:
        root = os.environ.get("XDG_CACHE_HOME") or (Path.home() / ".cache")
        base = Path(root) / "log_tfidf_reducer"
    return base / "bin" / version


def _make_executable(path: Path) -> None:
    if sys.platform == "win32":
        return
    mode = path.stat().st_mode
    path.chmod(mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


def _download(url: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    print(f"logreduce: downloading binary from {url}", file=sys.stderr)
    req = urllib.request.Request(url, headers={"User-Agent": "log-tfidf-reducer"})
    # Download to a temp file in the same dir, then atomically move into place.
    fd, tmp_name = tempfile.mkstemp(dir=str(dest.parent), suffix=".part")
    tmp = Path(tmp_name)
    try:
        with urllib.request.urlopen(req) as resp, os.fdopen(fd, "wb") as out:
            while True:
                chunk = resp.read(65536)
                if not chunk:
                    break
                out.write(chunk)
        tmp.replace(dest)
    except BaseException:
        tmp.unlink(missing_ok=True)
        raise
    _make_executable(dest)
    print(f"logreduce: cached at {dest}", file=sys.stderr)


def resolve_binary() -> Path:
    """Return a path to a runnable logreduce binary, downloading it if needed."""
    explicit = os.environ.get("LOGREDUCE_BINARY")
    if explicit:
        path = Path(explicit).expanduser()
        if not path.is_file():
            raise SystemExit(f"LOGREDUCE_BINARY does not point to a file: {path}")
        return path

    version = os.environ.get("LOGREDUCE_VERSION", DEFAULT_VERSION).strip() or DEFAULT_VERSION
    binary = _cache_dir(version) / local_binary_name()

    force = os.environ.get("LOGREDUCE_FORCE_DOWNLOAD", "").strip() not in ("", "0", "false", "False")
    if binary.is_file() and not force:
        return binary

    asset = asset_name()
    url = download_url(version, asset)
    try:
        _download(url, binary)
    except UnsupportedPlatform:
        raise
    except Exception as exc:  # noqa: BLE001 - surface a clear, actionable message
        raise SystemExit(
            f"logreduce: failed to download binary from {url}\n  {exc}\n"
            "Hints: check network/proxy, set LOGREDUCE_VERSION=latest, or point "
            "LOGREDUCE_BINARY at a logreduce you installed manually."
        )
    return binary


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    try:
        binary = resolve_binary()
    except UnsupportedPlatform as exc:
        print(f"logreduce: {exc}", file=sys.stderr)
        return 2

    try:
        completed = subprocess.run([str(binary), *args])
    except KeyboardInterrupt:
        return 130
    except OSError as exc:
        print(f"logreduce: could not execute {binary}: {exc}", file=sys.stderr)
        return 126
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
