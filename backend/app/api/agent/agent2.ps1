$ScriptContent = @'
$ServerIP = 'SERVER_IP_PLACEHOLDER'
$Token = 'TOKEN_PLACEHOLDER'
$Url = "http://$($ServerIP):8001/logs/ingest"

# Helper function to extract data from a Windows event XML
function Get-EventValue($EventData, $Name) {
    return ($EventData | Where-Object Name -eq $Name).'#text'
}

$StateFile = 'C:\ProgramData\AnkyloScan\AnkyloAgent_LastProcessEvent.txt' # Separate state file for this agent
$LastId = 0
if (Test-Path $StateFile) { $LastId = [long](Get-Content $StateFile) }

$EventIDs = @(4688) # Event ID for process creation

# Retrieves events since the last run, or the last 5 minutes if the state file is new
$Events = Get-WinEvent -FilterHashtable @{LogName='Security'; Id=$EventIDs; StartTime=(Get-Date).AddMinutes(-5)} -ErrorAction SilentlyContinue |
          Where-Object RecordId -gt $LastId |
          Sort-Object RecordId

$MaxId = $LastId

foreach ($Event in $Events) {
    $Id = $Event.Id
    $Xml = [xml]$Event.ToXml()
    $EventData = $Xml.Event.EventData.Data

    $NewProcessName = Get-EventValue $EventData "NewProcessName"
    $CommandLine = Get-EventValue $EventData "CommandLine"
    $SubjectUserName = Get-EventValue $EventData "SubjectUserName"
    $SubjectDomainName = Get-EventValue $EventData "SubjectDomainName"

    # Security: ignore the event if there is no process name
    if (-not $NewProcessName) { continue }

    # Extracts just the executable name
    $ProcessExecutable = Split-Path -Path $NewProcessName -Leaf

    # Detection of abnormal behaviors (what a standard user should not do)
    $SuspiciousProcesses = "(?i)^(vssadmin\.exe|certutil\.exe|bitsadmin\.exe|whoami\.exe|nltest\.exe|net\.exe|net1\.exe|wmic\.exe|reg\.exe|schtasks\.exe|sc\.exe|taskkill\.exe|ipconfig\.exe|ping\.exe|tracert\.exe|arp\.exe|route\.exe|ftp\.exe|tftp\.exe|mshta\.exe|cscript\.exe|wscript\.exe|rundll32\.exe|regsvr32\.exe|mmc\.exe|control\.exe)$"
    $SuspiciousCommands = "(?i)(-enc|-encodedcommand|iex|invoke-expression|downloadstring|bypass|hidden|net user|net localgroup|vssadmin|certutil|schtasks|reg add|reg delete|runas)"

    $IsSuspiciousProcess = $ProcessExecutable -match $SuspiciousProcesses
    $IsSuspiciousCommand = $CommandLine -match $SuspiciousCommands
    $IsShell = $ProcessExecutable -match "(?i)^(cmd\.exe|powershell\.exe|pwsh\.exe|powershell_ise\.exe|wsl\.exe|bash\.exe|wt\.exe)$"

    # Filter: we keep it if it's a shell OR if it's an abnormal/suspicious action
    if (-not ($IsSuspiciousProcess -or $IsSuspiciousCommand -or $IsShell)) {
        $MaxId = [math]::Max($MaxId, $Event.RecordId)
        continue
    }

    # Construct a pure key-value message (Language agnostic)
    $DetailedMsg = "Actor=$SubjectDomainName\$SubjectUserName, Process=$ProcessExecutable, CommandLine=$CommandLine"

    $Body = @{
        token = $Token
        event_id = $Id
        source = 'Agent-ProcessMonitor-Win'
        message = $DetailedMsg
    } | ConvertTo-Json -Compress

    try {
        Invoke-RestMethod -Uri $Url -Method Post -Body $Body -ContentType 'application/json; charset=utf-8' -ErrorAction Stop
    } catch {
        # Silent if the server is unreachable or other sending error
    }

    $MaxId = [math]::Max($MaxId, $Event.RecordId)
}
if ($MaxId -gt $LastId) { $MaxId | Set-Content -Path $StateFile }

'@

# 1. Create the permanent script file
$DestPath = "C:\ProgramData\AnkyloScan"
if (-not (Test-Path $DestPath)) { New-Item -Path $DestPath -ItemType Directory | Out-Null }
Set-Content -Path "$DestPath\AnkyloLoginWorker.ps1" -Value $ScriptContent -Encoding UTF8

# 2. Configure the scheduled task at Login 🔓
$TaskName = "AnkyloProcessMonitor" # Task name changed for clarity

# Delete the old task if it exists
Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false -ErrorAction SilentlyContinue

$Action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-WindowStyle Hidden -ExecutionPolicy Bypass -File $DestPath\AnkyloLoginWorker.ps1"

# Trigger 1: At the moment a user logs on (Logon)
$TriggerLogon = New-ScheduledTaskTrigger -AtLogOn
# Trigger 2: Repeat every 5 minutes for continuous monitoring
$TriggerRepeat = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Minutes 5)

# Execution with the highest privileges (SYSTEM account) to read security logs
$Principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount -RunLevel Highest

Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger @($TriggerLogon, $TriggerRepeat) -Principal $Principal -Force

# --- Enable Security Audits (Local GPO equivalent) ---
Write-Host "Enabling Windows audit policies for process creation... 🛡️" -ForegroundColor Cyan
auditpol /set /subcategory:"{0CCE922B-69AE-11D9-BED3-505054503030}" /success:enable /failure:enable | Out-Null

# IMPORTANT: Enable command line logging for process creation events (Event 4688)
$RegPath = "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System\Audit"
if (-not (Test-Path $RegPath)) { New-Item -Path $RegPath -Force | Out-Null }
Set-ItemProperty -Path $RegPath -Name "ProcessCreationIncludeCmdLine_Enabled" -Value 1 -Type DWord -Force | Out-Null

Write-Host "Process creation auditing enabled. ✅" -ForegroundColor Green

Write-Host "Process monitoring agent installed successfully! It will continuously monitor cmd/powershell commands. 🚀" -ForegroundColor Green
