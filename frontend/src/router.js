const contentArea = document.getElementById('content-area');

async function loadPage(pageName) {
    try {
        const response = await fetch(`view/${pageName}.html`);
        if (!response.ok) throw new Error("Fichier introuvable");
        
        const html = await response.text();
        const parser = new DOMParser();
        const doc = parser.parseFromString(html, 'text/html');
        const newContent = doc.querySelector('.container');
        
        contentArea.innerHTML = newContent ? newContent.outerHTML : doc.body.innerHTML;

        setupLinks(); 
        // Le router ne fait plus rien d'autre ! 😌
    } catch (err) {
        console.error(err);
        contentArea.innerHTML = `<h2>Erreur 😱</h2>`;
    }
}

function setupLinks() {
    document.querySelectorAll('.nav-link').forEach(link => {
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