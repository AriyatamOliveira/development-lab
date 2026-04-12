// Cybersecurity Dashboard Frontend
class CyberDashboard {
    constructor() {
        this.socket = io();
        this.initElements();
        this.bindEvents();
        this.updateTime();
        this.setupSocketListeners();
        this.loadInitialData();
        this.startAutoRefresh();
    }

    initElements() {
        // Header elements
        this.connectionStatus = document.getElementById('connection-status');
        this.scanWifiBtn = document.getElementById('scan-wifi-btn');
        this.scanBluetoothBtn = document.getElementById('scan-bluetooth-btn');

        // Stats elements
        this.wifiCount = document.getElementById('wifi-count');
        this.bluetoothCount = document.getElementById('bluetooth-count');
        this.threatCount = document.getElementById('threat-count');
        this.safeDevices = document.getElementById('safe-devices');

        // Table bodies
        this.wifiBody = document.getElementById('wifi-body');
        this.bluetoothBody = document.getElementById('bluetooth-body');
        this.threatsBody = document.getElementById('threats-body');

        // Refresh buttons
        this.refreshWifi = document.getElementById('refresh-wifi');
        this.refreshBluetooth = document.getElementById('refresh-bluetooth');
        this.refreshThreats = document.getElementById('refresh-threats');
        this.clearLogs = document.getElementById('clear-logs');

        // Logs container
        this.logsContainer = document.getElementById('logs-container');
        this.lastScanTime = document.getElementById('last-scan-time');
    }

    bindEvents() {
        // Scan buttons
        this.scanWifiBtn.addEventListener('click', () => this.scanWifi());
        this.scanBluetoothBtn.addEventListener('click', () => this.scanBluetooth());

        // Refresh buttons
        this.refreshWifi.addEventListener('click', () => this.scanWifi());
        this.refreshBluetooth.addEventListener('click', () => this.scanBluetooth());
        this.refreshThreats.addEventListener('click', () => this.loadThreats());
        this.clearLogs.addEventListener('click', () => this.clearLogs());

        // Auto-refresh every 30 seconds
        setInterval(() => {
            this.updateTime();
        }, 1000);
    }

    setupSocketListeners() {
        this.socket.on('connect', () => {
            this.updateConnectionStatus(true);
            this.addLog('Connected to server', 'info');
        });

        this.socket.on('disconnect', () => {
            this.updateConnectionStatus(false);
            this.addLog('Disconnected from server', 'warn');
        });

        this.socket.on('wifiUpdate', (networks) => {
            this.updateWifiTable(networks);
            this.updateStats();
            this.addLog(`WiFi scan updated: ${networks.length} networks found`, 'info');
        });

        this.socket.on('bluetoothUpdate', (devices) => {
            this.updateBluetoothTable(devices);
            this.updateStats();
            this.addLog(`Bluetooth scan updated: ${devices.length} devices found`, 'info');
        });

        this.socket.on('threatUpdate', (threats) => {
            this.updateThreatsTable(threats);
            this.updateStats();
            this.addLog(`New threats detected: ${threats.length}`, 'warn');
        });

        this.socket.on('init', (data) => {
            if (data.wifiDevices) this.updateWifiTable(data.wifiDevices);
            if (data.bluetoothDevices) this.updateBluetoothTable(data.bluetoothDevices);
            if (data.threats) this.updateThreatsTable(data.threats);
            this.updateStats();
        });
    }

    updateConnectionStatus(connected) {
        const statusDot = this.connectionStatus.querySelector('.status-dot');
        const statusText = this.connectionStatus.querySelector('.status-text');

        if (connected) {
            statusDot.className = 'status-dot connected';
            statusText.textContent = 'Connected';
        } else {
            statusDot.className = 'status-dot disconnected';
            statusText.textContent = 'Disconnected';
        }
    }

    async scanWifi() {
        try {
            this.scanWifiBtn.disabled = true;
            this.scanWifiBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Scanning...';

            const response = await fetch('/api/scan/wifi');
            const data = await response.json();

            if (data.success) {
                this.updateWifiTable(data.networks);
                if (data.threats && data.threats.length > 0) {
                    this.updateThreatsTable(data.threats);
                }
                this.updateStats();
                this.lastScanTime.textContent = new Date().toLocaleTimeString();
                this.addLog(`WiFi scan completed: ${data.networks.length} networks`, 'info');
            } else {
                this.addLog(`WiFi scan failed: ${data.error}`, 'error');
            }
        } catch (error) {
            this.addLog(`WiFi scan error: ${error.message}`, 'error');
        } finally {
            this.scanWifiBtn.disabled = false;
            this.scanWifiBtn.innerHTML = '<i class="fas fa-wifi"></i> Scan WiFi';
        }
    }

    async scanBluetooth() {
        try {
            this.scanBluetoothBtn.disabled = true;
            this.scanBluetoothBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Scanning...';

            const response = await fetch('/api/scan/bluetooth');
            const data = await response.json();

            if (data.success) {
                this.updateBluetoothTable(data.devices);
                if (data.threats && data.threats.length > 0) {
                    this.updateThreatsTable(data.threats);
                }
                this.updateStats();
                this.lastScanTime.textContent = new Date().toLocaleTimeString();
                this.addLog(`Bluetooth scan completed: ${data.devices.length} devices`, 'info');
            } else {
                this.addLog(`Bluetooth scan failed: ${data.error}`, 'error');
            }
        } catch (error) {
            this.addLog(`Bluetooth scan error: ${error.message}`, 'error');
        } finally {
            this.scanBluetoothBtn.disabled = false;
            this.scanBluetoothBtn.innerHTML = '<i class="fab fa-bluetooth"></i> Scan Bluetooth';
        }
    }

    updateWifiTable(networks) {
    if (!networks || networks.length === 0) {
        this.wifiBody.innerHTML = '<tr><td colspan="4" class="empty-row">No networks found</td></tr>';
        return;
    }

    let html = '';

    networks.forEach(network => {
        const ssid = network.ssid ? network.ssid : `Hidden (${network.bssid.slice(0,8)})`;

        const signal = (network.signal !== undefined && network.signal !== null)
            ? `${network.signal} dBm`
            : 'N/A';

        const security = network.security || 'Unknown';
        const signalBars = this.getSignalBars(network.signal);

        let statusBadge = '<span class="status-badge badge-safe">Secure</span>';

        if (!network.ssid || network.ssid === '' || network.ssid === 'Hidden Network') {
            statusBadge = '<span class="status-badge badge-hidden">Hidden</span>';
        } else if (security.toLowerCase() === 'open') {
            statusBadge = '<span class="status-badge badge-danger">Open</span>';
        } else if (security.toLowerCase() === 'wep') {
            statusBadge = '<span class="status-badge badge-warning">Weak</span>';
        }

        html += `
            <tr>
                <td>${this.escapeHtml(ssid)}</td>
                <td>
                    <div class="signal-strength">
                        <div class="signal-bars">${signalBars}</div>
                        <span>${signal}</span>
                    </div>
                </td>
                <td><span class="status-badge badge-safe">${this.escapeHtml(security)}</span></td>
                <td>${statusBadge}</td>
            </tr>
        `;
    });

    this.wifiBody.innerHTML = html;
}

    updateBluetoothTable(devices) {
        if (!devices || devices.length === 0) {
            this.bluetoothBody.innerHTML = '<tr><td colspan="4" class="empty-row">No devices found</td></tr>';
            return;
        }

        let html = '';
        devices.forEach(device => {
            const status = device.name ? 'safe' : 'warning';
            const statusBadge = status === 'safe'
                ? '<span class="status-badge badge-safe">Safe</span>'
                : '<span class="status-badge badge-warning">Unknown</span>';

            html += `
                <tr>
                    <td>${this.escapeHtml(device.name || 'Unknown Device')}</td>
                    <td>${this.escapeHtml(device.mac || 'N/A')}</td>
                    <td>${this.escapeHtml(device.type || 'Unknown')}</td>
                    <td>${statusBadge}</td>
                </tr>
            `;
        });

        this.bluetoothBody.innerHTML = html;
    }

    updateThreatsTable(threats) {
        if (!threats || threats.length === 0) {
            this.threatsBody.innerHTML = '<tr><td colspan="4" class="empty-row">No threats detected</td></tr>';
            return;
        }

        let html = '';
        threats.slice(0, 20).forEach(threat => {
            const severityClass = this.getSeverityClass(threat.severity);
            const severityBadge = `<span class="status-badge ${severityClass}">${this.capitalize(threat.severity)}</span>`;

            html += `
                <tr>
                    <td>${this.escapeHtml(threat.type)}</td>
                    <td>${this.escapeHtml(threat.description)}</td>
                    <td>${threat.device ? this.escapeHtml(threat.device.ssid || threat.device.name || threat.device.mac || 'Unknown') : 'N/A'}</td>
                    <td>${severityBadge}</td>
                </tr>
            `;
        });

        this.threatsBody.innerHTML = html;
    }

    updateStats() {
        // In a real implementation, we would fetch actual counts from the server
        // For now, we'll estimate based on table content
        const wifiRows = this.wifiBody.querySelectorAll('tr:not(.empty-row)');
        const bluetoothRows = this.bluetoothBody.querySelectorAll('tr:not(.empty-row)');
        const threatRows = this.threatsBody.querySelectorAll('tr:not(.empty-row)');

        this.wifiCount.textContent = wifiRows.length > 0 && wifiRows[0].classList.contains('empty-row') ? 0 : wifiRows.length;
        this.bluetoothCount.textContent = bluetoothRows.length > 0 && bluetoothRows[0].classList.contains('empty-row') ? 0 : bluetoothRows.length;
        this.threatCount.textContent = threatRows.length > 0 && threatRows[0].classList.contains('empty-row') ? 0 : threatRows.length;

        // Calculate safe devices (total devices minus threats)
        const totalDevices = parseInt(this.wifiCount.textContent) + parseInt(this.bluetoothCount.textContent);
        this.safeDevices.textContent = Math.max(0, totalDevices - parseInt(this.threatCount.textContent));
    }

    getSignalBars(signal) {
    if (signal === undefined || signal === null || isNaN(signal)) return '';

    let bars = 0;
    if (signal >= -50) bars = 4;
    else if (signal >= -60) bars = 3;
    else if (signal >= -70) bars = 2;
    else if (signal >= -80) bars = 1;

    let html = '';
    for (let i = 0; i < 4; i++) {
        const active = i < bars ? 'active-strong' : '';
        html += `<div class="signal-bar ${active}"></div>`;
    }

    return html;
}

    getSecurityClass(security) {
        if (!security) return 'badge-warning';

        const sec = security.toLowerCase();
        if (sec === 'open' || sec === 'none') return 'badge-danger';
        if (sec === 'wep') return 'badge-warning';
        return 'badge-safe';
    }

    getStatusBadge(network) {
        if (network.ssid && (network.ssid.startsWith('<') || network.ssid === '')) {
            return '<span class="status-badge badge-hidden">Hidden</span>';
        }
        if (network.security === 'Open' || network.security === 'NONE') {
            return '<span class="status-badge badge-danger">Unsafe</span>';
        }
        if (network.security === 'WEP') {
            return '<span class="status-badge badge-warning">Weak</span>';
        }
        return '<span class="status-badge badge-safe">Secure</span>';
    }

    getSeverityClass(severity) {
        switch (severity) {
            case 'critical': return 'badge-danger';
            case 'high': return 'badge-danger';
            case 'medium': return 'badge-warning';
            case 'low': return 'badge-warning';
            default: return 'badge-safe';
        }
    }

    addLog(message, level = 'info') {
        const time = new Date().toLocaleTimeString();
        const logEntry = document.createElement('div');
        logEntry.className = 'log-entry';
        logEntry.innerHTML = `
            <span class="log-time">${time}</span>
            <span class="log-level ${level}">${level.toUpperCase()}</span>
            <span class="log-message">${this.escapeHtml(message)}</span>
        `;

        this.logsContainer.prepend(logEntry);

        // Keep only last 50 logs
        const logs = this.logsContainer.querySelectorAll('.log-entry');
        if (logs.length > 50) {
            logs[logs.length - 1].remove();
        }
    }

    clearLogs() {
        this.logsContainer.innerHTML = '';
        this.addLog('Logs cleared', 'info');
    }

    loadInitialData() {
        // Load initial data from server
        this.loadThreats();
        this.addLog('Dashboard initialized', 'info');
    }

    async loadThreats() {
        try {
            const response = await fetch('/api/threats');
            const data = await response.json();

            if (data.success) {
                this.updateThreatsTable(data.threats);
                this.updateStats();
            }
        } catch (error) {
            console.error('Failed to load threats:', error);
        }
    }

    startAutoRefresh() {
        // Auto-refresh every 30 seconds
        setInterval(async () => {
            try {
                // Refresh threats
                await this.loadThreats();

                // Update connection status
                this.updateConnectionStatus(this.socket.connected);
            } catch (error) {
                console.error('Auto-refresh failed:', error);
            }
        }, 30000);
    }

    updateTime() {
        const now = new Date();
        document.getElementById('current-time').textContent = now.toLocaleTimeString();
    }

    escapeHtml(text) {
        if (!text) return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    capitalize(str) {
        if (!str) return '';
        return str.charAt(0).toUpperCase() + str.slice(1);
    }
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.dashboard = new CyberDashboard();
});