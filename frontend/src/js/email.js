// email.js 📧

document.addEventListener('alpine:init', () => {
    Alpine.data('emailConfig', () => ({
        senderEmail: '',
        apiKey: '',
        recipients: '',
        vulnLevel3Alerts: false,
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
                    this.vulnLevel3Alerts = config.vuln_level3_alerts || false;
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
                        vuln_level3_alerts: this.vulnLevel3Alerts,
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