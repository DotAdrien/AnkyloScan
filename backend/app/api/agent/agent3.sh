#!/bin/bash

# Variables injectées par le serveur Python
# Ces variables seront remplacées par le serveur lors de la génération du script.
SERVER_IP="SERVER_IP_PLACEHOLDER"
TOKEN="TOKEN_PLACEHOLDER"
INSTALL_DIR="/usr/local/bin"
SCRIPT_NAME="ankylo_linux_agent.sh"

echo "Installation de l'agent Linux AnkyloScan... 🐧"

# 1.5. Vérifier et créer le répertoire d'installation du script si nécessaire
if [ ! -d "$INSTALL_DIR" ]; then
    echo "Création du répertoire d'installation du script: $INSTALL_DIR"
    mkdir -p "$INSTALL_DIR"
fi

# 1.6. Définir et créer le répertoire pour le fichier d'état de l'agent
STATE_DIR="/var/lib/ankyloscan"
if [ ! -d "$STATE_DIR" ]; then
    echo "Création du répertoire d'état de l'agent: $STATE_DIR"
    mkdir -p "$STATE_DIR"
    chmod 700 "$STATE_DIR" # S'assurer que seul root peut lire/écrire
fi

# 1. Création du script de payload (le worker) qui sera exécuté par cron
cat << EOF > "$INSTALL_DIR/$SCRIPT_NAME"
#!/bin/bash

# Variables injectées (du script parent)
SERVER_IP="$SERVER_IP"
TOKEN="$TOKEN"
STATE_FILE="$STATE_DIR/ankylo_ports_state.txt"

# Récupère les ports en écoute (TCP/UDP). 
# On évite "grep LISTEN" car les ports UDP apparaissent en "UNCONN" !
CURRENT_PORTS=\$(ss -tuln | awk 'NR>1 {print \$5}' | sort | paste -sd "," -)
DATE=\$(date '+%Y-%m-%d %H:%M:%S')

LAST_PORTS=""
if [ -f "\$STATE_FILE" ]; then
    LAST_PORTS=\$(cat "\$STATE_FILE")
fi

# Comparer l'état actuel avec le dernier état connu
if [ "\$CURRENT_PORTS" != "\$LAST_PORTS" ]; then
    MESSAGE="Changement de ports détecté. Nouveaux ports ouverts: \$CURRENT_PORTS. Précédents: \$LAST_PORTS | Scan: \$DATE"
    EVENT_ID=5002 # ID pour un changement de port
    SOURCE="Agent-Linux-PortChangeMonitor"

# Si LAST_PORTS est vide, c'est la première exécution ou le fichier d'état a été supprimé
    if [ -z "\$LAST_PORTS" ]; then
        MESSAGE="Initialisation de la surveillance des ports. Ports ouverts: \$CURRENT_PORTS | Scan: \$DATE"
        EVENT_ID=5001 # ID pour le scan initial
    fi

    # Construction du JSON
    JSON_DATA=\$(cat <<JSON
{
  "token": "$TOKEN",
  "event_id": \$EVENT_ID,
  "source": "\$SOURCE",
  "message": "\$MESSAGE"
}
JSON
    )

    # Envoi au serveur
    curl -s -X POST -H "Content-Type: application/json" -d "\$JSON_DATA" http://\$SERVER_IP:8001/logs/ingest

    # Vérifier le statut de la commande curl
    if [ \$? -ne 0 ]; then
        logger -t "AnkyloScan_Agent" "Erreur: Impossible d'envoyer les logs au serveur AnkyloScan."
    fi

    # Mettre à jour le fichier d'état avec les ports actuels
    echo "\$CURRENT_PORTS" > "\$STATE_FILE"
fi # Fin du bloc if pour la comparaison des ports
EOF

# Rendre le script exécutable
chmod +x "$INSTALL_DIR/$SCRIPT_NAME"

# 2. Configuration du CRON JOB (toutes les 5 minutes) 🕒
CRON_CMD="*/5 * * * * $INSTALL_DIR/$SCRIPT_NAME"

# Vérifie si le cron existe déjà pour éviter les doublons
echo "Configuration de la tâche Cron pour exécuter l'agent toutes les 5 minutes..."

# Supprime toute entrée existante pour ce script et ajoute la nouvelle.
# Utilise '|| true' pour éviter une erreur si crontab -l est vide.
(crontab -l 2>/dev/null | grep -v "$SCRIPT_NAME" || true; echo "$CRON_CMD") | crontab -

if [ $? -eq 0 ]; then
    echo "Succès ! L'agent Linux est installé et surveillera les changements de ports toutes les 5 minutes. 🛡️"
else
    echo "Erreur lors de la configuration du Cron. Essayez avec sudo. 😱"
fi
