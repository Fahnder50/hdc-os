$ErrorActionPreference = "Stop"
$procurementRoot = Split-Path -Parent $PSScriptRoot
$pythonCommand = Get-Command python -ErrorAction SilentlyContinue
if (-not $pythonCommand) { throw "Python 3.12 is required but was not found." }
python --version
python -m venv (Join-Path $procurementRoot ".venv")
$venvPython = Join-Path $procurementRoot ".venv\Scripts\python.exe"
& $venvPython -m pip install --upgrade pip
& $venvPython -m pip install -e "${procurementRoot}[test]"
