# Image Nginx légère
FROM nginx:alpine

# Mise à jour des paquets 🛠️
RUN apk update && apk upgrade

# Copie du contenu src 📂
COPY ./src /usr/share/nginx/html

# Port 80 🌐
EXPOSE 80

# Start 🚀
CMD ["nginx", "-g", "daemon off;"]
