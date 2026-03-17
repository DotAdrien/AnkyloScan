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
        // Liste des pages et configuration des menus 👤
        const publicMenu = [
            { id: 'landing', label: 'LANDING' },
            { id: 'about', label: 'ABOUT' },
            { id: 'contact', label: 'CONTACT' }
        ];

        // La nouvelle arborescence pour les administrateurs avec les groupes 🛠️
        const privateMenu = [
            { id: 'dashboard', label: 'DASHBOARD' },
            { id: 'email', label: 'EMAIL' },
            { 
                id: 'scanner_menu', 
                label: 'SCANNER', 
                sub: [
                    { id: 'work', label: 'SCAN' },
                    { id: 'result', label: 'RÉSULTATS' }
                ] 
            },
            { 
                id: 'travail_menu', 
                label: 'TRAVAIL', 
                sub: [
                    { id: 'agent', label: 'AGENTS' },
                    { id: 'logs', label: 'LOGS' }
                ] 
            }
        ];

        const menuToShow = isConnected ? privateMenu : publicMenu;

        // 4. Génération de la structure HTML des menus et sous-menus
        navContainer.innerHTML = menuToShow.map(item => {
            if (item.sub) {
                // Si l'élément possède un "sub", on crée un menu déroulant
                const subItemsHtml = item.sub.map(sub => `
                    <button @click="changePage('${sub.id}'); localStorage.setItem('ankyloscan_last_view', '${sub.id}')"                            
                            :class="currentPage === '${sub.id}' ? 'active' : ''">
                        <span>${sub.label}</span>
                    </button>
                `).join('');

                // Permet de colorer dynamiquement le bouton parent si l'une des pages de son sous-menu est active avec Alpine !
                const subIdsArray = item.sub.map(s => `'${s.id}'`).join(', ');

                return `
                    <div class="nav-dropdown">
                        <button class="nav-btn" style="cursor: default;" :class="[${subIdsArray}].includes(currentPage) ? 'active' : ''">
                            ${item.label}
                        </button>
                        <div class="nav-dropdown-content">
                            ${subItemsHtml}
                        </div>
                    </div>
                `;
            } else {
                // C'est un bouton standard (Dashboard, Email)
                return `
                    <button @click="changePage('${item.id}'); localStorage.setItem('ankyloscan_last_view', '${item.id}')" 
                            class="nav-btn"
                            :class="currentPage === '${item.id}' ? 'active' : ''">
                        ${item.label}
                    </button>
                `;
            }
        }).join('');
    }
});