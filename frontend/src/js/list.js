async function loadList() {
    const container = document.getElementById('words-list-container');
    if (!container) return;

    container.innerHTML = '<p style="color: white; grid-column: 1 / -1; text-align: center;">Loading the list... ⏳</p>';

    try {
        const response = await fetch(`${window.API_BASE}/liste`, {
            method: 'GET',
            credentials: 'include'
        });

        if (!response.ok) throw new Error("Error retrieving the list");

        const items = await response.json();
        
        if (items.length === 0) {
            container.innerHTML = '<p style="color: #9ca3af; grid-column: 1 / -1; text-align: center;">The list is empty. No rules ignored. 😌</p>';
            return;
        }

        container.innerHTML = items.map(item => `
            <div class="scan-card" style="display: flex; justify-content: space-between; align-items: center;">
                <div style="overflow: hidden; text-overflow: ellipsis; padding-right: 1rem;">
                    <h3 style="margin-bottom: 0.2rem; font-size: 1.1rem; word-break: break-all;">Host: ${item.host}</h3>
                    <p style="margin: 0; color: #9ca3af; font-size: 0.9rem;">Port: ${item.port}</p>
                </div>
                <button class="btn-action" onclick="deleteWord(${item.id})" style="background: #ef4444; width: auto; padding: 0.5rem 1rem; flex-shrink: 0;">
                    Delete 🗑️
                </button>
            </div>
        `).join('');
    } catch (error) {
        console.error("Error:", error);
        container.innerHTML = '<p style="color: #ef4444; grid-column: 1 / -1; text-align: center;">Unable to load the list 😱</p>';
    }
}

async function addWordToList() {
    const hostInput = document.getElementById('new-host-input');
    const portInput = document.getElementById('new-port-input');
    const host = hostInput.value.trim();
    const port = portInput.value.trim();

    if (!host || !port) return;

    try {
        const response = await fetch(`${window.API_BASE}/liste`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify({ host: host, port: port })
        });

        if (response.ok) {
            hostInput.value = '';
            portInput.value = '';
            loadList();
        } else {
            const data = await response.json();
            alert("Error: " + (data.detail || "Unable to add the rule 😱"));
        }
    } catch (error) {
        console.error("Error:", error);
        alert("The server is not responding... 😩");
    }
}

async function deleteWord(id) {
    if (!confirm("Are you sure you want to delete this rule from the list? 🗑️")) return;

    try {
        const response = await fetch(`${window.API_BASE}/liste/${id}`, {
            method: 'DELETE',
            credentials: 'include'
        });

        if (response.ok) {
            loadList();
        } else {
            const data = await response.json();
            alert("Error: " + (data.detail || "Deletion failed 😱"));
        }
    } catch (error) {
        console.error("Error:", error);
        alert("The server is not responding... 😩");
    }
}