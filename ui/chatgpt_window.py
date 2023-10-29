import tkinter as tk
from tkinter import filedialog, ttk, messagebox, Scrollbar
from ttkthemes import ThemedTk
from models import chatgpt
import shutil
import os
import logging
import concurrent.futures
from queue import Queue, Empty

# Logging setup
logging.basicConfig(level=logging.INFO, format='[%(threadName)s] %(message)s')
logger = logging.getLogger(__name__)

class ChatGPTWindow(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master=master)
        master.withdraw()
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        # Initialize attributes
        self.download_boxes = {}
        self.queue = Queue()
        self.download_folder = os.path.expanduser('~/Downloads')  # Default download folder

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

        # Attachments Frame
        self.attachments_frame = ttk.LabelFrame(self, text="Attachments (Word)", padding=(10, 5))

        self.files_canvas = tk.Canvas(self.attachments_frame)
        self.scrollbar = Scrollbar(self.attachments_frame, orient="vertical", command=self.files_canvas.yview)
        self.files_canvas.config(yscrollcommand=self.scrollbar.set)

        self.files_frame = ttk.Frame(self.files_canvas)

        # Modify the submit_button and attach_button
        self.prompt_label = ttk.Label(self, text="Comandă pentru ChatGPT")
        self.prompt_entry = ttk.Entry(self, width=40)

        self.attach_button = ttk.Button(self.files_frame, text="Atașează", command=self.attach_files)
        self.submit_button = ttk.Button(self.files_frame, text="Procesează", command=self.process_files)

        self.prompt_label.grid(row=0, column=0, padx=20, pady=5, columnspan=2)
        self.prompt_entry.grid(row=1, column=0, padx=20, pady=5, columnspan=2)

        # Add a button to select the download folder
        self.select_download_folder_button = ttk.Button(self, text="Alege folder", command=self.select_download_folder)
        self.select_download_folder_button.grid(row=3, column=0, padx=20, pady=5, columnspan=2)

        # Layout Attachments Frame
        self.files_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.files_canvas.create_window((0, 0), window=self.files_frame, anchor="nw")
        self.files_frame.bind("<Configure>", lambda e: self.files_canvas.configure(scrollregion=self.files_canvas.bbox("all")))

        self.attach_button.grid(row=0, column=0, padx=(20, 5), pady=5, sticky="w")
        self.submit_button.grid(row=0, column=1, padx=(5, 20), pady=5, sticky="e")

        self.attachments_frame.grid(row=2, column=0, columnspan=2, padx=20, pady=10, sticky="nsew")

        # Configure grid rows and columns to expand properly
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

    def on_close(self):
        self.master.deiconify()
        self.destroy()

    def attach_files(self):
        logger.info("Attaching files.")
        filepaths = filedialog.askopenfilenames(title="Alege fișiere", filetypes=[("Word Documents", "*.docx")])
        for filepath in filepaths:
            filename = os.path.basename(filepath)

            # Create a frame to hold the filename label and its status square
            file_frame = ttk.Frame(self.files_frame)
            file_frame.grid(sticky="ew")
            file_label = ttk.Label(file_frame, text=filename)
            file_label.grid(row=0, column=0, padx=5, sticky="w")

            # Status square (initialized as grey) for each file
            canvas = tk.Canvas(file_frame, height=20, width=20)  # Adjusting size for a square
            canvas.grid(row=0, column=1, padx=5, sticky="e")
            status_rect = canvas.create_rectangle(0, 0, 20, 20, fill="grey", outline="grey")
            self.download_boxes[filename] = {'canvas': canvas, 'status_rect': status_rect, 'path': filepath}

    def update_progress(self, filename, status):
        if filename in self.download_boxes:
            if status == "started":
                self.download_boxes[filename]['canvas'].itemconfig(self.download_boxes[filename]['status_rect'], fill="yellow", outline="yellow")
            elif status == "completed":
                self.download_boxes[filename]['canvas'].itemconfig(self.download_boxes[filename]['status_rect'], fill="green", outline="green")

    def process_files(self):
        prompt = self.prompt_entry.get()
        files = self.download_boxes.keys()

        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [executor.submit(chatgpt.process_docx, self.download_boxes[filename]['path'], prompt, lambda status: self.queue.put((filename, status))) for filename in files]
            
        # Periodically check the queue for updates
        self.after(100, self.check_queue)

    def check_queue(self):
        try:
            while True:
                # Non-blocking get from the queue
                filename, status = self.queue.get_nowait()
                self.update_progress(filename, status)
        except Empty:
            # If there's nothing in the queue, reschedule the check
            self.after(100, self.check_queue)

    def display_processed_file(self, original_path, processed_path):
        filename = os.path.basename(original_path)
        logger.info(f"Displaying processed file: {filename}")

        download_frame = ttk.Frame(self)
        label = ttk.Label(download_frame, text=f"Processed {filename}")
        label.grid(row=0, column=0)
        download_frame.pack(pady=5, padx=20, fill=tk.X)

        self.download_boxes[filename] = label
        self.download_file(processed_path, filename)

    def select_download_folder(self):
        """ Open a dialog to select a download folder. """
        folder_selected = filedialog.askdirectory()
        if folder_selected:  # Update the download folder only if a folder was selected
            self.download_folder = folder_selected
            logger.info(f"Download folder set to: {self.download_folder}")
            messagebox.showinfo("Folder selectat", f"Fișierele se vor descărca în: {self.download_folder}")

    def download_file(self, processed_path, filename):
      """ Download the processed file to the selected folder. """
      dest_path = os.path.join(self.download_folder, os.path.basename(processed_path))
    
      try:
        shutil.copy2(processed_path, dest_path)
        logger.info(f"Fișier descărcat în {dest_path}")

        label = self.download_boxes.get(filename)
        if label:
            label.config(text=f"{filename} (Descărcat)")
            messagebox.showinfo("Fișier descărcat", f"Fișier descărcat în {dest_path}")
      except Exception as e:
        logger.error(f"Failed to download file to {dest_path}: {e}")
        messagebox.showerror("Descărcarea a eșuat", f"Nu s-a putut salva în {dest_path}")


if __name__ == "__main__":
    root = ThemedTk(theme="arc")
    app = ChatGPTWindow(master=root)
    app.mainloop()
