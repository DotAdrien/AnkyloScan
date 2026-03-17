async function saveAndScheduleScan() {
    const frequency = document.getElementById('scan-frequency').value;
    const type = document.getElementById('scan-type-select').value;

try {
        const response = await fetch(`${window.API_BASE}/plan/save`, {
            method: 'POST',
            credentials: 'include',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                frequency: parseInt(frequency),
                scan_type: parseInt(type)
            })
        });

        if (response.ok) {
            alert("C'est bon ! Le serveur a pris le relais. Tu peux fermer la page. 🌷");
        } else {
            const data = await response.json();
            alert("Erreur : " + (data.detail || "Échec de la planification 😱"));
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
            alert("Scan envoyé au serveur ! 🦖\nTu peux suivre sa progression globale dans l'onglet RÉSULTATS.");
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