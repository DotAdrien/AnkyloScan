async function downloadAgent(agentId, agentName) {
    // Construit un message personnalisé. S'il n'y a pas de nom, message générique.
    const message = agentName ? `Veux tu telecharger l'agent ${agentName} ?` : "Veux tu telecharger l'agent ?";
    if (!confirm(message)) return;
    
    // Construit l'URL dynamiquement. agentId=1 -> /download, agentId=2 -> /download2
    const endpoint = agentId === 1 ? 'download' : `download${agentId}`;
    window.location.href = `${window.API_BASE}/agent/${endpoint}`;
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