param(
    [Parameter(Mandatory = $true)]
    [string]$PythonPath
)

$repositoryRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
$env:PYTHONPATH = "$(Join-Path $repositoryRoot 'Dashboard\src');$(Join-Path $repositoryRoot '30-Procurement\src');$(Join-Path $repositoryRoot '20-Operations\src');$repositoryRoot"
$externalRuntime = Join-Path $env:LOCALAPPDATA "HDC-OS\agent-runtime\procurement"
New-Item -ItemType Directory -Path $externalRuntime -Force | Out-Null
$env:HDC_AGENT_RUNTIME = $externalRuntime
$executionLog = Join-Path $externalRuntime "scheduled-execution.log"
& $PythonPath -m procurement_agent.cli scheduled *>> $executionLog
exit $LASTEXITCODE
