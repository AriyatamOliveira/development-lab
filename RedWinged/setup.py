import os
import sys

# Check Python version
if sys.version_info[:3] != (3, 11, 9):
    print("This tool requires Python 3.11.9. Please install the correct version from https://www.python.org/downloads/macos/.")
    sys.exit(1)

# Install dependencies with error handling
print("Installing dependencies from requirements.txt...")
try:
    os.system('pip3.11 install -r requirements.txt')
    print("Installation complete. If errors occurred, check your pip setup or network.")
except Exception as e:
    print(f"Error during installation: {e}")
print("Run 'python3.11 redwinged.py' to start the tool.")

os.system('python3.11 redwinged.py')