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

// Logique de connexion pour account.html 🥵
function handleLogin() {
    const form = document.querySelector('#login-form form');
    if (!form) return;

    form.onsubmit = async (e) => {
        e.preventDefault();
        const email = form.querySelectorAll('input')[0].value;
        const password = form.querySelectorAll('input')[1].value;

        try {
            const response = await fetch(`${API_BASE_URL}/auth/login`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, password })
            });

            const result = await response.json();

            if (response.ok) {
                alert("Content de te revoir ! 🥰"); //
                document.getElementById('login-form').style.display = 'none';
                document.getElementById('profile-view').style.display = 'block';
            } else {
                alert(result.detail || "Accès refusé ❌");
            }
        } catch (error) {
            console.error("Erreur API :", error);
        }
    };
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