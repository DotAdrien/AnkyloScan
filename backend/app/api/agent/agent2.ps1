$ScriptContent = @'
$ServerIP = 'SERVER_IP_PLACEHOLDER'
$Token = 'TOKEN_PLACEHOLDER'
$Url = "http://$($ServerIP):8001/logs/ingest"

# Récupération des infos de sécurité (Processus lancés au démarrage)
$Processes = Get-Process | Sort-Object CPU -Descending | Select-Object -First 10
$User = $env:USERNAME
 
# Fonction helper pour extraire une donnée du XML d'un événement Windows
function Get-EventValue($EventData, $Name) {
    return ($EventData | Where-Object Name -eq $Name).'#text'
}

$StateFile = 'C:\ProgramData\AnkyloScan\AnkyloAgent_LastProcessEvent.txt' # Fichier d'état séparé pour cet agent
$LastId = 0
if (Test-Path $StateFile) { $LastId = [long](Get-Content $StateFile) }

$EventIDs = @(4688) # ID d'événement pour la création de processus

# Récupère les événements depuis la dernière exécution, ou les 5 dernières minutes si le fichier d'état est nouveau
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

    # Extrait juste le nom de l'exécutable
    $ProcessExecutable = Split-Path -Path $NewProcessName -Leaf

    # Filtre pour cmd.exe ou powershell.exe
    if ($ProcessExecutable -notmatch "(?i)^(cmd.exe|powershell.exe)$") {
        $MaxId = [math]::Max($MaxId, $Event.RecordId)
        continue
    }

    $DetailedMsg = "Commande exécutée: '$CommandLine' (Processus: '$ProcessExecutable') par '$SubjectDomainName\$SubjectUserName'."

    $Body = @{
        token = $Token
        event_id = $Id
        source = 'Agent-ProcessMonitor-Win'
        message = $DetailedMsg
    } | ConvertTo-Json -Compress

    try {
        Invoke-RestMethod -Uri $Url -Method Post -Body $Body -ContentType 'application/json; charset=utf-8' -ErrorAction Stop
    } catch {
        # Silencieux si le serveur est injoignable ou autre erreur d'envoi
    }

    $MaxId = [math]::Max($MaxId, $Event.RecordId)
}
'@

if ($MaxId -gt $LastId) { $MaxId | Set-Content -Path $StateFile }

'@

# 1. Création du fichier de script permanent
$DestPath = "C:\ProgramData\AnkyloScan"
if (-not (Test-Path $DestPath)) { New-Item -Path $DestPath -ItemType Directory | Out-Null }
Set-Content -Path "$DestPath\AnkyloLoginWorker.ps1" -Value $ScriptContent -Encoding UTF8

# 2. Configuration de la tâche planifiée au Login 🔓
$TaskName = "AnkyloProcessMonitor" # Nom de la tâche modifié pour plus de clarté

# Supprime l'ancienne tâche si elle existe
Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false -ErrorAction SilentlyContinue

$Action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-WindowStyle Hidden -ExecutionPolicy Bypass -File $DestPath\AnkyloLoginWorker.ps1"
# Le déclencheur est la connexion de n'importe quel utilisateur, répété toutes les 5 minutes
$Trigger = New-ScheduledTaskTrigger -AtLogon
$Trigger.RepetitionInterval = (New-TimeSpan -Minutes 5) # Répéter toutes les 5 minutes
$Trigger.RepetitionDuration = (New-TimeSpan -Days 365) # Répéter pendant un an

# Exécution avec les privilèges les plus élevés (compte SYSTEM) pour lire les journaux de sécurité
$Principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount -RunLevel Highest

Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Principal $Principal -Force

# --- Activation des Audits de Sécurité (équivalent GPO locale) ---
Write-Host "Activation des politiques d'audit Windows pour la création de processus... 🛡️" -ForegroundColor Cyan
auditpol /set /category:"Detailed Tracking" /success:enable /failure:enable | Out-Null
Write-Host "Audit de création de processus activé. ✅" -ForegroundColor Green

Write-Host "Agent de surveillance des processus installé avec succès ! Il se lancera à chaque connexion utilisateur et surveillera les commandes cmd/powershell. 🚀" -ForegroundColor Green
