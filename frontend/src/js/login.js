// On ajoute cette fonction pour lire le token sans requête API 🧠
function parseJwt(token) {
    try {
        const base64Url = token.split('.')[1];
        const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
        return JSON.parse(window.atob(base64));
    } catch (e) {
        return null;
    }
}

async function login() {
    const email = document.querySelector('input[type="email"]').value;
    const password = document.querySelector('input[type="password"]').value;

    try {
        const response = await fetch('http://localhost:8001/auth/login', {
            method: 'POST',
            credentials: 'include',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });

        const data = await response.json();

        if (response.ok) {
            // On décode le token reçu ✨
            const userData = parseJwt(data.token);
            this.user = {
                loggedIn: true,
                id: userData.user_id,
                name: userData.name,
                email: userData.email,
                rank: userData.rank
            };
            await this.changePage('profile');
        } else {
            alert(data.detail || "Erreur ❌");
        }
    } catch (error) {
        alert("Serveur HS... 😱");
    }
}