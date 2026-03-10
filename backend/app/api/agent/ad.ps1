$ScriptContent = @"
`$ServerIP = 'SERVER_IP_PLACEHOLDER'
`$Token = 'TOKEN_PLACEHOLDER'
`$Url = 'http://' + `$ServerIP + ':8001/logs/ingest'

`$Events = Get-WinEvent -FilterHashtable @{LogName='Security'; Id=4625; StartTime=(Get-Date).AddMinutes(-1)} -ErrorAction SilentlyContinue

foreach (`$Event in `$Events) {
    `$Time = `$Event.TimeCreated.ToString('yyyy-MM-dd HH:mm:ss')
    `$Body = @{
        token = `$Token
        event_id = 4625
        source = 'Agent-AD'
        message = 'Échec de mot de passe à ' + `$Time + ' 😱'
    } | ConvertTo-Json -Compress
    
    Invoke-RestMethod -Uri `$Url -Method Post -Body `$Body -ContentType 'application/json'
}
"@

# Création du script de l'agent 🤓
Set-Content -Path "C:\AnkyloAgent.ps1" -Value $ScriptContent

# Création de la tâche planifiée (toutes les minutes) ⏳
$Action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-WindowStyle Hidden -File C:\AnkyloAgent.ps1"
$Trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Minutes 1)
$Principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount -RunLevel Highest

Register-ScheduledTask -TaskName "AnkyloAgentTask" -Action $Action -Trigger $Trigger -Principal $Principal -Force