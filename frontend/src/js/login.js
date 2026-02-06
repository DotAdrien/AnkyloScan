async function submitLogin(context) { 
    const emailInput = document.querySelector('input[type="email"]');
    const passwordInput = document.querySelector('input[type="password"]');

    if (!emailInput || !passwordInput) return;


        const response = await fetch(`${window.API_BASE}/auth/login`, {
            method: 'POST',
            credentials: 'include', // Très important pour les cookies 🍪
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                email: emailInput.value,
                password: passwordInput.value
            })
        });

        const data = await response.json();

        if (response.ok) {
            // Petit délai pour laisser le navigateur digérer le cookie ⏱️
            setTimeout(async () => {
                context.user = fetchMe(); 
                await context.changePage('profile'); 
            }, 100);
        } else {
            alert(data.detail || "Email ou mot de passe incorrect ❌");
        }
    }

function logout() {
    document.cookie = "session_token=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
    location.reload(); 
}