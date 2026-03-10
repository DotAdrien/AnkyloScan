$ScriptContent = @"
`$ServerIP = 'SERVER_IP_PLACEHOLDER'
`$Token = 'TOKEN_PLACEHOLDER'
`$Url = 'http://' + `$ServerIP + ':8001/logs/ingest'

# Fichier pour memoriser le dernier log lu et eviter les doublons 
`$StateFile = 'C:\AnkyloAgent_LastRecord.txt'
`$LastId = 0
if (Test-Path `$StateFile) { `$LastId = [long](Get-Content `$StateFile) }

`$EventIDs = @(4624, 4625, 4768, 4769, 4720, 4728, 4732, 4756, 1102, 4719, 5136)

# On regarde les 5 dernieres minutes en filtrant par le RecordId memorise
`$Events = Get-WinEvent -FilterHashtable @{LogName='Security'; Id=`$EventIDs; StartTime=(Get-Date).AddMinutes(-5)} -ErrorAction SilentlyContinue | Where-Object RecordId -gt `$LastId | Sort-Object RecordId

`$MaxId = `$LastId

foreach (`$Event in `$Events) {
    `$Time = `$Event.TimeCreated.ToString('yyyy-MM-dd HH:mm:ss')
    `$Id = `$Event.Id
    
    `$Msg = switch (`$Id) {
        4625 { 'echec de connexion (Brute-force) ' }
        4624 { 'Connexion reussie ' }
        4768 { 'Requête ticket Kerberos (TGT) ' }
        4769 { 'Requête ticket service Kerberos ' }
        4720 { 'Creation compte utilisateur ' }
        4728 { 'Ajout groupe de securite global ' }
        4732 { 'Ajout groupe de securite local ' }
        4756 { 'Ajout groupe de securite universel ' }
        1102 { 'Journal audit efface ' }
        4719 { 'Politique audit modifiee ' }
        5136 { 'Objet AD modifie ' }
    }

    `$Body = @{
        token = `$Token
        event_id = `$Id
        source = 'Agent-AD'
        message = "`$Msg a `$Time"
    } | ConvertTo-Json -Compress
    
    Invoke-RestMethod -Uri `$Url -Method Post -Body `$Body -ContentType 'application/json; charset=utf-8'
    
    `$MaxId = [math]::Max(`$MaxId, `$Event.RecordId)
}

# Sauvegarde du nouveau record pour la prochaine execution 
if (`$MaxId -gt `$LastId) { `$MaxId | Set-Content -Path `$StateFile }
"@

# Creation du script de l'agent 
Set-Content -Path "C:\AnkyloAgent.ps1" -Value $ScriptContent

# Creation de la tâche planifiee (toutes les minutes) ⏳
$Action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-WindowStyle Hidden -File C:\AnkyloAgent.ps1"
$Trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Minutes 1)
$Principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount -RunLevel Highest

Register-ScheduledTask -TaskName "AnkyloAgentTask" -Action $Action -Trigger $Trigger -Principal $Principal -Force