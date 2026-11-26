
import tkinter as tk
from tkinter import scrolledtext
import pyttsx3
import datetime
import subprocess
import webbrowser
import threading

# ==============================
# IGRIS - PERSONAL AI ASSISTANT
# ==============================

BG_COLOR = "#080D1A"
PANEL_COLOR = "#101A2C"
ACCENT_COLOR = "#00E5FF"
TEXT_COLOR = "#EAFBFF"
MUTED_COLOR = "#7D9AA8"

# ---------- VOICE SYSTEM ----------

def speak(text):
    print("Speech requested:", text)

    try:
        # This is the voice method that worked for us
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()
        engine.stop()
    except Exception as error:
        print("Speech error:", error)


# ---------- COMMAND SYSTEM ----------

def process_command(command):
    command = command.lower().strip()

    if not command:
        return "Please enter a command."

    if command in ["hello", "hi", "hey"]:
        return "Hello! I am online."

    elif command == "help":
        return (
            "Available commands:\n"
            "1. hello\n"
            "2. help\n"
            "3. time\n"
            "4. open calculator\n"
            "5. open notepad\n"
            "6. open youtube"
        )

    elif command == "time":
        current_time = datetime.datetime.now().strftime("%I:%M %p")
        return f"The current time is {current_time}."

    elif command == "open calculator":
        try:
            subprocess.Popen(["calc.exe"])
            return "Opening calculator."
        except Exception as error:
            print("Calculator error:", error)
            return "I could not open calculator."

    elif command == "open notepad":
        try:
            subprocess.Popen(["notepad.exe"])
            return "Opening notepad."
        except Exception as error:
            print("Notepad error:", error)
            return "I could not open notepad."

    elif command == "open youtube":
        webbrowser.open("https://www.youtube.com")
        return "Opening YouTube."

    else:
        return "Command not recognized. Type help to see commands."


# ---------- CHAT DISPLAY ----------

def add_message(sender, message):
    chat_area.config(state="normal")
    chat_area.insert(tk.END, f"\n{sender}\n", "sender")
    chat_area.insert(tk.END, f"{message}\n", "message")
    chat_area.see(tk.END)
    chat_area.config(state="disabled")


def execute_command(event=None):
    command = command_entry.get().strip()

    if not command:
        return

    command_entry.delete(0, tk.END)
    add_message("YOU", command)

    response = process_command(command)
    add_message("IGRIS", response)

    # Keep the working direct voice method
    threading.Thread(
        target=speak,
        args=(response,),
        daemon=True
    ).start()


# ---------- WINDOW ----------

root = tk.Tk()
root.title("IGRIS | Personal Assistant")
root.geometry("850x650")
root.minsize(650, 500)
root.configure(bg=BG_COLOR)

# ---------- HEADER ----------

header = tk.Frame(root, bg=BG_COLOR)
header.pack(fill="x", padx=25, pady=(20, 10))

title = tk.Label(
    header,
    text="I G R I S",
    font=("Consolas", 28, "bold"),
    fg=ACCENT_COLOR,
    bg=BG_COLOR
)
title.pack(anchor="w")

subtitle = tk.Label(
    header,
    text="PERSONAL ASSISTANT  //  SYSTEM ONLINE",
    font=("Consolas", 10),
    fg=MUTED_COLOR,
    bg=BG_COLOR
)
subtitle.pack(anchor="w", pady=(2, 0))

# ---------- STATUS ----------

status_frame = tk.Frame(
    root,
    bg=PANEL_COLOR,
    highlightbackground=ACCENT_COLOR,
    highlightthickness=1
)
status_frame.pack(fill="x", padx=25, pady=10)

status_label = tk.Label(
    status_frame,
    text="●  ONLINE",
    font=("Consolas", 10, "bold"),
    fg="#00FF99",
    bg=PANEL_COLOR,
    padx=15,
    pady=10
)
status_label.pack(anchor="w")

# ---------- CHAT PANEL ----------

chat_area = scrolledtext.ScrolledText(
    root,
    bg=PANEL_COLOR,
    fg=TEXT_COLOR,
    insertbackground=ACCENT_COLOR,
    font=("Consolas", 11),
    wrap=tk.WORD,
    relief="flat",
    padx=15,
    pady=12,
    height=18,
    state="disabled"
)
chat_area.pack(fill="both", expand=True, padx=25, pady=10)

chat_area.tag_config(
    "sender",
    foreground=ACCENT_COLOR,
    font=("Consolas", 10, "bold")
)
chat_area.tag_config(
    "message",
    foreground=TEXT_COLOR,
    font=("Consolas", 11)
)

# ---------- COMMAND INPUT ----------

input_frame = tk.Frame(root, bg=BG_COLOR)
input_frame.pack(fill="x", padx=25, pady=(5, 20))

command_entry = tk.Entry(
    input_frame,
    bg=PANEL_COLOR,
    fg=TEXT_COLOR,
    insertbackground=ACCENT_COLOR,
    font=("Consolas", 12),
    relief="flat"
)
command_entry.pack(
    side="left",
    fill="x",
    expand=True,
    ipady=12,
    padx=(0, 10)
)
command_entry.bind("<Return>", execute_command)

execute_button = tk.Button(
    input_frame,
    text="EXECUTE",
    command=execute_command,
    bg=ACCENT_COLOR,
    fg=BG_COLOR,
    activebackground="#8AF4FF",
    activeforeground=BG_COLOR,
    font=("Consolas", 10, "bold"),
    relief="flat",
    cursor="hand2",
    padx=20,
    pady=10
)
execute_button.pack(side="right")

# ---------- STARTUP ----------

root.after(
    500,
    lambda: add_message(
        "IGRIS",
        "ARISE sequence initiated. IGRIS is online."
    )
)

root.after(
    800,
    lambda: threading.Thread(
        target=speak,
        args=("ARISE sequence initiated. IGRIS is online.",),
        daemon=True
    ).start()
)

command_entry.focus_set()

root.mainloop()
