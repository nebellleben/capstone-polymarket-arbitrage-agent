/**
 * Alert Cards Component
 *
 * Provides detailed, expandable alert cards with full information display.
 * Shows news, reasoning, prices, market question, confidence scores, and more.
 */

class AlertCard {
    constructor(alertData) {
        this.data = alertData;
        this.expanded = false;
    }

    /**
     * Render the alert card as HTML string
     */
    render() {
        const severityColor = this.getSeverityColor();
        const confidencePercent = (this.data.confidence * 100).toFixed(1);
        const discrepancyPercent = (this.data.discrepancy * 100).toFixed(1);
        const discrepancyClass = this.getDiscrepancyClass();

        return `
            <div class="alert-card ${severityColor} ${this.expanded ? 'expanded' : ''}" data-alert-id="${this.data.id}">
                <!-- Card Header -->
                <div class="alert-card-header" onclick="alertCards.toggleExpand('${this.data.id}')">
                    <div class="alert-header-left">
                        <span class="alert-severity-badge ${this.data.severity}">${this.data.severity}</span>
                        <span class="alert-card-title">${this.escapeHtml(this.data.title)}</span>
                    </div>
                    <div class="alert-header-right">
                        <span class="alert-timestamp">${this.formatTimestamp(this.data.timestamp)}</span>
                        <button class="expand-toggle" aria-label="Toggle details">
                            ${this.expanded ? '▼' : '▶'}
                        </button>
                    </div>
                </div>

                <!-- Summary View (always visible) -->
                <div class="alert-card-summary">
                    <div class="alert-summary-row">
                        <span class="summary-label">Confidence:</span>
                        <div class="confidence-bar-container">
                            <div class="confidence-bar" style="width: ${confidencePercent}%">
                                <span class="confidence-text">${confidencePercent}%</span>
                            </div>
                        </div>
                    </div>
                    <div class="alert-summary-row">
                        <span class="summary-label">Discrepancy:</span>
                        <span class="summary-value ${discrepancyClass}">+${discrepancyPercent}%</span>
                    </div>
                </div>

                <!-- Expanded Details (hidden by default) -->
                <div class="alert-card-details" style="display: ${this.expanded ? 'block' : 'none'}">
                    <!-- Message -->
                    <div class="alert-detail-section">
                        <h4 class="detail-section-title">Message</h4>
                        <p class="detail-text">${this.escapeHtml(this.data.message)}</p>
                    </div>

                    <!-- News Section -->
                    ${this.data.news_title ? `
                    <div class="alert-detail-section">
                        <h4 class="detail-section-title">News Impact Analysis</h4>
                        <div id="news-impact-${this.data.id}" class="alert-card-news-impact"></div>
                    </div>
                    ` : ''}

                    <!-- Reasoning -->
                    <div class="alert-detail-section">
                        <h4 class="detail-section-title">Reasoning</h4>
                        <p class="detail-text reasoning-text">${this.escapeHtml(this.data.reasoning)}</p>
                    </div>

                    <!-- Market Details -->
                    <div class="alert-detail-section">
                        <h4 class="detail-section-title">Market Analysis</h4>
                        <div class="market-analysis">
                            <div class="market-question">${this.escapeHtml(this.data.market_question)}</div>

                            <!-- Price Comparison -->
                            <div class="price-comparison">
                                <div class="price-bar-container">
                                    <div class="price-bar-label">Current: $${this.data.current_price.toFixed(2)}</div>
                                    <div class="price-bar current-price-bar" style="width: ${(this.data.current_price * 100).toFixed(0)}%"></div>
                                </div>
                                <div class="price-bar-container">
                                    <div class="price-bar-label">Expected: $${this.data.expected_price.toFixed(2)}</div>
                                    <div class="price-bar expected-price-bar" style="width: ${(this.data.expected_price * 100).toFixed(0)}%"></div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Recommended Action -->
                    <div class="alert-detail-section">
                        <h4 class="detail-section-title">Recommended Action</h4>
                        <span class="action-badge ${this.data.recommended_action.toLowerCase()}">${this.escapeHtml(this.data.recommended_action)}</span>
                    </div>

                    <!-- Metadata -->
                    <div class="alert-metadata">
                        <div class="metadata-item">
                            <span class="metadata-label">Alert ID:</span>
                            <code class="alert-id">${this.data.id}</code>
                            <button class="copy-button" onclick="alertCards.copyId('${this.data.id}')" title="Copy ID">📋</button>
                        </div>
                        <div class="metadata-item">
                            <span class="metadata-label">Market ID:</span>
                            <code class="market-id">${this.data.market_id}</code>
                        </div>
                        <div class="metadata-item">
                            <span class="metadata-label">Opportunity ID:</span>
                            <code>${this.data.opportunity_id}</code>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    /**
     * Get color class for severity
     */
    getSeverityColor() {
        switch (this.data.severity) {
            case 'CRITICAL':
                return 'severity-critical';
            case 'WARNING':
                return 'severity-warning';
            case 'INFO':
                return 'severity-info';
            default:
                return '';
        }
    }

    /**
     * Get CSS class for discrepancy level
     */
    getDiscrepancyClass() {
        const discrepancy = this.data.discrepancy;
        if (discrepancy >= 0.15) return 'discrepancy-high';
        if (discrepancy >= 0.08) return 'discrepancy-medium';
        return 'discrepancy-low';
    }

    /**
     * Format timestamp for display
     */
    formatTimestamp(timestamp) {
        const date = new Date(timestamp);
        const now = new Date();
        const diffMs = now - date;
        const diffMins = Math.floor(diffMs / 60000);

        if (diffMins < 1) return 'Just now';
        if (diffMins < 60) return `${diffMins}m ago`;
        if (diffMins < 1440) return `${Math.floor(diffMins / 60)}h ago`;
        return date.toLocaleDateString();
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
     * Toggle expanded state
     */
    toggle() {
        this.expanded = !this.expanded;
        return this.expanded;
    }
}

/**
 * AlertCards Manager
 * Manages multiple alert cards and rendering
 */
class AlertCardsManager {
    constructor() {
        this.cards = new Map(); // alertId -> AlertCard
        this.container = null;
    }

    /**
     * Initialize the manager
     */
    initialize(containerId) {
        this.container = document.getElementById(containerId);
        if (!this.container) {
            console.error(`Container ${containerId} not found`);
            return false;
        }
        return true;
    }

    /**
     * Add or update an alert card
     */
    addAlert(alertData) {
        let card = this.cards.get(alertData.id);

        if (!card) {
            card = new AlertCard(alertData);
            this.cards.set(alertData.id, card);
            this.prependCard(card);

            // Render news impact visualizer after card is added to DOM
            if (alertData.news_title && typeof newsImpactVisualizer !== 'undefined') {
                setTimeout(() => {
                    const container = document.getElementById(`news-impact-${alertData.id}`);
                    if (container) {
                        const visualizer = new NewsImpactVisualizer(`news-impact-${alertData.id}`);
                        visualizer.render(alertData);
                    }
                }, 0);
            }
        } else {
            // Update existing card
            card.data = alertData;
            this.updateCard(card);
        }
    }

    /**
     * Prepend a new card to the container
     */
    prependCard(card) {
        if (!this.container) return;

        const tempDiv = document.createElement('div');
        tempDiv.innerHTML = card.render();
        const cardElement = tempDiv.firstElementChild;

        this.container.insertBefore(cardElement, this.container.firstChild);
    }

    /**
     * Update an existing card in the DOM
     */
    updateCard(card) {
        const existingElement = this.container.querySelector(`[data-alert-id="${card.data.id}"]`);
        if (existingElement) {
            const wasExpanded = card.expanded;
            const tempDiv = document.createElement('div');
            tempDiv.innerHTML = card.render();
            const newElement = tempDiv.firstElementChild;

            existingElement.replaceWith(newElement);

            // Preserve expanded state
            if (wasExpanded) {
                card.expanded = true;
            }
        }
    }

    /**
     * Toggle expanded state for a card
     */
    toggleExpand(alertId) {
        const card = this.cards.get(alertId);
        if (card) {
            card.toggle();
            this.updateCard(card);
        }
    }

    /**
     * Copy alert ID to clipboard
     */
    async copyId(alertId) {
        try {
            await navigator.clipboard.writeText(alertId);
            console.log('Copied alert ID:', alertId);
            // TODO: Show toast notification
        } catch (err) {
            console.error('Failed to copy:', err);
        }
    }

    /**
     * Clear all cards
     */
    clear() {
        this.cards.clear();
        if (this.container) {
            this.container.innerHTML = '';
        }
    }

    /**
     * Remove a specific card
     */
    removeCard(alertId) {
        this.cards.delete(alertId);
        const element = this.container.querySelector(`[data-alert-id="${alertId}"]`);
        if (element) {
            element.remove();
        }
    }

    /**
     * Get total card count
     */
    get count() {
        return this.cards.size;
    }
}

// Global instance
const alertCards = new AlertCardsManager();
