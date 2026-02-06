async function submitLogin(context) { 
    const emailInput = document.querySelector('input[type="email"]');
    const passwordInput = document.querySelector('input[type="password"]');

    if (!emailInput || !passwordInput) return;

    try {
        // Détection automatique de l'IP pour l'auth 👤
        const response = await fetch(`${window.API_BASE}/auth/login`, {
            method: 'POST',
            credentials: 'include',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                email: emailInput.value,
                password: passwordInput.value
            })
        });

        const data = await response.json();

        if (response.ok) {
            context.user = fetchMe(); 
            await context.changePage('profile'); 
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
    location.reload(); 
}