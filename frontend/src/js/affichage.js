// affichage.js 🎨

document.addEventListener('DOMContentLoaded', () => {
    // 1. Fonction pour vérifier si le cookie de session existe 🍪
    function checkSessionCookie() {
        return document.cookie.split(';').some((item) => item.trim().startsWith('session_token='));
    }

    // 2. Sélection des boutons de navigation (on se base sur les noms dans Alpine.js)
    const isConnected = checkSessionCookie();
    const navContainer = document.querySelector('.nav-links');

    // Si l'utilisateur n'est pas connecté, on oublie la dernière page visitée pour éviter de le renvoyer sur une page privée
    if (!isConnected) {
        localStorage.removeItem('ankyloscan_last_view');
    }

    if (navContainer) {
        // Liste des pages selon l'état de connexion 👤
        const publicPages = ['landing', 'about', 'contact'];
        const privatePages = ['dashboard', 'email', 'work', 'result', 'agent', 'logs'];

        const pagesToShow = isConnected ? privatePages : publicPages;

        // 3. Mise à jour du contenu du menu 🛠️
        // Note : On vide et on reconstruit pour correspondre à la logique de ton index.html
        navContainer.innerHTML = pagesToShow.map(item => `
            <button @click="changePage('${item}'); localStorage.setItem('ankyloscan_last_view', '${item}')" 
                    class="nav-btn"
                    :class="currentPage === '${item}' ? 'active' : ''">
                ${item === 'work' ? 'SCAN' : item.toUpperCase()}
            </button>
        `).join('');
    }
});