// affichage.js 🎨

document.addEventListener('DOMContentLoaded', () => {
    // 1. Fonction pour vérifier si le cookie de session existe 🍪
    function checkSessionCookie() {
        return document.cookie.split(';').some((item) => item.trim().startsWith('session_token='));
    }

    // 2. Sélection des boutons de navigation (on se base sur les noms dans Alpine.js)
    const isConnected = checkSessionCookie();
    const navContainer = document.querySelector('.nav-links');

    if (navContainer) {
        // Liste des pages selon l'état de connexion 👤
        const publicPages = ['landing', 'about', 'contact'];
        const privatePages = ['work', 'email', 'result',  'agent', 'logs', 'contact'];

        const pagesToShow = isConnected ? privatePages : publicPages;

        // 3. Mise à jour du contenu du menu 🛠️
        // Note : On vide et on reconstruit pour correspondre à la logique de ton index.html
        navContainer.innerHTML = pagesToShow.map(item => `
            <button @click="changePage('${item}')" 
                    class="nav-btn"
                    :class="currentPage === '${item}' ? 'active' : ''">
                ${item === 'work' ? 'SCAN' : item.toUpperCase()}
            </button>
        `).join('');
    }
});