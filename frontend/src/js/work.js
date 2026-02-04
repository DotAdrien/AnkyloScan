async function runNetworkScan() {
    const targetNetwork = "192.168.1.0/24";
    
    try {
        const response = await fetch('http://localhost:8001/scan/start', {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json' 
            },
            credentials: 'include', // Indispensable pour envoyer le cookie session_token 🍪
            body: JSON.stringify({ network: targetNetwork })
        });

        const data = await response.json();

        if (response.ok) {
            alert("Scanner lancé ! Réponse du binaire Rust : " + data.output);
        } else {
            // Affiche l'erreur si l'utilisateur n'est pas admin par exemple 🚫
            alert("Erreur : " + (data.detail || "Impossible de lancer le scan 😱"));
        }
    } catch (error) {
        console.error("Erreur scan:", error);
        alert("Le serveur ne répond pas... 😩");
    }
}