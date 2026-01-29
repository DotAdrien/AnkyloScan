async function login() {
    const email = document.querySelector('input[type="email"]').value;
    const password = document.querySelector('input[type="password"]').value;

    try {
        const response = await fetch('http://localhost:8001/auth/login', {
            method: 'POST',
            credentials: 'include', // <--- AJOUTE CETTE LIGNE
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                email: email,
                password: password
            })
        });

        const data = await response.json();

        if (response.ok) {
            // On met à jour l'état dans Alpine.js 🔓
            // 'this' fonctionnera si la fonction est appelée depuis le contexte Alpine
            this.user = 1; 
            await this.changePage('profile');
        } else {
            alert(data.detail || "Email ou mot de passe incorrect ❌");
        }
    } catch (error) {
        console.error("Erreur API :", error);
        alert("Le serveur AnkyloScan ne répond pas... 😱");
    }
}