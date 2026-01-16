not working / finish

# 🦖 AnkyloScan

**AnkyloScan** is a robust, armored network vulnerability scanner designed for rapid deployment via **Docker**. It guards your network like an Ankylosaurus protects its territory. 🛡️✨

## 🚀 Features
- 🔍 **Network Discovery**: Detect active hosts and open ports.
- 🐳 **Docker-Native**: Easy one-command setup with Docker Compose.
- 💻 **Web UI**: Intuitive dashboard to manage your scans.
- 🛡️ **Hardened**: Identification of vulnerable services and CVEs.
- 📧 **Email Notifications**: Send alerts and notifications via email. 

## 🛠️ Quick Start
```bash
# Tool install
sudo apt update -y
sudo apt install -y docker.io docker-compose

# AnkyloScan install
git clone https://github.com/DotAdrien/AnkyloScan
cd AnkyloScan
export ADMIN_PASSWORD=$(openssl rand -base64 12)
sudo -E docker-compose up --build
