const { exec } = require('child_process');

/**
 * Scan WiFi using macOS CoreWLAN via Python
 */
function scanWifi() {
  return new Promise((resolve, reject) => {
    exec('python3 wifi_scan.py', (err, stdout, stderr) => {
      if (err) {
        return reject(new Error(stderr || err.message));
      }

      try {
        const data = JSON.parse(stdout);

        const cleaned = data
          .filter(n => n && typeof n.rssi === 'number')
          .map(n => ({
            // ❗ DO NOT force hidden — let frontend decide
            ssid: (n.ssid && n.ssid.trim() !== '') ? n.ssid : null,

            bssid: n.bssid || 'unknown',

            // ✅ FIX: frontend expects "signal", not "rssi"
            signal: n.rssi,

            channel: n.channel || null,

            security: mapSecurity(n.security)
          }));

        resolve(cleaned);
      } catch (e) {
        reject(new Error("Failed to parse WiFi scan output"));
      }
    });
  });
}

/**
 * Convert macOS security codes → readable
 */
function mapSecurity(code) {
  switch (String(code)) {
    case "0": return "Open";
    case "1": return "WEP";
    case "2": return "WPA Personal";
    case "3": return "WPA2/WPA3";
    default: return "Unknown";
  }
}

/**
 * Scan Bluetooth devices
 */
const scanBluetooth = async () => {
  try {
    const { exec } = require('child_process');

    const execWithTimeout = (command, timeout = 15000) => {
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

    const { stdout } = await execWithTimeout('system_profiler SPBluetoothDataType', 15000);

    const devices = [];
    const lines = stdout.split('\n');
    let currentDevice = null;

    for (const line of lines) {
      const trimmed = line.trim();

      if (trimmed.startsWith('Device') && trimmed.includes('Address')) {
        const addrMatch = trimmed.match(/Address:\s*([0-9a-f:]+)/i);
        if (addrMatch) {
          currentDevice = { mac: addrMatch[1].toUpperCase() };
        }
      }

      if (currentDevice && trimmed.startsWith('Name:')) {
        currentDevice.name = trimmed.replace('Name:', '').trim();
      }

      if (currentDevice && trimmed.startsWith('Device Type:')) {
        currentDevice.type = trimmed.replace('Device Type:', '').trim();
      }

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

    if (currentDevice && currentDevice.name && currentDevice.mac) {
      devices.push({
        name: currentDevice.name,
        mac: currentDevice.mac,
        signal: null,
        type: currentDevice.type || 'Unknown'
      });
    }

    return devices;
  } catch (error) {
    return [];
  }
};

module.exports = { scanWifi, scanBluetooth };