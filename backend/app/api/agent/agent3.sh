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
STATE_DIR="/var/lib/ankyloscan"
PORTS_STATE_FILE="\$STATE_DIR/ankylo_ports_state.txt"
DATE=\$(date '+%Y-%m-%d %H:%M:%S')

REPORT_MESSAGE=""
EVENT_ID=5003 # Nouvel ID pour incident critique
SOURCE="Agent-Linux-Security"
CHANGES_DETECTED=false

# 1. Surveillance des nouveaux ports (alerte uniquement si NOUVEAU port)
CURRENT_PORTS=\$(ss -tuln | awk 'NR>1 {print \$5}' | sort -u | paste -sd "," -)
LAST_PORTS=""
if [ -f "\$PORTS_STATE_FILE" ]; then
    LAST_PORTS=\$(cat "\$PORTS_STATE_FILE")
fi

if [ -n "\$LAST_PORTS" ] && [ "\$CURRENT_PORTS" != "\$LAST_PORTS" ]; then
    CURRENT_PORTS_NL=\$(echo "\$CURRENT_PORTS" | tr ',' '\n' | sort -u)
    LAST_PORTS_NL=\$(echo "\$LAST_PORTS" | tr ',' '\n' | sort -u)
    NEWLY_OPENED_PORTS=\$(comm -13 <(echo "\$LAST_PORTS_NL") <(echo "\$CURRENT_PORTS_NL") | paste -sd "," -)
    
    if [ -n "\$NEWLY_OPENED_PORTS" ]; then
        REPORT_MESSAGE+="Nouveaux ports ouverts (\$NEWLY_OPENED_PORTS). "
        CHANGES_DETECTED=true
    fi
fi
echo "\$CURRENT_PORTS" > "\$PORTS_STATE_FILE"

# 2. Surveillance des fichiers critiques (comptes, mots de passe, SSH, Sudo)
CRITICAL_FILES=("/etc/passwd" "/etc/shadow" "/etc/group" "/etc/sudoers" "/etc/ssh/sshd_config")
for FILE_PATH in "\${CRITICAL_FILES[@]}"; do
    if [ -f "\$FILE_PATH" ]; then
        FILE_BASENAME=\$(basename "\$FILE_PATH")
        STATE_FILE="\$STATE_DIR/ankylo_file_\$FILE_BASENAME.md5"
        CURRENT_MD5=\$(md5sum "\$FILE_PATH" | awk '{print \$1}')
        
        LAST_MD5=""
        if [ -f "\$STATE_FILE" ]; then
            LAST_MD5=\$(cat "\$STATE_FILE")
        fi

        if [ -n "\$LAST_MD5" ] && [ "\$CURRENT_MD5" != "\$LAST_MD5" ]; then
            REPORT_MESSAGE+="Fichier critique modifié (\$FILE_PATH). "
            CHANGES_DETECTED=true
        fi
        echo "\$CURRENT_MD5" > "\$STATE_FILE"
    fi
done

# Envoi de l'alerte uniquement si un vrai problème est détecté
if \$CHANGES_DETECTED; then
    MESSAGE="Incident de sécurité détecté: \$REPORT_MESSAGE | Scan: \$DATE"
    
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
fi
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
