async function loadScanHistory() {
    const listContainer = document.querySelector('.result-list');
    if (!listContainer) return;

    try {
        const response = await fetch('http://localhost:8001/db/history');
        const scans = await response.json();

        const typeMap = {
            1: { label: 'Rapide 🔍', class: 'quick' },
            2: { label: 'Sécurité 🛡️', class: 'security' },
            3: { label: 'Complet 🦖', class: 'full' }
        };

        listContainer.innerHTML = scans.map(scan => `
            <div class="result-card">
                <div class="result-header">
                    <span class="scan-badge ${typeMap[scan.type].class}">${typeMap[scan.type].label}</span>
                    <span class="scan-time">${scan.time}</span>
                </div>
                <div class="result-body">
                    <p>${scan.description}</p>
                </div>
                <div class="result-footer">
                    <button class="btn-detail" onclick="alert('Scan #${scan.id} : Rapport détaillé bientôt disponible')">Voir le rapport 📄</button>
                </div>
            </div>
        `).join('');
    } catch (error) {
        console.error("Erreur :", error);
    }
}