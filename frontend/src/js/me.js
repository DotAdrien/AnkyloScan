// Fonction pour décoder le JWT (le "sac à dos" de données) 🧠
function parseJwt(token) {
    try {
        const base64Url = token.split('.')[1];
        const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
        const jsonPayload = decodeURIComponent(window.atob(base64).split('').map(function(c) {
            return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
        }).join(''));
        return JSON.parse(jsonPayload);
    } catch (e) {
        return null;
    }
}

// Fonction pour extraire le cookie par son nom 🍪
function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
}

function fetchMe() {
    const token = getCookie('session_token');
    if (token) {
        const data = parseJwt(token);
        if (data) {
            return {
                loggedIn: true,
                id: data.user_id,
                name: data.name,
                email: data.email,
                rank: data.rank
            };
        }
    }
    return { loggedIn: false, id: null, name: '', email: '', rank: '' };
}