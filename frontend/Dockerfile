# Base Debian légère 🐧
FROM debian:bookworm-slim

# Install Nginx et Docker 🛠️
RUN apt update && apt upgrade -y && \
    apt install -y nginx docker.io && \
    apt clean

# Copie du contenu 📂
COPY ./src /var/www/html

# Port 80 🌐
EXPOSE 80

# Start 🚀
CMD ["nginx", "-g", "daemon off;"]
