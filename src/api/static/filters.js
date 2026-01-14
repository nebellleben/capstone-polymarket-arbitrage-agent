/**
 * Filter Panel Component
 *
 * Provides comprehensive filtering for alerts including:
 * - Full-text search (debounced)
 * - Severity filters
 * - Confidence range slider
 * - Date range picker
 * - Market ID filter
 */

class FilterPanel {
    constructor(containerId, onFilterChange) {
        this.containerId = containerId;
        this.container = document.getElementById(containerId);
        this.onFilterChange = onFilterChange;

        // Default filter state
        this.filters = {
            severity: [], // ['CRITICAL', 'WARNING', 'INFO']
            minConfidence: 0,
            maxConfidence: 100,
            startDate: null,
            endDate: null,
            marketId: '',
            searchQuery: ''
        };

        // Debounce timer for search
        this.debounceTimer = null;
        this.debounceMs = 300;
    }

    /**
     * Initialize the filter panel
     */
    initialize() {
        if (!this.container) {
            console.error(`Filter container ${this.containerId} not found`);
            return false;
        }

        this.render();
        this.attachEventListeners();
        return true;
    }

    /**
     * Render the filter panel UI
     */
    render() {
        this.container.innerHTML = `
            <div class="filter-panel">
                <div class="filter-header">
                    <h3>Filters</h3>
                    <div class="filter-actions">
                        <span class="filter-count" id="filter-count">No filters active</span>
                        <button class="btn-reset-filters" id="reset-filters">Reset</button>
                    </div>
                </div>

                <!-- Search -->
                <div class="filter-section">
                    <label class="filter-label">Search</label>
                    <input
                        type="text"
                        class="filter-input search-input"
                        id="filter-search"
                        placeholder="Search title, message, news..."
                        value="${this.escapeHtml(this.filters.searchQuery)}"
                    />
                    <div class="filter-hint">Searches across title, message, reasoning, news, and market question</div>
                </div>

                <!-- Severity Filter -->
                <div class="filter-section">
                    <label class="filter-label">Severity</label>
                    <div class="checkbox-group">
                        <label class="checkbox-item">
                            <input type="checkbox" value="CRITICAL" class="severity-checkbox"
                                ${this.filters.severity.includes('CRITICAL') ? 'checked' : ''} />
                            <span class="severity-indicator critical"></span>
                            Critical
                        </label>
                        <label class="checkbox-item">
                            <input type="checkbox" value="WARNING" class="severity-checkbox"
                                ${this.filters.severity.includes('WARNING') ? 'checked' : ''} />
                            <span class="severity-indicator warning"></span>
                            Warning
                        </label>
                        <label class="checkbox-item">
                            <input type="checkbox" value="INFO" class="severity-checkbox"
                                ${this.filters.severity.includes('INFO') ? 'checked' : ''} />
                            <span class="severity-indicator info"></span>
                            Info
                        </label>
                    </div>
                </div>

                <!-- Confidence Range -->
                <div class="filter-section">
                    <label class="filter-label">Confidence Range</label>
                    <div class="range-slider-container">
                        <div class="range-inputs">
                            <input
                                type="number"
                                class="range-input min-input"
                                id="min-confidence"
                                min="0"
                                max="100"
                                value="${this.filters.minConfidence}"
                                placeholder="Min"
                            />
                            <span class="range-separator">-</span>
                            <input
                                type="number"
                                class="range-input max-input"
                                id="max-confidence"
                                min="0"
                                max="100"
                                value="${this.filters.maxConfidence}"
                                placeholder="Max"
                            />
                            <span class="range-unit">%</span>
                        </div>
                        <input
                            type="range"
                            class="range-slider"
                            id="confidence-slider"
                            min="0"
                            max="100"
                            value="${this.filters.minConfidence}"
                            disabled
                        />
                    </div>
                </div>

                <!-- Date Range -->
                <div class="filter-section">
                    <label class="filter-label">Date Range</label>
                    <div class="date-inputs">
                        <div class="date-input-group">
                            <label class="date-label">From:</label>
                            <input
                                type="datetime-local"
                                class="date-input"
                                id="start-date"
                            />
                        </div>
                        <div class="date-input-group">
                            <label class="date-label">To:</label>
                            <input
                                type="datetime-local"
                                class="date-input"
                                id="end-date"
                            />
                        </div>
                    </div>
                </div>

                <!-- Market ID -->
                <div class="filter-section">
                    <label class="filter-label">Market ID</label>
                    <input
                        type="text"
                        class="filter-input"
                        id="filter-market-id"
                        placeholder="Enter market ID..."
                        value="${this.escapeHtml(this.filters.marketId)}"
                    />
                </div>

                <!-- Active Filter Chips -->
                <div class="filter-section" id="active-filters-section" style="display: none;">
                    <label class="filter-label">Active Filters</label>
                    <div class="active-filters" id="active-filters"></div>
                </div>
            </div>
        `;
    }

    /**
     * Attach event listeners to filter inputs
     */
    attachEventListeners() {
        // Search input with debouncing
        const searchInput = document.getElementById('filter-search');
        searchInput.addEventListener('input', (e) => {
            clearTimeout(this.debounceTimer);
            this.debounceTimer = setTimeout(() => {
                this.filters.searchQuery = e.target.value;
                this.applyFilters();
            }, this.debounceMs);
        });

        // Severity checkboxes
        const severityCheckboxes = this.container.querySelectorAll('.severity-checkbox');
        severityCheckboxes.forEach(checkbox => {
            checkbox.addEventListener('change', () => {
                this.updateSeverityFilters();
                this.applyFilters();
            });
        });

        // Confidence range inputs
        const minConfidence = document.getElementById('min-confidence');
        const maxConfidence = document.getElementById('max-confidence');

        minConfidence.addEventListener('change', (e) => {
            this.filters.minConfidence = parseFloat(e.target.value) || 0;
            this.applyFilters();
        });

        maxConfidence.addEventListener('change', (e) => {
            this.filters.maxConfidence = parseFloat(e.target.value) || 100;
            this.applyFilters();
        });

        // Date inputs
        const startDate = document.getElementById('start-date');
        const endDate = document.getElementById('end-date');

        startDate.addEventListener('change', (e) => {
            this.filters.startDate = e.target.value ? new Date(e.target.value) : null;
            this.applyFilters();
        });

        endDate.addEventListener('change', (e) => {
            this.filters.endDate = e.target.value ? new Date(e.target.value) : null;
            this.applyFilters();
        });

        // Market ID input
        const marketIdInput = document.getElementById('filter-market-id');
        marketIdInput.addEventListener('input', (e) => {
            this.filters.marketId = e.target.value;
            this.applyFilters();
        });

        // Reset button
        document.getElementById('reset-filters').addEventListener('click', () => {
            this.reset();
        });
    }

    /**
     * Update severity filters from checkboxes
     */
    updateSeverityFilters() {
        const checkboxes = this.container.querySelectorAll('.severity-checkbox:checked');
        this.filters.severity = Array.from(checkboxes).map(cb => cb.value);
    }

    /**
     * Apply filters and trigger callback
     */
    applyFilters() {
        this.updateFilterCount();
        this.updateActiveFilterChips();

        if (this.onFilterChange) {
            this.onFilterChange(this.getFilters());
        }
    }

    /**
     * Get current filters (for API calls)
     */
    getFilters() {
        const filters = { ...this.filters };

        // Convert percentage to decimal for API
        filters.minConfidence = filters.minConfidence / 100;
        filters.maxConfidence = filters.maxConfidence / 100;

        // Remove empty filters
        if (filters.severity.length === 0) delete filters.severity;
        if (!filters.searchQuery) delete filters.searchQuery;
        if (!filters.marketId) delete filters.marketId;
        if (!filters.startDate) delete filters.startDate;
        if (!filters.endDate) delete filters.endDate;

        return filters;
    }

    /**
     * Update the filter count badge
     */
    updateFilterCount() {
        const countElement = document.getElementById('filter-count');
        let activeCount = 0;

        if (this.filters.searchQuery) activeCount++;
        if (this.filters.severity.length > 0) activeCount++;
        if (this.filters.minConfidence > 0 || this.filters.maxConfidence < 100) activeCount++;
        if (this.filters.startDate || this.filters.endDate) activeCount++;
        if (this.filters.marketId) activeCount++;

        if (activeCount === 0) {
            countElement.textContent = 'No filters active';
            countElement.className = 'filter-count inactive';
        } else {
            countElement.textContent = `${activeCount} filter${activeCount > 1 ? 's' : ''} active`;
            countElement.className = 'filter-count active';
        }
    }

    /**
     * Update active filter chips display
     */
    updateActiveFilterChips() {
        const section = document.getElementById('active-filters-section');
        const container = document.getElementById('active-filters');
        container.innerHTML = '';

        const chips = [];

        // Severity chips
        this.filters.severity.forEach(sev => {
            chips.push({
                label: sev,
                onRemove: () => {
                    const checkbox = this.container.querySelector(`.severity-checkbox[value="${sev}"]`);
                    if (checkbox) checkbox.checked = false;
                    this.updateSeverityFilters();
                    this.applyFilters();
                }
            });
        });

        // Search query chip
        if (this.filters.searchQuery) {
            chips.push({
                label: `Search: "${this.filters.searchQuery}"`,
                onRemove: () => {
                    document.getElementById('filter-search').value = '';
                    this.filters.searchQuery = '';
                    this.applyFilters();
                }
            });
        }

        // Confidence range chip
        if (this.filters.minConfidence > 0 || this.filters.maxConfidence < 100) {
            chips.push({
                label: `Confidence: ${this.filters.minConfidence}-${this.filters.maxConfidence}%`,
                onRemove: () => {
                    document.getElementById('min-confidence').value = 0;
                    document.getElementById('max-confidence').value = 100;
                    this.filters.minConfidence = 0;
                    this.filters.maxConfidence = 100;
                    this.applyFilters();
                }
            });
        }

        // Market ID chip
        if (this.filters.marketId) {
            chips.push({
                label: `Market: ${this.filters.marketId}`,
                onRemove: () => {
                    document.getElementById('filter-market-id').value = '';
                    this.filters.marketId = '';
                    this.applyFilters();
                }
            });
        }

        // Show/hide section and render chips
        if (chips.length > 0) {
            section.style.display = 'block';
            chips.forEach(chip => {
                const chipElement = document.createElement('div');
                chipElement.className = 'filter-chip';
                chipElement.innerHTML = `
                    ${this.escapeHtml(chip.label)}
                    <button class="chip-remove">×</button>
                `;
                chipElement.querySelector('.chip-remove').addEventListener('click', chip.onRemove);
                container.appendChild(chipElement);
            });
        } else {
            section.style.display = 'none';
        }
    }

    /**
     * Reset all filters to default
     */
    reset() {
        this.filters = {
            severity: [],
            minConfidence: 0,
            maxConfidence: 100,
            startDate: null,
            endDate: null,
            marketId: '',
            searchQuery: ''
        };

        this.render();
        this.attachEventListeners();
        this.applyFilters();
    }

    /**
     * Escape HTML to prevent XSS
     */
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text || '';
        return div.innerHTML;
    }
}
