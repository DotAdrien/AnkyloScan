async function callScanAPI(endpoint) {
    try {
        const response = await fetch(`http://localhost:8001/scan/${endpoint}`, {
            method: 'POST',
            credentials: 'include'
        });
        const data = await response.json();

        if (response.ok) {
            alert("Analyse terminée ! 🦖\n" + data.output);
        } else {
            alert("Erreur : " + (data.detail || "Échec du scan 😱"));
        }
    } catch (error) {
        alert("Le serveur ne répond pas... 😩");
    }
}

function runQuickScan() {
    callScanAPI('quick');
}

function runSecurityScan() {
    callScanAPI('security');
}

function runFullScan() {
    callScanAPI('full');
}