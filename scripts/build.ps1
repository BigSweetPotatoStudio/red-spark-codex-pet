param(
  [string]$Python = "python"
)

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent $PSScriptRoot
& $Python "$RepoRoot\scripts\build.py"
