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

$EventIDs = @(4625, 4768, 4769, 4720, 4728, 4732, 4756, 1102, 4719, 5136)

$Events = Get-WinEvent -FilterHashtable @{LogName='Security'; Id=$EventIDs; StartTime=(Get-Date).AddMinutes(-5)} -ErrorAction SilentlyContinue | 
          Where-Object RecordId -gt $LastId | 
          Sort-Object RecordId

$MaxId = $LastId

foreach ($Event in $Events) {
    # On parse le XML pour extraire les infos clés de manière propre ✨
    $Xml = [xml]$Event.ToXml()
    $EventData = $Xml.Event.EventData.Data
    
    $TargetUserName = Get-EventValue $EventData "TargetUserName"
    $SubjectUserName = Get-EventValue $EventData "SubjectUserName"

    # On ignore les comptes machines qui finissent par $
    if ($TargetUserName -like "*$") { continue }

    # On ignore les TGT Kerberos réussis (trop de bruit)
    $ResultCode = Get-EventValue $EventData "ResultCode"
    $Status = Get-EventValue $EventData "Status"
    if (($Event.Id -eq 4768 -and $Status -eq "0x0") -or ($Event.Id -eq 4769 -and $ResultCode -eq "0x0")) {
        $MaxId = [math]::Max($MaxId, $Event.RecordId)
        continue 
    }

    $Id = $Event.Id
    
    # Construction d'un message clair et concis selon l'événement 📜
    $DetailedMsg = switch ($Id) {
        4625 { "Échec de connexion pour '$TargetUserName' depuis l'IP '$(Get-EventValue $EventData 'IpAddress')'." }
        4768 { "Échec TGT Kerberos pour '$TargetUserName' depuis l'IP '$(Get-EventValue $EventData 'ClientAddr')' (Code: $Status)." }
        4769 { "Échec ticket de service Kerberos pour '$TargetUserName' (Service: $(Get-EventValue $EventData 'ServiceName'))." }
        4720 { "Le compte '$TargetUserName' a été créé par '$SubjectUserName'." }
        4728 { "L'utilisateur '$(Get-EventValue $EventData 'MemberName')' a été ajouté au groupe global '$TargetUserName' par '$SubjectUserName'." }
        4732 { "L'utilisateur '$(Get-EventValue $EventData 'MemberName')' a été ajouté au groupe local '$TargetUserName' par '$SubjectUserName'." }
        4756 { "L'utilisateur '$(Get-EventValue $EventData 'MemberName')' a été ajouté au groupe universel '$TargetUserName' par '$SubjectUserName'." }
        1102 { "Le journal de sécurité a été effacé par '$SubjectUserName'." }
        4719 { "La politique d'audit du système a été modifiée par '$SubjectUserName'." }
        5136 { "Un objet AD ('$(Get-EventValue $EventData 'ObjectDN')') a été modifié par '$SubjectUserName'." }
        Default { "Événement de sécurité non classifié (ID: $Id)." }
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

$Action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-WindowStyle Hidden -ExecutionPolicy Bypass -File C:\AnkyloAgent.ps1"
$Trigger = New-ScheduledTaskTrigger -At (Get-Date) -RepetitionInterval (New-TimeSpan -Minutes 1)
$Principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount -RunLevel Highest

Register-ScheduledTask -TaskName "AnkyloLogAgent" -Action $Action -Trigger $Trigger -Principal $Principal -Force 👍