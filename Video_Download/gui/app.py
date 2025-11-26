import customtkinter as ctk
import yt_dlp
import requests
import os
import threading
import queue
import time
from urllib.parse import urlparse
from tkinter import filedialog, messagebox

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("green")

class DownloadTask(ctk.CTkFrame):
    """Widget hiển thị tiến độ của 1 file"""
    def __init__(self, master, url, title_hint, **kwargs):
        super().__init__(master, **kwargs)
        self.pack(fill="x", pady=5, padx=5)
        
        self.grid_columnconfigure(0, weight=1)
        
        display_name = title_hint if title_hint else url
        
        self.label_title = ctk.CTkLabel(self, text=f"Waiting... {display_name}", anchor="w", font=("Roboto", 12, "bold"))
        self.label_title.grid(row=0, column=0, sticky="ew", padx=10, pady=(5,0))
        
        self.progress_bar = ctk.CTkProgressBar(self, height=10)
        self.progress_bar.set(0)
        self.progress_bar.grid(row=1, column=0, sticky="ew", padx=10, pady=5)
        
        self.label_status = ctk.CTkLabel(self, text="Pending", anchor="e", font=("Roboto", 11), text_color="gray")
        self.label_status.grid(row=1, column=1, padx=10)

    def update_progress(self, percent, status_text=None):
        self.progress_bar.set(percent / 100)
        if status_text:
            self.label_status.configure(text=status_text)
            
    def set_finished(self, final_name=None):
        self.progress_bar.set(1)
        self.progress_bar.configure(progress_color="#2CC985")
        self.label_status.configure(text="Completed", text_color="#2CC985")
        if final_name:
            self.label_title.configure(text=f"Done: {final_name}")

    def set_error(self, error_msg):
        self.progress_bar.configure(progress_color="#FF4D4D")
        self.label_status.configure(text="Failed", text_color="#FF4D4D")
        self.label_title.configure(text=f"Error: {error_msg}")

class VideoDownloaderApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Universal Downloader (YouTube & Direct)")
        self.geometry("1000x700")
        
        # --- Variables ---
        self.download_queue = queue.Queue()
        self.max_threads = 4
        
        # --- Layout ---
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # === LEFT SIDEBAR (INPUTS) ===
        self.sidebar_frame = ctk.CTkFrame(self, width=350, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(6, weight=1) # Spacer row

        # Logo
        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="Downloader Pro", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        # 1. URLs Input
        self.lbl_sources = ctk.CTkLabel(self.sidebar_frame, text="URLs (One per line):", anchor="w")
        self.lbl_sources.grid(row=1, column=0, padx=20, pady=(10, 0), sticky="w")
        
        self.txt_sources = ctk.CTkTextbox(self.sidebar_frame, height=120)
        self.txt_sources.grid(row=2, column=0, padx=20, pady=5, sticky="ew")

        # 2. Titles Input (New)
        self.lbl_titles = ctk.CTkLabel(self.sidebar_frame, text="Custom Filenames (Optional, match line-by-line):", anchor="w")
        self.lbl_titles.grid(row=3, column=0, padx=20, pady=(10, 0), sticky="w")
        
        self.txt_titles = ctk.CTkTextbox(self.sidebar_frame, height=120)
        self.txt_titles.grid(row=4, column=0, padx=20, pady=5, sticky="ew")

        # 3. Location Input
        self.lbl_path = ctk.CTkLabel(self.sidebar_frame, text="Save Location:", anchor="w")
        self.lbl_path.grid(row=5, column=0, padx=20, pady=(10, 0), sticky="w")

        self.path_frame = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
        self.path_frame.grid(row=6, column=0, padx=20, pady=5, sticky="new")
        
        self.entry_path = ctk.CTkEntry(self.path_frame, placeholder_text="Downloads folder")
        self.entry_path.pack(side="left", fill="x", expand=True, padx=(0, 5))
        self.entry_path.insert(0, os.path.join(os.getcwd(), "downloads"))
        
        self.btn_browse = ctk.CTkButton(self.path_frame, text="...", width=30, command=self.browse_folder)
        self.btn_browse.pack(side="right")

        # Start Button
        self.btn_start = ctk.CTkButton(self.sidebar_frame, text="START DOWNLOAD", height=50, font=("Roboto", 14, "bold"), fg_color="#E03131", hover_color="#C92A2A", command=self.start_download_process)
        self.btn_start.grid(row=7, column=0, padx=20, pady=30, sticky="ew")

        # === RIGHT SIDE (QUEUE) ===
        self.right_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.right_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        
        self.lbl_queue = ctk.CTkLabel(self.right_frame, text="Download Queue", font=ctk.CTkFont(size=18, weight="bold"))
        self.lbl_queue.pack(anchor="w", pady=(0, 10))

        self.scrollable_tasks = ctk.CTkScrollableFrame(self.right_frame, label_text="Status")
        self.scrollable_tasks.pack(fill="both", expand=True)

    def browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.entry_path.delete(0, "end")
            self.entry_path.insert(0, folder)

    def start_download_process(self):
        raw_urls = self.txt_sources.get("1.0", "end").strip().split('\n')
        raw_titles = self.txt_titles.get("1.0", "end").strip().split('\n')
        out_dir = self.entry_path.get()

        urls = [u.strip() for u in raw_urls if u.strip()]
        titles = [t.strip() for t in raw_titles]

        if not urls:
            messagebox.showwarning("Warning", "Please enter at least one URL.")
            return

        if not os.path.exists(out_dir):
            try:
                os.makedirs(out_dir)
            except Exception as e:
                messagebox.showerror("Error", f"Cannot create directory: {e}")
                return

        for i, url in enumerate(urls):
            custom_title = titles[i] if i < len(titles) and titles[i].strip() else None
            
            task_widget = DownloadTask(self.scrollable_tasks, url, custom_title)
            
            self.download_queue.put((url, custom_title, out_dir, task_widget))
        
        self.start_workers()

    def start_workers(self):
        if not hasattr(self, 'workers_started'):
            self.workers_started = True
            for _ in range(self.max_threads):
                t = threading.Thread(target=self.worker_thread, daemon=True)
                t.start()

    def update_ui_safe(self, func, *args, **kwargs):
        self.after(0, lambda: func(*args, **kwargs))

    def worker_thread(self):
        while True:
            try:
                url, custom_title, out_dir, task_widget = self.download_queue.get(timeout=1)
            except queue.Empty:
                continue
            
            try:
                if "youtu.be" in url or "youtube.com" in url:
                    self.download_youtube(url, custom_title, out_dir, task_widget)
                else:
                    self.download_direct(url, custom_title, out_dir, task_widget)
            except Exception as e:
                print(f"Error: {e}")
                self.update_ui_safe(task_widget.set_error, str(e))
            finally:
                self.download_queue.task_done()

    def download_youtube(self, url, custom_title, out_dir, task_widget):
        self.update_ui_safe(task_widget.update_progress, 0, "Initializing yt-dlp...")
        
        if custom_title:
            outtmpl = os.path.join(out_dir, f"{custom_title}.%(ext)s")
            self.update_ui_safe(task_widget.label_title.configure, text=f"Downloading: {custom_title}")
        else:
            outtmpl = os.path.join(out_dir, "%(title).200s [%(id)s].%(ext)s")

        def progress_hook(d):
            if d['status'] == 'downloading':
                try:
                    p = d.get('_percent_str', '0%').replace('%','')
                    progress = float(p)
                    speed = d.get('_speed_str', 'N/A')
                    self.update_ui_safe(task_widget.update_progress, progress, f"DL: {speed}")
                    
                    if not custom_title and d.get('info_dict'):
                        real_title = d['info_dict'].get('title', 'Unknown')
                        self.update_ui_safe(task_widget.label_title.configure, text=f"{real_title}")
                except:
                    pass

        ydl_opts = {
            "noplaylist": True,
            "format": "bv*[ext=mp4]+ba[ext=m4a]/b[ext=mp4]/best",
            "merge_output_format": "mp4",
            "outtmpl": outtmpl,
            "progress_hooks": [progress_hook],
            "quiet": True,
            "no_warnings": True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
            
        self.update_ui_safe(task_widget.set_finished, custom_title)

    def download_direct(self, url, custom_title, out_dir, task_widget):
        self.update_ui_safe(task_widget.update_progress, 0, "Connecting...")
        
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
            
            response = requests.get(url, stream=True, headers=headers, timeout=10)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            
            if custom_title:
                filename = custom_title
                if "." not in filename:
                    ext = os.path.splitext(urlparse(url).path)[1]
                    if not ext: ext = ".mp4"
                    filename += ext
            else:
                filename = os.path.basename(urlparse(url).path)
                if not filename: filename = "downloaded_file.mp4"

            full_path = os.path.join(out_dir, filename)
            self.update_ui_safe(task_widget.label_title.configure, text=f"Downloading: {filename}")

            block_size = 8192
            downloaded = 0
            start_time = time.time()
            
            with open(full_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=block_size):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        if total_size > 0:
                            percent = (downloaded / total_size) * 100
                            
                            elapsed = time.time() - start_time
                            speed_str = "N/A"
                            if elapsed > 0:
                                speed = (downloaded / 1024 / 1024) / elapsed
                                speed_str = f"{speed:.2f} MB/s"
                            
                            self.update_ui_safe(task_widget.update_progress, percent, speed_str)
                        else:
                            downloaded_mb = downloaded / 1024 / 1024
                            self.update_ui_safe(task_widget.update_progress, 50, f"{downloaded_mb:.2f} MB received")

            self.update_ui_safe(task_widget.set_finished, filename)
            
        except Exception as e:
            raise Exception(f"Request failed: {str(e)}")

if __name__ == "__main__":
    app = VideoDownloaderApp()
    app.mainloop()