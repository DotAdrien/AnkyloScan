// list.js 📝 - Logique pour la page Liste

window.wordListManager = function() {
    return {
        newWord: '',
        words: JSON.parse(localStorage.getItem('ankyloscan_word_list')) || [],
        
        addWord() {
            if (this.newWord.trim() !== '') {
                this.words.push(this.newWord.trim());
                this.saveWords();
                this.newWord = ''; // On vide le champ
            }
        },
        removeWord(index) {
            this.words.splice(index, 1);
            this.saveWords();
        },
        saveWords() {
            localStorage.setItem('ankyloscan_word_list', JSON.stringify(this.words));
        }
    }
};