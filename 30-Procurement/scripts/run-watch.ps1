$ErrorActionPreference = "Stop"
$procurementRoot = Split-Path -Parent $PSScriptRoot
$venvPython = Join-Path $procurementRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $venvPython)) { throw "Virtual environment not found. Run .\scripts\install.ps1 first." }
& $venvPython -m procurement_watch watch run
exit $LASTEXITCODE
