# AutoType - Human-like Typing Simulator

AutoType is a Python-based automation tool that simulates human-like typing on macOS. It types text with variable rhythms, natural pauses, and occasional simulated mistakes to appear more human-like.

## Features

- Professional human typing speed ("Brisk" tier)
- Visible error correction for realistic typing behavior
- Normalization of special characters (em-dashes, smart quotes, ellipses)
- Buffer stability for reliable performance in browser-based applications
- Works with any macOS application

## Installation

1. Install the required dependencies:
   ```bash
   pip3.11 install -r requirements.txt
   ```

2. Grant accessibility permissions:
   - Open System Settings > Privacy & Security > Accessibility
   - Add Terminal.app (or your preferred terminal application) to the list of apps allowed to control your computer

## Usage

Run the script with:
```bash
python3.11 autotyper.py
```

1. Enter or paste the text you want to be typed
2. You'll have 5 seconds to switch to your target window
3. The script will begin typing with professional human-like behavior

## How It Works

### Speed Calibration

- **Base Typing Speed**: 0.05s to 0.12s between characters (fast but readable)
- **Punctuation Weight**: 0.2s to 0.4s pause after punctuation marks
- **Visible Error Correction**:
  - 3% chance of making a typing mistake
  - 0.15s pause after wrong character ("oops" moment)
  - 0.1s pause after backspacing to correct
- **Buffer Stability**: 0.01s mandatory cooldown after every keypress

### Character Normalization

Automatically converts special characters:
- Em-dashes (—) to double hyphens (--)
- Smart quotes (“, ”) to straight quotes (")
- Ellipses (…) to three periods (...)

## Requirements

- Python 3.11.9
- macOS operating system
- Accessibility permissions enabled for your terminal application