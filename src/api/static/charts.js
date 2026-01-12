// Chart.js visualizations for the dashboard

let opportunitiesChart = null;
let severityChart = null;

function updateCharts(metrics) {
    updateOpportunitiesChart(metrics.opportunities.by_cycle);
    updateSeverityChart(metrics.alerts.by_severity);
}

function updateOpportunitiesChart(data) {
    const ctx = document.getElementById('opportunities-chart').getContext('2d');

    // Destroy existing chart if it exists
    if (opportunitiesChart) {
        opportunitiesChart.destroy();
    }

    // Create new chart
    opportunitiesChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.map((_, i) => `Cycle ${i + 1}`),
            datasets: [{
                label: 'Opportunities Detected',
                data: data,
                borderColor: '#8b5cf6',
                backgroundColor: 'rgba(139, 92, 246, 0.1)',
                borderWidth: 2,
                tension: 0.4,
                fill: true,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    labels: {
                        color: '#cbd5e1'
                    }
                },
                title: {
                    display: true,
                    text: 'Opportunities Over Last 10 Cycles',
                    color: '#f1f5f9',
                    font: {
                        size: 14,
                        weight: '600'
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        color: '#cbd5e1',
                        stepSize: 1
                    },
                    grid: {
                        color: '#334155'
                    }
                },
                x: {
                    ticks: {
                        color: '#cbd5e1'
                    },
                    grid: {
                        color: '#334155'
                    }
                }
            }
        }
    });
}

function updateSeverityChart(severityData) {
    const ctx = document.getElementById('severity-chart').getContext('2d');

    // Destroy existing chart if it exists
    if (severityChart) {
        severityChart.destroy();
    }

    const labels = Object.keys(severityData);
    const data = Object.values(severityData);
    const colors = {
        'CRITICAL': '#dc2626',
        'WARNING': '#f59e0b',
        'INFO': '#3b82f6'
    };

    // Create new chart
    severityChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: labels.map(label => colors[label] || '#64748b'),
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    position: 'bottom',
                    labels: {
                        color: '#cbd5e1',
                        padding: 15
                    }
                },
                title: {
                    display: true,
                    text: 'Alert Severity Distribution',
                    color: '#f1f5f9',
                    font: {
                        size: 14,
                        weight: '600'
                    }
                }
            }
        }
    });
}
