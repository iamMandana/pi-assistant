import os
import requests


def wifi_scan():
    try:
        # Executes system command to scan WiFi networks 
        result = os.popen("iwlist wlan0 scan | grep 'ESSID'").read()

        # Extract and clean network names from command output
        networks = [line.strip() for line in result.split("\n") if line]

        # Return up to 5 networks to limit response size
        return " | ".join(networks[:5]) if networks else "No networks found"
    except:
        return "WiFi scan failed"


def public_ip():
    try:
        # Fetch public IP from external service
        ip = requests.get("https://api.ipify.org").text

        return f"Public IP: {ip}"
    except:
        return "Unable to get IP"
