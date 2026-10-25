import os
import subprocess
import sys

# The bot is started with the same python as the dashboard, so the virtual environment must be active
if sys.prefix == sys.base_prefix:
    print("\n" + "#" * 70)
    print("#  ERROR: No virtual environment is activated!")
    print("#  Activate it first, then start the dashboard again, e.g.:")
    print("#      <path to your venv>\\Scripts\\activate")
    print("#      python dashboard.py")
    print("#" * 70 + "\n")
    sys.exit(1)

import time
import tkinter as tk
from datetime import datetime
from tkinter import messagebox

from Testing_sqlite.sql_reader_halloween import Database_Reader
from utils.databasecontroller import DatabaseController


# Colours and fonts taken from Albot_dashboard.png
BACKGROUND_COLOUR = "black"
CARD_COLOUR       = "#968E55"
BORDER_COLOUR     = "#23233F"
STOP_COLOUR       = "#FF0000"
START_COLOUR      = "#2E9E3E"
BUSY_COLOUR       = "#7A7A7A"
PUMPKIN_COLOUR    = "#FF7518"
PUMPKIN_OFF_COLOUR = "#6B6540"

TITLE_FONT  = ("Segoe Script", 14)
TEXT_FONT   = ("Segoe Script", 12)
BUTTON_FONT = ("Segoe UI Symbol", 26, "bold")

REFRESH_MS = 5000
BOT_CHECK_MS = 1000
TOKEN_WARNING_DAYS = 3

START_TIMEOUT_S = 60    # Give up waiting for albot.pid after this long
STOP_TIMEOUT_S  = 20    # Time to say goodbye before the bot is force stopped
HALLOWEEN_CONFIRM_TIMEOUT_S = 10   # Stop waiting for the bot to confirm a Halloween change after this long
GHOST_COOLDOWN_S = 5               # Time before the ghost button can fire another gif

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
PID_FILE    = os.path.join(PROJECT_DIR, "albot.pid")   # Written by main.py

# Albot is "stopped", "starting", "running" or "stopping"
bot_state = "stopped"
bot_state_changed_at = time.time()
start_process = None

# Settings saved by the bot in Status_register, e.g. {"HALLOWEEN_MODE": "ON", "HALLOWEEN_SOUND": "OFF"}
bot_status = {}
# (status_name, wanted_value, sent_at) while waiting for the bot to carry out a Halloween click
halloween_pending = None
ghost_cooldown_until = 0


def set_bot_state(new_state):
    global bot_state, bot_state_changed_at

    bot_state = new_state
    bot_state_changed_at = time.time()
    update_power_button()


def get_running_bot_pid():
    # Returns the pid from albot.pid if that process is still a running python, otherwise None
    try:
        with open(PID_FILE) as f:
            pid = int(f.read().strip())
    except (OSError, ValueError):
        return None

    # Checking the name too, in case Windows has given the pid to another program after a crash
    tasklist = subprocess.run(["tasklist", "/FI", f"PID eq {pid}", "/FO", "CSV", "/NH"],
                              capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
    if "python" in tasklist.stdout.lower():
        return pid

    # Left behind after a crash or force stop - remove it so the pid can't be mistaken for Albot later
    try:
        os.remove(PID_FILE)
    except OSError:
        pass
    return None


def start_bot():
    global start_process

    # Own console window, so the bot's output and Ctrl+C work like when started by hand.
    # sys.executable = the same python (and virtual environment) that runs the dashboard.
    start_process = subprocess.Popen([sys.executable, "main.py"], cwd=PROJECT_DIR,
                                     creationflags=subprocess.CREATE_NEW_CONSOLE)
    print("Starting Albot..")
    set_bot_state("starting")


def stop_bot():
    if not messagebox.askyesno("Stop Albot", "Are you sure you want to stop Albot?\n\nAlbot will say goodbye and leave the chat.",
                               icon="warning", default="no"):
        return

    # Polite request - the bot reads Dashboard_cmd_register and runs its own shutdown with goodbye
    send_bot_command("SHUTDOWN")
    print("Asked Albot to shut down..")
    set_bot_state("stopping")


def send_bot_command(action, parameters=""):
    # The bot checks Dashboard_cmd_register every 2 seconds
    DatabaseController().insert_into("Dashboard_cmd_register", {"INVOKED_BY": "DASHBOARD", "ACTION": action, "PARAMETERS": parameters})


def force_stop_bot(pid):
    print(f"Albot did not stop within {STOP_TIMEOUT_S} seconds, force stopping it (pid {pid})")
    subprocess.run(["taskkill", "/PID", str(pid), "/T", "/F"], creationflags=subprocess.CREATE_NO_WINDOW)


def power_button_clicked():
    # Ignore clicks while starting/stopping
    if bot_state == "stopped":
        start_bot()
    elif bot_state == "running":
        stop_bot()


def check_bot_state():
    pid = get_running_bot_pid()
    seconds_in_state = time.time() - bot_state_changed_at

    if bot_state == "starting":
        if pid:
            set_bot_state("running")
        elif start_process.poll() is not None or seconds_in_state > START_TIMEOUT_S:
            print("Albot did not start, check the bot's window for errors")
            set_bot_state("stopped")

    elif bot_state == "stopping":
        if not pid:
            set_bot_state("stopped")
        elif seconds_in_state > STOP_TIMEOUT_S:
            force_stop_bot(pid)

    else:
        # Also finds a bot started before the dashboard was opened, or notices a bot that crashed
        set_bot_state("running" if pid else "stopped")

    update_halloween_controls()

    window.after(BOT_CHECK_MS, check_bot_state)


def toggle_halloween_setting(status_name, action, default_value):
    global halloween_pending

    # Only a running bot can carry it out, and one change at a time
    if bot_state != "running" or halloween_pending:
        return

    wanted_value = "OFF" if bot_status.get(status_name, default_value) == "ON" else "ON"
    send_bot_command(action, wanted_value)
    print(f"Asked Albot to turn {action} {wanted_value}..")

    halloween_pending = (status_name, wanted_value, time.time())
    update_halloween_controls()


def fire_halloween_gif():
    global ghost_cooldown_until

    if bot_state != "running" or time.time() < ghost_cooldown_until:
        return

    send_bot_command("HALLOWEEN_GIF")
    print("Asked Albot to show a Halloween gif..")

    ghost_cooldown_until = time.time() + GHOST_COOLDOWN_S
    update_halloween_controls()


def update_halloween_controls():
    global bot_status, halloween_pending

    bot_status = db_reader.get_status() if db_reader and bot_state == "running" else {}

    if halloween_pending:
        status_name, wanted_value, sent_at = halloween_pending
        if bot_status.get(status_name) == wanted_value or time.time() - sent_at > HALLOWEEN_CONFIRM_TIMEOUT_S:
            halloween_pending = None

    halloween_on = bot_status.get("HALLOWEEN_MODE") == "ON"
    sound_on     = bot_status.get("HALLOWEEN_SOUND", "ON") == "ON"

    if bot_state != "running":
        circle_colour, face_colour, status_text = BUSY_COLOUR, "#9A9A9A", "Start Albot first"
    elif halloween_pending:
        circle_colour, face_colour, status_text = BUSY_COLOUR, "#9A9A9A", "Telling Albot.."
    elif time.time() < ghost_cooldown_until:
        circle_colour = PUMPKIN_COLOUR if halloween_on else PUMPKIN_OFF_COLOUR
        face_colour   = BORDER_COLOUR if halloween_on else CARD_COLOUR
        status_text   = "Boo! A gif is on its way"
    elif halloween_on:
        circle_colour, face_colour, status_text = PUMPKIN_COLOUR, BORDER_COLOUR, "Halloween is on"
    else:
        circle_colour, face_colour, status_text = PUMPKIN_OFF_COLOUR, CARD_COLOUR, "Halloween is off"

    cursor = "hand2" if bot_state == "running" and not halloween_pending else "arrow"

    halloween_canvas.itemconfig(pumpkin_circle, fill=circle_colour)
    halloween_canvas.itemconfig("face", fill=face_colour)
    halloween_canvas.config(cursor=cursor)
    halloween_status_label.config(text=status_text)

    sound_colour = BORDER_COLOUR if bot_state == "running" and not halloween_pending else BUSY_COLOUR
    sound_canvas.itemconfig("speaker", fill=sound_colour)
    sound_canvas.itemconfig("waves", outline=sound_colour, state="normal" if sound_on else "hidden")
    sound_canvas.itemconfig("mute_x", fill=sound_colour, state="hidden" if sound_on else "normal")
    sound_canvas.config(cursor=cursor)

    ghost_ready = bot_state == "running" and time.time() >= ghost_cooldown_until
    ghost_canvas.itemconfig("ghost_body", fill="white" if ghost_ready else "#B5B5B5")
    ghost_canvas.config(cursor="hand2" if ghost_ready else "arrow")


def update_power_button():
    texts = {
        "stopped":  ("Start Albot", START_COLOUR, "Albot is stopped"),
        "starting": ("Starting..",  BUSY_COLOUR,  "Albot is starting"),
        "running":  ("Stop Albot",  STOP_COLOUR,  "Albot is running"),
        "stopping": ("Stopping..",  BUSY_COLOUR,  "Albot is saying goodbye"),
    }
    button_text, colour, status_text = texts[bot_state]

    cursor = "hand2" if bot_state in ("stopped", "running") else "watch"

    power_title_label.config(text=button_text, cursor=cursor)
    power_canvas.itemconfig(power_circle, fill=colour)
    power_canvas.config(cursor=cursor)
    power_status_label.config(text=status_text)


def update_tokens():
    token_expirations = db_reader.get_latest_token_expirations() if db_reader else {}

    for token_name, label in token_labels.items():
        label.config(text=f"{token_name} token: {describe_token_expiration(token_expirations.get(token_name))}")


def describe_token_expiration(expiration_date):
    # The bot saves the expiration date every time it starts
    if not expiration_date:
        return "not known yet (start the bot once)"

    expires = datetime.strptime(expiration_date, "%Y-%m-%d %H:%M:%S")
    days_left = (expires - datetime.now()).days

    if expires < datetime.now():
        return f"EXPIRED {expires:%d.%m.%Y}! Get a new token"
    if days_left < TOKEN_WARNING_DAYS:
        return f"expires {expires:%d.%m.%Y %H:%M} - SOON, get a new token!"
    return f"expires {expires:%d.%m.%Y} (in {days_left} days)"


def update_info():
    latest_info = db_reader.get_latest_info_as_touple() if db_reader else []

    if not latest_info:
        info_label.config(text="- Nothing has happened yet..")
        return

    # Row: (id, timestamp, action, invoked_by, function_name, parameters, bot_version)
    lines = [f"- {row[2]}   ({row[1]})" for row in latest_info[:3]]
    info_label.config(text="\n".join(lines))


def update_error_info():
    latest_error = db_reader.get_latest_error_as_touple() if db_reader else None

    if not latest_error:
        error_label.config(text="- No errors found..")
        return

    # Row: (id, timestamp, hostname, error_message, component, error_type, severity, ...)
    error_message = latest_error[3]
    if error_message == 'NULL':
        error_message = "Not specified.."

    error_label.config(text=f"- {error_message}   ({latest_error[1]})")


def refresh_dashboard():
    update_tokens()
    update_info()
    update_error_info()

    window.after(REFRESH_MS, refresh_dashboard)


def create_box(parent, title, row, sticky):
    box = tk.Frame(parent, bg=CARD_COLOUR, highlightbackground=BORDER_COLOUR,
                   highlightcolor=BORDER_COLOUR, highlightthickness=5, padx=12, pady=8)
    box.grid(row=row, column=0, columnspan=2, sticky=sticky, padx=10, pady=8)

    if title:
        tk.Label(box, text=title, font=TITLE_FONT, bg=CARD_COLOUR, fg=BORDER_COLOUR,
                 anchor="w").pack(fill="x")

    label = tk.Label(box, text="...", font=TEXT_FONT, bg=CARD_COLOUR, fg=BORDER_COLOUR,
                     anchor="w", justify="left", wraplength=780)
    label.pack(fill="x")
    return label


#db-connection
try:
    db_reader = Database_Reader()
except FileNotFoundError as e:
    print(e)
    db_reader = None

# Create the main window
window = tk.Tk()
window.title("Albot Keinstein Dashboard")
window.geometry("900x640")
window.configure(bg=BACKGROUND_COLOUR)

card = tk.Frame(window, bg=CARD_COLOUR, padx=20, pady=20)
card.pack(fill="both", expand=True, padx=30, pady=30)
card.columnconfigure(0, weight=1)
card.rowconfigure(2, weight=1)   # Empty space between the tokens and the info box

# TOKENS (top left)
token_labels = {
    "albot": create_box(card, None, row=0, sticky="w"),
    "TSTWT": create_box(card, None, row=1, sticky="w"),
}

# START/STOP BUTTON (top right) - texts and colour are set in update_power_button()
power_frame = tk.Frame(card, bg=CARD_COLOUR)
power_frame.grid(row=0, column=1, rowspan=2, sticky="ne", padx=10)

power_title_label = tk.Label(power_frame, font=TITLE_FONT, bg=CARD_COLOUR, fg=BORDER_COLOUR)
power_title_label.pack()

power_canvas = tk.Canvas(power_frame, width=90, height=90, bg=CARD_COLOUR, highlightthickness=0)
power_canvas.pack()
power_circle = power_canvas.create_oval(4, 4, 86, 86, outline="")
power_canvas.create_text(45, 45, text="⏻", font=BUTTON_FONT, fill="white")

power_status_label = tk.Label(power_frame, font=("Segoe Script", 10), bg=CARD_COLOUR, fg=BORDER_COLOUR)
power_status_label.pack()

power_canvas.bind("<Button-1>", lambda event: power_button_clicked())
power_title_label.bind("<Button-1>", lambda event: power_button_clicked())

# HALLOWEEN BUTTON + SOUND (under the start/stop button) - colours are set in update_halloween_controls()
halloween_frame = tk.Frame(power_frame, bg=CARD_COLOUR)
halloween_frame.pack(pady=(14, 0))

tk.Label(halloween_frame, text="Halloween", font=("Segoe Script", 12), bg=CARD_COLOUR, fg=BORDER_COLOUR).pack()

halloween_buttons = tk.Frame(halloween_frame, bg=CARD_COLOUR)
halloween_buttons.pack()

# Pumpkin: circle with triangle eyes and a zigzag mouth
halloween_canvas = tk.Canvas(halloween_buttons, width=56, height=56, bg=CARD_COLOUR, highlightthickness=0)
halloween_canvas.pack(side="left")
pumpkin_circle = halloween_canvas.create_oval(3, 3, 53, 53, outline="")
halloween_canvas.create_polygon(15, 25, 21, 15, 27, 25, tags="face")
halloween_canvas.create_polygon(29, 25, 35, 15, 41, 25, tags="face")
halloween_canvas.create_polygon(14, 32, 19, 36, 24, 33, 28, 37, 32, 33, 37, 36, 42, 32, 38, 42, 18, 42, tags="face")

# Speaker: crossed out when the Halloween sound is muted
sound_canvas = tk.Canvas(halloween_buttons, width=36, height=36, bg=CARD_COLOUR, highlightthickness=0)
sound_canvas.pack(side="left", padx=(8, 0))
sound_canvas.create_polygon(5, 14, 11, 14, 18, 7, 18, 29, 11, 22, 5, 22, tags="speaker")
sound_canvas.create_arc(12, 11, 24, 25, start=-50, extent=100, style="arc", width=2, tags="waves")
sound_canvas.create_arc(12, 5, 32, 31, start=-50, extent=100, style="arc", width=2, tags="waves")
sound_canvas.create_line(22, 12, 31, 24, width=3, tags="mute_x")
sound_canvas.create_line(22, 24, 31, 12, width=3, tags="mute_x")

# Ghost: fires one random Halloween gif right away
ghost_canvas = tk.Canvas(halloween_buttons, width=40, height=44, bg=CARD_COLOUR, highlightthickness=0)
ghost_canvas.pack(side="left", padx=(8, 0))
ghost_canvas.create_polygon(6, 40, 6, 18, 9, 8, 20, 3, 31, 8, 34, 18, 34, 40, 29, 35, 24, 40, 20, 35, 16, 40, 11, 35,
                            smooth=True, outline=BORDER_COLOUR, width=2, tags="ghost_body")
ghost_canvas.create_oval(13, 14, 18, 21, fill=BORDER_COLOUR, outline="")
ghost_canvas.create_oval(22, 14, 27, 21, fill=BORDER_COLOUR, outline="")
ghost_canvas.create_oval(17, 24, 23, 31, fill=BORDER_COLOUR, outline="")

# Fixed width, so the buttons above don't shift sideways when the text changes
halloween_status_label = tk.Label(halloween_frame, font=("Segoe Script", 10), bg=CARD_COLOUR, fg=BORDER_COLOUR, width=24)
halloween_status_label.pack()

halloween_canvas.bind("<Button-1>", lambda event: toggle_halloween_setting("HALLOWEEN_MODE", "HALLOWEEN", "OFF"))
sound_canvas.bind("<Button-1>", lambda event: toggle_halloween_setting("HALLOWEEN_SOUND", "HALLOWEEN_SOUND", "ON"))
ghost_canvas.bind("<Button-1>", lambda event: fire_halloween_gif())

# INFO AND ERROR (bottom)
info_label = create_box(card, "Last information:", row=3, sticky="ew")
error_label = create_box(card, "Last error:", row=4, sticky="ew")


refresh_dashboard()
check_bot_state()

# Run the application
window.mainloop()
