// Polymarket Arbitrage Agent Dashboard Application

// API base URL
const API_BASE = '/api';

// State
let ws = null;
let reconnectAttempts = 0;
const MAX_RECONNECT_ATTEMPTS = 5;

// Initialize on page load
document.addEventListener('DOMContentLoaded', async () => {
    console.log('Dashboard initializing...');

    // Set up event listeners
    document.getElementById('refresh-alerts').addEventListener('click', loadAlerts);

    // Initialize navigation
    initializeNavigation();

    // Initial data load
    await Promise.all([
        loadStatus(),
        loadAlerts(),
        loadMetrics(),
    ]);

    // Initialize WebSocket connection
    connectWebSocket();

    // Update last update time
    updateLastUpdateTime();
});

/**
 * Initialize navigation tabs
 */
function initializeNavigation() {
    const tabs = document.querySelectorAll('.nav-tab');

    tabs.forEach(tab => {
        tab.addEventListener('click', (e) => {
            const viewName = e.target.dataset.view;
            switchView(viewName);
        });
    });

    // Check URL hash for initial view
    const hash = window.location.hash.slice(1);
    if (hash && ['overview', 'alerts', 'timeline', 'analytics', 'markets'].includes(hash)) {
        switchView(hash);
    }
}

/**
 * Switch between views
 */
function switchView(viewName) {
    console.log('Switching to view:', viewName);

    // Hide all views
    document.querySelectorAll('.view').forEach(view => {
        view.classList.remove('active');
    });

    // Remove active class from all tabs
    document.querySelectorAll('.nav-tab').forEach(tab => {
        tab.classList.remove('active');
    });

    // Show selected view
    const selectedView = document.getElementById(`view-${viewName}`);
    if (selectedView) {
        selectedView.classList.add('active');
    }

    // Activate corresponding tab
    const selectedTab = document.querySelector(`[data-view="${viewName}"]`);
    if (selectedTab) {
        selectedTab.classList.add('active');
    }

    // Update URL hash
    window.location.hash = viewName;

    // Load view-specific data
    loadViewData(viewName);
}

/**
 * Load data for specific view
 */
async function loadViewData(viewName) {
    console.log('Loading data for view:', viewName);

    switch (viewName) {
        case 'overview':
            // Already loaded on page init
            break;

        case 'alerts':
            await loadAlertsHistoryView();
            break;

        case 'timeline':
            await loadTimelineView();
            break;

        case 'analytics':
            await loadAnalyticsView();
            break;

        case 'markets':
            await loadMarketsView();
            break;
    }
}

/**
 * Load alerts history view
 */
async function loadAlertsHistoryView() {
    console.log('Loading alerts history view');

    // Check if filter panel is initialized
    const filterPanelContainer = document.getElementById('filter-panel');
    if (!filterPanelContainer.hasAttribute('data-initialized')) {
        // Initialize filter panel
        const filterPanel = new FilterPanel('filter-panel', (filters) => {
            // Reload alerts when filters change
            loadAlertsHistory(filters);
        });
        filterPanel.initialize();
        filterPanelContainer.setAttribute('data-initialized', 'true');

        // Store globally for access
        window.filterPanel = filterPanel;
    }

    // Load initial alerts
    await loadAlertsHistory();
}

/**
 * Load alerts history with filters
 */
async function loadAlertsHistory(filters = {}) {
    try {
        const params = new URLSearchParams({
            limit: '50',
            offset: '0'
        });

        // Add filters
        if (filters.severity && filters.severity.length > 0) {
            params.append('severity', filters.severity[0]);
        }
        if (filters.minConfidence !== undefined) {
            params.append('min_confidence', filters.minConfidence);
        }
        if (filters.maxConfidence !== undefined) {
            params.append('max_confidence', filters.maxConfidence);
        }
        if (filters.searchQuery) {
            params.append('search_query', filters.searchQuery);
        }

        const response = await fetch(`${API_BASE}/alerts/history?${params}`);
        const data = await response.json();

        // Initialize alert cards manager
        alertCards.initialize('alerts-history-container');
        alertCards.clear();

        // Add alerts
        data.alerts.forEach(alert => {
            alertCards.addAlert(alert);
        });

        // Update pagination info
        document.getElementById('pagination-info').textContent =
            `Showing ${data.alerts.length} of ${data.total} alerts`;

    } catch (error) {
        console.error('Failed to load alerts history:', error);
        document.getElementById('alerts-history-container').innerHTML =
            '<div class="loading">Failed to load alerts</div>';
    }
}

/**
 * Load timeline view
 */
async function loadTimelineView() {
    console.log('Loading timeline view');

    await timelineView.initialize();
    await timelineView.loadTimeline();
}

/**
 * Load analytics view
 */
async function loadAnalyticsView() {
    console.log('Loading analytics view');

    // Load markets for dropdown
    try {
        const response = await fetch(`${API_BASE}/markets/leaderboard?min_alerts=1&limit=50`);
        const markets = await response.json();

        const marketSelect = document.getElementById('market-select');
        marketSelect.innerHTML = '<option value="">Select a market...</option>';

        markets.forEach(market => {
            const option = document.createElement('option');
            option.value = market.market_id;
            option.textContent = market.question.substring(0, 50) + '...';
            marketSelect.appendChild(option);
        });

        // Listen for market selection
        marketSelect.addEventListener('change', (e) => {
            if (e.target.value) {
                loadPriceTrendChart(e.target.value);
            }
        });

        // Load scatter plot with all alerts
        await loadScatterPlot();

    } catch (error) {
        console.error('Failed to load markets:', error);
    }
}

/**
 * Load confidence vs profit scatter plot
 */
async function loadScatterPlot() {
    try {
        // Fetch all alerts for scatter plot
        const response = await fetch(`${API_BASE}/alerts/history?limit=200`);
        const data = await response.json();

        if (data.alerts.length === 0) {
            console.log('No alerts for scatter plot');
            return;
        }

        // Create scatter plot
        confidenceProfitScatter.create(data.alerts);

    } catch (error) {
        console.error('Failed to load scatter plot:', error);
    }
}

/**
 * Load price trend chart for a market
 */
async function loadPriceTrendChart(marketId) {
    try {
        const response = await fetch(`${API_BASE}/alerts/price-trends?market_id=${marketId}`);
        const data = await response.json();

        // Use enhanced price trend chart
        priceTrendChart.create(marketId, data);

    } catch (error) {
        console.error('Failed to load price trends:', error);
    }
}

/**
 * Load markets leaderboard view
 */
async function loadMarketsView() {
    console.log('Loading markets view');

    try {
        const response = await fetch(`${API_BASE}/markets/leaderboard?min_alerts=1`);
        const markets = await response.json();

        const container = document.getElementById('markets-leaderboard');

        if (markets.length === 0) {
            container.innerHTML = '<div class="empty-state">No markets yet</div>';
            return;
        }

        container.innerHTML = `
            <table class="leaderboard-table">
                <thead>
                    <tr>
                        <th>Rank</th>
                        <th>Market</th>
                        <th>Alerts</th>
                        <th>Avg Discrepancy</th>
                        <th>Avg Confidence</th>
                        <th>Trend</th>
                    </tr>
                </thead>
                <tbody>
                    ${markets.map((market, index) => `
                        <tr>
                            <td>${getRankEmoji(index + 1)}</td>
                            <td>
                                <div class="market-question">${escapeHtml(market.question)}</div>
                            </td>
                            <td><span class="badge">${market.alert_count}</span></td>
                            <td class="${getDiscrepancyClass(market.avg_discrepancy)}">
                                ${(market.avg_discrepancy * 100).toFixed(1)}%
                            </td>
                            <td>
                                <div class="confidence-bar-container">
                                    <div class="confidence-bar" style="width: ${market.avg_confidence * 100}%">
                                        ${(market.avg_confidence * 100).toFixed(0)}%
                                    </div>
                                </div>
                            </td>
                            <td>${getTrendIcon(market.trend)}</td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;

    } catch (error) {
        console.error('Failed to load markets leaderboard:', error);
        document.getElementById('markets-leaderboard').innerHTML =
            '<div class="loading">Failed to load leaderboard</div>';
    }
}

/**
 * Get rank emoji
 */
function getRankEmoji(rank) {
    switch (rank) {
        case 1: return '🥇';
        case 2: return '🥈';
        case 3: return '🥉';
        default: return rank;
    }
}

/**
 * Get discrepancy CSS class
 */
function getDiscrepancyClass(discrepancy) {
    if (discrepancy >= 0.15) return 'discrepancy-high';
    if (discrepancy >= 0.08) return 'discrepancy-medium';
    return 'discrepancy-low';
}

/**
 * Get trend icon
 */
function getTrendIcon(trend) {
    switch (trend) {
        case 'up': return '📈';
        case 'down': return '📉';
        default: return '➡️';
    }
}

// WebSocket connection
function connectWebSocket() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/api/ws`;

    console.log('Connecting to WebSocket:', wsUrl);

    ws = new WebSocket(wsUrl);

    ws.onopen = () => {
        console.log('WebSocket connected');
        updateConnectionStatus('connected');
        reconnectAttempts = 0;
    };

    ws.onmessage = (event) => {
        const message = JSON.parse(event.data);
        console.log('WebSocket message:', message.type);
        handleWebSocketMessage(message);
    };

    ws.onclose = () => {
        console.log('WebSocket disconnected');
        updateConnectionStatus('disconnected');

        // Attempt to reconnect
        if (reconnectAttempts < MAX_RECONNECT_ATTEMPTS) {
            reconnectAttempts++;
            console.log(`Reconnecting... Attempt ${reconnectAttempts}`);
            setTimeout(connectWebSocket, 3000 * reconnectAttempts);
        } else {
            console.error('Max reconnect attempts reached');
        }
    };

    ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        updateConnectionStatus('error');
    };
}

function handleWebSocketMessage(message) {
    switch (message.type) {
        case 'connection_established':
            console.log('Connection confirmed');
            break;

        case 'alert_created':
            console.log('New alert received:', message.data);
            addAlertToUI(message.data);
            updateAlertCounts();
            break;

        case 'cycle_completed':
            console.log('Cycle completed:', message.data);
            loadMetrics();
            loadStatus();
            break;

        case 'metrics_updated':
            console.log('Metrics updated');
            loadMetrics();
            break;

        default:
            console.log('Unknown message type:', message.type);
    }
}

// API calls
async function loadStatus() {
    try {
        const response = await fetch(`${API_BASE}/status`);

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        const status = await response.json();

        // Update status display
        document.getElementById('uptime').textContent = formatUptime(status.uptime_seconds || 0);
        document.getElementById('cycles-completed').textContent = status.worker?.current_cycle || 0;
        document.getElementById('worker-status').textContent =
            status.worker?.status === 'running' ? '🟢 Running' : '🔴 Stopped';
        document.getElementById('db-status').textContent =
            `${status.database?.total_alerts || 0} alerts, ${status.database?.total_cycles || 0} cycles`;

    } catch (error) {
        console.error('Failed to load status:', error);
        document.getElementById('worker-status').textContent = '⚠️ Error loading';
        document.getElementById('db-status').textContent = '⚠️ Error loading';
    }
}

async function loadAlerts() {
    try {
        const response = await fetch(`${API_BASE}/alerts/recent?limit=20`);
        const alerts = await response.json();

        const alertsList = document.getElementById('alerts-list');
        alertsList.innerHTML = '';

        if (alerts.length === 0) {
            alertsList.innerHTML = '<div class="empty-state">No alerts yet. Waiting for arbitrage opportunities...</div>';
            return;
        }

        alerts.forEach(alert => {
            addAlertToUI(alert);
        });

        // Update counts
        updateAlertCounts();

    } catch (error) {
        console.error('Failed to load alerts:', error);
        document.getElementById('alerts-list').innerHTML = '<div class="loading">Failed to load alerts</div>';
    }
}

async function loadMetrics() {
    try {
        const response = await fetch(`${API_BASE}/metrics?cycles=10`);

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        const metrics = await response.json();

        // Check if we have data
        if (!metrics.performance || Object.keys(metrics.performance).length === 0) {
            setMetricsEmpty();
            return;
        }

        // Update metrics display
        const avgDuration = metrics.performance.avg_cycle_duration_seconds ?? 0;
        const avgOpportunities = metrics.performance.avg_opportunities_per_cycle ?? 0;
        const avgAlerts = metrics.performance.avg_alerts_per_cycle ?? 0;
        const totalErrors = metrics.performance.total_errors ?? 0;

        document.getElementById('avg-duration').textContent = avgDuration > 0
            ? `${avgDuration.toFixed(1)}s`
            : 'No data';
        document.getElementById('avg-opportunities').textContent = avgOpportunities > 0
            ? avgOpportunities.toFixed(1)
            : 'No data';
        document.getElementById('avg-alerts').textContent = avgAlerts > 0
            ? avgAlerts.toFixed(1)
            : 'No data';
        document.getElementById('total-errors').textContent = totalErrors;

        // Update charts if we have data
        if (metrics.period && metrics.period.cycles_analyzed > 0) {
            updateCharts(metrics);
        }

    } catch (error) {
        console.error('Failed to load metrics:', error);
        setMetricsError();
    }
}

function setMetricsEmpty() {
    document.getElementById('avg-duration').textContent = 'No cycles yet';
    document.getElementById('avg-opportunities').textContent = 'No cycles yet';
    document.getElementById('avg-alerts').textContent = 'No cycles yet';
    document.getElementById('total-errors').textContent = '0';
}

function setMetricsError() {
    document.getElementById('avg-duration').textContent = 'Error loading';
    document.getElementById('avg-opportunities').textContent = 'Error loading';
    document.getElementById('avg-alerts').textContent = 'Error loading';
    document.getElementById('total-errors').textContent = '-';
}

// UI updates
function addAlertToUI(alert) {
    const alertsList = document.getElementById('alerts-list');

    // Remove empty state if present
    const emptyState = alertsList.querySelector('.empty-state');
    if (emptyState) {
        emptyState.remove();
    }

    // Check if alert already exists
    const existingAlert = document.getElementById(`alert-${alert.id}`);
    if (existingAlert) {
        return; // Alert already displayed
    }

    const alertElement = document.createElement('div');
    alertElement.id = `alert-${alert.id}`;
    alertElement.className = `alert-item ${alert.severity.toLowerCase()}`;

    alertElement.innerHTML = `
        <div class="alert-header">
            <span class="alert-title">${escapeHtml(alert.title)}</span>
            <span class="alert-severity ${alert.severity}">${alert.severity}</span>
        </div>
        <div class="alert-message">${escapeHtml(alert.message)}</div>
        <div class="alert-time">${formatTimestamp(alert.timestamp)}</div>
        <div class="alert-details">
            <div class="alert-detail">
                <span class="alert-detail-label">Confidence</span>
                <span class="alert-detail-value">${(alert.confidence * 100).toFixed(1)}%</span>
            </div>
            <div class="alert-detail">
                <span class="alert-detail-label">Price Discrepancy</span>
                <span class="alert-detail-value">${(alert.discrepancy * 100).toFixed(1)}%</span>
            </div>
            <div class="alert-detail">
                <span class="alert-detail-label">Current Price</span>
                <span class="alert-detail-value">$${alert.current_price.toFixed(2)}</span>
            </div>
            <div class="alert-detail">
                <span class="alert-detail-label">Expected Price</span>
                <span class="alert-detail-value">$${alert.expected_price.toFixed(2)}</span>
            </div>
        </div>
    `;

    // Add to top of list
    alertsList.insertBefore(alertElement, alertsList.firstChild);

    // Keep only recent 50 alerts
    while (alertsList.children.length > 50) {
        alertsList.removeChild(alertsList.lastChild);
    }
}

async function updateAlertCounts() {
    try {
        const response = await fetch(`${API_BASE}/alerts/stats`);
        const stats = await response.json();

        document.getElementById('total-alerts').textContent = stats.total_alerts;

    } catch (error) {
        console.error('Failed to update alert counts:', error);
    }
}

function updateConnectionStatus(status) {
    const statusElement = document.getElementById('connection-status');
    const statusDot = statusElement.querySelector('.status-dot');
    const statusText = statusElement.querySelector('.status-text');

    statusDot.className = 'status-dot';

    switch (status) {
        case 'connected':
            statusDot.classList.add('connected');
            statusText.textContent = 'Live';
            break;
        case 'disconnected':
            statusDot.classList.add('disconnected');
            statusText.textContent = 'Disconnected';
            break;
        case 'error':
            statusDot.classList.add('disconnected');
            statusText.textContent = 'Error';
            break;
        default:
            statusText.textContent = 'Connecting...';
    }
}

function updateLastUpdateTime() {
    const now = new Date();
    document.getElementById('last-update').textContent = now.toLocaleString();
}

// Utility functions
function formatUptime(seconds) {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = Math.floor(seconds % 60);

    if (hours > 0) {
        return `${hours}h ${minutes}m ${secs}s`;
    } else if (minutes > 0) {
        return `${minutes}m ${secs}s`;
    } else {
        return `${secs}s`;
    }
}

function formatTimestamp(timestamp) {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);

    if (diffMins < 1) {
        return 'Just now';
    } else if (diffMins < 60) {
        return `${diffMins} minute${diffMins > 1 ? 's' : ''} ago`;
    } else if (diffMins < 1440) {
        const hours = Math.floor(diffMins / 60);
        return `${hours} hour${hours > 1 ? 's' : ''} ago`;
    } else {
        return date.toLocaleString();
    }
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Auto-refresh metrics every 30 seconds
setInterval(() => {
    loadMetrics();
    loadStatus();
}, 30000);
