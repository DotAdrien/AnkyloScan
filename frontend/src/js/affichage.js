document.addEventListener('DOMContentLoaded', () => {
    function checkSessionCookie() {
        return document.cookie.split(';').some((item) => item.trim().startsWith('session_token='));
    }

    const isConnected = checkSessionCookie();
    const navContainer = document.querySelector('.nav-links');

    if (!isConnected) {
        localStorage.removeItem('ankyloscan_last_view');
    }

    if (navContainer) {
        const publicMenu = [
            { id: 'landing', label: 'LANDING' },
            { id: 'about', label: 'ABOUT' },
            { id: 'contact', label: 'CONTACT' }
        ];

        const privateMenu = [
            { id: 'dashboard', label: 'DASHBOARD' },
            { id: 'email', label: 'EMAIL' },
            { 
                id: 'scanner_menu', 
                label: 'SCANNER', 
                sub: [
                    { id: 'work', label: 'SCAN' },
                    { id: 'list', label: 'LIST' },
                    { id: 'result', label: 'RESULTS' }
                ] 
            },
            { 
                id: 'travail_menu', 
                label: 'WORK', 
                sub: [
                    { id: 'agent', label: 'AGENTS' },
                    { id: 'logs', label: 'LOGS' }
                ] 
            }
        ];

        const menuToShow = isConnected ? privateMenu : publicMenu;

        navContainer.innerHTML = menuToShow.map(item => {
            if (item.sub) {
                const subItemsHtml = item.sub.map(sub => `
                    <button @click="changePage('${sub.id}'); localStorage.setItem('ankyloscan_last_view', '${sub.id}')"                            
                            :class="currentPage === '${sub.id}' ? 'active' : ''">
                        <span>${sub.label}</span>
                    </button>
                `).join('');

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