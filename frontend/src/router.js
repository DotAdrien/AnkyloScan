const contentArea = document.getElementById('content-area');

async function loadPage(pageName) {
    console.log("Tentative de chargement de :", pageName); // Pour debugger 🤓
    try {
        const response = await fetch(`view/${pageName}.html`);
        
        if (!response.ok) throw new Error("Fichier introuvable");
        
        const html = await response.text();
        const parser = new DOMParser();
        const doc = parser.parseFromString(html, 'text/html');
        
        // On cherche la section container
        const newContent = doc.querySelector('.container');
        
        if (newContent) {
            contentArea.innerHTML = newContent.outerHTML;
        } else {
            // Si le fichier n'a pas de classe .container, on prend tout le body
            contentArea.innerHTML = doc.body.innerHTML;
        }

        // Relancer les écouteurs de clics pour les nouveaux boutons
        setupLinks();

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

// Initialisation
window.onload = () => {
    setupLinks();
    loadPage('landing'); // Charge landing par défaut
};