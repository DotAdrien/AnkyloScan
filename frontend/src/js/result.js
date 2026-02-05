async function showReportContent(filePath) {
    // On récupère l'instance Alpine pour changer l'état
    const root = document.querySelector('[x-data]');
    const content = document.getElementById('report-content');
    
    content.innerText = "Chargement... ⏳";
    
    // Accès à l'état Alpine pour déclencher la transition douce
    const alpineData = Alpine.$data(root);
    alpineData.reportVisible = true;

    try {
        const response = await fetch(`http://localhost:8001/db/report?path=${encodeURIComponent(filePath)}`);
        if (!response.ok) throw new Error();
        const text = await response.text();
        content.innerText = text;
    } catch (error) {
        content.innerText = "Le fichier fait sa timide... 😱";
    }
}

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
                    <button class="btn-detail" onclick="showReportContent('${scan.file_path}')">Voir le rapport 📄</button>
                </div>
            </div>
        `).join('');
    } catch (error) {
        console.error("Erreur :", error);
    }
}