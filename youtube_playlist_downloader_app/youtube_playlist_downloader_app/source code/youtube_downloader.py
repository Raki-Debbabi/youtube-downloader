import os
import tkinter as tk
from tkinter import Tk, Label, Entry, Button, StringVar, filedialog, messagebox, ttk
from yt_dlp import YoutubeDL
from threading import Thread, Event

def download_playlist():
    playlist_url = url_var.get()
    output_format = format_var.get()
    output_folder = filedialog.askdirectory()

    if not playlist_url:
        messagebox.showerror("Error", "Please provide a playlist URL.")
        return
    if not output_folder:
        messagebox.showerror("Error", "Please select an output folder.")
        return

    os.makedirs(output_folder, exist_ok=True)

    if output_format == 'mp3':
        ydl_opts = {
            'format': 'bestaudio/best',
                'postprocessors': [
                    {'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'},
                ],
            'outtmpl': os.path.join(output_folder, '%(title)s.%(ext)s'),
            'progress_hooks': [progress_hook]
        }
    elif output_format == 'mp4':
        ydl_opts = {
            'format': 'bestvideo[height<=420]+bestaudio[ext=mp4]/best',
            'outtmpl': os.path.join(output_folder, '%(title)s.%(ext)s'),
            'merge_output_format': 'mp4',
            'progress_hooks': [progress_hook]
        }
    else:
        raise ValueError("Unsupported format. Use 'mp3' or 'mp4'.")
    download_progress["speed"] = "0 KB/s"
    download_progress["cancelled"] = False

    
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(playlist_url, download=False)
        total_videos = len(info.get('entries', []))
        download_progress["total"] = total_videos
        download_progress["completed"] = 0

        progress_label.config(text=f"0/{total_videos} Downloaded")
        for entry in info['entries']:
            if download_progress["cancelled"]:
                break
            try:
                ydl.download([playlist_url])
                download_progress["completed"] += 1
            except Exception as e:
                print(e)

    if not download_progress["cancelled"]:
        messagebox.showinfo("Success", "Playlist downloaded successfully!")

def progress_hook(d):
    if d['status'] == 'downloading':
        speed = d.get('_speed_str', '0 KB/s')
        download_progress["speed"] = speed
        speed_label.config(text=f"Speed: {speed}")

    if d['status'] == 'finished':
        print(f"Downloaded {d['filename']}")

def threaded_download():
    download_thread = Thread(target=download_playlist)
    download_thread.start()

def cancel_download():
    download_progress["cancelled"] = True
    messagebox.showinfo("Cancelled", "Download has been cancelled.")

root = Tk()
root.title("YouTube Playlist Downloader")
root.geometry("800x400")
root.configure(bg="#2d3436")
root.resizable(False, False)

label_style = {"bg": "#2d3436", "fg": "#dfe6e9", "font": ("Arial", 12)}


Label(root, text="Playlist URL:", **label_style).grid(row=0, column=0, padx=10, pady=10, sticky="w")
url_var = StringVar()
Entry(root, textvariable=url_var, width=50, font=("Arial", 12)).grid(row=0, column=1, padx=10, pady=10)

Label(root, text="Select Format:", **label_style).grid(row=1, column=0, padx=10, pady=10, sticky="w")
format_var = StringVar(value=" mp3")
format_dropdown = ttk.Combobox(root, textvariable=format_var, values=["mp4", "mp3"], state="readonly", width=10)
format_dropdown.grid(row=1, column=1, padx=10, pady=10, sticky="w")

speed_label = Label(root, text="Speed: 0 KB/s", **label_style)
speed_label.grid(row=2, column=0, columnspan=2, pady=10)

progress_label = Label(root, text="0/0 Downloaded", **label_style)
progress_label.grid(row=3, column=0, columnspan=2, pady=10)

button_style = {"bg": "#0984e3", "fg": "white", "font": ("Arial", 10, "bold")}
button_frame = tk.Frame(root,bg=root["bg"])
button_frame.grid(row=5, column=0,  pady=20)
Button(button_frame, text="Download", command=threaded_download, **button_style).pack(side=tk.RIGHT, padx=10)
Button(button_frame, text="Cancel", command=cancel_download, **button_style).pack(side=tk.RIGHT, padx=10)

download_progress = {"total": 0, "completed": 0, "speed": "0 KB/s", "cancelled": False}

root.mainloop()


