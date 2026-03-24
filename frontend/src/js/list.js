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

        const words = await response.json();
        
        if (words.length === 0) {
            container.innerHTML = '<p style="color: #9ca3af; grid-column: 1 / -1; text-align: center;">The list is empty. No words ignored. 😌</p>';
            return;
        }

        container.innerHTML = words.map(word => `
            <div class="scan-card" style="display: flex; justify-content: space-between; align-items: center;">
                <div style="overflow: hidden; text-overflow: ellipsis; padding-right: 1rem;">
                    <h3 style="margin-bottom: 0.2rem; font-size: 1.1rem; word-break: break-all;">${word.text}</h3>
                </div>
                <button class="btn-action" onclick="deleteWord(${word.id || word.id_liste})" style="background: #ef4444; width: auto; padding: 0.5rem 1rem; flex-shrink: 0;">
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
    const input = document.getElementById('new-word-input');
    const word = input.value.trim();

    if (!word) return;

    try {
        const response = await fetch(`${window.API_BASE}/liste`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify({ text: word })
        });

        if (response.ok) {
            input.value = '';
            loadList();
        } else {
            const data = await response.json();
            alert("Error: " + (data.detail || "Unable to add the word 😱"));
        }
    } catch (error) {
        console.error("Error:", error);
        alert("The server is not responding... 😩");
    }
}

async function deleteWord(id) {
    if (!confirm("Are you sure you want to delete this word from the list? 🗑️")) return;

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