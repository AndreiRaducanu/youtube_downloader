import glob
import subprocess
import sys
import tkinter as tk
from tkinter import ttk
import threading
import os
from pathlib import Path
import traceback

# Error logging function
def log_error():
    with open("error_log.txt", "w") as f:
        traceback.print_exc(file=f)

sys.excepthook = lambda *args: log_error()

# Update libraries function
def update_libraries():
    try:
        # Update pip itself first
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip", "--no-input"])

        # Update specific libraries
        libraries = ["yt-dlp"]
        for lib in libraries:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", lib, "--no-input"])
        print("Libraries updated successfully!")
    except Exception as e:
        print(f"Failed to update libraries: {e}")

# Run update on start
update_libraries()

# Get desktop path based on OS
def get_desktop_path():
    if os.name == 'nt':
        desktop = Path(os.environ.get('USERPROFILE', '')) / 'Desktop'
    else:
        desktop = Path(os.environ.get('HOME', '')) / 'Desktop'
    return desktop

# Ensure the output directory exists
def ensure_directory_exists():
    desktop_path = get_desktop_path()
    output_path = desktop_path / 'MUZICA_TRASA'
    if not output_path.exists():
        output_path.mkdir(parents=True, exist_ok=True)
    return str(output_path)

OUTPUT_PATH = ensure_directory_exists()

# Download video function
def download_youtube_video():
    youtube_url = url_entry.get()
    if not youtube_url:
        update_status("Vă rugăm să introduceți un URL YouTube.")
        return
    threading.Thread(target=run_download, args=(youtube_url,), daemon=True).start()

def cleanup_m4a_files():
    """Scan the output directory and delete any .m4a files"""
    try:
        m4a_files = glob.glob(os.path.join(OUTPUT_PATH, '*.m4a'))
        for file_path in m4a_files:
            try:
                os.remove(file_path)
                print(f"Deleted temporary file: {file_path}")
            except Exception as e:
                print(f"Could not delete {file_path}: {e}")
        return len(m4a_files)
    except Exception as e:
        print(f"Error during cleanup: {e}")
        return 0


# Run the yt-dlp command
def run_download(youtube_url):
    try:
        update_status("Descărcare în curs... Vă rugăm să așteptați.")
        status_box.config(bg="orange")

        # Wrap URL in quotes to handle special characters
        youtube_url = f'"{youtube_url}"'
        # Decide whether to include --no-playlist
        playlist_option = '--yes-playlist' if playlist_var.get() else '--no-playlist'


        # Construct the yt-dlp command
        command = (
            f'yt-dlp --verbose -f "bestvideo[vcodec^=avc1][height<=600][width<=1024][fps<=30]+bestaudio[ext=m4a]/best[vcodec^=avc1]" '
            f'--merge-output-format mp4 '
            f'-o "{OUTPUT_PATH}/%(title)s.%(ext)s" '
            f'{playlist_option} {youtube_url}'
        )

        # Run the command using shell to interpret correctly
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, shell=True)

        # Capture output dynamically
        for line in iter(process.stdout.readline, ""):
            update_status(line.strip())

        process.wait()

        # deleted_files = cleanup_m4a_files()
        # if deleted_files > 0:
        #     update_status(f"Șters {deleted_files} fișiere temporare .m4a")

        if process.returncode == 0:
            update_status(f"Descărcare finalizată cu succes! Fisier salvat in {OUTPUT_PATH}")
            status_box.config(bg="green")
            clear_url_entry()
        else:
            update_status(f"A apărut o eroare. Cod de ieșire: {process.returncode}")
            status_box.config(bg="red")
    except Exception as e:
        update_status(f"Eroare neașteptată: {str(e)}")
        status_box.config(bg="red")

# Update status function
def update_status(message):
    status_text.set(message)

# Clear URL entry function
def clear_url_entry():
    url_entry.delete(0, tk.END)
    url_entry.bind("<Control-a>", select_all)  # Windows/Linux
    url_entry.bind("<Command-a>", select_all)  # macOS


# Center the window
def center_window(window, width, height):
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    position_top = int(screen_height / 2 - height / 2)
    position_right = int(screen_width / 2 - width / 2)
    window.geometry(f'{width}x{height}+{position_right}+{position_top}')
    window.resizable(False, False)

def select_all(event):
    event.widget.select_range(0, tk.END)
    event.widget.icursor(tk.END)
    return "break"


# Tkinter GUI setup
root = tk.Tk()
root.title("Descărcător YouTube")
window_width = 900
window_height = 650
center_window(root, window_width, window_height)


# Main frame
main_frame = ttk.Frame(root, padding="30")
main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

clear_button = ttk.Button(main_frame, text="Sterge", command=clear_url_entry)
clear_button.grid(row=4, column=1, padx=(20, 0), pady=(0, 10))


playlist_var = tk.BooleanVar(value=False)

playlist_checkbox = tk.Checkbutton(
    main_frame,
    text="Playlist (bifeaza)",
    variable=playlist_var,
    font=("Arial", 22),
    padx=20,
    pady=10
)
playlist_checkbox.grid(row=4, column=0, columnspan=2, pady=(0, 10), sticky=tk.W)

# YouTube URL Entry
url_label = ttk.Label(main_frame, text="URL YouTube:", font=("Arial", 32, "bold"))
url_label.grid(row=0, column=0, sticky=tk.W, pady=(0, 10), columnspan=2)
url_entry = ttk.Entry(main_frame, font=("Arial", 22), width=50)
url_entry.grid(row=1, column=0, columnspan=2, pady=(0, 10), sticky=(tk.W, tk.E))

# Button styling
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

# Bottom status box
status_box = tk.Label(root, text="", relief=tk.SUNKEN, height=2)
status_box.grid(row=1, column=0, sticky=(tk.W, tk.E), padx=30, pady=10)

main_frame.columnconfigure(1, weight=1)

# Initialize status
update_status("Introduceți un URL YouTube și apăsați 'Descarcă' pentru a începe.")

# Start the Tkinter main loop
root.mainloop()
