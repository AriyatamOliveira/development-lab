# RedWinged Tools

RedWinged Tools is a free, educational multi-tool inspired by similar projects, focused on ethical learning in Cybersecurity, Pentesting, OSINT, and Network Scanning. (For educational purposes only. Compatible with macOS and Python 3.11.9.)

Developed in Python by [Your Name or Handle], this tool is in English and optimized for macOS (e.g., version 14+ or equivalent to "Tahoe 26"). It is open-source for transparency, with no malware, backdoors, or harmful code. Updates can be made as needed. Free for educational use.

## Disclaimer

* RedWinged Tools is developed solely for educational purposes and legal use. Use it only in accordance with the laws of your country. Any illegal activity is prohibited and punishable by law.
* This project is for personal learning only. Do not use for malicious purposes, unauthorized access, or harm.
* By using RedWinged Tools, you accept full responsibility for your actions. The creator is not liable for misuse.
* All features are ethical and non-intrusive, focusing on public data and consented testing (e.g., on your own networks). Automatic checks use public APIs/endpoints; respect rate limits and terms of service.

## Features & Descriptions

┌── ⚒️ - RedWinged Tools
│   ├── 0: Info                               : Displays general information about RedWinged Tools.
│   └── 1: Site                               : Placeholder for any related links (e.g., educational resources).
│
├── 🕵️‍♂️ - Network Scanner
│   ├── 2: Website Info Scanner               : Retrieves public headers and info from a website (using requests with user agents).
│   ├── 3: Ip Scanner                         : Retrieves public info about an IP.
│   ├── 4: Ip Port Scanner                    : Checks common open ports on an IP (ethical use on owned systems only).
│   └── 5: Ip Pinger                          : Tests connectivity to an IP via ping.
│
├── 🔎 - OSINT
│   ├── 6: Get Image Exif                     : Extracts metadata from a local image file (using Pillow).
│   ├── 7: Username Tracker                   : Automatically checks if username exists on popular sites (Instagram, Reddit, Twitter, Snapchat, etc.) with colored output.
│   ├── 8: Email Lookup                       : Checks for public breaches via HaveIBeenPwned API; generates search links.
│   ├── 9: Phone Number Lookup                : Parses phone number to detect country/code (using phonenumbers), validates, and generates search links.
│   ├── 10: Ip Lookup                         : Retrieves location and details from a public IP API.
│   ├── 11: Instagram Account                 : Retrieves public profile info using Instaloader (anonymous).
│   └── 12: Roblox Account                    : Retrieves public Roblox user info (name, description, creation date, favorites, creations) via public APIs.
│
├── 🔧 - Utilities
│   ├── 13: Password Encrypted                : Encrypts a password using SHA256 hashing (for learning).
│   ├── 14: Search In DataBase                : Searches keywords in a local text file (simulated database).
│   ├── 15: Dark Web Links                    : Displays example public .onion links (use with Tor for education).
│   ├── 16: Ip Generator                      : Generates random valid IP addresses (for testing).
│   └── 17: Virus Scanner                     : Lists files in a directory, selects one, computes hash, and checks against known bad hashes/signatures (educational example).

## New Enhancements
- Automatic username existence checks with random user agents and colored output.
- Public breach checks for emails via HaveIBeenPwned.
- Public Roblox profile fetching.
- Simple inbuilt antivirus using file hashing and signature scanning (expandable for learning).
- Improved error handling, comments, and performance across all scripts.

## Requirements

- Python 3.11.9 (install from https://www.python.org/downloads/macos/).
- macOS (optimized for recent versions; test on your "Tahoe 26" setup).
- pip3.11 for installing dependencies.

## Installation

1. Create the folder structure.
2. Open terminal in RedWinged.
3. Run `python3.11 setup.py` to install dependencies.
4. Run `python3.11 redwinged.py` to launch.

## About

RedWinged Tools is an ethical, educational tool for learning cybersecurity on macOS with Python 3.11.9. Focus on legal applications only. Expanded OSINT with automatic checks and new utilities.