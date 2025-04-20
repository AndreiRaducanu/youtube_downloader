import subprocess
import tkinter as tk
from tkinter import ttk
import threading
import os
from pathlib import Path

# Function to get the correct Desktop path based on the operating system
def get_desktop_path():
    if os.name == 'nt':  # Windows
        desktop = Path(os.environ.get('USERPROFILE', '')) / 'Desktop'
    else:  # Linux or MacOS
        desktop = Path(os.environ.get('HOME', '')) / 'Desktop'
    
    return desktop

# Function to ensure the directory exists on the Desktop
def ensure_directory_exists():
    desktop_path = get_desktop_path()
    # Define the path to MUZICA_TRASA
    output_path = desktop_path / 'MUZICA_TRASA'

    # Create the directory if it does not exist
    if not output_path.exists():
        output_path.mkdir(parents=True, exist_ok=True)

    return str(output_path)

# Set the OUTPUT_PATH to the correct path
OUTPUT_PATH = ensure_directory_exists()


def download_youtube_video():
    """
    Trigger the YouTube video download process in a separate thread.
    """
    youtube_url = url_entry.get()

    if not youtube_url:
        update_status("Vă rugăm să introduceți un URL YouTube.")
        return

    # Start a new thread to keep the UI responsive
    threading.Thread(target=run_download, args=(youtube_url,), daemon=True).start()


def run_download(youtube_url):
    """
    Execute the yt-dlp command and update the status dynamically.
    """
    try:
        update_status("Descărcare în curs... Vă rugăm să așteptați.")
        # Set the status box to orange while downloading
        status_box.config(bg="orange")

        # Construct the yt-dlp command
        command = [
            "yt-dlp",
            "-f", "bestvideo[vcodec^=avc1][height<=600][width<=1024][fps<=30]+bestaudio[ext=m4a]/best[vcodec^=avc1][ext=mp4]",  # Select videos encoded with H.264
            "--merge-output-format", "mp4",  # Ensure output is in MP4 format
            "-o", f"{OUTPUT_PATH}/%(title)s.%(ext)s",  # Set output path and naming
            "--no-playlist",  # Disable playlist downloadingeroar
            youtube_url
        ]


        # Run the command
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        # Dynamically update the status as output is received
        for line in iter(process.stdout.readline, ""):
            update_status(line.strip())

        process.wait()

        if process.returncode == 0:
            update_status(f"Descărcare finalizată cu succes! Fisier salvat in {OUTPUT_PATH}")
            status_box.config(bg="green")  # Set the status box to green when download finishes
            clear_url_entry()
        else:
            update_status("A apărut o eroare în timpul descărcării.")
            status_box.config(bg="red")  # Set to red in case of an error
    except Exception as e:
        update_status(f"A apărut o eroare neașteptată: {str(e)}")
        status_box.config(bg="red")  # Set to red if there is an exception


def update_status(message):
    """
    Update the status text in the UI dynamically.
    """
    status_text.set(message)


def clear_url_entry():
    """
    Clear the URL entry field.
    """
    url_entry.delete(0, tk.END)


def center_window(window, width, height):
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    
    # Calculate position x, y
    position_top = int(screen_height / 2 - height / 2)
    position_right = int(screen_width / 2 - width / 2)
    
    # Set the geometry of the window
    window.geometry(f'{width}x{height}+{position_right}+{position_top}')
    window.resizable(False, False)


# Tkinter GUI setup
root = tk.Tk()
root.title("Descărcător YouTube")

# Center the window and make it bigger
window_width = 900
window_height = 650
center_window(root, window_width, window_height)

# Main frame
main_frame = ttk.Frame(root, padding="30")
main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

# YouTube URL Entry
url_label = ttk.Label(main_frame, text="URL YouTube:", font=("Arial", 32, "bold"))
url_label.grid(row=0, column=0, sticky=tk.W, pady=(0, 10), columnspan=2)
url_entry = ttk.Entry(main_frame, font=("Arial", 22), width=50)
url_entry.grid(row=1, column=0, columnspan=2, pady=(0, 10), sticky=(tk.W, tk.E))

# Create style Object
style = ttk.Style()
style.configure('TButton', font=('calibri', 20, 'bold'), borderwidth='4')
style.map('TButton', foreground=[('active', '!disabled', 'green')], background=[('active', 'black')])

# Download Button
download_button = ttk.Button(main_frame, text="Descarcă", command=download_youtube_video)
download_button.grid(row=2, column=0, columnspan=2, pady=20, sticky=(tk.W, tk.E))

# Status Display
status_text = tk.StringVar()
status_label = ttk.Label(
    main_frame,
    textvariable=status_text,
    wraplength=650,
    font=("Arial", 32),
    relief=tk.SUNKEN,
    padding=10,
    anchor="center"
)
status_label.grid(row=3, column=0, columnspan=2, pady=20, sticky=(tk.W, tk.E))

# Bottom status box (use tk.Label instead of ttk.Label)
status_box = tk.Label(root, text="", relief=tk.SUNKEN, height=2)
status_box.grid(row=1, column=0, sticky=(tk.W, tk.E), padx=30, pady=10)

# Adjust column weights for resizing
main_frame.columnconfigure(1, weight=1)

# Initialize status
update_status("Introduceți un URL YouTube și apăsați 'Descarcă' pentru a începe.")

# Start the Tkinter main loop
root.mainloop()