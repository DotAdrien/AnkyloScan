# Utilise l'image officielle MySQL 8.0
FROM mysql:8.0

# Copie la configuration personnalisée (my.cnf)
COPY my.cnf /etc/mysql/conf.d/my.cnf

# Copie les scripts d'initialisation (init.sql)
COPY ./init/ /docker-entrypoint-initdb.d/

# Expose le port interne par défaut
EXPOSE 3306
