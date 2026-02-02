# Utilise une version très récente de Rust
FROM rust:1.85-slim as builder
WORKDIR /usr/src/scanner
COPY . .
# On s'assure que les dépendances sont verrouillées sur des versions compatibles
RUN cargo build --release

FROM debian:bookworm-slim
RUN apt-get update && apt-get install -y libssl3 && rm -rf /var/lib/apt/lists/*
COPY --from=builder /usr/src/scanner/target/release/scanner /usr/local/bin/scanner
CMD ["scanner"]