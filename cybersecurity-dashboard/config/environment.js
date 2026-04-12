// Environment configuration
module.exports = {
  port: process.env.PORT || 3000,
  logLevel: process.env.LOG_LEVEL || 'info',
  scanInterval: process.env.SCAN_INTERVAL || 30000, // 30 seconds
  threatThreshold: process.env.THREAT_THRESHOLD || 3,
  enableRealTime: process.env.ENABLE_REAL_TIME !== 'false',
  enableAlerts: process.env.ENABLE_ALERTS !== 'false',
  enableLogging: process.env.ENABLE_LOGGING !== 'false'
};