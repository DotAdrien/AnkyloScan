import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_email_report(content):
    try:
        # 1. Lecture de la config dans email.txt 📄
        with open("/app/outputs/email.txt", "r") as f:
            lines = f.read().splitlines()
            sender_email = lines[0]
            app_password = lines[1]
            receiver_emails = lines[2] # Format "test@gmail.com;admin@gmail.com"

        # 2. Préparation de l'e-mail 📧
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = receiver_emails
        msg['Subject'] = "AnkyloScan : Rapport de Scan Rapide 🛡️"

        body = f"Salut ! Tigrounet a terminé le scan. Voici le rapport :\n\n{content}"
        msg.attach(MIMEText(body, 'plain'))

        # 3. Envoi via le serveur SMTP de Google 🚀
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, app_password)
        
        # Envoi à chaque destinataire
        for email in receiver_emails.split(';'):
            server.sendmail(sender_email, email.strip(), msg.as_string())
        
        server.quit()
        print("E-mails envoyés avec succès ! 🌷")
        return True
    except Exception as e:
        print(f"Erreur d'envoi d'email : {e} 😱")
        return False