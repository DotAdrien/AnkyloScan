const contentArea = document.getElementById('content-area');
const API_BASE_URL = "http://localhost:8001"; //

async function loadPage(pageName) {
    try {
        const response = await fetch(`view/${pageName}.html`);
        if (!response.ok) throw new Error("Fichier introuvable");
        
        const html = await response.text();
        const parser = new DOMParser();
        const doc = parser.parseFromString(html, 'text/html');
        const newContent = doc.querySelector('.container');
        
        contentArea.innerHTML = newContent ? newContent.outerHTML : doc.body.innerHTML;

        // Configuration spécifique selon la page
        setupLinks();
        if (pageName === 'account') {
            handleLogin(); // Active la surveillance du formulaire 👤
        }

    } catch (err) {
        console.error(err);
        contentArea.innerHTML = `<h2>Erreur de chargement 😱</h2><p>${err.message}</p>`;
    }
}

function setupLinks() {
    const links = document.querySelectorAll('.nav-link');
    links.forEach(link => {
        link.onclick = (e) => {
            e.preventDefault();
            const page = link.getAttribute('data-page');
            if(page) loadPage(page);
        };
    });
}

window.onload = () => {
    setupLinks();
    loadPage('landing');
};