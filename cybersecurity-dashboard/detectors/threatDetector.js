// Threat Detection Module
class ThreatDetector {
  constructor() {
    this.threatPatterns = [
      {
        name: 'Hidden Network',
        description: 'Network with hidden SSID detected',
        check: (device) => {
          if (!device.ssid) return true; // null or empty = hidden
          return device.ssid.startsWith('<') || device.ssid.trim() === '';
}
      },
      {
        name: 'Open Network',
        description: 'Unsecured network detected',
        check: (device) => device.security === 'Open' || device.security === 'NONE'
      },
      {
        name: 'Weak Encryption',
        description: 'Network with weak encryption detected',
        check: (device) => device.security === 'WEP'
      },
      {
        name: 'Rogue Device',
        description: 'Unknown device detected',
        check: (device) => this.isUnknownDevice(device)
      },
      {
        name: 'Signal Spoofing',
        description: 'Suspicious signal strength detected',
        check: (device) => device.signal > -20 // Unusually strong signal
      }
    ];

    this.knownDevices = new Set(); // Store known device fingerprints
    this.threatHistory = []; // Track detected threats
  }

  /**
   * Analyze devices for potential threats
   * @param {Array} devices - Array of network devices
   * @returns {Array} Array of detected threats
   */
  detectThreats(devices) {
    const threats = [];

    for (const device of devices) {
      // Check each threat pattern
      for (const pattern of this.threatPatterns) {
        if (pattern.check(device)) {
          const threat = {
            id: this.generateId(),
            timestamp: new Date().toISOString(),
            type: pattern.name,
            description: pattern.description,
            device: device,
            severity: this.calculateSeverity(pattern.name, device)
          };

          threats.push(threat);
          this.threatHistory.push(threat);
        }
      }

      // Add device to known devices
      if (device.mac) {
        this.knownDevices.add(device.mac.toLowerCase());
      }
    }

    // Keep only recent threats (last 100)
    if (this.threatHistory.length > 100) {
      this.threatHistory = this.threatHistory.slice(-100);
    }

    return threats;
  }

  /**
   * Check if a device is unknown
   * @param {Object} device - Device object
   * @returns {Boolean} True if device is unknown
   */
  isUnknownDevice(device) {
    // For demonstration, we'll consider devices with certain characteristics as unknown
    // In a real implementation, this would check against a database of known devices
    if (!device.mac) return true;

    // Check if MAC address is in known devices list
    return !this.knownDevices.has(device.mac.toLowerCase());
  }

  /**
   * Calculate threat severity
   * @param {String} threatType - Type of threat
   * @param {Object} device - Device object
   * @returns {String} Severity level (low, medium, high, critical)
   */
  calculateSeverity(threatType, device) {
    const severityMap = {
      'Hidden Network': 'medium',
      'Open Network': 'high',
      'Weak Encryption': 'high',
      'Rogue Device': 'medium',
      'Signal Spoofing': 'critical'
    };

    return severityMap[threatType] || 'low';
  }

  /**
   * Generate unique ID for threats
   * @returns {String} Unique ID
   */
  generateId() {
    return Math.random().toString(36).substr(2, 9);
  }

  /**
   * Get threat statistics
   * @returns {Object} Threat statistics
   */
  getStatistics() {
    const stats = {
      total: this.threatHistory.length,
      bySeverity: {
        critical: 0,
        high: 0,
        medium: 0,
        low: 0
      },
      byType: {}
    };

    for (const threat of this.threatHistory) {
      stats.bySeverity[threat.severity]++;

      if (!stats.byType[threat.type]) {
        stats.byType[threat.type] = 0;
      }
      stats.byType[threat.type]++;
    }

    return stats;
  }

  /**
   * Get recent threats
   * @param {Number} limit - Number of recent threats to return
   * @returns {Array} Recent threats
   */
  getRecentThreats(limit = 10) {
    return this.threatHistory.slice(-limit).reverse();
  }
}

module.exports = ThreatDetector;