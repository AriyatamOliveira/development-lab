const { exec } = require('child_process');
const logger = require('./logger');

/**
 * Execute a shell command and return a promise
 */
const execPromise = (command, timeout = 30000) => {
  return new Promise((resolve, reject) => {
    const timer = setTimeout(() => {
      reject(new Error(`Command timeout: ${command}`));
    }, timeout);

    exec(command, { maxBuffer: 1024 * 1024 * 10 }, (error, stdout, stderr) => {
      clearTimeout(timer);
      if (error && !stdout) {
        reject(error);
      } else {
        resolve({ stdout, stderr });
      }
    });
  });
};

/**
 * Scan WiFi networks using airport utility
 */
const scanWifi = async () => {
  logger.scan('wifi', 'Starting WiFi scan...');

  try {
    // Check if airport utility exists
    const airportPath = '/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport';

    const { stdout } = await execPromise(`${airportPath} -s`, 15000);

    const networks = parseAirportOutput(stdout);
    logger.scan('wifi', `Found ${networks.length} WiFi networks`);
    return networks;
  } catch (error) {
    // Fallback: try using networksetup
    logger.warn('Airport scan failed, trying networksetup...');
    return scanWifiViaNetworksetup();
  }
};

/**
 * Parse airport -s output into structured data
 */
const parseAirportOutput = (stdout) => {
  const lines = stdout.trim().split('\n');
  const networks = [];

  // Skip header line
  for (let i = 1; i < lines.length; i++) {
    const line = lines[i].trim();
    if (!line) continue;

    // Airport output format: SSID              BSSID             RSSI  CHANNEL  HT  CC  SECURITY (auth/unicom/certs)
    const match = line.match(/^(.+?)\s+([0-9a-f:]+)\s+(-?\d+)\s+(\d+)\s+[Y/N]\s+([A-Z]{2})\s+(.+)$/);

    if (match) {
      const ssid = match[1].trim();
      const bssid = match[2];
      const rssi = parseInt(match[3], 10);
      const channel = parseInt(match[4], 10);
      const security = match[6].trim() || 'Open';

      // Skip hidden or empty SSIDs
      if (ssid && ssid.length > 0 && !ssid.startsWith('<')) {
        networks.push({
          ssid,
          bssid,
          signal: rssi,
          channel,
          security: parseSecurity(security)
        });
      }
    }
  }

  return networks;
};

/**
 * Parse security string into readable format
 */
const parseSecurity = (security) => {
  if (!security || security === 'NONE') return 'Open';

  const sec = security.toUpperCase();
  if (sec.includes('WPA3')) return 'WPA3';
  if (sec.includes('WPA2')) return 'WPA2';
  if (sec.includes('WPA')) return 'WPA';
  if (sec.includes('WEP')) return 'WEP';
  return security;
};

/**
 * Fallback WiFi scan using networksetup
 */
const scanWifiViaNetworksetup = async () => {
  try {
    const { stdout } = await execPromise('networksetup -listpreferredwirelessnetworks en0', 10000);
    const networks = [];

    const lines = stdout.trim().split('\n');
    for (let i = 1; i < lines.length; i++) {
      const line = lines[i].trim();
      if (!line || line.includes('There are no preferred')) continue;

      // networksetup output: Network Name           Security
      const parts = line.split(/\s{2,}/);
      if (parts.length >= 1) {
        networks.push({
          ssid: parts[0].trim(),
          bssid: 'N/A',
          signal: 0,
          channel: 0,
          security: parts[1] ? parts[1].trim() : 'Unknown'
        });
      }
    }

    logger.scan('wifi', `Found ${networks.length} WiFi networks (via networksetup)`);
    return networks;
  } catch (error) {
    logger.error(`WiFi scan fallback failed: ${error.message}`);
    throw new Error('WiFi scanning is not available. Please ensure you have the necessary permissions and tools.');
  }
};

/**
 * Scan Bluetooth devices
 */
const scanBluetooth = async () => {
  logger.scan('bluetooth', 'Starting Bluetooth scan...');

  try {
    // Try using system_profiler for Bluetooth info
    const { stdout } = await execPromise('system_profiler SPBluetoothDataType', 15000);
    const devices = parseBluetoothOutput(stdout);

    if (devices.length > 0) {
      logger.scan('bluetooth', `Found ${devices.length} Bluetooth devices`);
      return devices;
    }

    // Fallback: try using blueutil if available
    return await scanBluetoothViaBlueutil();
  } catch (error) {
    logger.warn(`system_profiler scan failed: ${error.message}`);
    return await scanBluetoothViaBlueutil();
  }
};

/**
 * Parse system_profiler Bluetooth output
 */
const parseBluetoothOutput = (stdout) => {
  const devices = [];
  const lines = stdout.split('\n');

  let currentDevice = null;

  for (const line of lines) {
    const trimmed = line.trim();

    // Device name pattern
    if (trimmed.startsWith('Device') && trimmed.includes('Address')) {
      const addrMatch = trimmed.match(/Address:\s*([0-9a-f:]+)/i);
      if (addrMatch) {
        currentDevice = { mac: addrMatch[1].toUpperCase() };
      }
    }

    // Device name
    if (currentDevice && trimmed.startsWith('Name:')) {
      currentDevice.name = trimmed.replace('Name:', '').trim();
    }

    // Device type
    if (currentDevice && trimmed.startsWith('Device Type:')) {
      currentDevice.type = trimmed.replace('Device Type:', '').trim();
    }

    // End of device block (empty line or new device)
    if (currentDevice && (trimmed === '' || trimmed.startsWith('Device'))) {
      if (currentDevice.name && currentDevice.mac) {
        devices.push({
          name: currentDevice.name,
          mac: currentDevice.mac,
          signal: null,
          type: currentDevice.type || 'Unknown'
        });
      }
      currentDevice = null;
    }
  }

  // Handle last device if no trailing newline
  if (currentDevice && currentDevice.name && currentDevice.mac) {
    devices.push({
      name: currentDevice.name,
      mac: currentDevice.mac,
      signal: null,
      type: currentDevice.type || 'Unknown'
    });
  }

  return devices;
};

/**
 * Fallback Bluetooth scan using blueutil
 */
const scanBluetoothViaBlueutil = async () => {
  try {
    // Check if blueutil is installed
    await execPromise('which blueutil', 5000);

    const { stdout } = await execPromise('blueutil --paired', 10000);
    const devices = [];

    const lines = stdout.trim().split('\n');
    for (const line of lines) {
      const trimmed = line.trim();
      if (!trimmed) continue;

      // blueutil output: address, name, [not] connected
      const parts = trimmed.split(',').map(p => p.trim());
      if (parts.length >= 1) {
        devices.push({
          name: parts[1] || 'Unknown Device',
          mac: parts[0],
          signal: null,
          type: 'Bluetooth Device'
        });
      }
    }

    logger.scan('bluetooth', `Found ${devices.length} Bluetooth devices (via blueutil)`);
    return devices;
  } catch (error) {
    logger.warn(`blueutil not available: ${error.message}`);
    throw new Error('Bluetooth scanning requires additional tools. On macOS, you can install blueutil via: brew install blueutil');
  }
};

module.exports = {
  scanWifi,
  scanBluetooth
};
