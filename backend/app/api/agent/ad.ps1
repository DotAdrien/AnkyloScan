$ScriptContent = @"
`$ServerIP = 'SERVER_IP_PLACEHOLDER'
`$Token = 'TOKEN_PLACEHOLDER'
`$Url = 'http://' + `$ServerIP + ':8001/logs/ingest'

# Fichier pour mémoriser le dernier log lu et éviter les doublons 🤓
`$StateFile = 'C:\AnkyloAgent_LastRecord.txt'
`$LastId = 0
if (Test-Path `$StateFile) { `$LastId = [long](Get-Content `$StateFile) }

`$EventIDs = @(4624, 4625, 4768, 4769, 4720, 4728, 4732, 4756, 1102, 4719, 5136)

# On regarde les 5 dernières minutes en filtrant par le RecordId mémorisé 🫣
`$Events = Get-WinEvent -FilterHashtable @{LogName='Security'; Id=`$EventIDs; StartTime=(Get-Date).AddMinutes(-5)} -ErrorAction SilentlyContinue | Where-Object RecordId -gt `$LastId | Sort-Object RecordId

`$MaxId = `$LastId

foreach (`$Event in `$Events) {
    `$Time = `$Event.TimeCreated.ToString('yyyy-MM-dd HH:mm:ss')
    `$Id = `$Event.Id
    
    `$Msg = switch (`$Id) {
        4625 { 'Échec de connexion (Brute-force) 😱' }
        4624 { 'Connexion réussie 🤨' }
        4768 { 'Requête ticket Kerberos (TGT) 🥵' }
        4769 { 'Requête ticket service Kerberos 🥵' }
        4720 { 'Création compte utilisateur 😶' }
        4728 { 'Ajout groupe de sécurité global 🫣' }
        4732 { 'Ajout groupe de sécurité local 🫣' }
        4756 { 'Ajout groupe de sécurité universel 🫣' }
        1102 { 'Journal audit effacé 😤' }
        4719 { 'Politique audit modifiée 😐' }
        5136 { 'Objet AD modifié 🤓' }
    }

    `$Body = @{
        token = `$Token
        event_id = `$Id
        source = 'Agent-AD'
        message = "`$Msg à `$Time"
    } | ConvertTo-Json -Compress
    
    Invoke-RestMethod -Uri `$Url -Method Post -Body `$Body -ContentType 'application/json'
    
    `$MaxId = [math]::Max(`$MaxId, `$Event.RecordId)
}

# Sauvegarde du nouveau record pour la prochaine exécution 👍
if (`$MaxId -gt `$LastId) { `$MaxId | Set-Content -Path `$StateFile }
"@

# Création du script de l'agent 🤓
Set-Content -Path "C:\AnkyloAgent.ps1" -Value $ScriptContent

# Création de la tâche planifiée (toutes les minutes) ⏳
$Action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-WindowStyle Hidden -File C:\AnkyloAgent.ps1"
$Trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Minutes 1)
$Principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount -RunLevel Highest

Register-ScheduledTask -TaskName "AnkyloAgentTask" -Action $Action -Trigger $Trigger -Principal $Principal -Force