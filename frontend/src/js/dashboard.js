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
            const counts = data.map(item => item.count);

            this.chartInstance = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: labels,
                    datasets: [{
                        label: 'Detected Vulnerabilities',
                        data: counts,
                        backgroundColor: 'rgba(231, 76, 60, 0.6)',
                        borderColor: 'rgba(231, 76, 60, 1)',
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