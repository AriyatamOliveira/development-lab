# Network Scanner Application - Architecture Plan

## Overview
A full-stack network scanner with WiFi and Bluetooth scanning capabilities, styled with a dark cyber theme.

## Technology Stack
- **Backend**: Node.js + Express
- **Frontend**: Vanilla HTML/CSS/JavaScript
- **macOS Compatibility**: Apple Silicon supported

## Architecture

```
/Users/ariyatamoliveira/Scanner
├── package.json
├── server.js              # Express server entry point
├── src/
│   ├── scanner.js          # WiFi & Bluetooth scanning logic
│   └── logger.js           # Terminal logging utility
├── public/
│   ├── index.html          # Main HTML page
│   ├── style.css           # Dark cyber theme styles
│   └── app.js              # Frontend JavaScript
└── PLAN.md
```

## Backend Design

### Endpoints
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/scan/wifi` | Scan available WiFi networks |
| GET | `/api/scan/bluetooth` | Scan nearby Bluetooth devices |
| GET | `/api/health` | Health check endpoint |

### WiFi Scanning
- Use `/usr/sbin/networksetup` for configured networks
- Use `/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport` for scanning
- Parse SSID, signal strength (dBm), and security type

### Bluetooth Scanning
- Use `blueutil` CLI tool (brew-installed) or `system_profiler`
- Alternative: `networksetup` for Bluetooth info
- Parse device name, MAC address

### Error Handling
- Graceful degradation if tools not available
- Meaningful error messages returned as JSON
- HTTP status codes: 200 success, 500 server error

## Frontend Design

### UI Components
1. **Header** - App title with cyber styling
2. **WiFi Scanner Section**
   - Scan button
   - Network list (SSID, Signal, Security)
3. **Bluetooth Scanner Section**
   - Scan button
   - Device list (Name, MAC, Signal)
4. **Status Bar** - Loading states and error messages

### States
- Idle: Ready to scan
- Loading: Spinner + "Scanning..." text
- Success: Display results
- Error: Error message with retry option

### Terminal Logs
- Console output styled as terminal logs
- Show scan start/complete timestamps
- Display device counts found

## Security Considerations
- Input validation on any user inputs
- Sanitize output to prevent XSS
- No sensitive data logging

## Dependencies
- express: ^4.18.x
- cors: ^2.8.x (if needed for dev)

## Dev Dependencies (optional)
- nodemon: for auto-restart during development
