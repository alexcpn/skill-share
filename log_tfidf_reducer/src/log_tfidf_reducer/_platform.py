"""Map the current OS/architecture to a logreduce release asset.

Release assets (https://github.com/alexcpn/log_tfidf_reducer/releases):

    Linux x64             logreduce-linux-x64
    macOS Apple Silicon   logreduce-darwin-arm64
    macOS Intel           logreduce-darwin-x64
    Windows x64           logreduce-win32-x64.exe
"""
import platform
import sys

REPO = "alexcpn/log_tfidf_reducer"

# Pin a known-good release by default; set LOGREDUCE_VERSION=latest to track the
# newest release, or LOGREDUCE_VERSION=vX.Y.Z to pin a specific one.
DEFAULT_VERSION = "v0.2.2"


class UnsupportedPlatform(RuntimeError):
    pass


def _arch() -> str:
    machine = platform.machine().lower()
    if machine in ("x86_64", "amd64", "x64"):
        return "x64"
    if machine in ("arm64", "aarch64"):
        return "arm64"
    return machine


def asset_name() -> str:
    """Release asset filename for the current platform."""
    system = sys.platform
    arch = _arch()

    if system == "win32":
        # Only an x64 Windows build is published; it runs fine under x64 emulation.
        return "logreduce-win32-x64.exe"
    if system == "darwin":
        if arch == "arm64":
            return "logreduce-darwin-arm64"
        return "logreduce-darwin-x64"
    if system.startswith("linux"):
        if arch != "x64":
            raise UnsupportedPlatform(
                f"No published logreduce binary for Linux/{arch}. "
                "Build from source with `cargo install logreduce`."
            )
        return "logreduce-linux-x64"

    raise UnsupportedPlatform(
        f"Unsupported platform: {system}/{arch}. "
        "Build from source with `cargo install logreduce`."
    )


def local_binary_name() -> str:
    """Filename to use for the cached binary on this OS."""
    return "logreduce.exe" if sys.platform == "win32" else "logreduce"


def download_url(version: str, asset: str) -> str:
    base = f"https://github.com/{REPO}/releases"
    if version == "latest":
        return f"{base}/latest/download/{asset}"
    return f"{base}/download/{version}/{asset}"
