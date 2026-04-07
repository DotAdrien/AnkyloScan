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
            alert("Success! The server has taken over. You can now close this page.");
        } else {
            const data = await response.json();
            alert("Error: " + (data.detail || "Scheduling failed"));
        }
    } catch (error) {
        alert("Connection error with the server...");
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
            alert("Scan started!\n" + (data.message || ""));
        } else {
            alert("Error: " + (data.detail || "Scan failed"));
        }
    } catch (error) {
        alert("The server is not responding...");
    }
}

function runQuickScan() { callScanAPI('quick'); }
function runSecurityScan() { callScanAPI('security'); }
function runFullScan() { callScanAPI('full'); }