async function loadScanHistory() {
    const listContainer = document.querySelector('.result-list');
    listContainer.innerHTML = '<div style="text-align:center; padding: 2rem; color: #ec4899;">Loading archives... 🦖</div>';

    try {
        const response = await fetch(`${window.API_BASE}/db/history`, { credentials: 'include' });
        if (!response.ok) throw new Error("Unable to load history");
        
        const scans = await response.json();

        if (scans.length === 0) {
            listContainer.innerHTML = '<div style="text-align:center; padding: 2rem;">No scans performed yet. 🤷‍♂️</div>';
            return;
        }

        listContainer.innerHTML = scans.map(scan => `
            <div style="background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.1); border-radius: 12px; padding: 1rem; margin-bottom: 1rem; display: flex; justify-content: space-between; align-items: center;">
                <div style="display: flex; align-items: center; gap: 1rem;">
                    <div style="font-size: 2rem;">${scan.status === 0 ? '⏳' : scan.status === -1 ? '❌' : getScanIcon(parseInt(scan.type))}</div>
                    <div>
                        <h4 style="margin: 0; color: #fff;">Scan #${scan.id} <span style="font-size:0.8rem; color:#9ca3af;">(${scan.time})</span></h4>
                        <p style="margin: 0.2rem 0 0 0; color: ${scan.status === 0 ? '#fbbf24' : scan.status === -1 ? '#ef4444' : '#d1d5db'}; font-size: 0.9rem;">${scan.status === -1 ? 'Scan failed 😱' : scan.description}</p>
                    </div>
                </div>
                <div style="display: flex; gap: 0.5rem; flex-direction: column; min-width: 140px;">
                    ${scan.status === 1 ? `
                        <button onclick="viewReport('${scan.file_path}')" class="btn-detail" style="width: 100%; text-align: center; padding: 0.5rem; font-size: 0.8rem;">
                            View Report 📄
                        </button>
                        ${parseInt(scan.type) === 3 ? `
                            <button onclick="viewVulns('${scan.file_path}')" class="btn-detail" style="width: 100%; text-align: center; padding: 0.5rem; font-size: 0.8rem; background-color: #f97316; color: white; border: none;">
                                Vulnerabilities 😱
                            </button>
                        ` : ''}
                    ` : scan.status === 0 ? `
                        <button disabled class="btn-detail" style="width: 100%; text-align: center; padding: 0.5rem; font-size: 0.8rem; background-color: #4b5563; color: #9ca3af; cursor: not-allowed; border: none;">
                            In progress... 🚀
                        </button>
                    ` : `
                        <button disabled class="btn-detail" style="width: 100%; text-align: center; padding: 0.5rem; font-size: 0.8rem; background-color: #7f1d1d; color: #fca5a5; cursor: not-allowed; border: none;">
                            Error ⚠️
                        </button>
                    `}
                </div>
            `;
        }).join('');

    } catch (error) {
        console.error(error);
        listContainer.innerHTML = `<div style="color: #ef4444; text-align: center;">Error: ${error.message}</div>`;
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
    content.innerText = "Loading report...";

    try {
        const res = await fetch(`${window.API_BASE}/db/report?path=${encodeURIComponent(path)}`, { credentials: 'include' });
        if (!res.ok) throw new Error("File not found");
        const text = await res.text();
        content.innerText = text;
    } catch (e) {
        content.innerText = "Loading error: " + e.message;
    }
}

async function viewVulns(path) {
    const viewer = document.getElementById('vuln-viewer');
    const content = document.getElementById('vuln-content');
    viewer.style.display = 'block';
    content.innerHTML = '<div style="color:#d1d5db;">Analysis in progress... 🧠</div>';

    try {
        const res = await fetch(`${window.API_BASE}/db/vulns?path=${encodeURIComponent(path)}`, { credentials: 'include' });
        if (!res.ok) throw new Error("Analysis impossible");
        
        const vulns = await res.json();
        
        if (vulns.length === 0) {
            content.innerHTML = '<div style="padding: 1rem; color: #4ade80;">✅ No major vulnerabilities detected by the expert script.</div>';
            return;
        }

        content.innerHTML = vulns.map(host => `
            <div style="margin-bottom: 1.5rem; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 1rem;">
                <h4 style="color: #60a5fa; margin-bottom: 0.5rem;">🌐 Host: ${host.ip}</h4>
                ${host.ports ? host.ports.map(portObj => `
                    <div style="margin-left: 0.5rem; margin-bottom: 0.5rem;">
                        <h5 style="color: #fbbf24; margin: 0.5rem 0;">↳ Port: ${portObj.port}</h5>
                        ${portObj.vulns ? portObj.vulns.map(v => `
                            <div style="margin-left: 1.5rem; margin-bottom: 0.2rem; color: #e5e7eb;">
                                <span style="font-weight: bold;">${v.badge}</span> ${v.title} <span style="color: #9ca3af; font-size: 0.85em;">(${v.state})</span>
                            </div>
                        `).join('') : ''}
                    </div>
                `).join('') : ''}
            </div>
        `).join('');

    } catch (e) {
        content.innerHTML = `<div style="color: #ef4444;">Error: ${e.message}</div>`;
    }
}