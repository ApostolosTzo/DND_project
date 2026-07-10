import os
import msvcrt

def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")

def show(text: str):
    print(text)
    
#============================
# Menu and Input Functions
#============================

def get_key():
    key = msvcrt.getch()
    if key == b'\xe0':
        arrow = msvcrt.getch()
        if arrow == b'H':
            return "up"
        if arrow == b'P':
            return "down"
        if arrow == b'K':
            return "left"
        if arrow == b'M':
            return "right"
    elif key == b'\r':
        return "enter"
    elif key == b'\x1b':
        return "esc"
    else:
        try:
            return key.decode().lower()
        except:
            return None


#===========================
# Menu and Input Functions
#===========================

def menu(title: str, options: list, body: str = "") -> int:
    selected = 0
    while True:
        clear_screen()
        print(f"=== {title} ===\n")
        if body:
            print(body)
            print("")
        for i, opt in enumerate(options):
            prefix = " >" if i == selected else "  "
            print(f"{prefix} {opt}")
        print("\n(\u2191/\u2193 to navigate, Enter to select)")

        key = get_key()
        if key == "up":
            selected = (selected - 1) % len(options)
        elif key == "down":
            selected = (selected + 1) % len(options)
        elif key == "enter":
            return selected

def prompt(text: str) -> str:
    print(f"\n{text}")
    return input("> ").strip()

def press_any_key():
    print("\nPress any key to continue...")
    msvcrt.getch()
