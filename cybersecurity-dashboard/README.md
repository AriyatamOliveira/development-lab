# Cybersecurity Dashboard - Backend

A complete backend system for a cybersecurity dashboard with real-time network scanning, threat detection, and alerting capabilities.

## Features

- Real-time network scanner (WiFi + Bluetooth)
- Device fingerprinting
- Threat detection system
- WebSocket-based real-time updates
- Comprehensive logging
- Alert system

## Directory Structure

```
cybersecurity-dashboard/
├── api/                 # Main server and routes
├── detectors/           # Threat detection modules
├── fingerprinters/      # Device fingerprinting modules
├── alerts/              # Alert system components
├── utils/               # Utility functions
├── config/              # Configuration files
├── logs/                # Log storage (to be implemented)
└── public/              # Static files (to be implemented)
```

## Installation

```bash
npm install
```

## Usage

```bash
# Development mode
npm run dev

# Production mode
npm start
```

## API Endpoints

- `GET /api/health` - Health check
- `GET /api/scan/wifi` - Scan WiFi networks
- `GET /api/scan/bluetooth` - Scan Bluetooth devices
- `GET /api/threats` - Get detected threats
- `GET /api/threats/stats` - Get threat statistics
- `GET /api/history` - Get scan history

## WebSocket Events

- `wifiUpdate` - WiFi scan results
- `bluetoothUpdate` - Bluetooth scan results
- `threatUpdate` - New threats detected
- `init` - Initial data for new connections

## Environment Variables

- `PORT` - Server port (default: 3000)
- `SCAN_INTERVAL` - Auto-scan interval in ms (default: 30000)
- `LOG_LEVEL` - Logging level (default: info)

## Integration with Original Scanner

The system can be integrated with the original scanner code by copying the scanner utilities and updating imports.