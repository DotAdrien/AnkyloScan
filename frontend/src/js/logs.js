async function loadSystemLogs() {
    const listContainer = document.querySelector('.logs-list');
    if (!listContainer) return;

    try {
        const response = await fetch(`${window.API_BASE}/logs/`, {credentials: 'include'});
        const logs = await response.json();

        listContainer.innerHTML = logs.map(log => `
            <div class="result-card">
                <div class="result-header">
                    <span class="scan-badge security">Event ID: ${log.event_id}</span>
                    <span class="scan-time">${log.timestamp}</span>
                </div>
                <div class="result-body">
                    <p style="color: #ec4899;"><strong>Source:</strong> ${log.source}</p>
                    <p>${log.message}</p>
                </div>
            </div>
        `).join('');
    } catch (error) {
        listContainer.innerHTML = "<p>Erreur lors du chargement 😱</p>";
    }
}