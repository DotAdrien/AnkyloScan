async function saveEmailConfig() {
    const sender = document.querySelector('input[placeholder="alerte@ankyloscan.com"]').value;
    const apiKey = document.querySelector('input[placeholder="A1B2C3D4E5F6G7H8"]').value;
    const receivers = document.querySelector('input[placeholder="admin@test.com;user@test.com"]').value;

    try {
        const response = await fetch(`${window.API_BASE}/email/save`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                sender: sender,
                api_key: apiKey,
                receivers: receivers
            })
        });

        const data = await response.json();

        if (response.ok) {
            alert(data.message);
        } else {
            alert("Erreur : " + (data.detail || "Impossible de sauvegarder 😱"));
        }
    } catch (error) {
        console.error("Erreur API :", error);
        alert("Le serveur ne répond pas... 😩");
    }
}