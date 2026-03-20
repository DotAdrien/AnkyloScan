import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.api.email_sender import get_current_email_config

def send_email_report(content):
    try:
        # 1. Récupération de la nouvelle configuration dynamique JSON ✨
        config = get_current_email_config()

        if not config.sender_email or not config.recipients:
            print("📧 [EMAIL SENDER] : Impossible d'envoyer le rapport. Config manquante.")
            return False

        # 2. Préparation de l'e-mail 📧
        msg = MIMEMultipart()
        msg['From'] = config.sender_email
        
        # Gestion de plusieurs destinataires séparés par des points-virgules ou virgules
        recipients_list = [r.strip() for r in config.recipients.replace(';', ',').split(',') if r.strip()]
        msg['To'] = ", ".join(recipients_list)
        msg['Subject'] = "AnkyloScan : Rapport de Scan Rapide 🛡️"

        body = f"Salut ! Tigrounet a terminé le scan. Voici le rapport :\n\n{content}"
        msg.attach(MIMEText(body, 'plain', 'utf-8'))

        if not recipients_list:
            return False

        # 3. Envoi via le serveur SMTP de Google en SSL (Port 465) 🚀
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(config.sender_email, config.api_key)
            server.sendmail(config.sender_email, recipients_list, msg.as_string())
            
        print("E-mails envoyés avec succès ! 🌷")
        return True
    except Exception as e:
        print(f"Erreur d'envoi d'email : {e} 😱")
        return False