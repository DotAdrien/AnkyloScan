FROM rust:1.85-slim as builder
WORKDIR /usr/src/scanner
COPY . .
RUN cargo build --release

FROM debian:bookworm-slim
COPY --from=builder /usr/src/scanner/target/release/scanner /usr/local/bin/scanner
CMD ["scanner"]