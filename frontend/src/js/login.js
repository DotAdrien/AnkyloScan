async function submitLogin(context) { 
    const emailInput = document.querySelector('input[type="email"]');
    const passwordInput = document.querySelector('input[type="password"]');

    if (!emailInput || !passwordInput) return;

    try {
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
            location.reload();
        } else {
            alert(data.detail || "Incorrect email or password ❌");
        }
    } catch (error) {
        console.error("API Error:", error);
        alert("The AnkyloScan server is not responding... 😱");
    }
}

function logout() {
    document.cookie = "session_token=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
    location.reload(); 
}