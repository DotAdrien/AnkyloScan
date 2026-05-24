document.addEventListener('alpine:init', () => {
    Alpine.data('dashboard', () => ({
        stats: { scans: 0, agents: 0 },
        chartInstance: null,

        async init() {
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
                console.error("Error loading stats:", error);
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
                console.error("Error loading graph:", error);
            }
        },

        renderChart(data) {
            const ctx = document.getElementById('scanChart');
            if (!ctx) return;

            if (this.chartInstance) {
                this.chartInstance.destroy();
            }

            const labels = data.map(item => item.date);
            const vulnData = data.map(item => item.vulns);
            const logData = data.map(item => item.logs);

            this.chartInstance = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: labels,
                    datasets: [
                        {
                            label: 'Vulnérabilités détectées',
                            data: vulnData,
                            borderColor: '#e74c3c', // Rouge
                            backgroundColor: 'rgba(231, 76, 60, 0.1)',
                            borderWidth: 3,
                            tension: 0.3, // Courbe un peu lisse
                            fill: true
                        },
                        {
                            label: 'Logs Agents',
                            data: logData,
                            borderColor: '#3498db', // Bleu
                            backgroundColor: 'rgba(52, 152, 219, 0.1)',
                            borderWidth: 3,
                            tension: 0.3,
                            fill: true
                        }
                    ]
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