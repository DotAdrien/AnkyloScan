$ScriptContent = @'
$ServerIP = 'SERVER_IP_PLACEHOLDER'
$Token = 'TOKEN_PLACEHOLDER'
$Url = "http://$($ServerIP):8001/logs/ingest"

# Helper function to extract data from a Windows event XML
function Get-EventValue($EventData, $Name) {
    return ($EventData | Where-Object Name -eq $Name).'#text'
}

$StateFile = 'C:\AnkyloAgent_LastRecord.txt'
$LastId = 0
if (Test-Path $StateFile) { $LastId = [long](Get-Content $StateFile) }

$EventIDs = @(4720, 4728, 4732, 4756, 1102, 4719, 5136)

$Events = Get-WinEvent -FilterHashtable @{LogName='Security'; Id=$EventIDs; StartTime=(Get-Date).AddMinutes(-5)} -ErrorAction SilentlyContinue | 
          Where-Object RecordId -gt $LastId | 
          Sort-Object RecordId

$MaxId = $LastId
$SeenEvents = @{}

foreach ($Event in $Events) {
    $Id = $Event.Id
    $Xml = [xml]$Event.ToXml()
    $EventData = $Xml.Event.EventData.Data
    
    $TargetUserName = Get-EventValue $EventData "TargetUserName"
    $SubjectUserName = Get-EventValue $EventData "SubjectUserName"

    # Ignore machine accounts ending with $
    if ($TargetUserName -like "*$") { 
        $MaxId = [math]::Max($MaxId, $Event.RecordId)
        continue 
    }

    $DedupKey = "$Id-$TargetUserName"
    
    if ($SeenEvents.ContainsKey($DedupKey)) { 
        $MaxId = [math]::Max($MaxId, $Event.RecordId)
        continue 
    }
    $SeenEvents[$DedupKey] = $true
    
    $DetailedMsg = switch ($Id) {
        4720 { "Target=$TargetUserName, Actor=$SubjectUserName" }
        4728 { "Group=$TargetUserName, Member=$(Get-EventValue $EventData 'MemberName'), Actor=$SubjectUserName" }
        4732 { "Group=$TargetUserName, Member=$(Get-EventValue $EventData 'MemberName'), Actor=$SubjectUserName" }
        4756 { "Group=$TargetUserName, Member=$(Get-EventValue $EventData 'MemberName'), Actor=$SubjectUserName" }
        1102 { "Actor=$SubjectUserName" }
        4719 { "Actor=$SubjectUserName" }
        5136 { "Object=$(Get-EventValue $EventData 'ObjectDN'), Actor=$SubjectUserName" }
        Default { "ID=$Id" }
    }

    $Body = @{
        token = $Token
        event_id = $Id
        source = 'Agent-AD'
        message = $DetailedMsg
    } | ConvertTo-Json -Compress

    try {
        Invoke-RestMethod -Uri $Url -Method Post -Body $Body -ContentType 'application/json; charset=utf-8' -ErrorAction Stop
    } catch { }

    $MaxId = [math]::Max($MaxId, $Event.RecordId)
}

if ($MaxId -gt $LastId) { $MaxId | Set-Content -Path $StateFile }
'@

# Installation
Set-Content -Path "C:\AnkyloAgent.ps1" -Value $ScriptContent -Encoding UTF8

Write-Host "Enabling Windows audit policies... 🛡️" -ForegroundColor Cyan

# Enable audit for Account Management (User creation, group addition...)
auditpol /set /category:"{6997984E-797A-11D9-BED3-505054503030}" /success:enable /failure:enable | Out-Null
# Enable audit for Policy Change
auditpol /set /category:"{6997984D-797A-11D9-BED3-505054503030}" /success:enable /failure:enable | Out-Null
# Enable audit for System (Audit logs cleared...)
auditpol /set /category:"{69979848-797A-11D9-BED3-505054503030}" /success:enable /failure:enable | Out-Null

Write-Host "All set! Windows logs are now configured. ✅" -ForegroundColor Green

$Action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-WindowStyle Hidden -ExecutionPolicy Bypass -File C:\AnkyloAgent.ps1"
$Trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Minutes 1)
$Principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount -RunLevel Highest

Register-ScheduledTask -TaskName "AnkyloLogAgent" -Action $Action -Trigger $Trigger -Principal $Principal -Force
