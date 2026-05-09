param(
  [string]$CodexHome = "$env:USERPROFILE\.codex"
)

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent $PSScriptRoot
$Source = Join-Path $RepoRoot "pets\red-spark"
$Destination = Join-Path $CodexHome "pets\red-spark"

if (!(Test-Path $Source)) {
  throw "Pet package not found: $Source. Run scripts\build.ps1 first."
}

New-Item -ItemType Directory -Force -Path (Split-Path -Parent $Destination) | Out-Null
Copy-Item -Recurse -Force -LiteralPath $Source -Destination $Destination
Write-Host "Installed Red Spark to $Destination"
