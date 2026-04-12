class AlertSystem {
  constructor() {
    this.alerts = [];
    this.subscribers = [];
  }

  /**
   * Subscribe to alerts
   */
  subscribe(callback) {
    this.subscribers.push(callback);
  }

  /**
   * Unsubscribe from alerts
   */
  unsubscribe(callback) {
    const index = this.subscribers.indexOf(callback);
    if (index > -1) {
      this.subscribers.splice(index, 1);
    }
  }

  /**
   * Create a new alert
   */
  createAlert(type, message, severity = 'info', data = {}) {
    const alert = {
      id: this.generateId(),
      timestamp: new Date().toISOString(),
      type,
      message,
      severity,
      data
    };

    this.alerts.push(alert);

    // Keep only recent alerts (last 100)
    if (this.alerts.length > 100) {
      this.alerts = this.alerts.slice(-100);
    }

    // Notify subscribers
    this.notifySubscribers(alert);

    return alert;
  }

  /**
   * Notify all subscribers of a new alert
   */
  notifySubscribers(alert) {
    for (const subscriber of this.subscribers) {
      try {
        subscriber(alert);
      } catch (error) {
        console.error('Error notifying alert subscriber:', error);
      }
    }
  }

  /**
   * Get recent alerts
   */
  getAlerts(limit = 50) {
    return this.alerts.slice(-limit).reverse();
  }

  /**
   * Get alert statistics
   */
  getStats() {
    const stats = {
      total: this.alerts.length,
      bySeverity: {
        critical: 0,
        high: 0,
        medium: 0,
        low: 0,
        info: 0
      },
      byType: {}
    };

    for (const alert of this.alerts) {
      stats.bySeverity[alert.severity]++;

      if (!stats.byType[alert.type]) {
        stats.byType[alert.type] = 0;
      }
      stats.byType[alert.type]++;
    }

    return stats;
  }

  /**
   * Clear all alerts
   */
  clearAlerts() {
    this.alerts = [];
  }

  /**
   * Generate unique ID
   */
  generateId() {
    return Math.random().toString(36).substr(2, 9);
  }
}

module.exports = AlertSystem;