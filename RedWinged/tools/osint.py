# Improved osint.py: Added automatic username checks with colors, HIBP for email, Roblox API, better handling

import requests
import random
from PIL import Image, ExifTags
import instaloader
import sys
import time
import phonenumbers
from phonenumbers import geocoder, carrier, NumberParseException
from colorama import Fore
from tools.shared import USER_AGENTS, typewriter_print  # From shared

# Sites for username checks (public endpoints; ethical use only)
USERNAME_SITES = {
    "Instagram": "https://www.instagram.com/{}/",
    "Reddit": "https://www.reddit.com/user/{}/",
    "Twitter": "https://twitter.com/{}",
    "Snapchat": "https://www.snapchat.com/add/{}",
    "GitHub": "https://github.com/{}",
    "TikTok": "https://www.tiktok.com/@{}",
    "Pinterest": "https://www.pinterest.com/{}/"
}

# Error indicators for sites that return 200 OK but show "not found" messages (case-insensitive)
ERROR_INDICATORS = {
    "Instagram": "Sorry, this page isn't available.",
    "Reddit": "Sorry, nobody on Reddit goes by that name.",
    "Twitter": "This account doesn’t exist",
    "Snapchat": "This user does not exist.",
    "GitHub": "Didn’t find anything here!",
    "TikTok": "Couldn't find this account.",
    "Pinterest": "This user doesn't exist."
}

def get_image_exif(image_path):
    """Extract EXIF metadata from image."""
    try:
        img = Image.open(image_path)
        exif_data = img._getexif()
        if exif_data:
            for tag_id in exif_data:
                tag = ExifTags.TAGS.get(tag_id, tag_id)
                data = exif_data.get(tag_id)
                typewriter_print(f"{tag}: {data}")
        else:
            typewriter_print("No EXIF data found.")
    except FileNotFoundError:
        typewriter_print("Error: File not found.")
    except Exception as e:
        typewriter_print(f"Error: {e}")

def username_tracker(username):
    """Automatically check if username exists on popular sites (public checks only)."""
    typewriter_print("Checking username existence (ethical/public data only):")
    headers = {'User-Agent': random.choice(USER_AGENTS)}
    for site, url_template in USERNAME_SITES.items():
        url = url_template.format(username)
        try:
            response = requests.get(url, headers=headers, timeout=5)
            text_lower = response.text.lower()
            error_msg = ERROR_INDICATORS.get(site, "").lower()
            if response.status_code != 200:
                typewriter_print(Fore.RED + f"{site}: Does not exist ({url}) - Status {response.status_code}")
            elif error_msg and error_msg in text_lower:
                typewriter_print(Fore.RED + f"{site}: Does not exist ({url})")
            elif site == "Snapchat" and "error" in text_lower:  # Extra fallback for Snapchat
                typewriter_print(Fore.RED + f"{site}: Does not exist ({url})")
            else:
                typewriter_print(Fore.GREEN + f"{site}: Exists ({url})")
            time.sleep(1)  # Rate limit ethically
        except Exception as e:
            typewriter_print(f"Error checking {site}: {e}")
    typewriter_print("Note: Discord not supported (no public check without API). Results based on status codes and content inspection for accuracy.")
    typewriter_print("Disclaimer: This tool may not be accurate as some websites provide an HTTP 200 no matter if the account does not exist.")

def email_lookup(email):
    """Check for public breaches via HIBP API and generate links."""
    typewriter_print("Checking email for public breaches (via HaveIBeenPwned API - ethical awareness tool):")
    headers = {'User-Agent': random.choice(USER_AGENTS), 'hibp-api-key': ''}  # Add key if you have one; free tier ok
    url = f"https://haveibeenpwned.com/api/v3/breachedaccount/{email}?truncateResponse=false"
    try:
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            breaches = response.json()
            if breaches:
                typewriter_print(Fore.RED + f"Email breached in {len(breaches)} incidents:")
                for breach in breaches:
                    typewriter_print(f"- {breach['Name']} (compromised on {breach['BreachDate']})")
            else:
                typewriter_print(Fore.GREEN + "No public breaches found.")
        elif response.status_code == 404:
            typewriter_print(Fore.GREEN + "No public breaches found.")
        else:
            typewriter_print(f"Error: API returned {response.status_code}")
    except Exception as e:
        typewriter_print(f"Error checking breaches: {e}")
    typewriter_print("Generating additional public search links:")
    typewriter_print(f"https://www.google.com/search?q={email}")
    typewriter_print(f"https://haveibeenpwned.com/{email}")

def phone_number_lookup(phone):
    """Parse phone and generate links (improved error handling)."""
    try:
        parsed = phonenumbers.parse(phone)
        if not phonenumbers.is_valid_number(parsed):
            raise NumberParseException(0, "Invalid number")
        country_code = phonenumbers.region_code_for_number(parsed)
        country_name = geocoder.description_for_number(parsed, "en")
        carrier_name = carrier.name_for_number(parsed, "en")
        typewriter_print(f"Detected Country Code: {country_code}")
        typewriter_print(f"Detected Country Name: {country_name}")
        typewriter_print(f"Is Valid Number: Yes")
        typewriter_print(f"Approximate Carrier: {carrier_name if carrier_name else 'Unknown'}")
    except NumberParseException:
        typewriter_print("Invalid phone number format. Falling back to basic search.")
    except Exception as e:
        typewriter_print(f"Error parsing number: {e}")
    finally:
        typewriter_print("Generating public search links (use ethically):")
        typewriter_print(f"https://www.google.com/search?q={phone}")

def ip_lookup(ip):
    """Lookup IP details from public API."""
    try:
        headers = {'User-Agent': random.choice(USER_AGENTS)}
        response = requests.get(f"https://ipapi.co/{ip}/json/", headers=headers, timeout=5)
        data = response.json()
        typewriter_print(f"City: {data.get('city', 'Unknown')}")
        typewriter_print(f"Region: {data.get('region', 'Unknown')}")
        typewriter_print(f"Country: {data.get('country_name', 'Unknown')}")
        typewriter_print(f"ISP: {data.get('org', 'Unknown')}")
    except Exception as e:
        typewriter_print(f"Error: {e}")

def instagram_account(username):
    """Fetch public Instagram profile (improved error messages)."""
    L = instaloader.Instaloader()
    try:
        profile = instaloader.Profile.from_username(L.context, username)
        typewriter_print(f"Username: {profile.username}")
        typewriter_print(f"Full Name: {profile.full_name if profile.full_name else 'Not publicly available'}")
        typewriter_print(f"Post Count: {profile.mediacount}")
        typewriter_print(f"Privacy Status: {'Private' if profile.is_private else 'Public'}")
        typewriter_print(f"Followers: {profile.followers}")
        typewriter_print(f"Followees: {profile.followees}")
        typewriter_print(f"Biography: {profile.biography}")
        typewriter_print("Note: Public data only; for educational use.")
    except instaloader.exceptions.ProfileNotExistsException:
        typewriter_print("Error: Profile does not exist.")
    except Exception as e:
        typewriter_print(f"Error: {e}. May be rate limit or private.")

def roblox_account(username):
    """Fetch public Roblox user info via APIs (educational/public data)."""
    headers = {'User-Agent': random.choice(USER_AGENTS)}
    try:
        # Get user ID from username
        id_url = "https://users.roblox.com/v1/usernames/users"
        payload = {"usernames": [username], "excludeBannedUsers": True}
        response = requests.post(id_url, json=payload, headers=headers, timeout=5)
        if response.status_code != 200 or not response.json().get('data'):
            typewriter_print("Error: Username not found.")
            return
        user_id = response.json()['data'][0]['id']
        
        # Get profile info
        profile_url = f"https://users.roblox.com/v1/users/{user_id}"
        profile = requests.get(profile_url, headers=headers, timeout=5).json()
        typewriter_print(f"Username: {profile['name']}")
        typewriter_print(f"Display Name: {profile['displayName']}")
        typewriter_print(f"Description: {profile['description']}")
        typewriter_print(f"Creation Date: {profile['created']}")
        
        # Get favorites (up to 5)
        favorites_url = f"https://games.roblox.com/v2/users/{user_id}/favorites/games?limit=5"
        favorites = requests.get(favorites_url, headers=headers, timeout=5).json().get('data', [])
        typewriter_print("Favorited Games (up to 5):")
        for game in favorites:
            typewriter_print(f"- {game['name']} (ID: {game['id']})")
        
        # Get creations (up to 5)
        creations_url = f"https://games.roblox.com/v2/users/{user_id}/games?accessFilter=2&limit=5&sortOrder=Asc"
        creations = requests.get(creations_url, headers=headers, timeout=5).json().get('data', [])
        typewriter_print("Own Creations (up to 5):")
        for game in creations:
            typewriter_print(f"- {game['name']} (ID: {game['rootPlace']['id']})")
        
        typewriter_print("Note: Public data only via Roblox APIs; for educational use.")
    except Exception as e:
        typewriter_print(f"Error fetching Roblox info: {e}")