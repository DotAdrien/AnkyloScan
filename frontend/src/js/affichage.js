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
        // 3. Styles CSS injectés dynamiquement pour les menus déroulants fluides et modernes 🎨
        if (!document.getElementById('dropdown-styles')) {
            const style = document.createElement('style');
            style.id = 'dropdown-styles';
            style.innerHTML = `
                .nav-dropdown {
                    position: relative;
                    display: inline-block;
                }
                /* Soulignement subtil demandé pour les menus contenant des sous-menus */
                .nav-dropdown > .nav-btn {
                    border-right: 2px solid rgba(255, 255, 255, 0.2);
                    padding-right: 4px;
                    transition: border-color 0.3s ease;
                }
                .nav-dropdown:hover > .nav-btn,
                .nav-dropdown > .nav-btn.active {
                    border-color: #f97316; /* Orange typique de ton thème AnkyloScan */
                }
                /* Apparence de la boîte de sous-menu (fluide et moderne) */
                .nav-dropdown-content {
                    visibility: hidden;
                    opacity: 0;
                    position: absolute;
                    top: 0;
                    left: 100%;
                    transform: translateX(20px);
                    background: rgba(17, 24, 39, 0.95);
                    backdrop-filter: blur(8px);
                    border: 1px solid rgba(255,255,255,0.1);
                    border-radius: 8px;
                    box-shadow: 10px 0 25px rgba(0,0,0,0.5);
                    padding: 0.5rem;
                    z-index: 100;
                    transition: all 0.3s ease;
                    display: flex;
                    flex-direction: row;
                    gap: 0.5rem;
                }
                /* Animation de survol */
                .nav-dropdown:hover .nav-dropdown-content {
                    visibility: visible;
                    opacity: 1;
                    transform: translateX(5px);
                }
                /* Style des boutons du sous-menu */
                .nav-dropdown-content button {
                    background: none;
                    border: none;
                    color: #d1d5db;
                    padding: 1rem 0.5rem;
                    text-align: center;
                    cursor: pointer;
                    font-size: 0.9rem;
                    transition: background 0.2s, color 0.2s;
                    /* On force le texte à la verticale */
                    writing-mode: vertical-rl;
                    transform: rotate(180deg);
                    border-radius: 4px;
                }
                .nav-dropdown-content button:hover {
                    background: rgba(255,255,255,0.05);
                    color: #fff;
                }
                /* Mettre en valeur l'onglet actif dans le sous menu */
                .nav-dropdown-content button.active {
                    color: #f97316;
                    background: rgba(249, 115, 22, 0.1);
                    font-weight: bold;
                }
                /* Petite flèche d'indication pour montrer que c'est un menu déroulant */
                .nav-dropdown > .nav-btn::after {
                    content: ' ▶';
                    font-size: 0.6em;
                    opacity: 0.6;
                    margin: 6px 0;
                    display: inline-block;
                }
            `;
            document.head.appendChild(style);
        }

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
                            class="nav-btn"
                            :class="currentPage === '${sub.id}' ? 'active' : ''">
                        ${sub.label}
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