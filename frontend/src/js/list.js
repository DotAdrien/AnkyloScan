// list.js 🚫

async function loadList() {
    const container = document.getElementById('words-list-container');
    if (!container) return;

    container.innerHTML = '<p style="color: white; grid-column: 1 / -1; text-align: center;">Chargement de la liste... ⏳</p>';

    try {
        const response = await fetch(`${window.API_BASE}/liste`, {
            method: 'GET',
            credentials: 'include' // Obligatoire pour envoyer le cookie de session 🍪
        });

        if (!response.ok) throw new Error("Erreur de récupération de la liste");

        const words = await response.json();
        
        if (words.length === 0) {
            container.innerHTML = '<p style="color: #9ca3af; grid-column: 1 / -1; text-align: center;">La liste est vide. Aucun mot ignoré. 😌</p>';
            return;
        }

        container.innerHTML = words.map(word => `
            <div class="scan-card" style="display: flex; justify-content: space-between; align-items: center;">
                <div style="overflow: hidden; text-overflow: ellipsis; padding-right: 1rem;">
                    <h3 style="margin-bottom: 0.2rem; font-size: 1.1rem; word-break: break-all;">${word.text}</h3>
                </div>
                <button class="btn-action" onclick="deleteWord(${word.id || word.id_liste})" style="background: #ef4444; width: auto; padding: 0.5rem 1rem; flex-shrink: 0;">
                    Supprimer 🗑️
                </button>
            </div>
        `).join('');
    } catch (error) {
        console.error("Erreur:", error);
        container.innerHTML = '<p style="color: #ef4444; grid-column: 1 / -1; text-align: center;">Impossible de charger la liste 😱</p>';
    }
}

async function addWordToList() {
    const input = document.getElementById('new-word-input');
    const word = input.value.trim();

    if (!word) return;

    try {
        const response = await fetch(`${window.API_BASE}/liste`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify({ text: word })
        });

        if (response.ok) {
            input.value = '';
            loadList(); // Recharge la liste de façon fluide ✨
        } else {
            const data = await response.json();
            alert("Erreur : " + (data.detail || "Impossible d'ajouter le mot 😱"));
        }
    } catch (error) {
        console.error("Erreur:", error);
        alert("Le serveur ne répond pas... 😩");
    }
}

async function deleteWord(id) {
    if (!confirm("Veux-tu vraiment supprimer ce mot de la liste ? 🗑️")) return;

    try {
        const response = await fetch(`${window.API_BASE}/liste/${id}`, {
            method: 'DELETE',
            credentials: 'include'
        });

        if (response.ok) {
            loadList(); // Rafraîchit les cartes après suppression 🧹
        } else {
            const data = await response.json();
            alert("Erreur : " + (data.detail || "Échec de la suppression 😱"));
        }
    } catch (error) {
        console.error("Erreur:", error);
        alert("Le serveur ne répond pas... 😩");
    }
}