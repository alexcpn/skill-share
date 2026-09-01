<#
.SYNOPSIS
  Org installer (Windows): install the log-tfidf-reducer wrapper (`logreduce`)
  and register its skill into all AI agents (Claude Code, Cursor, Codex, .agents).

.DESCRIPTION
  Uses `uv` (preferred) to install the package as an isolated tool, then runs
  `logreduce-skill --install` to drop SKILL.md into each agent's skills dir.

  The `logreduce` command auto-downloads the correct binary for this OS on first
  use, so nothing else is needed.

  -Source controls where the package comes from. For org rollout, pass the Git
  URL of the repo (the package lives in the `log_tfidf_reducer` subdirectory):

    ./install.ps1 -Source "git+https://github.com/alexcpn/skill-share.git#subdirectory=log_tfidf_reducer"

  With no -Source, it installs from this local folder (handy for testing).

.PARAMETER Source
  pip/uv install source. Default: this script's folder.

.PARAMETER Agents
  Comma-separated agents or 'all'. Default: all.

.PARAMETER Scope
  'user' (default, ~/.<agent>/skills) or 'project' (./.<agent>/skills).

.EXAMPLE
  ./install.ps1

.EXAMPLE
  ./install.ps1 -Source "git+https://github.com/alexcpn/skill-share.git#subdirectory=log_tfidf_reducer"
#>
[CmdletBinding()]
param(
    [string]$Source = "",
    [string]$Agents = "all",
    [ValidateSet("user", "project")]
    [string]$Scope = "user"
)

$ErrorActionPreference = "Stop"
if (-not $Source) { $Source = $PSScriptRoot }

function Test-Command($name) {
    return [bool](Get-Command $name -ErrorAction SilentlyContinue)
}

Write-Host "Installing log-tfidf-reducer from: $Source"

if (Test-Command "uv") {
    # --native-tls uses the system cert store (needed behind TLS-inspecting proxies).
    uv tool install --native-tls --force "$Source"
    uv tool update-shell 2>$null
}
elseif (Test-Command "pip") {
    Write-Host "uv not found; falling back to pip install --user..."
    pip install --user --upgrade "$Source"
}
elseif (Test-Command "python") {
    python -m pip install --user --upgrade "$Source"
}
else {
    throw "Neither uv, pip, nor python found on PATH. Install uv (https://astral.sh/uv) or Python first."
}

$skillArgs = @("--install", "--agents", $Agents, "--scope", $Scope)

Write-Host "Registering the skill with agents: $Agents (scope=$Scope)..."
if (Test-Command "logreduce-skill") {
    & logreduce-skill @skillArgs
}
else {
    Write-Host "(logreduce-skill not on PATH yet; invoking via python module)"
    python -m log_tfidf_reducer.installer @skillArgs
}

Write-Host ""
Write-Host "Done. Open a new terminal so PATH refreshes, then run: logreduce --version"
