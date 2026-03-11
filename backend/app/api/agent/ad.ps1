$ScriptContent = @"
`$ServerIP = 'SERVER_IP_PLACEHOLDER'
`$Token = 'TOKEN_PLACEHOLDER'
`$Url = 'http://' + `$ServerIP + ':8001/logs/ingest'

`$StateFile = 'C:\AnkyloAgent_LastRecord.txt'
`$LastId = 0
if (Test-Path `$StateFile) { `$LastId = [long](Get-Content `$StateFile) }

# Liste de tous tes événements 🤓
`$EventIDs = @(4624, 4625, 4720, 4728, 4732, 4756, 1102, 4719, 5136)

`$Events = Get-WinEvent -FilterHashtable @{LogName='Security'; Id=`$EventIDs; StartTime=(Get-Date).AddMinutes(-5)} -ErrorAction SilentlyContinue | 
          Where-Object RecordId -gt `$LastId | 
          Sort-Object RecordId

`$MaxId = `$LastId

foreach (`$Event in `$Events) {
    `$Xml = [xml]`$Event.ToXml()
    
    # On récupère le compte (cible ou source selon l'event) 🕵️‍♂️
    `$TargetUserName = (`$Xml.Event.EventData.Data | Where-Object Name -in "TargetUserName", "SubjectUserName" | Select-Object -First 1).'#text'
    `$IpAddress = (`$Xml.Event.EventData.Data | Where-Object Name -eq "IpAddress").'#text'

    # Ignore les comptes machines 🚫
    if (`$TargetUserName -like "*`$") { continue }

    `$Time = `$Event.TimeCreated.ToString('yyyy-MM-dd HH:mm:ss')
    `$Id = `$Event.Id
    
    # Textes simplifiés 🌷
    `$Msg = switch (`$Id) {
        4624 { '✅ Connexion réussie' }
        4625 { '❌ Échec de connexion' }
        4720 { '👤 Création compte utilisateur' }
        4728 { '👥 Ajout groupe global' }
        4732 { '👥 Ajout groupe local' }
        4756 { '👥 Ajout groupe universel' }
        1102 { '🗑️ Journal audit effacé' }
        4719 { '⚙️ Politique audit modifiée' }
        5136 { '📝 Objet AD modifié' }
    }

    `$SimpleMessage = "`$Msg | Compte: `$TargetUserName | IP: `$IpAddress | Heure: `$Time"

    `$Body = @{
        token = `$Token
        event_id = `$Id
        source = 'Agent-AD'
        message = `$SimpleMessage
    } | ConvertTo-Json -Compress
    
    try {
        Invoke-RestMethod -Uri `$Url -Method Post -Body `$Body -ContentType 'application/json; charset=utf-8' -ErrorAction Stop
    } catch { }
    
    `$MaxId = [math]::Max(`$MaxId, `$Event.RecordId)
}

if (`$MaxId -gt `$LastId) { `$MaxId | Set-Content -Path `$StateFile }
"@

Set-Content -Path "C:\AnkyloAgent.ps1" -Value $ScriptContent -Encoding UTF8

$Action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-WindowStyle Hidden -ExecutionPolicy Bypass -File C:\AnkyloAgent.ps1"
$Trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Minutes 1)
$Principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount -RunLevel Highest

Register-ScheduledTask -TaskName "AnkyloAgentTask" -Action $Action -Trigger $Trigger -Principal $Principal -Force