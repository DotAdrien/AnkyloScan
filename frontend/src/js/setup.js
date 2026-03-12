document.addEventListener('DOMContentLoaded', async () => {
    // On vérifie d'abord si on est sur la page de login (vérification simple si un form existe)
    const loginForm = document.querySelector('form');
    if (!loginForm) return;

    try {
        // Demande au backend si l'admin existe déjà
        const response = await fetch(`${window.API_BASE}/auth/check-init`);
        const data = await response.json();

        // Si initialized est FALSE, c'est qu'il n'y a aucun user. On lance le mode SETUP. 🛠️
        if (data.initialized === false) {
            console.log("⚠️ Aucun utilisateur détecté. Passage en mode Initialisation.");
            enableSetupMode(loginForm);
        }
    } catch (error) {
        console.error("Impossible de vérifier l'état d'initialisation", error);
    }
});

function enableSetupMode(existingForm) {
    // On change le titre de la page ou du conteneur si possible
    const container = existingForm.parentElement;
    const title = container.querySelector('h1, h2, h3');
    if (title) title.innerText = "Bienvenue ! Crée ton compte Admin 🦖";

    // On remplace le HTML du formulaire
    existingForm.innerHTML = `
        <div class="input-group">
            <label for="setup-name">Nom d'affichage</label>
            <input type="text" id="setup-name" required placeholder="Ex: Admin Suprême">
        </div>
        
        <div class="input-group">
            <label for="setup-email">Email</label>
            <input type="email" id="setup-email" required placeholder="admin@ankyloscan.local">
        </div>

        <div class="input-group">
            <label for="setup-password">Mot de passe Maître</label>
            <input type="password" id="setup-password" required placeholder="••••••••">
        </div>

        <button type="submit" class="btn-primary" style="background-color: #e67e22;">Créer l'Admin & Démarrer 🚀</button>
    `;

    // On remplace l'événement de soumission
    // On clone le nœud pour supprimer les anciens event listeners (login)
    const newForm = existingForm.cloneNode(true);
    existingForm.parentNode.replaceChild(newForm, existingForm);

    newForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const name = document.getElementById('setup-name').value;
        const email = document.getElementById('setup-email').value;
        const password = document.getElementById('setup-password').value;

        try {
            const res = await fetch(`${window.API_BASE}/auth/setup`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name, email, password })
            });

            const result = await res.json();

            if (res.ok) {
                alert(result.message);
                location.reload(); // Recharger pour afficher le formulaire de login normal
            } else {
                alert("Erreur : " + result.detail);
            }
        } catch (err) {
            alert("Erreur de connexion au serveur 😱");
        }
    });
}