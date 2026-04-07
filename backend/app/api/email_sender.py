import os
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.api.email import EMAIL_FILE, EmailConfig

def get_current_email_config() -> EmailConfig:
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
        print(f"⚠️ Error reading or parsing email configuration file: {e}. Returning default config.")
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
    config = get_current_email_config()

    if not config.recipients or not config.sender_email:
        print(f"📧 [EMAIL SENDER]: Unable to send email ({subject}). Missing configuration.")
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
        
        print(f"✅ Email sent successfully: {subject}")
        return True
    except smtplib.SMTPAuthenticationError:
        print(f"⚠️ [EMAIL SENDER]: SMTP Authentication Error. Check sender email and API key (App Password).")
        return False
    except Exception as e:
        print(f"⚠️ [EMAIL SENDER]: Error while sending email: {e}")
        return False

def send_agent_log_alert(source: str, event_id: int, message: str):
    config = get_current_email_config()
    if not config.agent_log_alerts:
        return False
        
    subject = f"🤖 AnkyloScan Alert: New Agent Log ({source})"
    body = f"A new event has been recorded by an agent:\n\nSource: {source}\nEvent ID: {event_id}\nMessage: {message}\n\nLog in to AnkyloScan to view all logs."
    return send_email(subject, body)

def send_vuln_alert(scan_id: int, file_path: str, vuln_results: list):
    config = get_current_email_config()
    if not config.scan_full_alerts:
        return False
        
    has_level3 = False
    for host in vuln_results:
        for port_data in host.get('ports', []):
            for vuln in port_data.get('vulns', []):
                if vuln.get('level') == 3:
                    has_level3 = True
                    break

    if not has_level3:
        return False

    subject = f"🚨 AnkyloScan Alert: Level 3 Vulnerabilities Detected (Scan #{scan_id})"
    body = f"A full scan (Level 3) has detected critical vulnerabilities.\n\nScan Details: {file_path}\n\nDetected Vulnerabilities:\n"
    for host_data in vuln_results:
        body += f"  Host: {host_data['ip']}\n"
        for port_data in host_data.get('ports', []):
            body += f"    Port: {port_data['port']}\n"
            for vuln in port_data.get('vulns', []):
                body += f"      - {vuln.get('badge', '')} {vuln.get('title', '')} ({vuln.get('state', '')})\n"
    body += "\nLog in to AnkyloScan for more details."
    
    return send_email(subject, body)

def send_scan_report(scan_type: int, content: str):
    config = get_current_email_config()
    
    if scan_type == 1 and config.scan_quick_alerts:
        subject = "AnkyloScan: Quick Scan Report ⚡"
        body = f"Hello! The quick scan is finished. Here is the raw report:\n\n{content}"
    elif scan_type == 2 and config.scan_security_alerts:
        subject = "AnkyloScan: Security Scan Report 🛡️"
        body = f"Hello! The security scan is finished. Here is the raw report:\n\n{content}"
    elif scan_type == 3 and config.scan_full_alerts:
        subject = "AnkyloScan: Full Scan Report 🦖"
        body = f"Hello! The full scan is finished. Here is the raw report:\n\n{content}"
    else:
        return False

    return send_email(subject, body)