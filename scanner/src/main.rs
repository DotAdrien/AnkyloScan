use std::net::TcpStream;
use std::time::Duration;
use tokio;

#[tokio::main]
async fn main() {
    let target = "127.0.0.1";
    println!("Démarrage du scan sur {}... 🦖", target);

    for port in 1..1024 {
        let address = format!("{}:{}", target, port);
        if TcpStream::connect_timeout(&address.parse().unwrap(), Duration::from_millis(100)).is_ok() {
            println!("Port {} ouvert ! 🔓", port);
        }
    }
    println!("Scan terminé ! 🛡️");
}