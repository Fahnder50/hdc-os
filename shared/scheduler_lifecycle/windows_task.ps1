param(
    [Parameter(Mandatory = $true)][ValidateSet("Apply", "Export", "Remove")][string]$Operation,
    [Parameter(Mandatory = $true)][string]$Definition
)

$json = [Text.Encoding]::UTF8.GetString([Convert]::FromBase64String($Definition))
$item = $json | ConvertFrom-Json
if ($Operation -eq "Export") {
    $task = Get-ScheduledTask -TaskName $item.name -ErrorAction SilentlyContinue
    if ($null -eq $task) { exit 3 }
    Export-ScheduledTask -TaskName $item.name
    exit 0
}
if ($Operation -eq "Remove") {
    if (Get-ScheduledTask -TaskName $item.name -ErrorAction SilentlyContinue) {
        Unregister-ScheduledTask -TaskName $item.name -Confirm:$false
    }
    exit 0
}
$action = New-ScheduledTaskAction -Execute $item.runtime.command -Argument $item.runtime.arguments
$at = [datetime]::ParseExact($item.schedule.at, "HH:mm", [Globalization.CultureInfo]::InvariantCulture)
$trigger = New-ScheduledTaskTrigger -Daily -At $at
$settingsParameters = @{
    StartWhenAvailable = [bool]$item.schedule.start_when_available
    WakeToRun = [bool]$item.schedule.wake_to_run
    AllowStartIfOnBatteries = [bool]$item.runtime.allow_start_on_batteries
    DontStopIfGoingOnBatteries = -not [bool]$item.runtime.stop_on_batteries
}
$settings = New-ScheduledTaskSettingsSet @settingsParameters
$principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive -RunLevel Limited
Register-ScheduledTask -TaskName $item.name -Action $action -Trigger $trigger -Settings $settings -Principal $principal -Force | Out-Null
if (-not $item.runtime.enabled) { Disable-ScheduledTask -TaskName $item.name | Out-Null }
