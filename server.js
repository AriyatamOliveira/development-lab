const express = require('express');
const path = require('path');
const logger = require('./src/logger');
const { scanWifi, scanBluetooth } = require('./src/scanner');

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

// CORS for development
app.use((req, res, next) => {
  res.header('Access-Control-Allow-Origin', '*');
  res.header('Access-Control-Allow-Headers', 'Origin, X-Requested-With, Content-Type, Accept');
  next();
});

// Health check endpoint
app.get('/api/health', (req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

// WiFi scan endpoint
app.get('/api/scan/wifi', async (req, res) => {
  logger.divider();
  logger.info('WiFi scan requested');

  try {
    const networks = await scanWifi();
    logger.success(`WiFi scan completed: ${networks.length} networks found`);

    res.json({
      success: true,
      count: networks.length,
      networks
    });
  } catch (error) {
    logger.error(`WiFi scan failed: ${error.message}`);
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Bluetooth scan endpoint
app.get('/api/scan/bluetooth', async (req, res) => {
  logger.divider();
  logger.info('Bluetooth scan requested');

  try {
    const devices = await scanBluetooth();
    logger.success(`Bluetooth scan completed: ${devices.length} devices found`);

    res.json({
      success: true,
      count: devices.length,
      devices
    });
  } catch (error) {
    logger.error(`Bluetooth scan failed: ${error.message}`);
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Start server
app.listen(PORT, () => {
  logger.divider();
  logger.success(`Network Scanner Server running on http://localhost:${PORT}`);
  logger.info('Available endpoints:');
  logger.info('  GET /api/health - Health check');
  logger.info('  GET /api/scan/wifi - Scan WiFi networks');
  logger.info('  GET /api/scan/bluetooth - Scan Bluetooth devices');
  logger.divider();
});

// Graceful shutdown
process.on('SIGTERM', () => {
  logger.warn('SIGTERM received, shutting down gracefully...');
  process.exit(0);
});

process.on('SIGINT', () => {
  logger.warn('SIGINT received, shutting down gracefully...');
  process.exit(0);
});
