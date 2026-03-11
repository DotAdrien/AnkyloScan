#!/bin/bash

# Variables injectées par le serveur Python
SERVER_IP="SERVER_IP_PLACEHOLDER"
TOKEN="TOKEN_PLACEHOLDER"
INSTALL_DIR="/usr/local/bin"
SCRIPT_NAME="ankylo_linux_agent.sh"

echo "Installation de l'agent Linux AnkyloScan... 🐧"

# 1. Création du script de payload (le worker)
cat << EOF > "$INSTALL_DIR/$SCRIPT_NAME"
#!/bin/bash

# Récupère les ports en écoute (TCP/UDP) pour surveiller les backdoors ou services exposés
PORTS=\$(ss -tuln | grep LISTEN | awk '{print \$5}' | paste -sd "," -)
DATE=\$(date '+%Y-%m-%d %H:%M:%S')

# Construction du JSON
JSON_DATA=\$(cat <<JSON
{
  "token": "$TOKEN",
  "event_id": 5001,
  "source": "Agent-Linux-Cron",
  "message": "Ports ouverts détectés: \$PORTS | Scan: \$DATE"
}
JSON
)

# Envoi au serveur
curl -s -X POST -H "Content-Type: application/json" -d "\$JSON_DATA" http://$SERVER_IP:8001/logs/ingest
EOF

# Rendre le script exécutable
chmod +x "$INSTALL_DIR/$SCRIPT_NAME"

# 2. Configuration du CRON JOB (toutes les 5 minutes) 🕒
CRON_CMD="*/5 * * * * $INSTALL_DIR/$SCRIPT_NAME"

# Vérifie si le cron existe déjà pour éviter les doublons
(crontab -l 2>/dev/null | grep -v "$SCRIPT_NAME"; echo "$CRON_CMD") | crontab -

if [ $? -eq 0 ]; then
    echo "Succès ! L'agent Linux tournera toutes les 5 minutes. 🛡️"
else
    echo "Erreur lors de la configuration du Cron. Essayez avec sudo. 😱"
fi
