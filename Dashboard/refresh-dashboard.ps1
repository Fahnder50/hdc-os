param(
    [string]$PythonPath = "python"
)

$repositoryRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$contractDirectory = Join-Path $PSScriptRoot "contracts"
$env:PYTHONPATH = "$(Join-Path $repositoryRoot 'Dashboard\src');$(Join-Path $repositoryRoot '30-Procurement\src');$(Join-Path $repositoryRoot '20-Operations\src');$repositoryRoot"
& $PythonPath -m procurement_agent.dashboard_cli $contractDirectory
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
& $PythonPath -m operations_dashboard.cli $repositoryRoot $contractDirectory
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
& $PythonPath -m operations_cockpit.cli $PSScriptRoot
exit $LASTEXITCODE
