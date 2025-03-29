import os
import tkinter as tk
from tkinter import Tk, Label, Entry, Button, StringVar, filedialog, messagebox, ttk
from yt_dlp import YoutubeDL
from threading import Thread

def download_playlist():
    playlist_url = url_var.get()
    output_format = format_var.get()
    selected_quality = quality_var.get()
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
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': selected_quality,
            }],
            'outtmpl': os.path.join(output_folder, '%(title)s.%(ext)s'),
            'progress_hooks': [progress_hook]
        }
    elif output_format == 'mp4':
        video_format_map = {
            '360p': 'bestvideo[height<=360]+bestaudio/best',
            '480p': 'bestvideo[height<=480]+bestaudio/best',
            '720p': 'bestvideo[height<=720]+bestaudio/best',
            '1080p': 'bestvideo[height<=1080]+bestaudio/best',
            '1440p': 'bestvideo[height<=1440]+bestaudio/best',
            '4K': 'bestvideo[height<=2160]+bestaudio/best',
        }
        ydl_opts = {
            'format': video_format_map.get(selected_quality, 'bestvideo[height<=720]+bestaudio/best'),
            'outtmpl': os.path.join(output_folder, '%(title)s.%(ext)s'),
            'merge_output_format': 'mp4',
            'progress_hooks': [progress_hook]
        }
    else:
        raise ValueError("Unsupported format.")

    download_progress["speed"] = "0 KB/s"
    download_progress["cancelled"] = False

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(playlist_url, download=False)
            # Handle both playlists and single videos
            entries = info.get('entries', [info]) if info else []
            total_videos = len(entries)
            download_progress["total"] = total_videos
            download_progress["completed"] = 0

            progress_label.config(text=f"0/{total_videos} Downloaded")
            
            for entry in entries:
                if download_progress["cancelled"]:
                    break
                try:
                    video_url = entry['webpage_url']
                    ydl.download([video_url])
                    download_progress["completed"] += 1
                    progress_label.config(text=f"{download_progress['completed']}/{total_videos} Downloaded")
                except Exception as e:
                    print(f"Error downloading {video_url}: {e}")

        if not download_progress["cancelled"]:
            messagebox.showinfo("Success", "Download completed successfully!")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")

def progress_hook(d):
    if d['status'] == 'downloading':
        speed = d.get('_speed_str', '0 KB/s')
        download_progress["speed"] = speed
        speed_label.config(text=f"Speed: {speed}")

def threaded_download():
    download_thread = Thread(target=download_playlist)
    download_thread.start()

def cancel_download():
    download_progress["cancelled"] = True
    messagebox.showinfo("Cancelled", "Download has been cancelled.")

def update_quality_options(event=None):
    if format_var.get() == 'mp3':
        quality_dropdown['values'] = ['128', '192', '320']
        quality_var.set('192')
    else:
        quality_dropdown['values'] = ['360p', '480p', '720p', '1080p', '1440p', '4K']
        quality_var.set('720p')

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
format_var = StringVar(value="mp3")
format_dropdown = ttk.Combobox(root, textvariable=format_var, values=["mp4", "mp3"], state="readonly", width=10)
format_dropdown.grid(row=1, column=1, padx=10, pady=10, sticky="w")
format_dropdown.bind('<<ComboboxSelected>>', update_quality_options)


Label(root, text="Quality:", **label_style).grid(row=2, column=0, padx=10, pady=10, sticky="w")
quality_var = StringVar()
quality_dropdown = ttk.Combobox(root, textvariable=quality_var, state="readonly", width=10)
quality_dropdown.grid(row=2, column=1, padx=10, pady=10, sticky="w")
update_quality_options()  

speed_label = Label(root, text="Speed: 0 KB/s", **label_style)
speed_label.grid(row=3, column=0, columnspan=2, pady=10)
progress_label = Label(root, text="0/0 Downloaded", **label_style)
progress_label.grid(row=4, column=0, columnspan=2, pady=10)


button_style = {"bg": "#0984e3", "fg": "white", "font": ("Arial", 10, "bold")}
button_frame = tk.Frame(root, bg=root["bg"])
button_frame.grid(row=5, column=0, columnspan=2, pady=20)
Button(button_frame, text="Download", command=threaded_download, **button_style).pack(side=tk.LEFT, padx=10)
Button(button_frame, text="Cancel", command=cancel_download, **button_style).pack(side=tk.LEFT, padx=10)

download_progress = {"total": 0, "completed": 0, "speed": "0 KB/s", "cancelled": False}

root.mainloop()