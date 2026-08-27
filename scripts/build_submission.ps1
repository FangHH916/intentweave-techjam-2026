$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot
$submissionRoot = Join-Path $projectRoot "submission"
$sourceRoot = Join-Path $submissionRoot "src\intentweave"

New-Item -ItemType Directory -Force -Path $sourceRoot | Out-Null
Copy-Item -LiteralPath (Join-Path $projectRoot "intentweave\__init__.py") -Destination $sourceRoot -Force
Copy-Item -LiteralPath (Join-Path $projectRoot "intentweave\agent.py") -Destination $sourceRoot -Force
Copy-Item -LiteralPath (Join-Path $projectRoot "intentweave\state.py") -Destination $sourceRoot -Force
Copy-Item -LiteralPath (Join-Path $projectRoot "intentweave\retrieval.py") -Destination $sourceRoot -Force
Copy-Item -LiteralPath (Join-Path $projectRoot "requirements.txt") -Destination $submissionRoot -Force
Copy-Item -LiteralPath (Join-Path $projectRoot "docs\METHOD_REPORT.md") -Destination (Join-Path $submissionRoot "METHOD_REPORT.md") -Force
Copy-Item -LiteralPath (Join-Path $projectRoot "docs\ARCHITECTURE.md") -Destination (Join-Path $submissionRoot "ARCHITECTURE.md") -Force
Copy-Item -LiteralPath (Join-Path $projectRoot "docs\RESULTS.md") -Destination (Join-Path $submissionRoot "RESULTS.md") -Force

Write-Host "Standalone submission built at $submissionRoot"
