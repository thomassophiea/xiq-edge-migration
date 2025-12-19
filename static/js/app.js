// Global state
let state = {
    xiqData: null,
    edgeData: null,
    selectedSsids: [],
    selectedVlans: [],
    selectedRadius: [],
    profileAssignments: {},
    edgeCredentials: null,
    convertedServices: []  // Store converted services for profile assignment
};

// Widget Management System
class WidgetManager {
    constructor() {
        this.widgets = new Map();
        this.preferences = this.loadPreferences();
        this.container = null;
        this.sortable = null;
    }

    loadPreferences() {
        const stored = localStorage.getItem('widgetPreferences');
        if (stored) {
            return JSON.parse(stored);
        }
        return this.getDefaultPreferences();
    }

    getDefaultPreferences() {
        return {
            order: [
                'worst-sites',
                'rate-limiters',
                'cos-policies',
                'topologies',
                'aaa-policies',
                'services',
                'ap-configs',
                'profile-assignments'
            ],
            visibility: {
                'worst-sites': true,
                'rate-limiters': true,
                'cos-policies': true,
                'topologies': true,
                'aaa-policies': true,
                'services': true,
                'ap-configs': true,
                'profile-assignments': true
            },
            sizes: {
                'worst-sites': 'large',
                'rate-limiters': 'medium',
                'cos-policies': 'medium',
                'topologies': 'medium',
                'aaa-policies': 'medium',
                'services': 'medium',
                'ap-configs': 'medium',
                'profile-assignments': 'medium'
            }
        };
    }

    savePreferences() {
        localStorage.setItem('widgetPreferences', JSON.stringify(this.preferences));
    }

    registerWidget(id, element) {
        this.widgets.set(id, element);
    }

    toggleVisibility(widgetId) {
        this.preferences.visibility[widgetId] = !this.preferences.visibility[widgetId];
        this.savePreferences();
        this.applyPreferences();
    }

    setSize(widgetId, size) {
        this.preferences.sizes[widgetId] = size;
        this.savePreferences();
        this.applyPreferences();
    }

    applyPreferences() {
        // Apply visibility
        this.widgets.forEach((element, id) => {
            element.style.display = this.preferences.visibility[id] ? 'flex' : 'none';

            // Remove old size classes
            element.classList.remove('size-small', 'size-medium', 'size-large');

            // Add new size class
            const size = this.preferences.sizes[id] || 'medium';
            element.classList.add(`size-${size}`);
        });

        // Apply order
        if (this.container) {
            this.preferences.order.forEach((id, index) => {
                const element = this.widgets.get(id);
                if (element) {
                    element.style.order = index;
                }
            });
        }
    }

    initializeSortable(container) {
        this.container = container;

        // Initialize SortableJS
        this.sortable = Sortable.create(container, {
            animation: 150,
            handle: '.widget-drag-handle',
            ghostClass: 'sortable-ghost',
            dragClass: 'sortable-drag',
            onEnd: (evt) => {
                // Update order preference
                const newOrder = [];
                const children = Array.from(container.children);
                children.forEach(child => {
                    const widgetId = child.getAttribute('data-widget-id');
                    if (widgetId) {
                        newOrder.push(widgetId);
                    }
                });
                this.preferences.order = newOrder;
                this.savePreferences();
            }
        });
    }

    reset() {
        this.preferences = this.getDefaultPreferences();
        this.savePreferences();
        this.applyPreferences();
    }
}

// Initialize widget manager
const widgetManager = new WidgetManager();

// Cache DOM elements for better performance
const elements = {};

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
    cacheDOMElements();
    initializeTheme();
    setupEventListeners();
    setupTabs();
    startLogPolling();
});

// Cache frequently accessed DOM elements
function cacheDOMElements() {
    elements.progressSection = document.getElementById('progressSection');
    elements.progressBar = document.getElementById('progressBar');
    elements.progressText = document.getElementById('progressText');
    elements.logsPanel = document.getElementById('logsPanel');
    elements.xiqResults = document.getElementById('xiqResults');
    elements.step2 = document.getElementById('step2');
    elements.step3 = document.getElementById('step3');
    elements.step4 = document.getElementById('step4');
    elements.step5 = document.getElementById('step5');
    elements.step6 = document.getElementById('step6');
}

// Setup event listeners
function setupEventListeners() {
    // XIQ Form
    document.getElementById('xiqForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        await connectToXIQ();
    });

    // Edge Form
    document.getElementById('edgeForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        await connectToEdge();
    });
}

// Setup tabs
function setupTabs() {
    const tabButtons = document.querySelectorAll('.tab-button');
    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            const tabName = button.getAttribute('data-tab');
            switchTab(tabName);
        });
    });
}

function switchTab(tabName) {
    // Update buttons
    document.querySelectorAll('.tab-button').forEach(btn => {
        btn.classList.remove('active');
    });
    document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');

    // Update panels
    document.querySelectorAll('.tab-panel').forEach(panel => {
        panel.classList.remove('active');
    });
    document.getElementById(`${tabName}-panel`).classList.add('active');
}

// Connect to XIQ
async function connectToXIQ() {
    const formData = {
        username: document.getElementById('xiqUsername').value,
        password: document.getElementById('xiqPassword').value,
        region: document.getElementById('xiqRegion').value
    };

    updateProgress('Connecting to XIQ...', 10);
    updateStepStatus('step1', 'In Progress');

    try {
        const response = await fetch('/api/connect_xiq', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(formData)
        });

        const result = await response.json();

        if (result.success) {
            state.xiqData = result.data;

            // Update counts
            document.getElementById('xiqSsidCount').textContent = result.data.ssids.length;
            document.getElementById('xiqVlanCount').textContent = result.data.vlans.length;
            document.getElementById('xiqRadiusCount').textContent = result.data.radius_servers.length;
            document.getElementById('xiqDeviceCount').textContent = result.data.devices.length;

            // Show results
            (elements.xiqResults || document.getElementById('xiqResults')).style.display = 'block';
            updateStepStatus('step1', 'Completed');
            updateProgress('XIQ connection successful', 50);

            // Populate selection lists
            populateSelectionLists(result.data);

            // Show step 2
            (elements.step2 || document.getElementById('step2')).style.display = 'block';
            updateStepStatus('step2', 'Ready');
        } else {
            alert('Error: ' + result.error);
            updateStepStatus('step1', 'Error');
        }
    } catch (error) {
        alert('Connection error: ' + error.message);
        updateStepStatus('step1', 'Error');
    }
}

// Populate selection lists
function populateSelectionLists(data) {
    // SSIDs
    const ssidList = document.getElementById('ssidList');
    ssidList.innerHTML = '';
    data.ssids.forEach(ssid => {
        const item = createSelectionItem(ssid.id, ssid.name, '', 'ssids');
        ssidList.appendChild(item);
    });

    // VLANs
    const vlanList = document.getElementById('vlanList');
    vlanList.innerHTML = '';
    data.vlans.forEach(vlan => {
        const item = createSelectionItem(vlan.id, vlan.name, `VLAN ${vlan.vlan_id}`, 'vlans');
        vlanList.appendChild(item);
    });

    // RADIUS
    const radiusList = document.getElementById('radiusList');
    radiusList.innerHTML = '';
    data.radius_servers.forEach(radius => {
        const item = createSelectionItem(radius.id, radius.name, radius.ip, 'radius');
        radiusList.appendChild(item);
    });
}

// Create selection item
function createSelectionItem(id, name, details, category) {
    const div = document.createElement('div');
    div.className = 'selection-item';

    const checkbox = document.createElement('input');
    checkbox.type = 'checkbox';
    checkbox.id = `${category}-${id}`;
    checkbox.value = id;
    checkbox.addEventListener('change', (e) => {
        updateSelection(category, id, e.target.checked);
    });

    const label = document.createElement('label');
    label.className = 'selection-item-label';
    label.htmlFor = `${category}-${id}`;
    label.textContent = name;

    div.appendChild(checkbox);
    div.appendChild(label);

    if (details) {
        const detailsSpan = document.createElement('span');
        detailsSpan.className = 'selection-item-details';
        detailsSpan.textContent = details;
        div.appendChild(detailsSpan);
    }

    return div;
}

// Update selection
function updateSelection(category, id, checked) {
    const categoryMap = {
        'ssids': 'selectedSsids',
        'vlans': 'selectedVlans',
        'radius': 'selectedRadius'
    };

    const stateKey = categoryMap[category];

    if (checked) {
        if (!state[stateKey].includes(id)) {
            state[stateKey].push(id);
        }
    } else {
        state[stateKey] = state[stateKey].filter(item => item !== id);
    }
}

// Select all/none
function selectAll(category) {
    const checkboxes = document.querySelectorAll(`#${category}List input[type="checkbox"]`);
    checkboxes.forEach(cb => {
        cb.checked = true;
        updateSelection(category, cb.value, true);
    });
}

function selectNone(category) {
    const checkboxes = document.querySelectorAll(`#${category}List input[type="checkbox"]`);
    checkboxes.forEach(cb => {
        cb.checked = false;
        updateSelection(category, cb.value, false);
    });
}

// Auto-select VLANs used by selected SSIDs
function autoSelectVlans() {
    if (state.selectedSsids.length === 0) {
        alert('Please select SSIDs first before auto-selecting VLANs.');
        return;
    }

    // First, clear all VLAN selections
    selectNone('vlans');

    // Get selected SSIDs
    const selectedSsids = state.xiqData.ssids.filter(s => state.selectedSsids.includes(s.id));

    // Extract VLAN IDs used by these SSIDs
    const usedVlanIds = new Set();
    selectedSsids.forEach(ssid => {
        // SSIDs can reference VLANs in different ways
        if (ssid.vlan_id) {
            usedVlanIds.add(ssid.vlan_id);
        }
        if (ssid.default_vlan_id) {
            usedVlanIds.add(ssid.default_vlan_id);
        }
    });

    // Find matching VLANs and select them
    state.xiqData.vlans.forEach(vlan => {
        if (usedVlanIds.has(vlan.vlan_id)) {
            const checkbox = document.getElementById(`vlans-${vlan.id}`);
            if (checkbox) {
                checkbox.checked = true;
                updateSelection('vlans', vlan.id, true);
            }
        }
    });

    const count = state.selectedVlans.length;
    alert(`Auto-selected ${count} VLAN${count !== 1 ? 's' : ''} used by selected SSIDs.`);
}

// Proceed to Edge connection
function proceedToEdge() {
    if (state.selectedSsids.length === 0) {
        alert('Please select at least one SSID to migrate.');
        return;
    }

    updateStepStatus('step2', 'Completed');
    (elements.step3 || document.getElementById('step3')).style.display = 'block';
    updateStepStatus('step3', 'Ready');
    (elements.step3 || document.getElementById('step3')).scrollIntoView({ behavior: 'smooth' });
}

// Connect to Edge Services
async function connectToEdge() {
    const formData = {
        controller_url: document.getElementById('edgeUrl').value,
        username: document.getElementById('edgeUsername').value,
        password: document.getElementById('edgePassword').value
    };

    state.edgeCredentials = formData;
    updateProgress('Connecting to Edge Services...', 60);
    updateStepStatus('step3', 'In Progress');

    try {
        const response = await fetch('/api/connect_edge', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(formData)
        });

        const result = await response.json();

        if (result.success) {
            state.edgeData = result.data;

            updateStepStatus('step3', 'Completed');
            updateProgress('Edge Services connection successful', 70);

            // Convert configuration
            await convertConfiguration();
        } else {
            alert('Error: ' + result.error);
            updateStepStatus('step3', 'Error');
        }
    } catch (error) {
        alert('Connection error: ' + error.message);
        updateStepStatus('step3', 'Error');
    }
}

// Display profiles
function displayProfiles(profiles) {
    const profileList = document.getElementById('profileList');
    profileList.innerHTML = '';

    profiles.forEach(profile => {
        const div = document.createElement('div');
        div.className = `profile-item ${profile.is_custom ? 'custom' : 'default'}`;

        div.innerHTML = `
            <div class="profile-name">${profile.name}</div>
            <div class="profile-platform">${profile.platform}</div>
            <span class="profile-badge ${profile.is_custom ? 'custom' : 'default'}">
                ${profile.is_custom ? 'CUSTOM' : 'DEFAULT'}
            </span>
        `;

        profileList.appendChild(div);
    });

    document.getElementById('edgeResults').style.display = 'block';
}

// Convert configuration
async function convertConfiguration() {
    updateProgress('Converting configuration...', 75);

    console.log('=== CONVERSION DEBUG ===');
    console.log('Selected SSID IDs being sent:', state.selectedSsids);
    console.log('  SSID ID value:', state.selectedSsids[0]);
    console.log('  SSID ID type:', typeof state.selectedSsids[0]);
    console.log('All SSIDs in XIQ data:', state.xiqData.ssids.map(s => ({ id: s.id, name: s.name, type: typeof s.id })));
    console.log('Selected VLAN IDs being sent:', state.selectedVlans);
    console.log('Selected RADIUS IDs being sent:', state.selectedRadius);

    try {
        const response = await fetch('/api/convert', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                selected_ssids: state.selectedSsids,
                selected_vlans: state.selectedVlans,
                selected_radius: state.selectedRadius
            })
        });

        const result = await response.json();

        console.log('Services returned from conversion:', result.data.services);
        console.log('Number of services:', result.data.services.length);

        if (result.success) {
            updateProgress('Configuration converted', 80);

            // Store converted services
            state.convertedServices = result.data.services;

            // Show profile assignment step
            buildProfileAssignmentUI(result.data.services, state.edgeData.profiles);

            (elements.step4 || document.getElementById('step4')).style.display = 'block';
            updateStepStatus('step4', 'Ready');
            (elements.step4 || document.getElementById('step4')).scrollIntoView({ behavior: 'smooth' });
        } else {
            alert('Conversion error: ' + result.error);
        }
    } catch (error) {
        alert('Conversion error: ' + error.message);
    }
}

// Build profile assignment UI
function buildProfileAssignmentUI(services, profiles) {
    const container = document.getElementById('profileAssignments');
    container.innerHTML = '';

    // Show only custom profiles by default (filter out all the default profiles)
    const customProfiles = profiles.filter(p => p.is_custom);
    const profilesToShow = customProfiles.length > 0 ? customProfiles : profiles;

    console.log(`Building profile UI for ${services.length} services with ${profilesToShow.length} profiles`);
    console.log('Selected SSID IDs:', state.selectedSsids);
    console.log('Converted services:', services.map(s => ({ id: s.id, name: s.name })));

    services.forEach(service => {
        const section = document.createElement('div');
        section.className = 'assignment-section';

        const header = document.createElement('div');
        header.className = 'assignment-header';
        header.textContent = `SSID: ${service.name}`;
        section.appendChild(header);

        // Add info text
        const info = document.createElement('p');
        info.style.color = 'var(--text-secondary)';
        info.style.marginBottom = '12px';
        info.style.fontSize = '0.9rem';
        info.textContent = `Select which profiles should broadcast this SSID (showing ${profilesToShow.length} ${customProfiles.length > 0 ? 'custom' : ''} profiles)`;
        section.appendChild(info);

        const grid = document.createElement('div');
        grid.className = 'assignment-grid';

        profilesToShow.forEach(profile => {
            const checkboxDiv = document.createElement('div');
            checkboxDiv.className = 'assignment-checkbox';

            const checkbox = document.createElement('input');
            checkbox.type = 'checkbox';
            checkbox.id = `assign-${service.id}-${profile.id}`;
            checkbox.value = profile.id;
            checkbox.addEventListener('change', (e) => {
                updateProfileAssignment(service.id, profile, e.target.checked);
            });

            const label = document.createElement('label');
            label.htmlFor = checkbox.id;
            label.textContent = profile.name;
            label.style.cursor = 'pointer';

            checkboxDiv.appendChild(checkbox);
            checkboxDiv.appendChild(label);
            grid.appendChild(checkboxDiv);
        });

        section.appendChild(grid);

        // Radio selector
        const radioDiv = document.createElement('div');
        radioDiv.className = 'radio-selector';
        radioDiv.id = `radio-${service.id}`;
        radioDiv.innerHTML = `
            <label>Broadcast on which radios?</label>
            <select id="radio-select-${service.id}">
                <option value="0">All radios (2.4GHz + 5GHz + 6GHz)</option>
                <option value="1">Radio 1 only (typically 2.4GHz)</option>
                <option value="2">Radio 2 only (typically 5GHz)</option>
                <option value="3">Radio 3 only (typically 6GHz)</option>
            </select>
        `;
        section.appendChild(radioDiv);

        container.appendChild(section);
    });
}

// Update profile assignment
function updateProfileAssignment(serviceId, profile, checked) {
    if (!state.profileAssignments[serviceId]) {
        state.profileAssignments[serviceId] = [];
    }

    const radioSelect = document.getElementById(`radio-select-${serviceId}`);
    const radioIndex = radioSelect ? parseInt(radioSelect.value) : 0;

    if (checked) {
        // Add assignment
        const existing = state.profileAssignments[serviceId].find(a => a.profile_id === profile.id);
        if (!existing) {
            state.profileAssignments[serviceId].push({
                profile_id: profile.id,
                profile_name: profile.name,
                radio_index: radioIndex
            });
        }
    } else {
        // Remove assignment
        state.profileAssignments[serviceId] = state.profileAssignments[serviceId].filter(
            a => a.profile_id !== profile.id
        );
    }
}

// Assign all SSIDs to all profiles
function assignAllToAll() {
    const services = state.convertedServices;  // Use converted services, not full XIQ data
    const profiles = state.edgeData.profiles;

    services.forEach(service => {
        profiles.forEach(profile => {
            const checkbox = document.getElementById(`assign-${service.id}-${profile.id}`);
            if (checkbox) {
                checkbox.checked = true;
                updateProfileAssignment(service.id, profile, true);
            }
        });
    });

    alert(`Assigned ${services.length} SSID(s) to all profiles on all radios`);
}

// Assign all to custom profiles only
function assignAllToCustom() {
    const services = state.convertedServices;  // Use converted services, not full XIQ data
    const customProfiles = state.edgeData.profiles.filter(p => p.is_custom);

    services.forEach(service => {
        customProfiles.forEach(profile => {
            const checkbox = document.getElementById(`assign-${service.id}-${profile.id}`);
            if (checkbox) {
                checkbox.checked = true;
                updateProfileAssignment(service.id, profile, true);
            }
        });
    });

    alert(`Assigned ${services.length} SSID(s) to ${customProfiles.length} custom profile(s)`);
}

// Proceed to migration
function proceedToMigration() {
    updateStepStatus('step4', 'Completed');

    // Build summary
    const summary = {
        ssids: state.selectedSsids.length,
        vlans: state.selectedVlans.length,
        radius: state.selectedRadius.length,
        assignments: Object.keys(state.profileAssignments).reduce(
            (total, key) => total + state.profileAssignments[key].length, 0
        )
    };

    displayMigrationSummary(summary);

    (elements.step5 || document.getElementById('step5')).style.display = 'block';
    updateStepStatus('step5', 'Ready');
    (elements.step5 || document.getElementById('step5')).scrollIntoView({ behavior: 'smooth' });
}

// Display migration summary
function displayMigrationSummary(summary) {
    const container = document.getElementById('migrationSummary');
    container.innerHTML = `
        <div class="summary-item">
            <span class="label">SSIDs</span>
            <span class="value">${summary.ssids}</span>
        </div>
        <div class="summary-item">
            <span class="label">VLANs</span>
            <span class="value">${summary.vlans}</span>
        </div>
        <div class="summary-item">
            <span class="label">RADIUS Servers</span>
            <span class="value">${summary.radius}</span>
        </div>
        <div class="summary-item">
            <span class="label">Profile Assignments</span>
            <span class="value">${summary.assignments}</span>
        </div>
        <div class="summary-item" style="padding-top: 10px; margin-top: 10px; border-top: 1px solid var(--border-color); grid-column: 1 / -1;">
            <span class="label" style="font-weight: 600; color: var(--primary-color);">Note:</span>
            <span class="value" style="font-size: 0.9em; color: var(--text-medium);">Configure SSID broadcast settings below before executing migration</span>
        </div>
    `;
}

// Execute migration
async function executeMigration() {
    const dryRun = document.getElementById('dryRun').checked;

    // Get SSID status preference
    const ssidStatusRadio = document.querySelector('input[name="ssidStatus"]:checked');
    const ssidStatus = ssidStatusRadio ? ssidStatusRadio.value : 'disabled';

    // Get PDF download preference
    const downloadPdf = document.getElementById('downloadPdfSummary').checked;

    if (!dryRun && !confirm('This will migrate the selected configuration to Edge Services. Are you sure?')) {
        return;
    }

    updateProgress('Executing migration...', 85);
    updateStepStatus('step5', 'In Progress');

    try {
        const response = await fetch('/api/migrate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                controller_url: state.edgeCredentials.controller_url,
                username: state.edgeCredentials.username,
                password: state.edgeCredentials.password,
                dry_run: dryRun,
                profile_assignments: state.profileAssignments,
                ssid_status: ssidStatus  // Add SSID status preference
            })
        });

        const result = await response.json();

        if (result.success) {
            updateProgress('Migration completed!', 100);
            updateStepStatus('step5', 'Completed');

            // Show results
            displayMigrationResults(result.data, dryRun);

            (elements.step6 || document.getElementById('step6')).style.display = 'block';
            updateStepStatus('step6', 'Completed');
            (elements.step6 || document.getElementById('step6')).scrollIntoView({ behavior: 'smooth' });

            // Auto-download PDF summary if requested
            if (downloadPdf && !dryRun) {
                setTimeout(() => {
                    downloadPDFReport();
                }, 1000); // Small delay to let the UI update
            }
        } else {
            alert('Migration error: ' + result.error);
            updateStepStatus('step5', 'Error');
        }
    } catch (error) {
        alert('Migration error: ' + error.message);
        updateStepStatus('step5', 'Error');
    }
}

// Display migration results with widget system
async function displayMigrationResults(data, dryRun) {
    const container = document.getElementById('migrationResults');

    if (dryRun) {
        container.innerHTML = `
            <div class="results">
                <h3>Dry Run Complete</h3>
                <p>Configuration saved to: <code>${data.output_file}</code></p>
                <p>No changes were made to Edge Services.</p>
            </div>
        `;
        return;
    }

    // Create widget controls header
    const controlsHtml = `
        <div class="widget-controls">
            <button class="btn btn-sm" onclick="showWidgetSettings()">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <circle cx="12" cy="12" r="3"></circle>
                    <path d="M12 1v6m0 6v6m8.66-15L17 7.66M7 17l-3.66 3.66M23 12h-6m-6 0H1m15.66 8.66L17 17M7 7 3.34 3.34"></path>
                </svg>
                Customize Widgets
            </button>
            <button class="btn btn-sm" onclick="widgetManager.reset()">Reset Layout</button>
        </div>
    `;

    // Fetch worst sites data
    let worstSitesData = [];
    try {
        const response = await fetch('/api/worst_sites');
        const result = await response.json();
        if (result.success) {
            worstSitesData = result.data;
        }
    } catch (error) {
        console.error('Failed to fetch worst sites:', error);
    }

    // Create results container with grid
    let html = controlsHtml + '<div class="results"><h3>Migration Successful!</h3><div class="results-grid" id="widgetGrid">';

    // Add worst sites widget
    if (worstSitesData.length > 0) {
        html += createWorstSitesWidget(worstSitesData);
    }

    // Add existing widgets
    html += createMigrationWidget('rate-limiters', 'Rate Limiters', data.results.rate_limiters);
    html += createMigrationWidget('cos-policies', 'CoS Policies', data.results.cos_policies);
    html += createMigrationWidget('topologies', 'Topologies', data.results.topologies);
    html += createMigrationWidget('aaa-policies', 'AAA Policies', data.results.aaa_policies);
    html += createMigrationWidget('services', 'Services', data.results.services);
    html += createMigrationWidget('ap-configs', 'AP Configs', data.results.ap_configs);
    html += createMigrationWidget('profile-assignments', 'Profile Assignments', data.results.profile_assignments);

    html += '</div></div>';
    container.innerHTML = html;

    // Register all widgets
    const widgetGrid = document.getElementById('widgetGrid');
    document.querySelectorAll('[data-widget-id]').forEach(element => {
        const widgetId = element.getAttribute('data-widget-id');
        widgetManager.registerWidget(widgetId, element);
    });

    // Initialize sortable and apply preferences
    widgetManager.initializeSortable(widgetGrid);
    widgetManager.applyPreferences();
}

// Create worst sites widget
function createWorstSitesWidget(sites) {
    const sitesHtml = sites.map((site, index) => `
        <div class="site-issue-item">
            <div class="site-rank">#${index + 1}</div>
            <div class="site-info">
                <div class="site-name">${site.name || 'Unknown Site'}</div>
                <div class="site-stats">
                    <span class="stat-badge stat-errors">${site.error_count} errors</span>
                    <span class="stat-badge stat-warnings">${site.warning_count} warnings</span>
                    <span class="stat-badge">${site.device_count} devices</span>
                </div>
                ${site.errors && site.errors.length > 0 ? `
                <div class="site-errors-preview">
                    ${site.errors.map(err => `<div class="error-preview">• ${err}</div>`).join('')}
                </div>
                ` : ''}
            </div>
            <div class="site-score" style="background: ${getScoreColor(site.score)}">
                ${site.score}
            </div>
        </div>
    `).join('');

    return `
        <div class="result-item widget-worst-sites" data-widget-id="worst-sites">
            <div class="widget-header">
                <span class="widget-drag-handle" title="Drag to reorder">⋮⋮</span>
                <span class="result-label">Worst Sites</span>
                <div class="widget-actions">
                    <button class="widget-action-btn" onclick="cycleWidgetSize('worst-sites')" title="Resize">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M15 3h6v6M9 21H3v-6M21 3l-7 7M3 21l-7-7"></path>
                        </svg>
                    </button>
                    <button class="widget-action-btn" onclick="widgetManager.toggleVisibility('worst-sites')" title="Hide">×</button>
                </div>
            </div>
            <div class="widget-content">
                ${sitesHtml}
            </div>
        </div>
    `;
}

// Create standard migration widget
function createMigrationWidget(id, label, result) {
    if (!result) return '';

    const formatResult = (result) => {
        if (typeof result === 'string') {
            const match = result.match(/(\d+\/\d+)/);
            return match ? match[1] : result;
        } else if (result && typeof result === 'object') {
            return `${result.posted || result.updated || 0}/${result.total || 0}`;
        }
        return '0/0';
    };

    return `
        <div class="result-item" data-widget-id="${id}">
            <div class="widget-header">
                <span class="widget-drag-handle" title="Drag to reorder">⋮⋮</span>
                <span class="result-label">${label}</span>
                <div class="widget-actions">
                    <button class="widget-action-btn" onclick="cycleWidgetSize('${id}')" title="Resize">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M15 3h6v6M9 21H3v-6M21 3l-7 7M3 21l-7-7"></path>
                        </svg>
                    </button>
                    <button class="widget-action-btn" onclick="widgetManager.toggleVisibility('${id}')" title="Hide">×</button>
                </div>
            </div>
            <span class="result-value">${formatResult(result)}</span>
        </div>
    `;
}

// Helper: Get color based on score
function getScoreColor(score) {
    if (score >= 20) return '#f44336'; // Red for critical
    if (score >= 10) return '#ff9800'; // Orange for high
    if (score >= 5) return '#ffc107';  // Amber for medium
    return '#4caf50'; // Green for low
}

// Helper: Cycle through widget sizes
function cycleWidgetSize(widgetId) {
    const sizes = ['small', 'medium', 'large'];
    const currentSize = widgetManager.preferences.sizes[widgetId] || 'medium';
    const currentIndex = sizes.indexOf(currentSize);
    const nextSize = sizes[(currentIndex + 1) % sizes.length];
    widgetManager.setSize(widgetId, nextSize);
}

// Show widget settings modal
function showWidgetSettings() {
    // Create modal dynamically
    const modal = document.createElement('div');
    modal.className = 'modal-overlay';
    modal.innerHTML = `
        <div class="modal-content widget-settings-modal">
            <div class="modal-header">
                <h3>Widget Settings</h3>
                <button class="modal-close" onclick="this.closest('.modal-overlay').remove()">×</button>
            </div>
            <div class="modal-body">
                <h4>Visibility</h4>
                <div class="widget-visibility-list">
                    ${Object.entries(widgetManager.preferences.visibility).map(([id, visible]) => `
                        <label class="widget-toggle">
                            <input type="checkbox" ${visible ? 'checked' : ''}
                                   onchange="widgetManager.preferences.visibility['${id}'] = this.checked; widgetManager.savePreferences(); widgetManager.applyPreferences();">
                            <span>${id.replace(/-/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}</span>
                        </label>
                    `).join('')}
                </div>
            </div>
            <div class="modal-footer">
                <button class="btn btn-secondary" onclick="widgetManager.reset(); this.closest('.modal-overlay').remove();">Reset to Defaults</button>
                <button class="btn btn-primary" onclick="this.closest('.modal-overlay').remove();">Done</button>
            </div>
        </div>
    `;
    document.body.appendChild(modal);
}

// Update progress - use cached elements
function updateProgress(message, percent) {
    const progressBar = elements.progressBar || document.getElementById('progressBar');
    const progressText = elements.progressText || document.getElementById('progressText');
    const progressSection = elements.progressSection || document.getElementById('progressSection');

    progressSection.style.display = 'block';
    progressBar.style.width = percent + '%';
    progressBar.textContent = percent + '%';
    progressText.textContent = message;
}

// Update step status
function updateStepStatus(stepId, status) {
    const statusElement = document.getElementById(`${stepId}Status`);
    statusElement.textContent = status;

    // Update colors
    statusElement.style.background = {
        'Pending': 'rgba(255, 255, 255, 0.2)',
        'Ready': 'rgba(255, 193, 7, 0.3)',
        'In Progress': 'rgba(0, 123, 255, 0.3)',
        'Completed': 'rgba(40, 167, 69, 0.3)',
        'Error': 'rgba(220, 53, 69, 0.3)'
    }[status] || 'rgba(255, 255, 255, 0.2)';
}

// Reset migration
async function resetMigration() {
    if (!confirm('Are you sure you want to start over? All progress will be lost.')) {
        return;
    }

    // Reset backend state
    await fetch('/api/reset', { method: 'POST' });

    // Reset frontend state
    state = {
        xiqData: null,
        edgeData: null,
        selectedSsids: [],
        selectedVlans: [],
        selectedRadius: [],
        profileAssignments: {},
        edgeCredentials: null
    };

    // Hide all steps except step 1
    document.getElementById('step2').style.display = 'none';
    document.getElementById('step3').style.display = 'none';
    document.getElementById('step4').style.display = 'none';
    document.getElementById('step5').style.display = 'none';
    document.getElementById('step6').style.display = 'none';
    document.getElementById('progressSection').style.display = 'none';
    document.getElementById('xiqResults').style.display = 'none';
    document.getElementById('edgeResults').style.display = 'none';

    // Reset forms
    document.getElementById('xiqForm').reset();
    document.getElementById('edgeForm').reset();

    // Reset status
    updateStepStatus('step1', 'Pending');
    updateStepStatus('step2', 'Pending');
    updateStepStatus('step3', 'Pending');
    updateStepStatus('step4', 'Pending');
    updateStepStatus('step5', 'Pending');
    updateStepStatus('step6', 'Pending');

    // Scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// Poll for logs - reduced frequency for better performance
function startLogPolling() {
    setInterval(async () => {
        try {
            const response = await fetch('/api/status');
            const result = await response.json();

            if (result.success && result.data.logs.length > 0) {
                updateLogs(result.data.logs);
            }
        } catch (error) {
            // Silently fail - don't spam console
        }
    }, 3000);  // Reduced from 1000ms to 3000ms (3 seconds)
}

// Update logs - optimized to only append new entries
let lastLogCount = 0;

function updateLogs(logs) {
    const logsPanel = elements.logsPanel || document.getElementById('logsPanel');

    // Only append new log entries instead of rebuilding entire list
    const newLogs = logs.slice(lastLogCount);

    if (newLogs.length > 0) {
        const fragment = document.createDocumentFragment();

        newLogs.forEach(log => {
            const entry = document.createElement('div');
            entry.className = 'log-entry';

            entry.innerHTML = `
                <span class="log-timestamp">${log.timestamp}</span>
                <span class="log-level ${log.level}">[${log.level.toUpperCase()}]</span>
                <span class="log-message">${log.message}</span>
            `;

            fragment.appendChild(entry);
        });

        logsPanel.appendChild(fragment);
        lastLogCount = logs.length;

        // Auto-scroll to bottom
        logsPanel.scrollTop = logsPanel.scrollHeight;
    }
}

// Clear logs
function clearLogs() {
    const logsPanel = elements.logsPanel || document.getElementById('logsPanel');
    logsPanel.innerHTML = '';
    lastLogCount = 0;  // Reset the log count
}

// Toggle logs visibility
function toggleLogs() {
    const logsBody = document.getElementById('logsBody');
    const toggleIcon = document.getElementById('logsToggleIcon');

    logsBody.classList.toggle('collapsed');
    toggleIcon.classList.toggle('collapsed');
}

// Theme Management
function initializeTheme() {
    // Get saved preference or default to dark
    const savedTheme = localStorage.getItem('theme') || 'dark';

    // Apply theme
    applyTheme(savedTheme);

    // Update active button to match saved theme
    document.querySelectorAll('.theme-option').forEach(btn => {
        btn.classList.remove('active');
        if (btn.getAttribute('data-theme') === savedTheme) {
            btn.classList.add('active');
        }
    });

    // Set up theme switcher event listeners
    document.querySelectorAll('.theme-option').forEach(button => {
        button.addEventListener('click', () => {
            const theme = button.getAttribute('data-theme');
            setTheme(theme);
        });
    });

    // Listen for system theme changes when in auto mode
    if (window.matchMedia) {
        window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
            const currentTheme = localStorage.getItem('theme');
            if (currentTheme === 'auto') {
                applyTheme('auto');
            }
        });
    }
}

function setTheme(theme) {
    // Save preference
    localStorage.setItem('theme', theme);

    // Apply theme
    applyTheme(theme);

    // Update active button
    document.querySelectorAll('.theme-option').forEach(btn => {
        btn.classList.remove('active');
    });
    document.querySelector(`[data-theme="${theme}"]`).classList.add('active');
}

function applyTheme(theme) {
    const html = document.documentElement;

    if (theme === 'auto') {
        // Detect system preference
        const prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
        html.setAttribute('data-theme', prefersDark ? 'dark' : 'light');
    } else {
        html.setAttribute('data-theme', theme);
    }
}

// PDF Report Download
function downloadPDFReport() {
    // Show loading state
    const button = event.target.closest('button');
    const originalText = button.innerHTML;
    button.disabled = true;
    button.innerHTML = '<span>Generating PDF Report...</span>';

    // Download PDF
    fetch('/api/download_report')
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to generate report');
            }
            return response.blob();
        })
        .then(blob => {
            // Create download link
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `XIQ_Migration_Report_${new Date().toISOString().slice(0,10)}.pdf`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);

            // Restore button
            button.disabled = false;
            button.innerHTML = originalText;

            // Show success message
            alert('PDF report downloaded successfully!');
        })
        .catch(error => {
            console.error('Error downloading PDF:', error);
            button.disabled = false;
            button.innerHTML = originalText;
            alert('Error generating PDF report: ' + error.message);
        });
}
