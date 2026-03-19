import os
import json
import smtplib
from email.mime.text import MIMEText
from typing import Optional
from app.api.email import EMAIL_FILE, EmailConfig # Réutilise le modèle et le chemin du fichier

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
            vuln_level3_alerts=False,
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
            vuln_level3_alerts=False,
            agent_log_alerts=False
        )

def send_alert_email(subject: str, body: str):
    """
    Simule l'envoi d'un email d'alerte en utilisant la configuration sauvegardée.
    Pour un vrai envoi, il faudrait intégrer une bibliothèque SMTP ou une API d'envoi d'emails.
    """
    config = get_current_email_config()

    if not config.recipients or not config.sender_email:
        print("📧 [EMAIL SENDER] : Impossible d'envoyer l'email. Destinataires ou expéditeur non configurés.")
        return
    
    try:
        msg = MIMEText(body, 'plain', 'utf-8')
        msg['From'] = config.sender_email
        msg['Subject'] = subject
        
        # Split recipients by comma or semicolon and strip whitespace
        recipients_list = [r.strip() for r in config.recipients.replace(';', ',').split(',') if r.strip()]
        msg['To'] = ", ".join(recipients_list)

        if not recipients_list:
            print("📧 [EMAIL SENDER] : Aucun destinataire valide configuré.")
            return

        # Utilisation de smtplib pour l'envoi réel
        # Pour Gmail, l'api_key est généralement le mot de passe d'application
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server: # Utilise SMTP_SSL pour le port 465
            server.login(config.sender_email, config.api_key)
            server.sendmail(config.sender_email, recipients_list, msg.as_string())
        
        print(f"✅ Email d'alerte envoyé avec succès à {config.recipients} !")
    except smtplib.SMTPAuthenticationError:
        print(f"⚠️ [EMAIL SENDER] : Erreur d'authentification SMTP. Vérifiez l'expéditeur et la clé API (mot de passe d'application).")
    except Exception as e:
        print(f"⚠️ [EMAIL SENDER] : Erreur lors de l'envoi de l'email d'alerte : {e}")