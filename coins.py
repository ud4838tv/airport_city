# TODO add feature in send planes
'''Here I have added functionality that locates the game window and brings it
into focus before running subsequent lines of code. This will avoid the
necessity of using a sleep time while you click over to it.

The pydirectinput click feature works beatifully. Use this in tandem with your
pyautogui.LocateOnScreen function for best results.

The pyautogui documentation recommends enabling their failsafe feature to avoid
the code running a muck. Moving the mouse to any corner of the screen will
abort the python program.'''


import cv2
import numpy as np
import pyautogui
import pydirectinput
import time
import keyboard
import os

# -------- Settings --------
SEARCH_TIMEOUT_SEC = 4
MATCH_CONFIDENCE   = 0.80
PRE_CLICK_SLEEP    = 0.3   # wait before clicking
POST_CLICK_SLEEP   = 0.2   # wait after clicking
HOLD_DOWN_SEC      = 0.1  # how long to hold mouse down
MOVE_DURATION      = 0.08   # mouse move animation duration

# list of images to search for
targets = [
    "coin3.png",
    "pilot_cap3.png",
    "pilot_cap2.png",
    "neighbor.png",
    "ready_plane2.png",
    "depart.png",
    "ready_plane4.png",
    "depart.png",
    "fix_plane1.png",
    "repair.png",
    "speedup.png",
    "to_flight.png",
    "depart.png",
    "collections.png",
    "congratulations.png",
    "guest_planes_tower.png",
    "allow.png"
]

quit_img = "quit.png"  # quit confirmation popup

# -------- Helpers --------
def press_esc():
    """Press ESC (keyboard lib first, fallback to pyautogui)."""
    try:
        keyboard.press_and_release("esc")
    except Exception:
        pyautogui.press("esc")

def load_template(img_path):
    """Load template, converting BGRA->BGR if there is an alpha channel."""
    if not os.path.exists(img_path):
        print(f"[ERROR] Missing file: {img_path}")
        return None
    tpl = cv2.imread(img_path, cv2.IMREAD_UNCHANGED)
    if tpl is None:
        print(f"[ERROR] Could not read: {img_path}")
        return None
    if len(tpl.shape) == 3 and tpl.shape[2] == 4:
        tpl = cv2.cvtColor(tpl, cv2.COLOR_BGRA2BGR)
    return tpl

def locate_image(img_path, confidence=MATCH_CONFIDENCE):
    """Return center (x, y) if found; else None."""
    template = load_template(img_path)
    if template is None:
        return None

    screenshot = pyautogui.screenshot()
    screen_bgr = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

    res = cv2.matchTemplate(screen_bgr, template, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(res)
    if max_val >= confidence:
        h, w = template.shape[:2]
        cx = max_loc[0] + w // 2
        cy = max_loc[1] + h // 2
        return (int(cx), int(cy))
    return None

def click(x, y):
    """Game-friendly click using DirectInput: mouseDown + mouseUp."""
    time.sleep(PRE_CLICK_SLEEP)
    pydirectinput.moveTo(x, y, duration=MOVE_DURATION)
    pydirectinput.mouseDown()
    time.sleep(HOLD_DOWN_SEC)
    pydirectinput.mouseUp()
    time.sleep(POST_CLICK_SLEEP)
    print(f"[CLICK] at ({x},{y})")

def check_quit_popup():
    """If quit popup visible, press ESC and report True."""
    pos = locate_image(quit_img, confidence=0.90)
    if pos:
        print("[QUIT POPUP] Found → ESC")
        press_esc()
        time.sleep(0.5)
        return True
    return False

def search_and_click(img_name, timeout=SEARCH_TIMEOUT_SEC):
    """Try for up to `timeout` seconds; click when found; ESC if quit popup shows."""
    start = time.time()
    while time.time() - start < timeout:
        if check_quit_popup():
            # after dismissing popup, continue searching same target within remaining time
            continue
        pos = locate_image(img_name, confidence=MATCH_CONFIDENCE)
        if pos:
            print(f"[FOUND] {img_name} at {pos}")
            click(*pos)
            return True
        time.sleep(0.5)
    print(f"[TIMEOUT] {img_name} not found in {timeout}s")
    return False

# -------- Main Loop --------
def main():
    print("[START] Script running. Press CTRL+C to stop.")
    while True:
        # press ESC once before starting each full cycle
        print("[LOOP] ESC before searches…")
        press_esc()
        time.sleep(0.5)

        for img in targets:
            print(f"[SEARCH] {img}")
            found = search_and_click(img, timeout=SEARCH_TIMEOUT_SEC)
            if not found:
                print(f"[MISS] {img}")

        time.sleep(1)  # small pause before repeating

if __name__ == "__main__":
    # pyautogui safety (move mouse to a corner to abort)
    pyautogui.FAILSAFE = True
    main()