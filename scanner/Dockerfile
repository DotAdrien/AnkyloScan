# Utilise une version récente pour supporter l'édition 2024
FROM rust:1.84-slim as builder
WORKDIR /usr/src/scanner
COPY . .
RUN cargo build --release

FROM debian:bookworm-slim
# Installation de libssl car la bibliothèque mysql en a besoin
RUN apt-get update && apt-get install -y libssl3 && rm -rf /var/lib/apt/lists/*
COPY --from=builder /usr/src/scanner/target/release/scanner /usr/local/bin/scanner
CMD ["scanner"]