$ScriptContent = @'
$ServerIP = 'SERVER_IP_PLACEHOLDER'
$Token = 'TOKEN_PLACEHOLDER'
$Url = "http://$($ServerIP):8001/logs/ingest"

# Récupération des infos de sécurité (Processus lancés au démarrage)
$Processes = Get-Process | Sort-Object CPU -Descending | Select-Object -First 10
$User = $env:USERNAME

foreach ($Proc in $Processes) {
    $Msg = "Processus actif au login: $($Proc.ProcessName) (ID: $($Proc.Id)) - CPU: $($Proc.CPU)"
    
    $Body = @{
        token = $Token
        event_id = 1002 # ID arbitraire pour Login Scan
        source = 'Agent-Login-Win'
        message = "$Msg | Utilisateur: $User"
    } | ConvertTo-Json -Compress

    try {
        Invoke-RestMethod -Uri $Url -Method Post -Body $Body -ContentType 'application/json; charset=utf-8' -ErrorAction Stop
    } catch { 
        # Silencieux si le serveur est injoignable
    }
}
'@

# 1. Création du fichier de script permanent
$DestPath = "C:\ProgramData\AnkyloScan"
if (-not (Test-Path $DestPath)) { New-Item -Path $DestPath -ItemType Directory | Out-Null }
Set-Content -Path "$DestPath\AnkyloLoginWorker.ps1" -Value $ScriptContent -Encoding UTF8

# 2. Configuration de la tâche planifiée au Login 🔓
$TaskName = "AnkyloLoginScan"

# Supprime l'ancienne tâche si elle existe
Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false -ErrorAction SilentlyContinue

$Action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-WindowStyle Hidden -ExecutionPolicy Bypass -File $DestPath\AnkyloLoginWorker.ps1"
# Le déclencheur est la connexion de n'importe quel utilisateur
$Trigger = New-ScheduledTaskTrigger -AtLogon
# Exécution avec les privilèges les plus élevés pour voir tous les processus
$Principal = New-ScheduledTaskPrincipal -GroupId "BUILTIN\Users" -RunLevel Highest

Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Principal $Principal -Force

Write-Host "Agent 2 installé avec succès ! Il se lancera à chaque connexion utilisateur. 🚀" -ForegroundColor Green
