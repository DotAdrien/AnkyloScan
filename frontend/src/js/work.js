async function saveAndScheduleScan() {
    const frequency = document.getElementById('scan-frequency').value;
    const type = document.getElementById('scan-type-select').value;

    try {
        const response = await fetch(`${window.API_BASE}/plan/save`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                frequency: parseInt(frequency),
                scan_type: parseInt(type)
            })
        });

        if (response.ok) {
            alert("C'est bon ! Le serveur a pris le relais. Tu peux fermer la page. 🌷");
        }
    } catch (error) {
        alert("Erreur de connexion avec le serveur... 😩");
    }
}

async function callScanAPI(endpoint) {
    try {
        const response = await fetch(`${window.API_BASE}/scan/${endpoint}`, {
            method: 'POST',
            credentials: 'include'
        });
        const data = await response.json();

        if (response.ok) {
            alert("Analyse lancée ! 🦖\n" + (data.message || ""));
        } else {
            alert("Erreur : " + (data.detail || "Échec du scan 😱"));
        }
    } catch (error) {
        alert("Le serveur ne répond pas... 😩");
    }
}

function runQuickScan() { callScanAPI('quick'); }
function runSecurityScan() { callScanAPI('security'); }
function runFullScan() { callScanAPI('full'); }