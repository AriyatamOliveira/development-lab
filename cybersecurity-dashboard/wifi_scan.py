import json
from CoreWLAN import CWInterface

iface = CWInterface.interface()

networks = iface.scanForNetworksWithName_error_(None, None)[0]

results = []

for net in networks:
    results.append({
        "ssid": net.ssid() if net.ssid() else None,
        "bssid": net.bssid(),  # MUST exist
        "rssi": net.rssiValue(),
        "channel": net.wlanChannel().channelNumber() if net.wlanChannel() else None,
        "security": str(net.securityMode())
    })

print(json.dumps(results))