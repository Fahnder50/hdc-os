$ErrorActionPreference = "Stop"
param([Parameter(Mandatory = $true)][string]$Source, [switch]$Overwrite)
$procurementRoot = Split-Path -Parent $PSScriptRoot
$venvPython = Join-Path $procurementRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $venvPython)) { throw "Virtual environment not found. Run .\scripts\install.ps1 first." }
$arguments = @("-m", "procurement_watch", "restore", $Source)
if ($Overwrite) { $arguments += "--overwrite" }
& $venvPython @arguments
exit $LASTEXITCODE
