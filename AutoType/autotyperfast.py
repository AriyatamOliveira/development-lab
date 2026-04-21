import time
import random
from pynput.keyboard import Key, Controller

keyboard = Controller()

def get_user_input():
    """Prompt user for text input"""
    print("AutoType - Human-like Typing Simulator")
    print("=" * 40)
    print("EXTREMELY GLITCHY, DO NOT USE")
    text = input("Enter or paste the text to be typed: ")

    return text

def normalize_text(text):
    """Normalize special characters to ASCII equivalents"""
    # Replace em-dashes, en-dashes with double hyphens
    text = text.replace('—', '--').replace('–', '-')

    # Replace smart quotes with straight quotes
    text = text.replace('“', '"').replace('”', '"').replace('‘', "'").replace('’', "'")

    # Replace ellipses with three periods
    text = text.replace('…', '...')

    # Replace other common Unicode characters
    text = text.replace('–', '-')  # en dash
    text = text.replace('•', '*')  # bullet
    text = text.replace('£', 'GBP')
    text = text.replace('€', 'EUR')
    text = text.replace('©', '(c)')
    text = text.replace('®', '(R)')

    return text

def countdown_timer(seconds=5):
    """Display countdown timer before typing begins"""
    print(f"\nStarting typing in {seconds} seconds...")
    print("Switch to your target window now!\n")

    for i in range(seconds, 0, -1):
        print(f"{i} seconds remaining...", end="\r")
        time.sleep(1)

    print("Typing started!" + " " * 20)  # Clear the line

def human_typing(text):
    """Simulate human-like typing with variable speed and occasional mistakes"""
    # Normalize text first
    normalized_text = normalize_text(text)
    print(f"Normalized text length: {len(normalized_text)} characters")

    # Define neighboring keys for common typing errors
    neighbor_keys = {
        'a': ['q', 'w', 's', 'z'],
        'b': ['v', 'g', 'h', 'n'],
        'c': ['x', 'd', 'f', 'v'],
        'd': ['s', 'e', 'r', 'f', 'c', 'x'],
        'e': ['w', 'r', 'd', 's'],
        'f': ['d', 'r', 't', 'g', 'v', 'c'],
        'g': ['f', 't', 'y', 'h', 'b', 'v'],
        'h': ['g', 'y', 'u', 'j', 'n', 'b'],
        'i': ['u', 'o', 'k', 'j'],
        'j': ['h', 'u', 'i', 'k', 'm', 'n'],
        'k': ['j', 'i', 'o', 'l', 'm'],
        'l': ['k', 'o', 'p'],
        'm': ['n', 'j', 'k'],
        'n': ['b', 'h', 'j', 'm'],
        'o': ['i', 'p', 'l', 'k'],
        'p': ['o', 'l'],
        'q': ['w', 'a'],
        'r': ['e', 't', 'f', 'd'],
        's': ['a', 'w', 'e', 'd', 'x', 'z'],
        't': ['r', 'y', 'g', 'f'],
        'u': ['y', 'i', 'j', 'h'],
        'v': ['c', 'f', 'g', 'b'],
        'w': ['q', 'e', 's', 'a'],
        'x': ['z', 's', 'd', 'c'],
        'y': ['t', 'u', 'g', 'h'],
        'z': ['a', 's', 'x'],
        ' ': ['c', 'v', 'b', 'n', 'm'],
        '1': ['2', 'q'],
        '2': ['1', '3', 'w', 'q'],
        '3': ['2', '4', 'e', 'w'],
        '4': ['3', '5', 'r', 'e'],
        '5': ['4', '6', 't', 'r'],
        '6': ['5', '7', 'y', 't'],
        '7': ['6', '8', 'u', 'y'],
        '8': ['7', '9', 'i', 'u'],
        '9': ['8', '0', 'o', 'i'],
        '0': ['9', 'p', 'o']
    }

    # === SPEED CALIBRATION VARIABLES ===
    # Base typing speed (seconds between characters)
    BASE_SPEED_MIN = 0.00005  # Minimum delay between characters
    BASE_SPEED_MAX = 0.0001  # Maximum delay between characters

    # Punctuation weight (additional pause after punctuation)
    PUNCTUATION_PAUSE_MIN = 0.0003  # Minimum pause after punctuation
    PUNCTUATION_PAUSE_MAX = 0.0008  # Maximum pause after punctuation

    # Mistake probability (chance of making a typing error)
    MISTAKE_PROBABILITY = 0.00  # 3% chance of making a mistake

    # Error correction timing (visible correction sequence)
    MISTAKE_OOPS_PAUSE = 0.0  # Pause after typing wrong character
    MISTAKE_BACKSPACE_PAUSE = 0.0  # Pause after backspacing

    # Buffer stability (mandatory cooldown after every keypress)
    KEYBOARD_COOLDOWN = 0.0009  # Mandatory cooldown to prevent input lag
    # === END SPEED CALIBRATION VARIABLES ===

    for i, char in enumerate(normalized_text):
        # Occasionally make a typing mistake (3% chance)
        if random.random() < MISTAKE_PROBABILITY and char in neighbor_keys:
            # Make a mistake by typing a neighboring key
            mistake_char = random.choice(neighbor_keys[char])
            keyboard.press(mistake_char)
            keyboard.release(mistake_char)
            time.sleep(KEYBOARD_COOLDOWN)  # Mandatory cooldown
            time.sleep(MISTAKE_OOPS_PAUSE)  # "Oops" moment pause

            # Backspace to correct the mistake
            keyboard.press(Key.backspace)
            keyboard.release(Key.backspace)
            time.sleep(KEYBOARD_COOLDOWN)  # Mandatory cooldown
            time.sleep(MISTAKE_BACKSPACE_PAUSE)  # Pause after backspace

            # Type the correct character
            keyboard.press(char)
            keyboard.release(char)
            time.sleep(KEYBOARD_COOLDOWN)  # Mandatory cooldown
        else:
            # Type the correct character
            if char == '\n':
                keyboard.press(Key.enter)
                keyboard.release(Key.enter)
            elif char == '\t':
                keyboard.press(Key.tab)
                keyboard.release(Key.tab)
            else:
                keyboard.press(char)
                keyboard.release(char)

            time.sleep(KEYBOARD_COOLDOWN)  # Mandatory cooldown

        # Brisk typing speed with punctuation weighting
        if char in '.!?,;:()[]{}':
            # Longer pause for punctuation (thought pause)
            time.sleep(random.uniform(PUNCTUATION_PAUSE_MIN, PUNCTUATION_PAUSE_MAX))
        elif char == ' ':
            # Standard pause for spaces
            time.sleep(random.uniform(BASE_SPEED_MIN, BASE_SPEED_MAX))
        else:
            # Base typing speed for regular characters
            time.sleep(random.uniform(BASE_SPEED_MIN, BASE_SPEED_MAX))

        # Occasional thinking pauses (reduced frequency)
        if random.random() < 0.01:  # 1% chance of a thinking pause
            time.sleep(random.uniform(0.3, 0.7))

def main():
    """Main function to run the AutoType application"""
    try:
        # Get text from user
        user_text = get_user_input()

        if not user_text:
            print("No text entered. Exiting.")
            return

        # Start countdown
        countdown_timer()

        # Begin human-like typing
        human_typing(user_text)

        print("\n\nTyping completed!")

    except KeyboardInterrupt:
        print("\n\nTyping interrupted by user.")
    except Exception as e:
        print(f"\nAn error occurred: {e}")
        print("Please ensure you have granted accessibility permissions in System Settings > Privacy & Security > Accessibility")

if __name__ == "__main__":
    main()