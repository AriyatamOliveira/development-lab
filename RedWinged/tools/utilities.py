# Improved utilities.py: Added virus_scanner, more error handling, comments

import hashlib
import random
import os
import sys
import time
from colorama import Fore
from tools.shared import typewriter_print  # From shared

# Example known bad hashes (educational; add real ones from VirusTotal or databases)
BAD_HASHES = {
    'eicar_test': '44d88612fea8a8f36de82e1278abb02f',  # MD5 of EICAR test string
    'HorrorRansom': '1a8e74c4bb9a2c5b38b4412a6b484737',
}

# Simple signatures (strings to scan for in files)
BAD_SIGNATURES = [
    'X5O!P%@AP[4\\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*',  # EICAR
    'HorrorRansom',
    'APrivateAntiVirus',
]

def password_encrypted(password):
    """Hash password with SHA256 for learning."""
    try:
        hashed = hashlib.sha256(password.encode()).hexdigest()
        typewriter_print(f"Encrypted (SHA256): {hashed}")
        typewriter_print("Note: One-way hashing; use in secure apps.")
    except Exception as e:
        typewriter_print(f"Error: {e}")

def search_in_database(db_path, keyword):
    """Search local text file for keyword."""
    try:
        with open(db_path, 'r') as f:
            lines = f.readlines()
            found = False
            for line in lines:
                if keyword.lower() in line.lower():
                    typewriter_print(f"Match: {line.strip()}")
                    found = True
            if not found:
                typewriter_print("No matches found.")
    except FileNotFoundError:
        typewriter_print("Error: File not found.")
    except Exception as e:
        typewriter_print(f"Error: {e}")

def dark_web_links():
    """Display example .onion links (educational/Tor only)."""
    typewriter_print("Example public .onion links (access via Tor only):")
    typewriter_print("Facebook: facebookwkhpilnemxj7asaniu7vnjjbiltxjqhye3mhbshg7kx5tfyd.onion")
    typewriter_print("Search Engines:")
    typewriter_print("├─ Torch: http://xmh57jrknzkhv6y3ls3ubitzfqnkrwxhopf5aygthi7d6rplyvk3noyd.onion/")
    typewriter_print("├─ Danex: http://danexio627wiswvlpt6ejyhpxl5gla5nt2tgvgm2apj2ofrgm44vbeyd.onion/")
    typewriter_print("├─ Sentor: http://e27slbec2ykiyo26gfuovaehuzsydffbit5nlxid53kigw3pvz6uosqd.onion/")
    typewriter_print("├─ Hidden Answers: http://answerszuvs3gg2l64e6hmnryudl5zgrmwm3vh65hzszdghblddvfiqd.onion/")
    typewriter_print("└─ riseup searx: http://ozmh2zkwx5cjuzopui64csb5ertcooi5vya6c2gm4e3vcvf2c2qvjiyd.onion/")
    typewriter_print("")
    typewriter_print("Bitcoin Anonymity:")
    typewriter_print("├─ Dark Mixer: http://y22arit74fqnnc2pbieq3wqqvkfub6gnlegx3cl6thclos4f7ya7rvad.onion/")
    typewriter_print("├─ Mixabit: http://hqfld5smkr4b4xrjcco7zotvoqhuuoehjdvoin755iytmpk4sm7cbwad.onion/")
    typewriter_print("├─ EasyCoin: http://mp3fpv6xbrwka4skqliiifoizghfbjy5uyu77wwnfruwub5s4hly2oid.onion/")
    typewriter_print("├─ Onionwallet: http://p2qzxkca42e3wccvqgby7jrcbzlf6g7pnkvybnau4szl5ykdydzmvbid.onion/")
    typewriter_print("├─ VirginBitcoin: http://ovai7wvp4yj6jl3wbzihypbq657vpape7lggrlah4pl34utwjrpetwid.onion/")
    typewriter_print("└─ Cryptostamps: http://lgh3eosuqrrtvwx3s4nurujcqrm53ba5vqsbim5k5ntdpo33qkl7buyd.onion/")
    typewriter_print("")
    typewriter_print("DDoS:")
    typewriter_print("└─ Stresser: http://ecwvi3cd6h27r2kjx6ur6gdi4udrh66omvqeawp3dzqrtfwo432s7myd.onion/")
    typewriter_print("")
    typewriter_print("Market:")
    typewriter_print("├─ Deep Market: http://deepmar4ai3iff7akeuos3u3727lvuutm4l5takh3dmo3pziznl5ywqd.onion/")
    typewriter_print("├─ DrChronic: http://iwggpyxn6qv3b2twpwtyhi2sfvgnby2albbcotcysd5f7obrlwbdbkyd.onion/")
    typewriter_print("├─ TomAndJerry: http://rfyb5tlhiqtiavwhikdlvb3fumxgqwtg2naanxtiqibidqlox5vispqd.onion/")
    typewriter_print("├─ UKpassports: http://3bp7szl6ehbrnitmbyxzvcm3ieu7ba2kys64oecf4g2b65mcgbafzgqd.onion/")
    typewriter_print("├─ EuroGuns: http://t43fsf65omvf7grt46wlt2eo5jbj3hafyvbdb7jtr2biyre5v24pebad.onion/")
    typewriter_print("├─ Darkmining: http://jbtb75gqlr57qurikzy2bxxjftzkmanynesmoxbzzcp7qf5t46u7ekqd.onion/")
    typewriter_print("├─ DeDope: http://sga5n7zx6qjty7uwvkxpwstyoh73shst6mx3okouv53uks7ks47msayd.onion/")
    typewriter_print("├─ Webuybitcoins: http://wk3mtlvp2ej64nuytqm3mjrm6gpulix623abum6ewp64444oreysz7qd.onion/")
    typewriter_print("├─ ASAP Market \
│   ├─ ASAP Market 1: http://asap4u7rq4tyakf5gdahmj2c77blwc4noxnsppp5lzlhk7x34x2e22yd.onion/ \
│   ├─ ASAP Market 2: http://asap2u4pvplnkzl7ecle45wajojnftja45wvovl3jrvhangeyq67ziid.onion/ \
│   └─ ASAP Market 3: http://asap4u2ihsunfdsumm66pmado3mt3lemdiu3fbx5b7wj5hb3xpgmwkqd.onion/")
    typewriter_print("├─ Tor Market: http://rrlm2f22lpqgfhyydqkxxzv6snwo5qvc2krjt2q557l7z4te7fsvhbid.onion/")
    typewriter_print("├─ Drug Stores \
│   ├─ DCdutchconnectionUK: http://wbz2lrxhw4dd7h5t2wnoczmcz5snjpym4pr7dzjmah4vi6yywn37bdyd.onion/ \
│   ├─ CanabisUK: http://7mejofwihleuugda5kfnr7tupvfbaqntjqnfxc4hwmozlcmj2cey3hqd.onion/ \
│   ├─ Bitpharma: http://guzjgkpodzshso2nohspxijzk5jgoaxzqioa7vzy6qdmwpz3hq4mwfid.onion/ \
│   ├─ EuCanna: http://n6qisfgjauj365pxccpr5vizmtb5iavqaug7m7e4ewkxuygk5iim6yyd.onion/ \
│   ├─ Smokeables: http://kl4gp72mdxp3uelicjjslqnpomqfr5cbdd3wzo5klo3rjlqjtzhaymqd.onion/ \
│   └─ WeedShop: http://marijuanaman43fi4t7el66di7vdpbfyhvkgk4mt7wxkg6erfkv65npy3d.onion/ \
├─ Cartel: http://7myb7itqew5ffqftvxjh2k7qxwrh7imavxlpn3fxa32d3rvw32e3s7ad.onion/ \
└─ Kingdom Market: http://hdfozcnzivftjokvkdjzl6fhq3c7ltyct6db4efov2w4p7xb6rmhlfqd.onion/")
    typewriter_print("")
    typewriter_print("Torrents:")
    typewriter_print("├─ The Pirate Bay: http://uj3wazyk5kz5rzs.onion/ \
└─ 1337x: http://1337xwlc2c8sf3d7.onion/")
    typewriter_print("")
    typewriter_print("Wikis:")
    typewriter_print("├─ Hidden Wiki: http://wikitjerrta4qgz4.onion/ \
└─ Deep Web Wiki: http://wikicbtbf7rgjjbqe.onion/")
    typewriter_print("")
    typewriter_print("Government:")
    typewriter_print("└─ UK Passport Renewal: http://3bp7szl6ehbrnitmbyxzvcm3ieu7ba2kys64oecf4g2b65mcgbafzgqd.onion/")
    typewriter_print("Note: Use ethically.")

def ip_generator():
    """Generate random IP for testing."""
    ip = ".".join(str(random.randint(0, 255)) for _ in range(4))
    typewriter_print(f"Random IP (for testing): {ip}")

def virus_scanner(dir_path):
    """Educational antivirus: List files, select one, hash check and signature scan."""
    try:
        files = [f for f in os.listdir(dir_path) if os.path.isfile(os.path.join(dir_path, f))]
        if not files:
            typewriter_print("No files found in directory.")
            return
        typewriter_print("Files in directory:")
        for i, file in enumerate(files, 1):
            typewriter_print(f"{i}: {file}")
        selection = int(input("Select file number: "))
        if 1 <= selection <= len(files):
            file_path = os.path.join(dir_path, files[selection - 1])
            # Compute hash
            hasher = hashlib.md5()  # MD5 for example; can use SHA256
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hasher.update(chunk)
            file_hash = hasher.hexdigest()  # Fixed: Added () to call the method
            if file_hash in BAD_HASHES.values():
                typewriter_print(Fore.RED + f"Warning: File matches known bad hash ({file_hash}). Potential malware!")
            else:
                typewriter_print(Fore.GREEN + f"Hash check: Safe ({file_hash}).")
            # Signature scan
            with open(file_path, 'r', errors='ignore') as f:
                content = f.read()
                for sig in BAD_SIGNATURES:
                    if sig in content:
                        typewriter_print(Fore.RED + f"Warning: Matches bad signature! Potential test virus.")
                        break
                else:
                    typewriter_print(Fore.GREEN + "Signature scan: Safe.")
        else:
            typewriter_print("Invalid selection.")
    except ValueError:
        typewriter_print("Error: Invalid number.")
    except FileNotFoundError:
        typewriter_print("Error: Directory not found.")
    except Exception as e:
        typewriter_print(f"Error scanning: {e}")
    typewriter_print("Note: Educational example; use real AV for protection. Expand BAD_HASHES for more.")