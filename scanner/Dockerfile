# Étape de compilation
FROM rust:1.70-slim as builder
WORKDIR /usr/src/scanner
COPY . .
RUN cargo build --release

# Image finale légère
FROM debian:bullseye-slim
COPY --from=builder /usr/src/scanner/target/release/scanner /usr/local/bin/scanner
CMD ["scanner"]