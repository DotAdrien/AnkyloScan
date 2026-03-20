// email.js 📧

document.addEventListener('alpine:init', () => {
    Alpine.data('emailConfig', () => ({
        senderEmail: '',
        apiKey: '',
        recipients: '',
        scanQuickAlerts: false,
        scanSecurityAlerts: false,
        scanFullAlerts: false,
        agentLogAlerts: false,

        async loadEmailConfig() {
            try {
                const response = await fetch(`${window.API_BASE}/email/config`, {
                    method: 'GET',
                    credentials: 'include'
                });
                if (response.ok) {
                    const config = await response.json();
                    this.senderEmail = config.sender_email || '';
                    this.apiKey = config.api_key || '';
                    this.recipients = config.recipients || '';
                    this.scanQuickAlerts = config.scan_quick_alerts || false;
                    this.scanSecurityAlerts = config.scan_security_alerts || false;
                    this.scanFullAlerts = config.scan_full_alerts || false;
                    this.agentLogAlerts = config.agent_log_alerts || false;
                } else {
                    console.error("Failed to load email configuration.");
                }
            } catch (error) {
                console.error("Error loading email configuration:", error);
            }
        },

        async saveEmailConfig() {
            try {
                const response = await fetch(`${window.API_BASE}/email/save`, {
                    method: 'POST',
                    credentials: 'include',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        sender_email: this.senderEmail,
                        api_key: this.apiKey,
                        recipients: this.recipients,
                        scan_quick_alerts: this.scanQuickAlerts,
                        scan_security_alerts: this.scanSecurityAlerts,
                        scan_full_alerts: this.scanFullAlerts,
                        agent_log_alerts: this.agentLogAlerts
                    })
                });

                if (response.ok) {
                    alert("Configuration email sauvegardée ! ✨");
                } else {
                    const data = await response.json();
                    alert("Erreur : " + (data.detail || "Échec de la sauvegarde de la configuration email 😱"));
                }
            } catch (error) {
                alert("Erreur de connexion avec le serveur... 😩");
            }
        }
    }));
});