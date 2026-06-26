from pynput.mouse import Button, Controller as mouse_controller
from pynput.keyboard import Key, Controller as key_controller, KeyCode, Listener as key_listener
import threading
import tkinter as tk
from tkinter import ttk
import time

# State
mouse = mouse_controller()
keyboard = key_controller()
stop_event = threading.Event()   # stops the clicker loop
armed = False               # whether hotkeys are active
clicker_running = False            # whether clicker is currently clicking

# Click logic
def on_click(button):
    if button == "Left":
        mouse.press(Button.left);  mouse.release(Button.left)
    elif button == "Right":
        mouse.press(Button.right); mouse.release(Button.right)
    else:
        mouse.press(Button.middle); mouse.release(Button.middle)

def on_press_key(key):
    keyboard.press(KeyCode(char=key))
    keyboard.release(KeyCode(char=key))

def clicker(pressed, click_interval):
    while not stop_event.is_set():
        if pressed == "Key":
            on_press_key(key_var.get())
        else:
            on_click(pressed)
        time.sleep(click_interval)

# Clicker start/stop (hotkey triggered)
clicker_thread = None

def start_clicker():
    global clicker_thread, clicker_running
    if not armed or clicker_running:
        return
    clicker_running = True
    stop_event.clear()
    interval = int(min_var.get()) * 60 + int(sec_var.get()) + int(ms_var.get()) / 1000
    if interval == 0:
        interval = 0.1  # stop infinite loop
    clicker_thread = threading.Thread(target=clicker, args=(click_var.get(), interval), daemon=True)
    clicker_thread.start()
    root.after(0, update_clicker_status)

def stop_clicker():
    global clicker_running
    if not clicker_running:
        return
    stop_event.set()
    clicker_running = False
    root.after(0, update_clicker_status)

def update_clicker_status():
    if clicker_running:
        clicker_status.config(text="● CLICKING", fg=ACCENT)
    else:
        clicker_status.config(text="○ IDLE", fg=MUTED)

# Hotkey listener (F6 = start, F7 = stop)
def on_hotkey(key):
    if not armed:
        return
    if key == Key.f6:
        start_clicker()
    elif key == Key.f7:
        stop_clicker()

hotkey_listener = key_listener(on_press=on_hotkey)
hotkey_listener.daemon = True
hotkey_listener.start()

# Arm / Disarm
def arm():
    global armed
    armed = True
    arm_btn.config(state="disabled", bg=MUTED, fg=BG)
    disarm_btn.config(state="normal", bg=ACCENT, fg="#ffffff")
    armed_status.config(text="● ARMED", fg=ACCENT)

def disarm():
    global armed
    armed = False
    stop_clicker()
    arm_btn.config(state="normal", bg=ACCENT, fg="#ffffff")
    disarm_btn.config(state="disabled", bg=MUTED, fg=BG)
    armed_status.config(text="○ DISARMED", fg=MUTED)

# GUI
root = tk.Tk()
root.title("Autoclicker")
root.resizable(False, False)
root.configure(bg="#1a1a2e")

BG       = "#1a1a2e"
SURFACE  = "#16213e"
ACCENT   = "#e94560"
GREEN    = "#27ae60"
TEXT     = "#eaeaea"
MUTED    = "#7a7a9a"
BTN_OFF  = "#2a2a4a"

style = ttk.Style()
style.theme_use("clam")

# Title
tk.Label(root, text="AUTOCLICKER", font=("Courier", 22, "bold"),
         bg=BG, fg=ACCENT).pack(pady=(24, 2))


# Interval
interval_frame = tk.Frame(root, bg=SURFACE, padx=20, pady=16)
interval_frame.pack(padx=24, fill="x")

tk.Label(interval_frame, text="CLICK INTERVAL", font=("Courier", 9, "bold"),
         bg=SURFACE, fg=MUTED).grid(row=0, column=0, columnspan=6, sticky="w", pady=(0, 10))

def make_spinbox(parent, row, col, label):
    tk.Label(parent, text=label, font=("Courier", 8), bg=SURFACE, fg=MUTED)\
        .grid(row=row+1, column=col, padx=(0, 4))
    var = tk.StringVar(value="0")
    sb = tk.Spinbox(parent, from_=0, to=999, textvariable=var, width=4,
                    font=("Courier", 13, "bold"),
                    bg=SURFACE, fg=TEXT, buttonbackground=SURFACE,
                    highlightthickness=1, highlightcolor=ACCENT,
                    highlightbackground=MUTED, relief="flat", bd=0,
                    insertbackground=TEXT, justify="center")
    sb.grid(row=row, column=col, padx=(0, 8), ipady=4)
    return var

min_var = make_spinbox(interval_frame, 1, 0, "min")
sec_var = make_spinbox(interval_frame, 1, 1, "sec")
ms_var  = make_spinbox(interval_frame, 1, 2, "ms")

# Click type
btn_frame = tk.Frame(root, bg=SURFACE, padx=20, pady=16)
btn_frame.pack(padx=24, pady=(8, 0), fill="x")

tk.Label(btn_frame, text="CLICK TYPE", font=("Courier", 9, "bold"),
         bg=SURFACE, fg=MUTED).pack(anchor="w", pady=(0, 8))

click_var  = tk.StringVar(value="Left")
button_row = tk.Frame(btn_frame, bg=SURFACE)
button_row.pack(anchor="w")

def on_click_type_change():
    key_entry.config(state="normal" if click_var.get() == "Key" else "disabled")
    for rb in radio_buttons:
        val = rb.cget("value")
        if val == click_var.get():
            rb.config(bg=ACCENT, fg="#ffffff")
        else:
            rb.config(bg=BTN_OFF, fg=TEXT)

radio_buttons = []
for label in ("Left", "Right", "Middle", "Key"):
    rb = tk.Radiobutton(button_row, text=label, variable=click_var, value=label,
                        font=("Courier", 10),
                        bg=ACCENT if label == "Left" else BTN_OFF,
                        fg="#ffffff" if label == "Left" else TEXT,
                        selectcolor=ACCENT, activebackground=SURFACE,
                        activeforeground=TEXT, indicatoron=0,
                        relief="flat", bd=0, padx=12, pady=6,
                        highlightthickness=0, cursor="hand2",
                        command=on_click_type_change)
    rb.pack(side="left", padx=(0, 8))
    radio_buttons.append(rb)

key_row = tk.Frame(btn_frame, bg=SURFACE)
key_row.pack(anchor="w", pady=(10, 0))
tk.Label(key_row, text="KEY", font=("Courier", 8), bg=SURFACE, fg=MUTED)\
    .pack(side="left", padx=(0, 8))
key_var   = tk.StringVar()
key_entry = tk.Entry(key_row, textvariable=key_var, width=6,
                     font=("Courier", 12, "bold"),
                     bg=SURFACE, fg=TEXT, insertbackground=TEXT,
                     highlightthickness=1, highlightcolor=ACCENT,
                     highlightbackground=MUTED, relief="flat",
                     justify="center", state="disabled")
key_entry.pack(side="left", ipady=4)
tk.Label(key_row, text="(single key, e.g. a  space  f1)",
         font=("Courier", 8), bg=SURFACE, fg=MUTED).pack(side="left", padx=(10, 0))

# Hotkey info
hk_frame = tk.Frame(root, bg=SURFACE, padx=20, pady=12)
hk_frame.pack(padx=24, pady=(8, 0), fill="x")

tk.Label(hk_frame, text="HOTKEYS", font=("Courier", 9, "bold"),
         bg=SURFACE, fg=MUTED).pack(anchor="w", pady=(0, 6))
tk.Label(hk_frame, text="F6  start clicker        F7  stop clicker",
         font=("Courier", 10), bg=SURFACE, fg=TEXT).pack(anchor="w")

# Arm / Disarm + status
arm_frame = tk.Frame(root, bg=BG)
arm_frame.pack(padx=24, pady=(16, 4), fill="x")

arm_btn = tk.Button(arm_frame, text="▶  ARM",
                    font=("Courier", 11, "bold"),
                    bg=ACCENT, fg="#ffffff", relief="flat",
                    activebackground="#c73652", activeforeground="#ffffff",
                    padx=20, pady=10, cursor="hand2",
                    command=arm)
arm_btn.pack(side="left", expand=True, fill="x", padx=(0, 6))

disarm_btn = tk.Button(arm_frame, text="■  DISARM",
                       font=("Courier", 11, "bold"),
                       bg=BTN_OFF, fg=MUTED, relief="flat",
                       activebackground="#3a3a5a", activeforeground=TEXT,
                       padx=20, pady=10, cursor="hand2",
                       state="disabled",
                       command=disarm)
disarm_btn.pack(side="left", expand=True, fill="x", padx=(6, 0))

# Status indicators
status_frame = tk.Frame(root, bg=BG)
status_frame.pack(padx=24, pady=(4, 20), fill="x")

armed_status   = tk.Label(status_frame, text="○ DISARMED", font=("Courier", 9, "bold"),
                           bg=BG, fg=MUTED)
armed_status.pack(side="left")

clicker_status = tk.Label(status_frame, text="○ IDLE", font=("Courier", 9, "bold"),
                           bg=BG, fg=MUTED)
clicker_status.pack(side="right")

root.mainloop()