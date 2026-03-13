document.addEventListener('alpine:init', () => {
    Alpine.data('dashboard', () => ({
        stats: { scans: 0, agents: 0 },
        chartInstance: null,

        async init() {
            // Charge les données dès que le composant est monté
            await this.loadStats();
            await this.loadGraph();
        },

        async loadStats() {
            try {
                const response = await fetch(`${window.API_BASE}/dashboard/stats`, { credentials: 'include' });
                if (response.ok) {
                    this.stats = await response.json();
                }
            } catch (error) {
                console.error("Erreur chargement stats:", error);
            }
        },

        async loadGraph() {
            try {
                const response = await fetch(`${window.API_BASE}/dashboard/graph`, { credentials: 'include' });
                if (response.ok) {
                    const data = await response.json();
                    this.renderChart(data);
                }
            } catch (error) {
                console.error("Erreur chargement graph:", error);
            }
        },

        renderChart(data) {
            const ctx = document.getElementById('scanChart');
            console.log("Canvas context (ctx):", ctx); // Ajout pour le débogage
            if (!ctx) return;

            // Si un graphique existe déjà, on le détruit pour éviter les bugs
            if (this.chartInstance) {
                this.chartInstance.destroy();
            }

            
            const labels = data.map(item => item.date);
            console.log("Données du graphique reçues :", data); // Ajout pour le débogage
            const counts = data.map(item => item.count);

            this.chartInstance = new Chart(ctx, {
                type: 'bar', // ou 'line'
                data: {
                    labels: labels,
                    datasets: [{
                        label: 'Nombre de Scans',
                        data: counts,
                        backgroundColor: 'rgba(54, 162, 235, 0.6)',
                        borderColor: 'rgba(54, 162, 235, 1)',
                        borderWidth: 1,
                        borderRadius: 5
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: true,
                            grid: { color: '#333' }
                        },
                        x: {
                            grid: { display: false }
                        }
                    },
                    plugins: {
                        legend: { labels: { color: 'white' } }
                    }
                }
            });
        }
    }));
});
