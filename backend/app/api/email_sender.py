import os
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.api.email import EMAIL_FILE, EmailConfig

def get_current_email_config() -> EmailConfig:
    """
    Récupère la configuration email actuelle depuis le fichier.
    Retourne une configuration par défaut si le fichier n'existe pas ou est invalide.
    """
    if not os.path.exists(EMAIL_FILE):
        return EmailConfig(
            sender_email="",
            api_key="",
            recipients="",
            scan_quick_alerts=False,
            scan_security_alerts=False,
            scan_full_alerts=False,
            agent_log_alerts=False
        )
    
    try:
        with open(EMAIL_FILE, "r") as f:
            config_data = json.load(f)
        return EmailConfig(**config_data)
    except (json.JSONDecodeError, TypeError) as e:
        print(f"⚠️ Erreur de lecture ou de parsing du fichier de configuration email : {e}. Retourne la config par défaut.")
        return EmailConfig(
            sender_email="",
            api_key="",
            recipients="",
            scan_quick_alerts=False,
            scan_security_alerts=False,
            scan_full_alerts=False,
            agent_log_alerts=False
        )

def send_email(subject: str, body: str):
    """
    Fonction centrale et interne pour envoyer un email via SMTP 📧
    """
    config = get_current_email_config()

    if not config.recipients or not config.sender_email:
        print(f"📧 [EMAIL SENDER] : Impossible d'envoyer l'email ({subject}). Config manquante.")
        return False
    
    try:
        msg = MIMEMultipart()
        msg['From'] = config.sender_email
        msg['Subject'] = subject
        
        recipients_list = [r.strip() for r in config.recipients.replace(';', ',').split(',') if r.strip()]
        msg['To'] = ", ".join(recipients_list)

        if not recipients_list:
            return False

        msg.attach(MIMEText(body, 'plain', 'utf-8'))

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(config.sender_email, config.api_key)
            server.sendmail(config.sender_email, recipients_list, msg.as_string())
        
        print(f"✅ Email envoyé avec succès : {subject}")
        return True
    except smtplib.SMTPAuthenticationError:
        print(f"⚠️ [EMAIL SENDER] : Erreur d'authentification SMTP. Vérifiez l'expéditeur et la clé API (mot de passe d'application).")
        return False
    except Exception as e:
        print(f"⚠️ [EMAIL SENDER] : Erreur lors de l'envoi de l'email : {e}")
        return False

def send_agent_log_alert(source: str, event_id: int, message: str):
    """Vérifie la configuration et envoie une alerte de log d'agent si activé."""
    config = get_current_email_config()
    if not config.agent_log_alerts:
        return False
        
    subject = f"🤖 Alerte AnkyloScan: Nouveau log d'agent ({source})"
    body = f"Un nouvel événement a été enregistré par un agent:\n\nSource: {source}\nEvent ID: {event_id}\nMessage: {message}\n\nConnectez-vous à AnkyloScan pour consulter tous les logs."
    return send_email(subject, body)

def send_vuln_alert(scan_id: int, file_path: str, vuln_results: list):
    """Vérifie la configuration et envoie une alerte de vulnérabilité si activé et requise."""
    config = get_current_email_config()
    if not config.scan_full_alerts:
        return False
        
    # On vérifie s'il y a bien au moins une vuln de niveau 3 dans les résultats
    has_level3 = any(vuln.get for host in vuln_results for vuln in host.get('vulns', []))
    if not has_level3:
        return False

    subject = f"🚨 Alerte AnkyloScan: Vulnérabilités de Niveau 3 détectées (Scan #{scan_id})"
    body = f"Un scan complet (Niveau 3) a détecté des vulnérabilités critiques.\n\nDétails du scan: {file_path}\n\nVulnérabilités détectées:\n"
    for host_data in vuln_results:
        body += f"  Hôte: {host_data['ip']}\n"
        for vuln in host_data['vulns']:
            if vuln.get('level') == 3:
                body += f"    - {vuln.get('badge', '')} {vuln.get('title', '')} ({vuln.get('state', '')})\n"
    body += "\nConnectez-vous à AnkyloScan pour plus de détails."
    
    return send_email(subject, body)

def send_scan_report(scan_type: int, content: str):
    """Vérifie la config et envoie le rapport de scan brut selon le type."""
    config = get_current_email_config()
    
    if scan_type == 1 and config.scan_quick_alerts:
        subject = "AnkyloScan : Rapport de Scan Rapide ⚡"
        body = f"Salut ! Tigrounet a terminé le scan rapide. Voici le rapport brut :\n\n{content}"
    elif scan_type == 2 and config.scan_security_alerts:
        subject = "AnkyloScan : Rapport de Scan Sécurité 🛡️"
        body = f"Salut ! Tigrounet a terminé le scan de sécurité. Voici le rapport brut :\n\n{content}"
    elif scan_type == 3 and config.scan_full_alerts:
        subject = "AnkyloScan : Rapport de Scan Complet 🦖"
        body = f"Salut ! Tigrounet a terminé le scan complet. Voici le rapport brut :\n\n{content}"
    else:
        return False

    return send_email(subject, body)