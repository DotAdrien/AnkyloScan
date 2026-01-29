async function fetchMe() {
    try {
        const response = await fetch('http://localhost:8001/auth/me', {
            method: 'GET',
            credentials: 'include' // Obligatoire pour envoyer le cookie session_token 🍪
        });

        if (response.ok) {
            const data = await response.json();
            // On stocke les infos dans l'objet user d'index.html
            this.user = {
                loggedIn: true,
                id: data.user_id,
                message: data.message
            };
        } else {
            this.user = { loggedIn: false };
        }
    } catch (error) {
        console.error("Erreur lors de la récupération du profil 😱:", error);
        this.user = { loggedIn: false };
    }
}