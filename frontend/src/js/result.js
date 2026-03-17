// result.js - Gestion de l'historique et des rapports

async function loadScanHistory() {
    const listContainer = document.querySelector('.result-list');
    listContainer.innerHTML = '<div style="text-align:center; padding: 2rem; color: #ec4899;">Chargement des archives... 🦖</div>';

    try {
        // Récupération de l'historique
        const response = await fetch(`${window.API_BASE}/db/history`, { credentials: 'include' });
        if (!response.ok) throw new Error("Impossible de charger l'historique");
        
        const scans = await response.json();

        if (scans.length === 0) {
            listContainer.innerHTML = '<div style="text-align:center; padding: 2rem;">Aucun scan effectué pour le moment. 🤷‍♂️</div>';
            return;
        }

        // Construction du HTML pour la liste
        listContainer.innerHTML = scans.map(scan => `
            <div style="background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.1); border-radius: 12px; padding: 1rem; margin-bottom: 1rem; display: flex; justify-content: space-between; align-items: center;">
                <div style="display: flex; align-items: center; gap: 1rem;">
                    <div style="font-size: 2rem;">${scan.status === 0 ? '⏳' : scan.status === -1 ? '❌' : getScanIcon(parseInt(scan.type))}</div>
                    <div>
                        <h4 style="margin: 0; color: #fff;">Scan #${scan.id} <span style="font-size:0.8rem; color:#9ca3af;">(${scan.time})</span></h4>
                        <p style="margin: 0.2rem 0 0 0; color: ${scan.status === 0 ? '#fbbf24' : scan.status === -1 ? '#ef4444' : '#d1d5db'}; font-size: 0.9rem;">${scan.status === -1 ? 'Échec du scan 😱' : scan.description}</p>
                    </div>
                </div>
                <div style="display: flex; gap: 0.5rem; flex-direction: column; min-width: 140px;">
                    ${scan.status === 1 ? `
                        <button onclick="viewReport('${scan.file_path}')" class="btn-detail" style="width: 100%; text-align: center; padding: 0.5rem; font-size: 0.8rem;">
                            Voir Rapport 📄
                        </button>
                        ${parseInt(scan.type) === 3 ? `
                            <button onclick="viewVulns('${scan.file_path}')" class="btn-detail" style="width: 100%; text-align: center; padding: 0.5rem; font-size: 0.8rem; background-color: #f97316; color: white; border: none;">
                                Vulnérabilités 😱
                            </button>
                        ` : ''}
                    ` : scan.status === 0 ? `
                        <button disabled class="btn-detail" style="width: 100%; text-align: center; padding: 0.5rem; font-size: 0.8rem; background-color: #4b5563; color: #9ca3af; cursor: not-allowed; border: none;">
                            En cours... 🚀
                        </button>
                    ` : `
                        <button disabled class="btn-detail" style="width: 100%; text-align: center; padding: 0.5rem; font-size: 0.8rem; background-color: #7f1d1d; color: #fca5a5; cursor: not-allowed; border: none;">
                            Erreur ⚠️
                        </button>
                    `}
                </div>
            </div>
        `).join('');

    } catch (error) {
        console.error(error);
        listContainer.innerHTML = `<div style="color: #ef4444; text-align: center;">Erreur : ${error.message}</div>`;
    }
}

function getScanIcon(type) {
    const icons = { 1: '🔍', 2: '🛡️', 3: '🦖' };
    return icons[type] || '📁';
}

async function viewReport(path) {
    const viewer = document.getElementById('report-viewer');
    const content = document.getElementById('report-content');
    viewer.style.display = 'block';
    content.innerText = "Chargement du rapport...";

    try {
        const res = await fetch(`${window.API_BASE}/db/report?path=${encodeURIComponent(path)}`, { credentials: 'include' });
        if (!res.ok) throw new Error("Fichier introuvable");
        const text = await res.text();
        content.innerText = text;
    } catch (e) {
        content.innerText = "Erreur lors du chargement : " + e.message;
    }
}

async function viewVulns(path) {
    const viewer = document.getElementById('vuln-viewer');
    const content = document.getElementById('vuln-content');
    viewer.style.display = 'block';
    content.innerHTML = '<div style="color:#d1d5db;">Analyse en cours... 🧠</div>';

    try {
        const res = await fetch(`${window.API_BASE}/db/vulns?path=${encodeURIComponent(path)}`, { credentials: 'include' });
        if (!res.ok) throw new Error("Analyse impossible");
        
        const vulns = await res.json();
        
        if (vulns.length === 0) {
            content.innerHTML = '<div style="padding: 1rem; color: #4ade80;">✅ Aucune vulnérabilité majeure détectée par le script expert.</div>';
            return;
        }

        content.innerHTML = vulns.map(host => `
            <div style="margin-bottom: 1.5rem; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 1rem;">
                <h4 style="color: #60a5fa; margin-bottom: 0.5rem;">🌐 Hôte : ${host.ip}</h4>
                ${host.vulns.map(v => `
                    <div style="margin-left: 1rem; margin-bottom: 0.2rem; color: #e5e7eb;">
                        <span style="font-weight: bold;">${v.badge}</span> ${v.title} <span style="color: #9ca3af; font-size: 0.85em;">(${v.state})</span>
                    </div>
                `).join('')}
            </div>
        `).join('');

    } catch (e) {
        content.innerHTML = `<div style="color: #ef4444;">Erreur : ${e.message}</div>`;
    }
}