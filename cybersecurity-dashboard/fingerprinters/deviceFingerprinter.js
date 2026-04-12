class DeviceFingerprinter {
  constructor() {
    this.knownDevices = new Map(); // Store known device fingerprints
    this.deviceProfiles = new Map(); // Store detailed device profiles
  }

  /**
   * Create a fingerprint for a device
   */
  createFingerprint(device) {
    // Create a unique identifier based on device properties
    const fingerprint = {
      id: this.generateDeviceId(device),
      mac: device.mac || 'unknown',
      name: device.name || device.ssid || 'unknown',
      type: device.type || this.determineDeviceType(device),
      vendor: this.identifyVendor(device.mac),
      firstSeen: new Date().toISOString(),
      lastSeen: new Date().toISOString(),
      signalStrength: device.signal || null,
      security: device.security || null,
      channels: device.channel ? [device.channel] : [],
      threatScore: this.calculateThreatScore(device)
    };

    return fingerprint;
  }

  /**
   * Update an existing device fingerprint
   */
  updateFingerprint(deviceId, device) {
    const fingerprint = this.knownDevices.get(deviceId);
    if (fingerprint) {
      fingerprint.lastSeen = new Date().toISOString();
      fingerprint.signalStrength = device.signal || fingerprint.signalStrength;

      if (device.channel && !fingerprint.channels.includes(device.channel)) {
        fingerprint.channels.push(device.channel);
      }

      // Update threat score
      fingerprint.threatScore = this.calculateThreatScore(device);

      this.knownDevices.set(deviceId, fingerprint);
      return fingerprint;
    }
    return null;
  }

  /**
   * Register a new device
   */
  registerDevice(device) {
    const fingerprint = this.createFingerprint(device);
    this.knownDevices.set(fingerprint.id, fingerprint);
    return fingerprint;
  }

  /**
   * Get device fingerprint by ID
   */
  getDevice(deviceId) {
    return this.knownDevices.get(deviceId);
  }

  /**
   * Get all known devices
   */
  getAllDevices() {
    return Array.from(this.knownDevices.values());
  }

  /**
   * Check if device is known
   */
  isKnownDevice(device) {
    const deviceId = this.generateDeviceId(device);
    return this.knownDevices.has(deviceId);
  }

  /**
   * Generate unique device ID
   */
  generateDeviceId(device) {
    if (device.mac) {
      return device.mac.toLowerCase();
    }

    if (device.bssid) {
      return device.bssid.toLowerCase();
    }

    // Fallback to name-based ID
    const name = device.name || device.ssid || 'unknown';
    return `${name}-${Math.random().toString(36).substr(2, 9)}`;
  }

  /**
   * Determine device type based on properties
   */
  determineDeviceType(device) {
    if (device.ssid) return 'wifi-network';
    if (device.type) return device.type.toLowerCase();

    // Try to infer from name
    const name = (device.name || device.ssid || '').toLowerCase();
    if (name.includes('phone')) return 'smartphone';
    if (name.includes('laptop')) return 'laptop';
    if (name.includes('printer')) return 'printer';
    if (name.includes('camera')) return 'camera';
    if (name.includes('tv') || name.includes('television')) return 'smart-tv';

    return 'unknown';
  }

  /**
   * Identify vendor from MAC address
   */
  identifyVendor(mac) {
    if (!mac) return 'unknown';

    // Extract OUI (first 3 octets)
    const oui = mac.substring(0, 8).toUpperCase();

    // Common vendor mappings (simplified)
    const vendors = {
      '00:00:00': 'Xerox',
      '00:0A:95': 'Apple',
      '00:1A:11': 'Google',
      '00:50:56': 'VMware',
      '00:0C:29': 'VMware',
      '00:16:3E': 'XenSource',
      '08:00:27': 'PCS Systemtechnik',
      '52:54:00': 'QEMU',
      'AC:DE:48': 'Apple',
      'F0:18:98': 'Apple',
      '28:63:36': 'Apple',
      '8C:85:90': 'Apple',
      'A4:5E:60': 'Apple',
      '38:C9:86': 'Apple'
    };

    return vendors[oui] || 'unknown';
  }

  /**
   * Calculate threat score for a device
   */
  calculateThreatScore(device) {
    let score = 0;

    // Check for open/weak security
    if (device.security === 'Open' || device.security === 'NONE') {
      score += 3;
    } else if (device.security === 'WEP') {
      score += 2;
    }

    // Check for hidden SSID
    if (device.ssid && (device.ssid.startsWith('<') || device.ssid === '')) {
      score += 2;
    }

    // Check signal strength (unusually strong signals might be suspicious)
    if (device.signal && device.signal > -20) {
      score += 1;
    }

    // Unknown vendor increases score
    const vendor = this.identifyVendor(device.mac);
    if (vendor === 'unknown') {
      score += 1;
    }

    return Math.min(score, 10); // Cap at 10
  }

  /**
   * Get device statistics
   */
  getStatistics() {
    const stats = {
      total: this.knownDevices.size,
      byType: {},
      byVendor: {},
      threatLevels: {
        low: 0, // 0-2
        medium: 0, // 3-5
        high: 0, // 6-8
        critical: 0 // 9-10
      }
    };

    for (const device of this.knownDevices.values()) {
      // Count by type
      if (!stats.byType[device.type]) {
        stats.byType[device.type] = 0;
      }
      stats.byType[device.type]++;

      // Count by vendor
      if (!stats.byVendor[device.vendor]) {
        stats.byVendor[device.vendor] = 0;
      }
      stats.byVendor[device.vendor]++;

      // Count by threat level
      if (device.threatScore <= 2) {
        stats.threatLevels.low++;
      } else if (device.threatScore <= 5) {
        stats.threatLevels.medium++;
      } else if (device.threatScore <= 8) {
        stats.threatLevels.high++;
      } else {
        stats.threatLevels.critical++;
      }
    }

    return stats;
  }
}

module.exports = DeviceFingerprinter;