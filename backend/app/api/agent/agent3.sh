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
DATE=\$(date '+%Y-%m-%d %H:%M:%S')

REPORT_MESSAGE=""
EVENT_ID=5003 # Nouvel ID pour incident critique
SOURCE="Agent-Linux-Security"
CHANGES_DETECTED=false

# 1. Surveillance des processus et commandes (Comportements anormaux)
SUSPICIOUS_REGEX="\b(nc|netcat|socat|nmap|tcpdump|wireshark|strace|wget|curl|whoami|id|uname|ncat|john|hydra|sqlmap|chisel)\b|bash -i|sh -i|python[0-9]* -c|perl -e"

# a) Processus suspects en cours d'exécution
SUSPICIOUS_PROCESSES=\$(ps -eo user,pid,cmd --no-headers | grep -E -i "\$SUSPICIOUS_REGEX" | grep -v -E "(grep|ankylo_linux_agent)")

if [ -n "\$SUSPICIOUS_PROCESSES" ]; then
    CURRENT_PROC_MD5=\$(echo "\$SUSPICIOUS_PROCESSES" | md5sum | awk '{print \$1}')
    LAST_PROC_MD5=""
    if [ -f "\$STATE_DIR/ankylo_proc.md5" ]; then
        LAST_PROC_MD5=\$(cat "\$STATE_DIR/ankylo_proc.md5")
    fi

    if [ "\$CURRENT_PROC_MD5" != "\$LAST_PROC_MD5" ]; then
        FORMATTED_PROCS=\$(echo "\$SUSPICIOUS_PROCESSES" | tr '\n' '|' | sed 's/|\$//')
        REPORT_MESSAGE+="[ALERTE CRITIQUE] Processus suspect en cours: \$FORMATTED_PROCS. "
        CHANGES_DETECTED=true
        echo "\$CURRENT_PROC_MD5" > "\$STATE_DIR/ankylo_proc.md5"
    fi
else
    rm -f "\$STATE_DIR/ankylo_proc.md5" 2>/dev/null
fi

# b) Commandes suspectes dans l'historique (pour capter les actions rapides)
RECENT_BAD_CMDS=""
for HIST_FILE in /home/*/.bash_history /root/.bash_history; do
    if [ -f "\$HIST_FILE" ]; then
        USER_NAME=\$(basename \$(dirname "\$HIST_FILE"))
        FOUND_CMDS=\$(tail -n 20 "\$HIST_FILE" 2>/dev/null | grep -E -i "\$SUSPICIOUS_REGEX" | tr '\n' ',' | sed 's/,\$//')
        
        if [ -n "\$FOUND_CMDS" ]; then
            RECENT_BAD_CMDS+="User \$USER_NAME: [\$FOUND_CMDS]. "
        fi
    fi
done

if [ -n "\$RECENT_BAD_CMDS" ]; then
    CURRENT_HIST_MD5=\$(echo "\$RECENT_BAD_CMDS" | md5sum | awk '{print \$1}')
    LAST_HIST_MD5=""
    if [ -f "\$STATE_DIR/ankylo_hist.md5" ]; then
        LAST_HIST_MD5=\$(cat "\$STATE_DIR/ankylo_hist.md5")
    fi

    if [ "\$CURRENT_HIST_MD5" != "\$LAST_HIST_MD5" ]; then
        REPORT_MESSAGE+="[ALERTE HISTORIQUE] Commandes interdites exécutées: \$RECENT_BAD_CMDS. "
        CHANGES_DETECTED=true
        echo "\$CURRENT_HIST_MD5" > "\$STATE_DIR/ankylo_hist.md5"
    fi
fi

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
    echo "Succès ! L'agent Linux est installé et surveillera les commandes suspectes toutes les 5 minutes. 🛡️"
else
    echo "Erreur lors de la configuration du Cron. Essayez avec sudo. 😱"
fi
