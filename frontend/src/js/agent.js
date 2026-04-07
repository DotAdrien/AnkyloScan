async function downloadAgent(agentId, agentName) {
    const message = agentName ? `Do you want to download agent ${agentName}?` : "Do you want to download the agent?";
    if (!confirm(message)) return;
    
    const endpoint = agentId === 1 ? 'download' : `download${agentId}`;
    window.location.href = `${window.API_BASE}/agent/${endpoint}`;
}

async function clearTokens() {
    if (!confirm("Warning, this will delete all agents. Are you sure? 🫣")) return;

    try {
        const response = await fetch(`${window.API_BASE}/agent/clear`, {
            method: 'DELETE',
            credentials: 'include'
        });
        
        const data = await response.json();
        
        if (response.ok) {
            alert(data.message || "Table cleared! 😌");
        } else {
            alert("Error: " + (data.detail || "Failed 😱"));
        }
    } catch (error) {
        alert("The server is not responding... 😩");
    }
}