window.initAdminSetup = async () => {
    const loginForm = document.querySelector('.login-container form');
    if (!loginForm) return;

    try {
        const response = await fetch(`${window.API_BASE}/auth/check-init`);
        const data = await response.json();

        if (data.initialized === false) {
            enableSetupMode(loginForm);
        }
    } catch (error) {
        console.error("Failed to verify initialization status", error);
    }
};

document.addEventListener('DOMContentLoaded', window.initAdminSetup);

function enableSetupMode(existingForm) {
    const container = existingForm.parentElement;
    const title = container.querySelector('.auth-title') || container.querySelector('h1, h2, h3');
    if (title) title.innerText = "Welcome! Create your Admin account";

    const newForm = document.createElement('form');
    
    newForm.innerHTML = `
        <div class="form-group">
            <label for="setup-name" class="form-label">Display Name</label>
            <input type="text" id="setup-name" class="form-input" required placeholder="e.g. System Admin">
        </div>
        
        <div class="form-group">
            <label for="setup-email" class="form-label">Email</label>
            <input type="email" id="setup-email" class="form-input" required placeholder="admin@ankyloscan.local">
        </div>

        <div class="form-group">
            <label for="setup-password" class="form-label">Master Password</label>
            <input type="password" id="setup-password" class="form-input" required placeholder="••••••••">
        </div>

        <button type="submit" class="btn-login" style="background-color: #e67e22;">Create Admin & Start</button>
    `;

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
                location.reload();
            } else {
                alert("Error: " + result.detail);
            }
        } catch (err) {
            alert("Connection error with the server");
        }
    });
}