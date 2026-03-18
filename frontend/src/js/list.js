function wordList() {
    return {
        words: [],
        newWord: '',
        
        // Charge les mots au chargement de la vue
        async fetchWords() {
            try {
                const response = await fetch(`${window.API_BASE}/liste/`, { credentials: 'include' });
                if (response.ok) {
                    this.words = await response.json();
                }
            } catch (err) {
                console.error("Erreur de chargement :", err);
            }
        },
        
        // Ajoute un mot et rafraîchit la page 🔄
        async addWord() {
            if (!this.newWord.trim()) return;
            try {
                const response = await fetch(`${window.API_BASE}/liste/`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ text: this.newWord }),
                    credentials: 'include'
                });
                if (response.ok) window.location.reload();
            } catch (err) {
                console.error("Erreur d'ajout :", err);
            }
        },
        
        // Supprime un mot et rafraîchit la page 🔄
        async removeWord(id) {
            try {
                const response = await fetch(`${window.API_BASE}/liste/${id}`, {
                    method: 'DELETE',
                    credentials: 'include'
                });
                if (response.ok) window.location.reload();
            } catch (err) {
                console.error("Erreur de suppression :", err);
            }
        }
    };
}