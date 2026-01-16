# Utilise une image Nginx légère

FROM nginx:alpine



# Copie le contenu du dossier src dans le dossier que Nginx utilise pour servir les sites

COPY ./src /usr/share/nginx/html



# Expose le port 80 pour y accéder

EXPOSE 80



# Démarre Nginx

CMD ["nginx", "-g", "daemon off;"]
