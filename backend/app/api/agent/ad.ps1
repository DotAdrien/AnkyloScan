$ScriptContent = @'
$ServerIP = 'SERVER_IP_PLACEHOLDER'
$Token = 'TOKEN_PLACEHOLDER'
$Url = "http://$($ServerIP):8001/logs/ingest"

$StateFile = 'C:\AnkyloAgent_LastRecord.txt'
$LastId = 0
if (Test-Path $StateFile) { $LastId = [long](Get-Content $StateFile) }

$EventIDs = @(4625, 4768, 4769, 4720, 4728, 4732, 4756, 1102, 4719, 5136)

$Events = Get-WinEvent -FilterHashtable @{LogName='Security'; Id=$EventIDs; StartTime=(Get-Date).AddMinutes(-5)} -ErrorAction SilentlyContinue | 
          Where-Object RecordId -gt $LastId | 
          Sort-Object RecordId

$MaxId = $LastId

foreach ($Event in $Events) {
    $Xml = [xml]$Event.ToXml()
    $TargetUserName = ($Xml.Event.EventData.Data | Where-Object Name -eq "TargetUserName").'#text'
    $ResultCode = ($Xml.Event.EventData.Data | Where-Object Name -eq "ResultCode").'#text'
    $Status = ($Xml.Event.EventData.Data | Where-Object Name -eq "Status").'#text'

    if ($TargetUserName -like "*$") { continue }

    if (($Event.Id -eq 4768 -and $Status -eq "0x0") -or ($Event.Id -eq 4769 -and $ResultCode -eq "0x0")) {
        $MaxId = [math]::Max($MaxId, $Event.RecordId)
        continue 
    }

    $Time = $Event.TimeCreated.ToString('yyyy-MM-dd HH:mm:ss')
    $Id = $Event.Id
    
    $Msg = switch ($Id) {
        4625 { 'Échec connexion (Brute-force)' }
        4768 { 'Erreur TGT Kerberos' }
        4769 { 'Erreur Service Kerberos' }
        4720 { 'Création compte' }
        4728 { 'Ajout groupe global' }
        4732 { 'Ajout groupe local' }
        4756 { 'Ajout groupe universel' }
        1102 { 'Journal effacé' }
        4719 { 'Politique audit modifiée' }
        5136 { 'Objet AD modifié' }
        Default { 'Event AD' }
    }

    $Body = @{
        token = $Token
        event_id = $Id
        source = 'Agent-AD'
        message = "$Msg | Utilisateur: $TargetUserName | $($Event.Message) | $Time"
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

$Action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-WindowStyle Hidden -ExecutionPolicy Bypass -File C:\AnkyloAgent.ps1"
$Trigger = New-ScheduledTaskTrigger -At (Get-Date) -RepetitionInterval (New-TimeSpan -Minutes 1)
$Principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount -RunLevel Highest

Register-ScheduledTask -TaskName "AnkyloLogAgent" -Action $Action -Trigger $Trigger -Principal $Principal -Force 👍