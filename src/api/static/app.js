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
        const status = await response.json();

        // Update status display
        document.getElementById('uptime').textContent = formatUptime(status.uptime_seconds);
        document.getElementById('cycles-completed').textContent = status.worker.current_cycle;
        document.getElementById('worker-status').textContent = status.worker.status === 'running' ? '🟢 Running' : '🔴 Stopped';
        document.getElementById('db-status').textContent = `${status.database.total_alerts} alerts, ${status.database.total_cycles} cycles`;

    } catch (error) {
        console.error('Failed to load status:', error);
        document.getElementById('worker-status').textContent = '⚠️ Error loading';
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
        const metrics = await response.json();

        // Update metrics display
        document.getElementById('avg-duration').textContent = `${metrics.performance.avg_cycle_duration_seconds.toFixed(1)}s`;
        document.getElementById('avg-opportunities').textContent = metrics.performance.avg_opportunities_per_cycle.toFixed(1);
        document.getElementById('avg-alerts').textContent = metrics.performance.avg_alerts_per_cycle.toFixed(1);
        document.getElementById('total-errors').textContent = metrics.performance.total_errors;

        // Update charts
        updateCharts(metrics);

    } catch (error) {
        console.error('Failed to load metrics:', error);
    }
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
