/**
 * Enhanced Visualizations Module
 *
 * Provides advanced visualization components:
 * - News Impact Visualizer
 * - Confidence vs Profit Scatter Plot
 * - Enhanced Price Trend Charts
 */

/**
 * News Impact Visualizer
 *
 * Visualizes how news impacted market prices with before/after comparison
 */
class NewsImpactVisualizer {
    constructor(containerId) {
        this.containerId = containerId;
        this.container = document.getElementById(containerId);
    }

    /**
     * Render news impact visualization for an alert
     */
    render(alert) {
        if (!this.container) return;

        const currentPrice = alert.current_price;
        const expectedPrice = alert.expected_price;
        const priceChange = expectedPrice - currentPrice;
        const percentChange = (priceChange / currentPrice) * 100;

        const direction = priceChange > 0 ? 'up' : priceChange < 0 ? 'down' : 'neutral';
        const arrow = direction === 'up' ? '↑' : direction === 'down' ? '↓' : '→';

        this.container.innerHTML = `
            <div class="news-impact-visualizer">
                <div class="impact-header">
                    <h4>News Impact Analysis</h4>
                    <span class="impact-badge ${direction}">${arrow} ${Math.abs(percentChange).toFixed(1)}%</span>
                </div>

                <div class="price-comparison-visual">
                    <div class="price-point before">
                        <div class="price-label">Before News</div>
                        <div class="price-value">$${currentPrice.toFixed(2)}</div>
                    </div>

                    <div class="impact-arrow ${direction}">
                        <div class="arrow-line"></div>
                        <div class="arrow-head">${arrow}</div>
                        <div class="news-icon">📰</div>
                    </div>

                    <div class="price-point after">
                        <div class="price-label">Expected Price</div>
                        <div class="price-value">$${expectedPrice.toFixed(2)}</div>
                    </div>
                </div>

                <div class="impact-details">
                    <div class="impact-row">
                        <span class="impact-label">Price Movement:</span>
                        <span class="impact-value ${direction}">${arrow} $${Math.abs(priceChange).toFixed(2)} (${percentChange > 0 ? '+' : ''}${percentChange.toFixed(1)}%)</span>
                    </div>
                    <div class="impact-row">
                        <span class="impact-label">Confidence:</span>
                        <div class="confidence-visual">
                            <div class="confidence-bar" style="width: ${alert.confidence * 100}%">
                                ${(alert.confidence * 100).toFixed(0)}%
                            </div>
                        </div>
                    </div>
                </div>

                ${alert.news_title ? `
                <div class="news-source-card">
                    <div class="news-source-icon">📰</div>
                    <div class="news-source-content">
                        <div class="news-source-title">${this.escapeHtml(alert.news_title)}</div>
                        <a href="${alert.news_url}" target="_blank" rel="noopener noreferrer" class="news-source-link">
                            Read full article ↗
                        </a>
                    </div>
                </div>
                ` : ''}
            </div>
        `;
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text || '';
        return div.innerHTML;
    }
}

/**
 * Confidence vs Profit Scatter Plot
 *
 * Shows correlation between confidence level and price discrepancy
 */
class ConfidenceProfitScatter {
    constructor(canvasId) {
        this.canvas = document.getElementById(canvasId);
        this.chart = null;
    }

    /**
     * Create/update scatter plot
     */
    create(alerts) {
        if (!this.canvas) return;

        const ctx = this.canvas.getContext('2d');

        // Destroy existing chart if any
        if (this.chart) {
            this.chart.destroy();
        }

        // Prepare data
        const dataPoints = alerts.map(alert => ({
            x: alert.confidence * 100,
            y: alert.discrepancy * 100,
            alert: alert
        }));

        // Color by severity
        const backgroundColors = alerts.map(alert => {
            switch (alert.severity) {
                case 'CRITICAL': return 'rgba(220, 38, 38, 0.7)';
                case 'WARNING': return 'rgba(245, 158, 11, 0.7)';
                case 'INFO': return 'rgba(59, 130, 246, 0.7)';
                default: return 'rgba(107, 114, 128, 0.7)';
            }
        });

        const borderColors = alerts.map(alert => {
            switch (alert.severity) {
                case 'CRITICAL': return 'rgb(220, 38, 38)';
                case 'WARNING': return 'rgb(245, 158, 11)';
                case 'INFO': return 'rgb(59, 130, 246)';
                default: return 'rgb(107, 114, 128)';
            }
        });

        this.chart = new Chart(ctx, {
            type: 'scatter',
            data: {
                datasets: [{
                    label: 'Alerts',
                    data: dataPoints,
                    backgroundColor: backgroundColors,
                    borderColor: borderColors,
                    pointRadius: 8,
                    pointHoverRadius: 12,
                    pointBorderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: {
                        title: {
                            display: true,
                            text: 'Confidence (%)',
                            color: '#cbd5e1',
                            font: { size: 14, weight: '600' }
                        },
                        min: 0,
                        max: 100,
                        ticks: { color: '#94a3b8' },
                        grid: { color: 'rgba(71, 85, 105, 0.3)' }
                    },
                    y: {
                        title: {
                            display: true,
                            text: 'Price Discrepancy (%)',
                            color: '#cbd5e1',
                            font: { size: 14, weight: '600' }
                        },
                        min: 0,
                        max: Math.max(...dataPoints.map(d => d.y)) * 1.2 || 50,
                        ticks: {
                            color: '#94a3b8',
                            callback: (value) => `${value.toFixed(0)}%`
                        },
                        grid: { color: 'rgba(71, 85, 105, 0.3)' }
                    }
                },
                plugins: {
                    legend: {
                        display: true,
                        labels: { color: '#cbd5e1' }
                    },
                    tooltip: {
                        backgroundColor: 'rgba(30, 41, 59, 0.95)',
                        titleColor: '#f1f5f9',
                        bodyColor: '#cbd5e1',
                        borderColor: 'rgba(71, 85, 105, 0.5)',
                        borderWidth: 1,
                        padding: 12,
                        callbacks: {
                            label: (context) => {
                                const point = context.raw;
                                return [
                                    `Confidence: ${point.x.toFixed(1)}%`,
                                    `Discrepancy: ${point.y.toFixed(1)}%`,
                                    `Severity: ${point.alert.severity}`
                                ];
                            },
                            afterLabel: (context) => {
                                const point = context.raw;
                                return point.alert.title.substring(0, 50) + '...';
                            }
                        }
                    },
                    // Quadrant highlights
                    annotation: {
                        annotations: {
                            highQuadrant: {
                                type: 'box',
                                xMin: 70,
                                xMax: 100,
                                yMin: 10,
                                yMax: 50,
                                backgroundColor: 'rgba(16, 185, 129, 0.1)',
                                borderColor: 'rgba(16, 185, 129, 0.3)',
                                borderWidth: 1
                            }
                        }
                    }
                },
                onClick: (event, elements) => {
                    if (elements.length > 0) {
                        const index = elements[0].index;
                        const alert = dataPoints[index].alert;
                        this.onAlertClick(alert);
                    }
                }
            }
        });
    }

    /**
     * Handle alert click
     */
    onAlertClick(alert) {
        console.log('Clicked alert:', alert.id);
        // Trigger callback or navigate to alert details
        if (this.onClickCallback) {
            this.onClickCallback(alert);
        }
    }

    /**
     * Set click callback
     */
    setOnClick(callback) {
        this.onClickCallback = callback;
    }

    /**
     * Clear chart
     */
    clear() {
        if (this.chart) {
            this.chart.destroy();
            this.chart = null;
        }
    }
}

/**
 * Enhanced Price Trend Chart
 *
 * Shows current vs expected prices over time with annotations
 */
class PriceTrendChart {
    constructor(canvasId) {
        this.canvas = document.getElementById(canvasId);
        this.chart = null;
    }

    /**
     * Create/update price trend chart
     */
    create(marketId, data) {
        if (!this.canvas) return;

        const ctx = this.canvas.getContext('2d');

        // Destroy existing chart
        if (this.chart) {
            this.chart.destroy();
        }

        const labels = data.data_points.map(dp => {
            const date = new Date(dp.timestamp);
            return date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
        });

        const currentPrices = data.data_points.map(dp => dp.current_price);
        const expectedPrices = data.data_points.map(dp => dp.expected_price);

        this.chart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [
                    {
                        label: 'Current Price',
                        data: currentPrices,
                        borderColor: '#8b5cf6',
                        backgroundColor: 'rgba(139, 92, 246, 0.1)',
                        borderWidth: 2,
                        tension: 0.4,
                        fill: true,
                        pointRadius: 4,
                        pointHoverRadius: 6
                    },
                    {
                        label: 'Expected Price',
                        data: expectedPrices,
                        borderColor: '#06b6d4',
                        backgroundColor: 'rgba(6, 182, 212, 0.1)',
                        borderWidth: 2,
                        borderDash: [5, 5],
                        tension: 0.4,
                        fill: true,
                        pointRadius: 4,
                        pointHoverRadius: 6
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: {
                        title: {
                            display: true,
                            text: 'Time',
                            color: '#cbd5e1',
                            font: { size: 14, weight: '600' }
                        },
                        ticks: { color: '#94a3b8' },
                        grid: { color: 'rgba(71, 85, 105, 0.3)' }
                    },
                    y: {
                        title: {
                            display: true,
                            text: 'Price ($)',
                            color: '#cbd5e1',
                            font: { size: 14, weight: '600' }
                        },
                        min: 0,
                        max: 1,
                        ticks: {
                            color: '#94a3b8',
                            callback: (value) => `$${value.toFixed(2)}`
                        },
                        grid: { color: 'rgba(71, 85, 105, 0.3)' }
                    }
                },
                plugins: {
                    legend: {
                        display: true,
                        position: 'top',
                        labels: { color: '#cbd5e1' }
                    },
                    tooltip: {
                        mode: 'index',
                        intersect: false,
                        backgroundColor: 'rgba(30, 41, 59, 0.95)',
                        titleColor: '#f1f5f9',
                        bodyColor: '#cbd5e1',
                        borderColor: 'rgba(71, 85, 105, 0.5)',
                        borderWidth: 1,
                        padding: 12,
                        callbacks: {
                            label: (context) => {
                                return `${context.dataset.label}: $${context.raw.toFixed(2)}`;
                            }
                        }
                    }
                },
                interaction: {
                    mode: 'nearest',
                    axis: 'x',
                    intersect: false
                }
            }
        });
    }

    /**
     * Clear chart
     */
    clear() {
        if (this.chart) {
            this.chart.destroy();
            this.chart = null;
        }
    }
}

/**
 * Alert Severity Distribution Chart
 *
 * Doughnut chart showing distribution of alerts by severity
 */
class SeverityDistributionChart {
    constructor(canvasId) {
        this.canvas = document.getElementById(canvasId);
        this.chart = null;
    }

    /**
     * Create/update severity distribution chart
     */
    create(alerts) {
        if (!this.canvas) return;

        const ctx = this.canvas.getContext('2d');

        // Count by severity
        const severityCounts = {
            CRITICAL: 0,
            WARNING: 0,
            INFO: 0
        };

        alerts.forEach(alert => {
            if (severityCounts[alert.severity] !== undefined) {
                severityCounts[alert.severity]++;
            }
        });

        // Destroy existing chart
        if (this.chart) {
            this.chart.destroy();
        }

        this.chart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Critical', 'Warning', 'Info'],
                datasets: [{
                    data: [severityCounts.CRITICAL, severityCounts.WARNING, severityCounts.INFO],
                    backgroundColor: [
                        'rgba(220, 38, 38, 0.8)',
                        'rgba(245, 158, 11, 0.8)',
                        'rgba(59, 130, 246, 0.8)'
                    ],
                    borderColor: [
                        'rgb(220, 38, 38)',
                        'rgb(245, 158, 11)',
                        'rgb(59, 130, 246)'
                    ],
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            color: '#cbd5e1',
                            padding: 15,
                            font: { size: 12 }
                        }
                    },
                    tooltip: {
                        backgroundColor: 'rgba(30, 41, 59, 0.95)',
                        titleColor: '#f1f5f9',
                        bodyColor: '#cbd5e1',
                        borderColor: 'rgba(71, 85, 105, 0.5)',
                        borderWidth: 1,
                        padding: 12,
                        callbacks: {
                            label: (context) => {
                                const label = context.label || '';
                                const value = context.raw || 0;
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = ((value / total) * 100).toFixed(1);
                                return `${label}: ${value} (${percentage}%)`;
                            }
                        }
                    }
                }
            }
        });
    }

    /**
     * Clear chart
     */
    clear() {
        if (this.chart) {
            this.chart.destroy();
            this.chart = null;
        }
    }
}

// Global instances
const newsImpactVisualizer = new NewsImpactVisualizer('news-impact-container');
const confidenceProfitScatter = new ConfidenceProfitScatter('scatter-chart');
const priceTrendChart = new PriceTrendChart('price-trend-chart');
const severityDistributionChart = new SeverityDistributionChart('severity-chart');

console.log('Visualizations module loaded');
