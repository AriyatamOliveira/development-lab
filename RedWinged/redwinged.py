#!/usr/bin/env python3
# Shebang for macOS Python 3.11.9 - Improved with better structure and comments

import sys
import time
import os
from colorama import Fore, Style, init

# Initialize colorama with strip for non-TTY (e.g., VS Code Debug Console)
init(autoreset=True, strip=not sys.stdout.isatty())

# Import shared items
from tools.shared import USER_AGENTS, typewriter_print

# Import tools with improved modules
from tools.network_scanner import website_info_scanner, ip_scanner, ip_port_scanner, ip_pinger
from tools.osint import get_image_exif, username_tracker, email_lookup, phone_number_lookup, ip_lookup, instagram_account, roblox_account
from tools.utilities import password_encrypted, search_in_database, dark_web_links, ip_generator, virus_scanner

def clear_screen():
    """Clear the terminal screen on macOS."""
    os.system('clear')

def print_banner():
    """Display enhanced ASCII banner with faster typewriter effect."""
    banner_lines = [
        "__________           ._____      __.__                          .___",
        "\______   \ ____   __| _/  \    /  \__| ____    ____   ____   __| _/",
        " |       _// __ \ / __ |\   \/\/   /  |/    \  / ___\_/ __ \ / __ |",
        " |    |   \  ___// /_/ | \        /|  |   |  \/ /_/  >  ___// /_/ |",
        " |____|_  /\___  >____ |  \__/\  / |__|___|  /\___  / \___  >____ |",
        "       \/     \/     \/       \/          \//_____/      \/     \/",
        "                Tools"
    ]
    wing_lines = [
        " .-~-. ",
        " / \\ ",
        " | | ",
        " \\. ./ ",
        " `~` "
    ]
    for line in banner_lines:
        typewriter_print(Fore.RED + line.center(80), delay=0.001)  # Ultra-fast for banner
    for line in wing_lines:
        print(Fore.RED + line.center(80))
        time.sleep(0.05)  # Slightly faster loading

def display_category_icon(category):
    """Display small ASCII icons for categories with quick loading."""
    icons = {
        "network": [" /\\", "/  \\", "/____\\"],
        "osint": [" O", " /|\\", " / \\"],
        "utilities": [" []", " | |", " |_|"]
    }
    icon = icons.get(category, [])
    for line in icon:
        print(Fore.CYAN + line.center(80))
        time.sleep(0.05)  # Faster

def display_menu():
    """Display menu with sections loading quickly one by one."""
    menu_sections = [
        (Fore.RED, "┌── ⚒️ - RedWinged Tools"),
        (Fore.WHITE, "│   ├── 0: Info"),
        (Fore.WHITE, "│   └── 1: Site"),
        (Fore.WHITE, "│"),
        (Fore.BLUE, "├── 🕵️‍♂️ - Network Scanner"),
        (Fore.WHITE, "│   ├── 2: Website Info Scanner"),
        (Fore.WHITE, "│   ├── 3: Ip Scanner"),
        (Fore.WHITE, "│   ├── 4: Ip Port Scanner"),
        (Fore.WHITE, "│   └── 5: Ip Pinger"),
        (Fore.WHITE, "│"),
        (Fore.GREEN, "├── 🔎 - OSINT"),
        (Fore.WHITE, "│   ├── 6: Get Image Exif"),
        (Fore.WHITE, "│   ├── 7: Username Tracker"),
        (Fore.WHITE, "│   ├── 8: Email Lookup"),
        (Fore.WHITE, "│   ├── 9: Phone Number Lookup"),
        (Fore.WHITE, "│   ├── 10: Ip Lookup"),
        (Fore.WHITE, "│   ├── 11: Instagram Account"),
        (Fore.WHITE, "│   └── 12: Roblox Account"),
        (Fore.WHITE, "│"),
        (Fore.YELLOW, "├── 🔧 - Utilities"),
        (Fore.WHITE, "│   ├── 13: Password Encrypted"),
        (Fore.WHITE, "│   ├── 14: Search In DataBase"),
        (Fore.WHITE, "│   ├── 15: Dark Web Links"),
        (Fore.WHITE, "│   ├── 16: Ip Generator"),
        (Fore.WHITE, "│   └── 17: Virus Scanner"),
        (Fore.WHITE, "│"),
        (Fore.RED, "└── 99: Exit")
    ]
    current_category = ""
    for color, line in menu_sections:
        if "Network Scanner" in line:
            current_category = "network"
        elif "OSINT" in line:
            current_category = "osint"
        elif "Utilities" in line:
            current_category = "utilities"
        if "├──" in line and current_category:
            display_category_icon(current_category)
            current_category = ""
        print(color + line)
        time.sleep(0.05)  # Faster menu loading

def loading_animation():
    """Show processing animation then clear screen."""
    sys.stdout.write(Fore.CYAN + "Processing")
    for _ in range(3):
        sys.stdout.write('.')
        sys.stdout.flush()
        time.sleep(0.3)  # Slightly faster
    print()
    clear_screen()

def main():
    """Main loop for the tool with version check and menu handling."""
    if sys.version_info[:3] != (3, 11, 9):
        typewriter_print(Fore.RED + "This tool requires Python 3.11.9.")
        sys.exit(1)

    clear_screen()
    print_banner()

    while True:
        display_menu()
        choice = input(Fore.WHITE + "Enter your choice: ").strip()
        clear_screen()

        if choice in ['2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17']:
            loading_animation()

        try:
            if choice == '0':
                typewriter_print(Fore.CYAN + "RedWinged Tools: Ethical educational tool for cybersecurity learning on macOS.")
            elif choice == '1':
                typewriter_print(Fore.CYAN + "Visit educational sites like https://owasp.org for more learning.")
            elif choice == '2':
                url = input("Enter website URL: ")
                clear_screen()
                website_info_scanner(url)
            elif choice == '3':
                ip = input("Enter IP: ")
                clear_screen()
                ip_scanner(ip)
            elif choice == '4':
                ip = input("Enter IP: ")
                clear_screen()
                ip_port_scanner(ip)
            elif choice == '5':
                ip = input("Enter IP: ")
                clear_screen()
                ip_pinger(ip)
            elif choice == '6':
                image_path = input("Enter local image path: ")
                clear_screen()
                get_image_exif(image_path)
            elif choice == '7':
                username = input("Enter username: ")
                clear_screen()
                username_tracker(username)
            elif choice == '8':
                email = input("Enter email: ")
                clear_screen()
                email_lookup(email)
            elif choice == '9':
                phone = input("Enter phone number: ")
                clear_screen()
                phone_number_lookup(phone)
            elif choice == '10':
                ip = input("Enter IP: ")
                clear_screen()
                ip_lookup(ip)
            elif choice == '11':
                username = input("Enter Instagram username: ")
                clear_screen()
                instagram_account(username)
            elif choice == '12':
                username = input("Enter Roblox username: ")
                clear_screen()
                roblox_account(username)
            elif choice == '13':
                password = input("Enter password to encrypt: ")
                clear_screen()
                password_encrypted(password)
            elif choice == '14':
                db_path = input("Enter local database file path (txt): ")
                keyword = input("Enter keyword: ")
                clear_screen()
                search_in_database(db_path, keyword)
            elif choice == '15':
                clear_screen()
                dark_web_links()
            elif choice == '16':
                clear_screen()
                ip_generator()
            elif choice == '17':
                dir_path = input("Enter directory path (leave blank for current): ") or os.getcwd()
                clear_screen()
                virus_scanner(dir_path)
            elif choice == '99':
                typewriter_print(Fore.RED + "Exiting RedWinged Tools.")
                sys.exit(0)
            else:
                typewriter_print(Fore.RED + "Invalid choice. Try again.")
        except Exception as e:
            typewriter_print(Fore.RED + f"Error during execution: {e}. This is for educational debugging.")

        if choice != '99':
            input(Fore.CYAN + "Press Enter to continue...")
            clear_screen()
            print_banner()

if __name__ == "__main__":
    main()