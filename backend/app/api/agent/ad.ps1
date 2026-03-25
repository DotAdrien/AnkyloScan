$ScriptContent = @'
$ServerIP = 'SERVER_IP_PLACEHOLDER'
$Token = 'TOKEN_PLACEHOLDER'
$Url = "http://$($ServerIP):8001/logs/ingest"

# Fonction helper pour extraire une donnée du XML d'un événement Windows
function Get-EventValue($EventData, $Name) {
    return ($EventData | Where-Object Name -eq $Name).'#text'
}

$StateFile = 'C:\AnkyloAgent_LastRecord.txt'
$LastId = 0
if (Test-Path $StateFile) { $LastId = [long](Get-Content $StateFile) }

# Ajout de 4624 (Succès connexion) pour surveiller les admins
$EventIDs = @(4624, 4625, 4768, 4720, 4728, 4732, 4756, 1102, 4719, 5136)

$Events = Get-WinEvent -FilterHashtable @{LogName='Security'; Id=$EventIDs; StartTime=(Get-Date).AddMinutes(-5)} -ErrorAction SilentlyContinue | 
          Where-Object RecordId -gt $LastId | 
          Sort-Object RecordId

$MaxId = $LastId
$SeenEvents = @{} # Pour le dédoublonnage intelligent dans la boucle actuelle

foreach ($Event in $Events) {
    # On parse le XML pour extraire les infos clés de manière propre ✨
    $Id = $Event.Id
    $Xml = [xml]$Event.ToXml()
    $EventData = $Xml.Event.EventData.Data
    
    $TargetUserName = Get-EventValue $EventData "TargetUserName"
    $SubjectUserName = Get-EventValue $EventData "SubjectUserName"

    # On ignore les comptes machines qui finissent par $
    if ($TargetUserName -like "*$") { 
        $MaxId = [math]::Max($MaxId, $Event.RecordId)
        continue 
    }

    # On ignore les TGT Kerberos réussis (trop de bruit)
    $ResultCode = Get-EventValue $EventData "ResultCode"
    $Status = Get-EventValue $EventData "Status"
    if ($Event.Id -eq 4768 -and $Status -eq "0x0") {
        $MaxId = [math]::Max($MaxId, $Event.RecordId)
        continue 
    }

    # --- LOGIQUE DE DÉDOUBLONNAGE ET FILTRAGE INTELLIGENT ---
    # Clé unique pour éviter le spam (ex: "Kerberos-Administrateur" n'apparaitra qu'une fois par scan)
    $DedupKey = "$Id-$TargetUserName"
    if ($Id -eq 4768) { $DedupKey = "KerberosFail-$TargetUserName" } 
    
    if ($SeenEvents.ContainsKey($DedupKey)) { 
        $MaxId = [math]::Max($MaxId, $Event.RecordId)
        continue 
    }
    $SeenEvents[$DedupKey] = $true

    # Gestion du LDAP et LogonType
    $LogonType = Get-EventValue $EventData "LogonType"
    $NetworkTag = ""
    if ($LogonType -eq "3") { $NetworkTag = " (via LDAP/Appli Web)" }

    # FILTRE ADMIN POUR LES SUCCÈS (4624)
    if ($Id -eq 4624) {
        # Modifie cette condition selon tes conventions (ex: adm_*, admin, root)
        if ($TargetUserName -notmatch "(?i)admin|root") { 
            $MaxId = [math]::Max($MaxId, $Event.RecordId)
            continue 
        }
        $DetailedMsg = "Connexion Administrateur réussie pour '$TargetUserName'$NetworkTag."
    }
    
    if ($Id -ne 4624) {
        # Construction d'un message clair et concis selon l'événement 📜
        $DetailedMsg = switch ($Id) {
            4625 { "Échec de connexion pour '$TargetUserName'$NetworkTag depuis l'IP '$(Get-EventValue $EventData 'IpAddress')'." }
            4768 { "Échec TGT Kerberos pour '$TargetUserName'$NetworkTag depuis l'IP '$(Get-EventValue $EventData 'ClientAddr')' (Code: $Status)." }
            4720 { "Le compte '$TargetUserName' a été créé par '$SubjectUserName'." }
            4728 { "L'utilisateur '$(Get-EventValue $EventData 'MemberName')' a été ajouté au groupe global '$TargetUserName' par '$SubjectUserName'." }
            4732 { "L'utilisateur '$(Get-EventValue $EventData 'MemberName')' a été ajouté au groupe local '$TargetUserName' par '$SubjectUserName'." }
            4756 { "L'utilisateur '$(Get-EventValue $EventData 'MemberName')' a été ajouté au groupe universel '$TargetUserName' par '$SubjectUserName'." }
            1102 { "Le journal de sécurité a été effacé par '$SubjectUserName'." }
            4719 { "La politique d'audit du système a été modifiée par '$SubjectUserName'." }
            5136 { "Un objet AD ('$(Get-EventValue $EventData 'ObjectDN')') a été modifié par '$SubjectUserName'." }
            Default { "Événement de sécurité non classifié (ID: $Id)." }
        }
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

# --- Activation des Audits de Sécurité (équivalent GPO locale) ---
Write-Host "Activation des politiques d'audit Windows... 🛡️" -ForegroundColor Cyan

# Active l'audit pour les connexions de comptes (Kerberos, NTLM)
auditpol /set /category:"Account Logon" /success:enable /failure:enable | Out-Null
# Active l'audit pour les ouvertures et fermetures de session (Logon/Logoff)
auditpol /set /category:"Logon/Logoff" /success:enable /failure:enable | Out-Null
# Active l'audit pour la gestion des comptes (Création user, ajout groupe...)
auditpol /set /category:"Account Management" /success:enable /failure:enable | Out-Null
# Active l'audit pour les changements de stratégie et événements système (Audit logs effacés...)
auditpol /set /category:"Policy Change" /success:enable /failure:enable | Out-Null
auditpol /set /category:"System" /success:enable /failure:enable | Out-Null

Write-Host "Tout est activé ! Les logs Windows sont maintenant configurés. ✅" -ForegroundColor Green

$Action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-WindowStyle Hidden -ExecutionPolicy Bypass -File C:\AnkyloAgent.ps1"
$Trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Minutes 1)
$Principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount -RunLevel Highest

Register-ScheduledTask -TaskName "AnkyloLogAgent" -Action $Action -Trigger $Trigger -Principal $Principal -Force