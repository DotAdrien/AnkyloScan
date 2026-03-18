window.wordList = function() {
    return {
        words: [],
        newWord: '',
        
        // init() est appelé automatiquement par Alpine au montage de la vue 🚀
        init() {
            this.fetchWords();
        },

        // Charge les mots depuis la base de données
        async fetchWords() {
            try {
                const response = await fetch(`${window.API_BASE}/liste/`, { credentials: 'include' });
                if (response.ok) {
                    this.words = await response.json();
                }
            } catch (err) {
                console.error("Erreur de chargement :", err);
                if (window.showToast) window.showToast("Erreur de chargement", "error");
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
            if (response.ok) {
                const data = await response.json();
                if (window.showToast) window.showToast(data.message || "Mot ajouté ! ✨", "success");
                this.newWord = ''; // Vide l'input
                this.fetchWords(); // Rafraîchit la liste sans recharger la page
            }
            } catch (err) {
                console.error("Erreur d'ajout :", err);
                if (window.showToast) window.showToast("Erreur lors de l'ajout", "error");
            }
        },
        
        // Supprime un mot et rafraîchit la page 🔄
        async removeWord(id) {
            try {
                const response = await fetch(`${window.API_BASE}/liste/${id}`, {
                    method: 'DELETE',
                    credentials: 'include'
                });
            if (response.ok) {
                const data = await response.json();
                if (window.showToast) window.showToast(data.message || "Mot supprimé ! 🗑️", "success");
                this.fetchWords(); // Rafraîchit la liste sans recharger la page
            }
            } catch (err) {
                console.error("Erreur de suppression :", err);
                if (window.showToast) window.showToast("Erreur lors de la suppression", "error");
            }
        }
    };
};