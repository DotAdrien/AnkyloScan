// frontend/src/api/account.js

const API_BASE_URL = "http://localhost:8001";

export async function checkAuth() {
    try {
        const response = await fetch(`${API_BASE_URL}/auth/me`, {
            method: 'GET',
            credentials: 'include'
        });
        if (!response.ok) return null;
        return await response.json();
    } catch (error) {
        // L'API est injoignable 😱
        return null;
    }
}

export async function initAccountPage() {
    const loginForm = document.getElementById('login-form');
    const profileView = document.getElementById('profile-view');
    const userNameDisplay = document.getElementById('user-name');

    // On tente de récupérer le compte
    const user = await checkAuth();

    if (user) {
        // Succès : on affiche le profil 👤
        loginForm.style.display = 'none';
        profileView.style.display = 'block';
        userNameDisplay.innerText = `Bienvenue, ${user.pseudo} ! ✨`;
    } else {
        // Échec ou API hors-ligne : on force la connexion 🔑
        loginForm.style.display = 'block';
        profileView.style.display = 'none';
        console.log("API indisponible ou non connecté, affichage du login. 😶");
    }
}