# Étape 1 : Récupération du binaire RustScan
FROM rustscan/rustscan:2.1.1 as rustscan_bin

# Étape 2 : Image finale légère
FROM debian:bookworm-slim

# Installation de nmap (indispensable) 🔍
RUN apt-get update && apt-get install -y nmap && rm -rf /var/lib/apt/lists/*

# Création du dossier de partage
WORKDIR /share

# 1. Copie pour le partage (ce qui ira dans le volume)
COPY --from=rustscan_bin /usr/local/bin/rustscan /share/rustscan

# 2. Copie pour le système (pour que la commande "rustscan" fonctionne localement)
COPY --from=rustscan_bin /usr/local/bin/rustscan /usr/local/bin/rustscan

# On lance
CMD ["rustscan", "--help"]