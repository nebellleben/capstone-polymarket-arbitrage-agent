/**
 * Timeline View Component
 *
 * Displays alerts chronologically grouped by time intervals (hour, day, week).
 * Shows visual timeline with severity indicators and alert counts.
 */

class TimelineView {
    constructor(containerId) {
        this.containerId = containerId;
        this.container = document.getElementById(containerId);
        this.groupBy = 'hour'; // hour, day, week
        this.data = null;
        this.alerts = [];
    }

    /**
     * Initialize the timeline view
     */
    async initialize() {
        if (!this.container) {
            console.error(`Timeline container ${this.containerId} not found`);
            return false;
        }

        this.renderStructure();
        return true;
    }

    /**
     * Render the basic structure
     */
    renderStructure() {
        this.container.innerHTML = `
            <div class="timeline-view">
                <div class="timeline-header">
                    <h3>Timeline</h3>
                    <div class="timeline-controls">
                        <label class="timeline-label">Group by:</label>
                        <select class="interval-select" id="timeline-interval">
                            <option value="hour" ${this.groupBy === 'hour' ? 'selected' : ''}>Hour</option>
                            <option value="day" ${this.groupBy === 'day' ? 'selected' : ''}>Day</option>
                            <option value="week" ${this.groupBy === 'week' ? 'selected' : ''}>Week</option>
                        </select>
                    </div>
                </div>
                <div class="timeline-container" id="timeline-content">
                    <div class="timeline-loading">Loading timeline...</div>
                </div>
            </div>
        `;

        // Attach event listener for interval change
        const intervalSelect = document.getElementById('timeline-interval');
        intervalSelect.addEventListener('change', (e) => {
            this.setGrouping(e.target.value);
        });
    }

    /**
     * Load timeline data from API
     */
    async loadTimeline(filters = {}) {
        try {
            const params = new URLSearchParams({
                interval: this.groupBy,
                hours: 168 // 7 days max
            });

            // Add optional filters
            if (filters.severity && filters.severity.length > 0) {
                params.append('severity', filters.severity[0]);
            }
            if (filters.minConfidence !== undefined) {
                params.append('min_confidence', filters.minConfidence);
            }

            const response = await fetch(`/api/alerts/timeline?${params}`);
            this.data = await response.json();

            this.render();

        } catch (error) {
            console.error('Failed to load timeline:', error);
            this.showError('Failed to load timeline data');
        }
    }

    /**
     * Render the timeline
     */
    render() {
        const content = document.getElementById('timeline-content');
        if (!content) return;

        if (!this.data || !this.data.groups || this.data.groups.length === 0) {
            content.innerHTML = '<div class="timeline-empty">No alerts in the selected time range</div>';
            return;
        }

        content.innerHTML = '';
        const timelineElement = document.createElement('div');
        timelineElement.className = 'timeline';

        this.data.groups.forEach((group, index) => {
            const groupElement = this.createTimelineGroup(group, index);
            timelineElement.appendChild(groupElement);
        });

        content.appendChild(timelineElement);
    }

    /**
     * Create a timeline group element
     */
    createTimelineGroup(group, index) {
        const groupElement = document.createElement('div');
        groupElement.className = 'timeline-group';

        // Time header
        const timeHeader = document.createElement('div');
        timeHeader.className = 'timeline-time-header';
        timeHeader.innerHTML = `
            <div class="timeline-time">${this.formatTimeHeader(group.timestamp)}</div>
            <div class="timeline-count">${group.count} alert${group.count > 1 ? 's' : ''}</div>
        `;

        // Severity breakdown
        const severityBreakdown = document.createElement('div');
        severityBreakdown.className = 'timeline-severity-breakdown';

        const totalAlerts = group.by_severity.CRITICAL + group.by_severity.WARNING + group.by_severity.INFO;

        if (totalAlerts > 0) {
            severityBreakdown.innerHTML = `
                <div class="severity-bar critical" style="width: ${(group.by_severity.CRITICAL / totalAlerts) * 100}%"
                     title="${group.by_severity.CRITICAL} Critical"></div>
                <div class="severity-bar warning" style="width: ${(group.by_severity.WARNING / totalAlerts) * 100}%"
                     title="${group.by_severity.WARNING} Warning"></div>
                <div class="severity-bar info" style="width: ${(group.by_severity.INFO / totalAlerts) * 100}%"
                     title="${group.by_severity.INFO} Info"></div>
            `;
        }

        // Alerts list (sample alerts)
        const alertsList = document.createElement('div');
        alertsList.className = 'timeline-alerts';

        group.sample_alerts.forEach(alert => {
            const alertElement = this.createTimelineAlert(alert);
            alertsList.appendChild(alertElement);
        });

        // Assemble group
        groupElement.appendChild(timeHeader);
        groupElement.appendChild(severityBreakdown);
        groupElement.appendChild(alertsList);

        return groupElement;
    }

    /**
     * Create a single timeline alert item
     */
    createTimelineAlert(alert) {
        const alertElement = document.createElement('div');
        alertElement.className = `timeline-alert ${alert.severity.toLowerCase()}`;
        alertElement.dataset.alertId = alert.id;

        // Format time
        const time = this.formatAlertTime(alert.timestamp);

        // Severity icon
        const severityIcon = this.getSeverityIcon(alert.severity);

        alertElement.innerHTML = `
            <div class="timeline-alert-marker">${severityIcon}</div>
            <div class="timeline-alert-content">
                <div class="timeline-alert-header">
                    <span class="timeline-alert-time">${time}</span>
                    <span class="timeline-alert-severity ${alert.severity}">${alert.severity}</span>
                </div>
                <div class="timeline-alert-title">${this.escapeHtml(alert.title)}</div>
                <div class="timeline-alert-summary">
                    <span class="confidence-badge">${(alert.confidence * 100).toFixed(0)}% confidence</span>
                    <span class="discrepancy-badge">+${(alert.discrepancy * 100).toFixed(1)}%</span>
                </div>
                <button class="timeline-alert-expand" onclick="timelineView.expandAlert('${alert.id}')">
                    View Details →
                </button>
            </div>
        `;

        return alertElement;
    }

    /**
     * Format time header based on interval
     */
    formatTimeHeader(timestamp) {
        const date = new Date(timestamp);
        const now = new Date();
        const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
        const yesterday = new Date(today);
        yesterday.setDate(yesterday.getDate() - 1);

        const alertDate = new Date(date.getFullYear(), date.getMonth(), date.getDate());

        if (this.groupBy === 'hour') {
            const hours = date.getHours();
            const ampm = hours >= 12 ? 'PM' : 'AM';
            const hour12 = hours % 12 || 12;

            if (alertDate.getTime() === today.getTime()) {
                return `Today ${hour12}:00 ${ampm}`;
            } else if (alertDate.getTime() === yesterday.getTime()) {
                return `Yesterday ${hour12}:00 ${ampm}`;
            } else {
                return `${date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })} ${hour12}:00 ${ampm}`;
            }
        } else if (this.groupBy === 'day') {
            if (alertDate.getTime() === today.getTime()) {
                return 'Today';
            } else if (alertDate.getTime() === yesterday.getTime()) {
                return 'Yesterday';
            } else {
                return date.toLocaleDateString('en-US', { weekday: 'long', month: 'short', day: 'numeric' });
            }
        } else { // week
            const weekStart = new Date(date);
            weekStart.setDate(date.getDate() - date.getDay());
            const weekEnd = new Date(weekStart);
            weekEnd.setDate(weekStart.getDate() + 6);

            return `${weekStart.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })} - ${weekEnd.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}`;
        }
    }

    /**
     * Format alert time
     */
    formatAlertTime(timestamp) {
        const date = new Date(timestamp);
        const hours = date.getHours();
        const minutes = date.getMinutes().toString().padStart(2, '0');
        const ampm = hours >= 12 ? 'PM' : 'AM';
        const hour12 = hours % 12 || 12;

        return `${hour12}:${minutes} ${ampm}`;
    }

    /**
     * Get severity icon
     */
    getSeverityIcon(severity) {
        switch (severity) {
            case 'CRITICAL':
                return '🔴';
            case 'WARNING':
                return '🟡';
            case 'INFO':
                return '🔵';
            default:
                return '⚪';
        }
    }

    /**
     * Expand alert to show full details
     */
    expandAlert(alertId) {
        // This would typically open a modal or navigate to detailed view
        console.log('Expand alert:', alertId);
        // For now, just emit an event or call a callback
        if (this.onAlertClick) {
            this.onAlertClick(alertId);
        }
    }

    /**
     * Set time grouping interval
     */
    setGrouping(interval) {
        this.groupBy = interval;

        // Update select
        const select = document.getElementById('timeline-interval');
        if (select) {
            select.value = interval;
        }

        // Reload data
        this.loadTimeline();
    }

    /**
     * Show error message
     */
    showError(message) {
        const content = document.getElementById('timeline-content');
        if (content) {
            content.innerHTML = `
                <div class="timeline-error">
                    <div class="error-icon">⚠️</div>
                    <div class="error-message">${this.escapeHtml(message)}</div>
                </div>
            `;
        }
    }

    /**
     * Clear timeline
     */
    clear() {
        this.data = null;
        const content = document.getElementById('timeline-content');
        if (content) {
            content.innerHTML = '<div class="timeline-loading">Loading timeline...</div>';
        }
    }

    /**
     * Escape HTML to prevent XSS
     */
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text || '';
        return div.innerHTML;
    }

    /**
     * Set callback for alert click
     */
    onAlertClick(callback) {
        this.onAlertClick = callback;
    }
}

// Global instance
const timelineView = new TimelineView('timeline-view');
