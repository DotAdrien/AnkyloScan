# 🦖 AnkyloScan

**AnkyloScan** is a robust, armored network vulnerability scanner designed for rapid deployment via **Docker**. It guards your network like an Ankylosaurus protects its territory. 🛡️✨

## 🚀 Features
- 🔍 **Network Discovery**: Detect active hosts and open ports.
- 🐳 **Docker-Native**: Easy one-command setup with Docker Compose.
- 💻 **Web UI**: Intuitive dashboard to manage your scans.
- 🛡️ **Hardened**: Identification of vulnerable services and CVEs.
- 📧 **Email Notifications**: Send alerts and notifications via email.
- 🕵️ **Unified Agents**: Easy-to-deploy Windows and Linux agents for security log collection.


## 🛠️ Quick Start
```bash
# Installation of tool
sudo apt update -y && sudo apt install -y docker.io docker-compose

# Installation of AnkyloScan
git clone https://github.com/DotAdrien/AnkyloScan
cd AnkyloScan

# Generate unique password  🔑
echo "ADMIN_PASSWORD=$(openssl rand -base64 32)" > .env

# Start 🚀
sudo docker compose up --build
