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

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
    initializeTheme();
    setupEventListeners();
    setupTabs();
    startLogPolling();
});

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
            document.getElementById('xiqResults').style.display = 'block';
            updateStepStatus('step1', 'Completed');
            updateProgress('XIQ connection successful', 50);

            // Populate selection lists
            populateSelectionLists(result.data);

            // Show step 2
            document.getElementById('step2').style.display = 'block';
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
    document.getElementById('step3').style.display = 'block';
    updateStepStatus('step3', 'Ready');
    document.getElementById('step3').scrollIntoView({ behavior: 'smooth' });
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

            document.getElementById('step4').style.display = 'block';
            updateStepStatus('step4', 'Ready');
            document.getElementById('step4').scrollIntoView({ behavior: 'smooth' });
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

    document.getElementById('step5').style.display = 'block';
    updateStepStatus('step5', 'Ready');
    document.getElementById('step5').scrollIntoView({ behavior: 'smooth' });
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
    `;
}

// Execute migration
async function executeMigration() {
    const dryRun = document.getElementById('dryRun').checked;

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
                profile_assignments: state.profileAssignments
            })
        });

        const result = await response.json();

        if (result.success) {
            updateProgress('Migration completed!', 100);
            updateStepStatus('step5', 'Completed');

            // Show results
            displayMigrationResults(result.data, dryRun);

            document.getElementById('step6').style.display = 'block';
            updateStepStatus('step6', 'Completed');
            document.getElementById('step6').scrollIntoView({ behavior: 'smooth' });
        } else {
            alert('Migration error: ' + result.error);
            updateStepStatus('step5', 'Error');
        }
    } catch (error) {
        alert('Migration error: ' + error.message);
        updateStepStatus('step5', 'Error');
    }
}

// Display migration results
function displayMigrationResults(data, dryRun) {
    const container = document.getElementById('migrationResults');

    if (dryRun) {
        container.innerHTML = `
            <div class="results">
                <h3>Dry Run Complete</h3>
                <p>Configuration saved to: <code>${data.output_file}</code></p>
                <p>No changes were made to Edge Services.</p>
            </div>
        `;
    } else {
        // Helper function to format result - handles both string and object format
        const formatResult = (result) => {
            if (typeof result === 'string') {
                // Extract "X/Y" from strings like "5/10 posted successfully"
                const match = result.match(/(\d+\/\d+)/);
                return match ? match[1] : result;
            } else if (result && typeof result === 'object') {
                return `${result.posted || result.updated || 0}/${result.total || 0}`;
            }
            return '0/0';
        };

        let html = '<div class="results"><h3>Migration Successful!</h3><div class="results-grid">';

        if (data.results.rate_limiters) {
            html += `<div class="result-item">
                <span class="result-label">Rate Limiters</span>
                <span class="result-value">${formatResult(data.results.rate_limiters)}</span>
            </div>`;
        }

        if (data.results.cos_policies) {
            html += `<div class="result-item">
                <span class="result-label">CoS Policies</span>
                <span class="result-value">${formatResult(data.results.cos_policies)}</span>
            </div>`;
        }

        if (data.results.topologies) {
            html += `<div class="result-item">
                <span class="result-label">Topologies</span>
                <span class="result-value">${formatResult(data.results.topologies)}</span>
            </div>`;
        }

        if (data.results.aaa_policies) {
            html += `<div class="result-item">
                <span class="result-label">AAA Policies</span>
                <span class="result-value">${formatResult(data.results.aaa_policies)}</span>
            </div>`;
        }

        if (data.results.services) {
            html += `<div class="result-item">
                <span class="result-label">Services</span>
                <span class="result-value">${formatResult(data.results.services)}</span>
            </div>`;
        }

        if (data.results.ap_configs) {
            html += `<div class="result-item">
                <span class="result-label">AP Configs</span>
                <span class="result-value">${formatResult(data.results.ap_configs)}</span>
            </div>`;
        }

        if (data.results.profile_assignments) {
            html += `<div class="result-item">
                <span class="result-label">Profile Assignments</span>
                <span class="result-value">${data.results.profile_assignments}</span>
            </div>`;
        }

        html += '</div></div>';
        container.innerHTML = html;
    }
}

// Update progress
function updateProgress(message, percent) {
    const progressBar = document.getElementById('progressBar');
    const progressText = document.getElementById('progressText');
    const progressSection = document.getElementById('progressSection');

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

// Poll for logs
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
    }, 1000);
}

// Update logs
function updateLogs(logs) {
    const logsPanel = document.getElementById('logsPanel');
    logsPanel.innerHTML = '';

    logs.forEach(log => {
        const entry = document.createElement('div');
        entry.className = 'log-entry';

        entry.innerHTML = `
            <span class="log-timestamp">${log.timestamp}</span>
            <span class="log-level ${log.level}">[${log.level.toUpperCase()}]</span>
            <span class="log-message">${log.message}</span>
        `;

        logsPanel.appendChild(entry);
    });

    // Auto-scroll to bottom
    logsPanel.scrollTop = logsPanel.scrollHeight;
}

// Clear logs
function clearLogs() {
    document.getElementById('logsPanel').innerHTML = '';
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
