const express = require('express');
const http = require('http');
const socketIo = require('socket.io');
const path = require('path');
const cors = require('cors');
const ThreatDetector = require('../detectors/threatDetector');
const { scanWifi, scanBluetooth } = require('../utils/scanner');
const Logger = require('../utils/logger');

// Initialize components
const app = express();
const server = http.createServer(app);
const io = socketIo(server, {
  cors: {
    origin: "*",
    methods: ["GET", "POST"]
  }
});

const threatDetector = new ThreatDetector();
const logger = new Logger();

// Configuration
const PORT = process.env.PORT || 3000;
const SCAN_INTERVAL = parseInt(process.env.SCAN_INTERVAL) || 30000; // 30 seconds

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.static(path.join(__dirname, '../public')));

// Serve the main dashboard
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, '../public/index.html'));
});

// In-memory storage for devices and threats
let wifiDevices = [];
let bluetoothDevices = [];
let threats = [];
let scanHistory = [];

// Socket.IO connection handling
io.on('connection', (socket) => {
  console.log('Client connected');

  // Send initial data to newly connected clients
  socket.emit('init', {
    wifiDevices,
    bluetoothDevices,
    threats,
    scanHistory
  });

  socket.on('disconnect', () => {
    console.log('Client disconnected');
  });
});

// Helper function to broadcast updates
const broadcastUpdate = (event, data) => {
  io.emit(event, data);
};

// Routes
app.get('/api/health', (req, res) => {
  res.json({
    status: 'ok',
    timestamp: new Date().toISOString(),
    uptime: process.uptime()
  });
});

app.get('/api/scan/wifi', async (req, res) => {
  try {
    logger.info('WiFi scan initiated');
    const networks = await scanWifi();

    // Detect threats
    const newThreats = threatDetector.detectThreats(networks);
    threats = [...threats, ...newThreats];

    // Update storage
    wifiDevices = networks;

    // Add to scan history
    scanHistory.push({
      type: 'wifi',
      timestamp: new Date().toISOString(),
      count: networks.length,
      threats: newThreats.length
    });

    // Broadcast updates
    broadcastUpdate('wifiUpdate', networks);
    if (newThreats.length > 0) {
      broadcastUpdate('threatUpdate', newThreats);
    }

    logger.success(`WiFi scan completed: ${networks.length} networks, ${newThreats.length} threats`);

    res.json({
      success: true,
      count: networks.length,
      networks,
      threats: newThreats
    });
  } catch (error) {
    logger.error(`WiFi scan failed: ${error.message}`);
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

app.get('/api/scan/bluetooth', async (req, res) => {
  try {
    logger.info('Bluetooth scan initiated');
    const devices = await scanBluetooth();

    // Detect threats (for demonstration, we'll treat all bluetooth devices as potential threats)
    const deviceThreats = devices.map(device => ({
      id: Math.random().toString(36).substr(2, 9),
      timestamp: new Date().toISOString(),
      type: 'Unknown Bluetooth Device',
      description: 'Bluetooth device detected',
      device: device,
      severity: 'low'
    }));

    threats = [...threats, ...deviceThreats];

    // Update storage
    bluetoothDevices = devices;

    // Add to scan history
    scanHistory.push({
      type: 'bluetooth',
      timestamp: new Date().toISOString(),
      count: devices.length,
      threats: deviceThreats.length
    });

    // Broadcast updates
    broadcastUpdate('bluetoothUpdate', devices);
    if (deviceThreats.length > 0) {
      broadcastUpdate('threatUpdate', deviceThreats);
    }

    logger.success(`Bluetooth scan completed: ${devices.length} devices, ${deviceThreats.length} alerts`);

    res.json({
      success: true,
      count: devices.length,
      devices,
      threats: deviceThreats
    });
  } catch (error) {
    logger.error(`Bluetooth scan failed: ${error.message}`);
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

app.get('/api/threats', (req, res) => {
  res.json({
    success: true,
    count: threats.length,
    threats: threats.slice(-50) // Return last 50 threats
  });
});

app.get('/api/threats/stats', (req, res) => {
  const stats = threatDetector.getStatistics();
  res.json({
    success: true,
    stats
  });
});

app.get('/api/history', (req, res) => {
  const limit = parseInt(req.query.limit) || 50;
  res.json({
    success: true,
    count: scanHistory.length,
    history: scanHistory.slice(-limit)
  });
});

// Periodic scanning
let scanning = false;
const performScan = async () => {
  if (scanning) return;

  scanning = true;
  try {
    // Scan WiFi
    const wifiNetworks = await scanWifi();
    wifiDevices = wifiNetworks;
    broadcastUpdate('wifiUpdate', wifiNetworks);

    // Scan Bluetooth
    const btDevices = await scanBluetooth();
    bluetoothDevices = btDevices;
    broadcastUpdate('bluetoothUpdate', btDevices);

    // Detect threats
    const wifiThreats = threatDetector.detectThreats(wifiNetworks);
    const btThreats = btDevices.map(device => ({
      id: Math.random().toString(36).substr(2, 9),
      timestamp: new Date().toISOString(),
      type: 'Bluetooth Device',
      description: 'Bluetooth device detected',
      device: device,
      severity: 'low'
    }));

    const allThreats = [...wifiThreats, ...btThreats];
    if (allThreats.length > 0) {
      threats = [...threats, ...allThreats];
      broadcastUpdate('threatUpdate', allThreats);
    }

    // Update scan history
    scanHistory.push({
      type: 'auto',
      timestamp: new Date().toISOString(),
      wifiCount: wifiNetworks.length,
      btCount: btDevices.length,
      threats: allThreats.length
    });

    logger.info(`Auto scan completed: ${wifiNetworks.length} WiFi, ${btDevices.length} BT, ${allThreats.length} threats`);
  } catch (error) {
    logger.error(`Auto scan failed: ${error.message}`);
  } finally {
    scanning = false;
  }
};

// Start periodic scanning
setInterval(performScan, SCAN_INTERVAL);

// Start server
server.listen(PORT, () => {
  logger.success(`Cybersecurity Dashboard Server running on http://localhost:${PORT}`);
  logger.info('Available endpoints:');
  logger.info('  GET /api/health - Health check');
  logger.info('  GET /api/scan/wifi - Scan WiFi networks');
  logger.info('  GET /api/scan/bluetooth - Scan Bluetooth devices');
  logger.info('  GET /api/threats - Get detected threats');
  logger.info('  GET /api/threats/stats - Get threat statistics');
  logger.info('  GET /api/history - Get scan history');
  logger.info('WebSocket server listening for real-time updates');
});

// Graceful shutdown
process.on('SIGTERM', () => {
  logger.warn('SIGTERM received, shutting down gracefully...');
  server.close(() => {
    process.exit(0);
  });
});

process.on('SIGINT', () => {
  logger.warn('SIGINT received, shutting down gracefully...');
  server.close(() => {
    process.exit(0);
  });
});

module.exports = app;