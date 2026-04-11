// Network Scanner - Frontend Application

const API_BASE = '/api';
const WIFI_SCAN_URL = `${API_BASE}/scan/wifi`;
const BT_SCAN_URL = `${API_BASE}/scan/bluetooth`;

// DOM Elements
const wifiScanBtn = document.getElementById('wifiScanBtn');
const btScanBtn = document.getElementById('btScanBtn');
const wifiStatus = document.getElementById('wifiStatus');
const btStatus = document.getElementById('btStatus');
const wifiList = document.getElementById('wifiList');
const btList = document.getElementById('btList');
const terminalLog = document.getElementById('terminalLog');
const clearLogBtn = document.getElementById('clearLogBtn');

// State
let isWifiScanning = false;
let isBtScanning = false;

// Terminal Logging
function getTimestamp() {
  const now = new Date();
  return now.toTimeString().split(' ')[0];
}

function addLogEntry(prefix, message, type = 'info') {
  const entry = document.createElement('div');
  entry.className = 'log-entry';

  entry.innerHTML = `
    <span class="log-time">${getTimestamp()}</span>
    <span class="log-prefix ${type}">[${prefix}]</span>
    <span class="log-msg">${escapeHtml(message)}</span>
  `;

  terminalLog.appendChild(entry);
  terminalLog.scrollTop = terminalLog.scrollHeight;
}

function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

function clearLogs() {
  terminalLog.innerHTML = `
    <div class="log-entry">
      <span class="log-time">${getTimestamp()}</span>
      <span class="log-prefix">[SYSTEM]</span>
      <span class="log-msg">Terminal cleared.</span>
    </div>
  `;
}

// UI State Management
function setButtonLoading(button, isLoading) {
  const btnText = button.querySelector('.btn-text');
  const btnLoader = button.querySelector('.btn-loader');

  if (isLoading) {
    button.disabled = true;
    button.classList.add('loading');
    btnText.textContent = 'Scanning...';
    btnLoader.classList.remove('hidden');
  } else {
    button.disabled = false;
    button.classList.remove('loading');
    btnLoader.classList.add('hidden');
  }
}

function showStatus(element, message, type) {
  element.textContent = message;
  element.className = `status-bar ${type}`;
  element.classList.remove('hidden');
}

function hideStatus(element) {
  element.classList.add('hidden');
}

function showEmptyState(listElement, message) {
  listElement.innerHTML = `
    <div class="empty-state">
      <p>${escapeHtml(message)}</p>
    </div>
  `;
}

// Signal strength to bar conversion
function getSignalBars(signal) {
  // signal is in dBm, typically -100 to -30
  // -30 to -50: excellent (4 bars)
  // -50 to -60: good (3 bars)
  // -60 to -70: medium (2 bars)
  // -70 to -100: weak (1 bar)

  let bars = 0;
  let level = 'weak';

  if (signal >= -50) {
    bars = 4;
    level = 'strong';
  } else if (signal >= -60) {
    bars = 3;
    level = 'medium';
  } else if (signal >= -70) {
    bars = 2;
    level = 'weak';
  } else {
    bars = 1;
    level = 'weak';
  }

  let html = `<div class="signal-bar ${level}">`;
  for (let i = 0; i < 4; i++) {
    html += `<span class="${i < bars ? 'active' : ''}"></span>`;
  }
  html += '</div>';
  return html;
}

// Render WiFi Networks
function renderWifiNetworks(networks) {
  if (networks.length === 0) {
    showEmptyState(wifiList, 'No WiFi networks found.');
    return;
  }

  let html = '';
  for (const network of networks) {
    const securityClass = network.security.toLowerCase() === 'open' ? 'open' : '';
    html += `
      <div class="device-item wifi">
        <div class="device-name">
          <span class="ssid">${escapeHtml(network.ssid)}</span>
        </div>
        <div class="device-meta">
          <div class="meta-item">
            ${getSignalBars(network.signal)}
            <span>${network.signal} dBm</span>
          </div>
          <span class="security-badge ${securityClass}">${escapeHtml(network.security)}</span>
        </div>
      </div>
    `;
  }
  wifiList.innerHTML = html;
}

// Render Bluetooth Devices
function renderBluetoothDevices(devices) {
  if (devices.length === 0) {
    showEmptyState(btList, 'No Bluetooth devices found.');
    return;
  }

  let html = '';
  for (const device of devices) {
    html += `
      <div class="device-item bt">
        <div class="device-name">${escapeHtml(device.name)}</div>
        <div class="device-meta">
          <span class="mac-address">${escapeHtml(device.mac)}</span>
        </div>
      </div>
    `;
  }
  btList.innerHTML = html;
}

// WiFi Scan
async function scanWifi() {
  if (isWifiScanning) return;

  isWifiScanning = true;
  setButtonLoading(wifiScanBtn, true);
  hideStatus(wifiStatus);
  showStatus(wifiStatus, 'Scanning for WiFi networks...', 'loading');
  addLogEntry('WIFI', 'Initiating WiFi scan...', 'wifi');

  try {
    const response = await fetch(WIFI_SCAN_URL);

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    const data = await response.json();

    if (data.success) {
      renderWifiNetworks(data.networks);
      showStatus(wifiStatus, `Scan complete. Found ${data.count} networks.`, 'success');
      addLogEntry('WIFI', `Scan complete. Found ${data.count} networks.`, 'success');
    } else {
      throw new Error(data.error || 'Scan failed');
    }
  } catch (error) {
    showStatus(wifiStatus, `Error: ${error.message}`, 'error');
    showEmptyState(wifiList, `Scan failed: ${error.message}`);
    addLogEntry('WIFI', `Scan failed: ${error.message}`, 'error');
  } finally {
    isWifiScanning = false;
    setButtonLoading(wifiScanBtn, false);
  }
}

// Bluetooth Scan
async function scanBluetooth() {
  if (isBtScanning) return;

  isBtScanning = true;
  setButtonLoading(btScanBtn, true);
  hideStatus(btStatus);
  showStatus(btStatus, 'Scanning for Bluetooth devices...', 'loading');
  addLogEntry('BT', 'Initiating Bluetooth scan...', 'bt');

  try {
    const response = await fetch(BT_SCAN_URL);

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    const data = await response.json();

    if (data.success) {
      renderBluetoothDevices(data.devices);
      showStatus(btStatus, `Scan complete. Found ${data.count} devices.`, 'success');
      addLogEntry('BT', `Scan complete. Found ${data.count} devices.`, 'success');
    } else {
      throw new Error(data.error || 'Scan failed');
    }
  } catch (error) {
    showStatus(btStatus, `Error: ${error.message}`, 'error');
    showEmptyState(btList, `Scan failed: ${error.message}`);
    addLogEntry('BT', `Scan failed: ${error.message}`, 'error');
  } finally {
    isBtScanning = false;
    setButtonLoading(btScanBtn, false);
  }
}

// Event Listeners
wifiScanBtn.addEventListener('click', scanWifi);
btScanBtn.addEventListener('click', scanBluetooth);
clearLogBtn.addEventListener('click', clearLogs);

// Keyboard shortcuts
document.addEventListener('keydown', (e) => {
  if (e.key === 'w' && !e.ctrlKey && !e.metaKey && !e.altKey && document.activeElement === document.body) {
    scanWifi();
  } else if (e.key === 'b' && !e.ctrlKey && !e.metaKey && !e.altKey && document.activeElement === document.body) {
    scanBluetooth();
  }
});

// Initial log
addLogEntry('SYSTEM', 'Scanner initialized. Press W for WiFi scan, B for Bluetooth scan.', 'info');
