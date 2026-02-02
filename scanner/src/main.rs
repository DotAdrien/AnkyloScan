use std::env;
use std::time::Instant;

fn main() {
    let args: Vec<String> = env::args().collect();
    
    if args.len() > 1 {
        let target = &args[1];
        let iterations: u64 = 100_000_000; // Nombre de calculs à faire
        let mut val: f64 = 2.0;
        
        println!("Analyse de la puissance sur la cible : {} 🦖⚡", target);
        
        // Début du chrono ⏱️
        let start = Instant::now();

        // Boucle de calcul intensive
        for _ in 0..iterations {
            val = val.sqrt(); // Racine carrée
            val = val + 1.0;  // Addition
        }

        let duration = start.elapsed();
        
        // Calcul de la vitesse en Gigaflops (milliards d'opérations / seconde)
        let total_ops = iterations as f64 * 2.0; // On fait 2 opérations par tour
        let speed = (total_ops / duration.as_secs_f64()) / 1_000_000_000.0;

        println!("--------------------------------------------");
        println!("Vitesse de calcul : {:.2} GFLOPS 🚀", speed);
        println!("Temps écoulé : {:?} ⏳", duration);
        println!("Résultat final : {} 💎", val);
        println!("--------------------------------------------");
        
    } else {
        eprintln!("Erreur : Pas de cible spécifiée ! 😱");
    }
}