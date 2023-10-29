import tkinter as tk
from tkinter import filedialog, ttk, messagebox, Scrollbar
from ttkthemes import ThemedTk
from models import chatgpt
import shutil
import os
import logging
import concurrent.futures

# Logging setup
logging.basicConfig(level=logging.INFO, format='[%(threadName)s] %(message)s')
logger = logging.getLogger(__name__)

class ChatGPTWindow(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master=master)
        master.withdraw()
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        logger.info("ChatGPTWindow initialized.")
        self.title("ChatGPT Processor")

        # Set size and center window
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        window_width = int(screen_width * 0.4)
        window_height = int(screen_height * 0.4)
        position_x = (screen_width // 2) - (window_width // 2)
        position_y = (screen_height // 2) - (window_height // 2)
        self.geometry(f"{window_width}x{window_height}+{position_x}+{position_y}")

        # Components
        self.prompt_label = ttk.Label(self, text="Comandă pentru ChatGPT")
        self.prompt_entry = ttk.Entry(self, width=40)

        self.attachments_frame = ttk.LabelFrame(self, text="Atașamente (Word)", padding=(10, 5))
        self.files_canvas = tk.Canvas(self.attachments_frame)
        self.files_frame = ttk.Frame(self.files_canvas)
        
        self.files_canvas_frame_id = self.files_canvas.create_window((0, 0), window=self.files_frame, anchor="nw")
        self.files_canvas.bind("<Configure>", self.update_scroll_region)
        
        self.attach_button = ttk.Button(self.attachments_frame, text="Atașează", command=self.attach_files, width=10)
        self.scrollbar = Scrollbar(self.attachments_frame, orient="vertical", command=self.files_canvas.yview)
        self.files_canvas.config(yscrollcommand=self.scrollbar.set)

        self.submit_button = ttk.Button(self, text="Procesează", command=self.process_files)

        # Layout
        self.prompt_label.pack(pady=5)
        self.prompt_entry.pack(pady=5, padx=20, fill=tk.X)
        self.attachments_frame.pack(pady=10, padx=20, fill=tk.X)
        self.files_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.attach_button.pack(pady=5)
        self.submit_button.pack(pady=20)

    def update_scroll_region(self, event):
        self.files_canvas.configure(scrollregion=self.files_canvas.bbox("all"))

    def on_close(self):
        self.master.deiconify()
        self.destroy()

    def add_attachments(self):
        file_paths = filedialog.askopenfilenames(filetypes=[("Audio Files", "*.mp3;*.wav")])
        for file_path in file_paths:
            if file_path and len(self.attachments) < 10:
                attachment = Attachment(self.attachments_frame, file_path)
                attachment.pack(fill=tk.X)
                self.attachments.append(attachment)
                if len(self.attachments) == 10:
                    break

    def transcribe(self, attachment):
      result, job_id = my_speechmatics.transcribe_audio(attachment.file_path, attachment.update_progress)
      filename = attachment.file_path.split("/")[-1]

      while not job_id:
        time.sleep(1)  # Wait until job_id is assigned

      print(result)

      notification.notify(
        title='Transcription Completed',
        message=f'Transcription for {filename} is done! Result saved at: {result.split(" at ")[-1]}',
        app_icon=None,
        timeout=10,
    )

    def submit(self):
        for attachment in self.attachments:
            threading.Thread(target=self.transcribe, args=(attachment,)).start()

class Attachment(ttk.Frame):
    def __init__(self, parent, file_path):
        super().__init__(parent)
        self.file_path = file_path

        self.label = ttk.Label(self, text=file_path)
        self.label.pack(side=tk.LEFT)

        self.status_canvas = tk.Canvas(self, width=20, height=20)
        self.status_rect = self.status_canvas.create_rectangle(0, 0, 20, 20, fill="grey")
        self.status_canvas.pack(side=tk.RIGHT)

    def set_status(self, status):
      if status == "grey":
        self.status_canvas.itemconfig(self.status_rect, fill="grey")
      elif status == "yellow":
        self.status_canvas.itemconfig(self.status_rect, fill="yellow")
      elif status == "green":
        self.status_canvas.itemconfig(self.status_rect, fill="green")



    def update_progress(self, status_or_progress):
      if isinstance(status_or_progress, str):
          if status_or_progress == "submitted":
            self.set_status("yellow")
          elif status_or_progress == "done":
            self.set_status("green")


if __name__ == "__main__":
    import time
    root = tk.Tk()
    window = SpeechmaticsWindow(root)
    window.mainloop()