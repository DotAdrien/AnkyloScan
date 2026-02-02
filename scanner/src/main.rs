use std::env;

fn main() {
    // Récupère les arguments (le 1er est le nom du binaire, le 2ème est l'IP)
    let args: Vec<String> = env::args().collect();
    
    if args.len() > 1 {
        let target = &args[1];
        println!("Scan en cours sur la cible : {} 🦖🔥", target);
        // Ici tu mets ta logique de scan ultra rapide
    } else {
        eprintln!("Erreur : Pas de cible spécifiée ! 😱");
    }
}