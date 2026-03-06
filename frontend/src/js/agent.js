async function downloadAgent() {
    if (!confirm("Veux tu telecharger l'agent ?")) return;
    window.location.href = `${window.API_BASE}/agent/download`;
}

async function clearTokens() {
    if (!confirm("Attention, cela va supprimer tous les agents. Tu es sûr ? 🫣")) return;

    try {
        const response = await fetch(`${window.API_BASE}/agent/clear`, {
            method: 'DELETE',
            credentials: 'include'
        });
        
        const data = await response.json();
        
        if (response.ok) {
            alert(data.message || "Table vidée ! 😌");
        } else {
            alert("Erreur : " + (data.detail || "Échec 😱"));
        }
    } catch (error) {
        alert("Le serveur ne répond pas... 😩");
    }
}