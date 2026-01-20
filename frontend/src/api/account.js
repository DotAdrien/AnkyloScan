// frontend/src/api_js/api.js

const API_BASE_URL = "http://localhost:8001"; // L'URL de ton API Python 🦖

export async function checkAuth() {
    try {
        const response = await fetch(`${API_BASE_URL}/auth/me`, {
            method: 'GET',
            credentials: 'include' // Important pour envoyer le cookie de Tigrounet 🍪
        });

        if (!response.ok) {
            throw new Error("Non autorisé ❌");
        }

        return await response.json();
    } catch (error) {
        console.error("Erreur d'authentification :", error);
        return null;
    }
}