# 🦖 AnkyloScan

<p align="center">
  <img src="https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker&logoColor=white" />
  <img src="https://img.shields.io/badge/Python-FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white" />
  <img src="https://img.shields.io/badge/MySQL-Database-4479A1?style=for-the-badge&logo=mysql&logoColor=white" />
  <img src="https://img.shields.io/badge/Nmap-Powered-EF3B2D?style=for-the-badge" />
</p>

> **A self-hosted network security scanner built for small and medium-sized businesses — deploy in minutes, protect from day one.**

---

## 🏢 Why AnkyloScan for your SMB?

Most small and medium-sized businesses don't have a dedicated security team or the budget for enterprise-grade monitoring tools. Yet the threat is real: open ports, outdated services, and unpatched vulnerabilities are the most common entry points for attackers.

**AnkyloScan was designed with this reality in mind.**

It is a lightweight, fully self-hosted solution that gives your organization a first layer of real network security — without requiring any cybersecurity expertise to deploy. You only need a machine with Docker installed.

In less than 5 minutes you get:

- A **live dashboard** showing all active hosts and open ports on your network.
- **Automated vulnerability detection** using Nmap scripts and CVE databases.
- **Security log collection** from your Windows and Linux machines via agents.
- **Email alerts** whenever something suspicious is detected.
- **Scheduled scans** so your network is checked regularly without any manual action.

No complex configuration, no external SaaS subscription, no data leaving your infrastructure.

---

## ✨ Features
- 🔍 **Network Discovery**: Detect active hosts and open ports.
- 🐳 **Docker-Native**: Easy one-command setup with Docker Compose.
- 💻 **Web UI**: Intuitive dashboard to manage your scans.
- 🛡️ **Hardened**: Identification of vulnerable services and CVEs.
- 📧 **Email Notifications**: Send alerts and notifications via email.
- 🕵️ **Unified Agents**: Easy-to-deploy Windows and Linux agents for security log collection.

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────┐
│                   Your Network                   │
│                                                  │
│  ┌──────────┐   ┌──────────┐   ┌─────────────┐   │
│  │ Windows  │   │  Linux   │   │  Any Host   │   │
│  │  Agent   │   │  Agent   │   │  (scanned)  │   │
│  └────┬─────┘   └────┬─────┘   └──────┬──────┘   │
│       │              │                │          │
└───────┼──────────────┼────────────────┼──────────┘
        │ Logs (token) │ Logs (token)   │ Nmap scan
        ▼              ▼                ▼
┌───────────────────────────────────────────────────┐
│                AnkyloScan Stack (Docker)          │
│                                                   │
│  ┌─────────────┐      ┌──────────────────────┐    │
│  │  Frontend   │      │       Backend        │    │
│  │  (Nginx)    │◄────►│  (FastAPI / Python)  │    │
│  │  Port 8000  │      │      Port 8001       │    │
│  └─────────────┘      └──────────┬───────────┘    │
│                                  │                │
│                       ┌──────────▼───────────┐    │
│                       │       MySQL DB       │    │
│                       │  Scans, Logs, Agents │    │
│                       └──────────────────────┘    │
└───────────────────────────────────────────────────┘
```

**3 Docker containers:**

| Container | Role | Port |
|---|---|---|
| `frontend` | Static web UI served by Nginx | `8000` |
| `backend` | FastAPI REST API + Nmap runner | `8001` |
| `db` | MySQL 8 — stores scans, logs, agents | `3306` |

---

## 🚀 Quick Start

### Prerequisites

- A Linux machine (physical, VM, or VPS) on the network you want to monitor
- Docker and Docker Compose installed

```bash
sudo apt update -y && sudo apt install -y docker.io docker-compose
```

### Installation

```bash
# Clone the repository
git clone https://github.com/DotAdrien/AnkyloScan
cd AnkyloScan

# Generate a secure random admin password
echo "ADMIN_PASSWORD=$(openssl rand -base64 32)" > .env

# Build and start all containers
sudo docker compose up --build
```

The `welcome` container will print your credentials in the terminal output:

```
--------------------------------------------
🦖 AnkyloScan is ready! 🛡️
URL    : http://localhost:8000
--------------------------------------------
```

Open `http://<your-server-ip>:8000` in any browser on your network.

---

## 🕵️ Deploying Agents

Agents allow AnkyloScan to receive security event logs from your machines in real time.

### Windows Agent

1. Log into the AnkyloScan dashboard.
2. Navigate to the **Agents** section.
3. Click **Download Windows Agent** — this generates a PowerShell script with a unique token pre-filled.
4. Run the script on the target Windows machine as Administrator:

```powershell
Set-ExecutionPolicy Bypass -Scope Process -Force
.\InstallAnkyloAgent.ps1
```

The agent will start forwarding Windows Security Event Logs to AnkyloScan immediately.

### Linux Agent

Download `agent3.sh` from the Agents page and run it on the target machine:

```bash
chmod +x agent3.sh
sudo ./agent3.sh
```
---

## 🛣️ Roadmap

- [ ] Multi-user support with role-based access control
- [ ] HTTPS / TLS built-in support
- [ ] PDF export for scan reports
- [ ] Custom scan target (manual IP or range instead of auto-detected network)
- [ ] CVE severity filtering and search in results
- [ ] Agent auto-update mechanism

---


---

<p align="center">Built with 🦖 by <a href="https://github.com/DotAdrien">DotAdrien</a> — Because every network deserves armor.</p>
