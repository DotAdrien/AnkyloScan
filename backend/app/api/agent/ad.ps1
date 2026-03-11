$ScriptContent = @"
`$ServerIP = 'SERVER_IP_PLACEHOLDER'
`$Token = 'TOKEN_PLACEHOLDER'
`$Url = 'http://' + `$ServerIP + ':8001/logs/ingest'

# Fichier pour mémoriser le dernier log lu
`$StateFile = 'C:\AnkyloAgent_LastRecord.txt'
`$LastId = 0
if (Test-Path `$StateFile) { `$LastId = [long](Get-Content `$StateFile) }

`$EventIDs = @(4625, 4768, 4769, 4720, 4728, 4732, 4756, 1102, 4719, 5136)

# Récupération des logs des 5 dernières minutes
`$Events = Get-WinEvent -FilterHashtable @{LogName='Security'; Id=`$EventIDs; StartTime=(Get-Date).AddMinutes(-5)} -ErrorAction SilentlyContinue | 
          Where-Object RecordId -gt `$LastId | 
          Sort-Object RecordId

`$MaxId = `$LastId

foreach (`$Event in `$Events) {
    # Extraction des données XML pour le filtrage précis 🔍
    `$Xml = [xml]`$Event.ToXml()
    `$TargetUserName = (`$Xml.Event.EventData.Data | Where-Object Name -eq "TargetUserName").'#text'
    `$ResultCode = (`$Xml.Event.EventData.Data | Where-Object Name -eq "ResultCode").'#text'
    `$Status = (`$Xml.Event.EventData.Data | Where-Object Name -eq "Status").'#text'

    # --- FILTRAGE DU BRUIT ---
    # 1. On ignore les comptes machines (ex: WIN-SERV$) 🚫
    if (`$TargetUserName -like "*$") { continue }

    # 2. On ignore les succès Kerberos (0x0) pour ne garder que les anomalies/erreurs
    if ((`$Event.Id -eq 4768 -and `$Status -eq "0x0") -or (`$Event.Id -eq 4769 -and `$ResultCode -eq "0x0")) {
        `$MaxId = [math]::Max(`$MaxId, `$Event.RecordId)
        continue 
    }

    `$Time = `$Event.TimeCreated.ToString('yyyy-MM-dd HH:mm:ss')
    `$Id = `$Event.Id
    
    `$Msg = switch (`$Id) {
        4625 { 'Échec de connexion (Brute-force) ' }
        4768 { 'Erreur Ticket Kerberos (TGT) ' }
        4769 { 'Erreur Ticket Service Kerberos ' }
        4720 { 'Création compte utilisateur ' }
        4728 { 'Ajout groupe de sécurité global ' }
        4732 { 'Ajout groupe de sécurité local ' }
        4756 { 'Ajout groupe de sécurité universel ' }
        1102 { 'Journal audit effacé ' }
        4719 { 'Politique audit modifiée ' }
        5136 { 'Objet AD modifié ' }
    }

    `$Body = @{
        token = `$Token
        event_id = `$Id
        source = 'Agent-AD'
        message = "`$Msg | Utilisateur: `$TargetUserName | `$(`$Event.Message) | `$Time"
    } | ConvertTo-Json -Compress -Depth 10
    
    try {
        Invoke-RestMethod -Uri `$Url -Method Post -Body `$Body -ContentType 'application/json; charset=utf-8' -ErrorAction Stop
    } catch {
        # Erreur réseau, on continue
    }
    
    `$MaxId = [math]::Max(`$MaxId, `$Event.RecordId)
}

# Sauvegarde du nouveau record
if (`$MaxId -gt `$LastId) { `$MaxId | Set-Content -Path `$StateFile }
"@

# Création du script sur le disque
Set-Content -Path "C:\AnkyloAgent.ps1" -Value $ScriptContent -Encoding UTF8

# Création de la tâche planifiée (SYSTEM / Niveau max) ⏳
$Action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-WindowStyle Hidden -ExecutionPolicy Bypass -File C:\AnkyloAgent.ps1"
$Trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Minutes 1)
$Principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount -RunLevel Highest

Register-ScheduledTask -TaskName "AnkyloAgentTask" -Action $Action -Trigger $Trigger -Principal $Principal -Force