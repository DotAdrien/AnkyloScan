async function submitLogin() {
    const emailInput = document.querySelector('input[type="email"]');
    const passwordInput = document.querySelector('input[type="password"]');

    if (!emailInput || !passwordInput) return;

    try {
        const response = await fetch('http://localhost:8001/auth/login', {
            method: 'POST',
            credentials: 'include', // Indispensable pour recevoir le cookie 🍪
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                email: emailInput.value,
                password: passwordInput.value
            })
        });

        const data = await response.json();

        if (response.ok) {
            // On utilise la logique de me.js pour récupérer les infos du nouveau cookie ✨
            this.user = fetchMe(); 
            
            // Redirection vers le profil
            await this.changePage('profile');
        } else {
            alert(data.detail || "Email ou mot de passe incorrect ❌");
        }
    } catch (error) {
        console.error("Erreur API :", error);
        alert("Le serveur AnkyloScan ne répond pas... 😱");
    }
}


function logout() {
    document.cookie = "session_token=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
    location.reload(); // Redémarre pour vider l'état AlpineJS ✨
}