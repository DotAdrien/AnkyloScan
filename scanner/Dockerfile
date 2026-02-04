# Étape 1 : Récupération du binaire RustScan
FROM rustscan/rustscan:2.1.1 as rustscan_bin

# Étape 2 : Image finale légère
FROM debian:bookworm-slim

# Installation de nmap (indispensable pour que RustScan fonctionne) 🔍
RUN apt-get update && apt-get install -y nmap && rm -rf /var/lib/apt/lists/*

# Copie du binaire RustScan depuis l'image officielle
COPY --from=rustscan_bin /usr/local/bin/rustscan /usr/local/bin/rustscan

# Dans ton scanner/Dockerfile
COPY --from=rustscan_bin /usr/local/bin/rustscan /usr/local/bin/shared/rustscan

# On laisse le conteneur ouvert ou on définit un point d'entrée
CMD ["rustscan", "--help"]