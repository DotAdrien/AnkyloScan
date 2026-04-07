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

# Added 4624 (Successful logon) to monitor admins
$EventIDs = @(4624, 4625, 4768, 4720, 4728, 4732, 4756, 1102, 4719, 5136)

$Events = Get-WinEvent -FilterHashtable @{LogName='Security'; Id=$EventIDs; StartTime=(Get-Date).AddMinutes(-5)} -ErrorAction SilentlyContinue | 
          Where-Object RecordId -gt $LastId | 
          Sort-Object RecordId

$MaxId = $LastId
$SeenEvents = @{} # For smart deduplication in the current loop

foreach ($Event in $Events) {
    # Parse the XML to extract key information cleanly ✨
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

    # Ignore successful Kerberos TGTs (too noisy)
    $ResultCode = Get-EventValue $EventData "ResultCode"
    $Status = Get-EventValue $EventData "Status"
    if ($Event.Id -eq 4768 -and $Status -eq "0x0") {
        $MaxId = [math]::Max($MaxId, $Event.RecordId)
        continue 
    }

    # --- SMART DEDUPLICATION AND FILTERING LOGIC ---
    # Unique key to avoid spam (e.g., "Kerberos-Administrator" will only appear once per scan)
    $DedupKey = "$Id-$TargetUserName"
    if ($Id -eq 4768) { $DedupKey = "KerberosFail-$TargetUserName" } 
    
    if ($SeenEvents.ContainsKey($DedupKey)) { 
        $MaxId = [math]::Max($MaxId, $Event.RecordId)
        continue 
    }
    $SeenEvents[$DedupKey] = $true

    # Get LogonType for connection events
    $LogonType = Get-EventValue $EventData "LogonType"

    # ADMIN FILTER FOR SUCCESSFUL LOGONS (4624)
    if ($Id -eq 4624) {
        # Modify this condition based on your conventions (e.g., adm_*, admin, root)
        if ($TargetUserName -notmatch "(?i)admin|root") { 
            $MaxId = [math]::Max($MaxId, $Event.RecordId)
            continue 
        }
    }
    
    # Construct a pure key-value message (Language agnostic) 📜
    $DetailedMsg = switch ($Id) {
        4624 { "User=$TargetUserName, IP=$(Get-EventValue $EventData 'IpAddress'), LogonType=$LogonType" }
        4625 { "User=$TargetUserName, IP=$(Get-EventValue $EventData 'IpAddress'), LogonType=$LogonType" }
        4768 { "User=$TargetUserName, IP=$(Get-EventValue $EventData 'ClientAddr'), Status=$Status" }
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

# --- Enable Security Audits (Local GPO equivalent) ---
Write-Host "Enabling Windows audit policies... 🛡️" -ForegroundColor Cyan

# Enable audit for Account Logon (Kerberos, NTLM) using GUID to avoid localization issues
auditpol /set /category:"{69979850-797A-11D9-BED3-505054503030}" /success:enable /failure:enable | Out-Null
# Enable audit for Logon/Logoff
auditpol /set /category:"{69979849-797A-11D9-BED3-505054503030}" /success:enable /failure:enable | Out-Null
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