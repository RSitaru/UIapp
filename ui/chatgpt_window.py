import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from ttkthemes import ThemedTk
from models import chatgpt
import shutil
import os

class ChatGPTWindow(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master=master)

        self.title("ChatGPT Processor")
        self.geometry("800x600")

        # Components
        self.attachments_frame = ttk.LabelFrame(self, text="Attachments (Word documents only)", padding=(10, 5))
        self.attachments_listbox = tk.Listbox(self.attachments_frame, width=50)
        self.attach_button = ttk.Button(self.attachments_frame, text="Attach", command=self.attach_files)
        self.download_boxes = {}  # {filename: (label, download_button)}

        self.prompt_label = ttk.Label(self, text="Prompt for ChatGPT")
        self.prompt_entry = ttk.Entry(self, width=50)

        self.submit_button = ttk.Button(self, text="Process", command=self.process_files)

        # Layout
        self.attachments_frame.grid(row=0, column=0, pady=10, padx=10, sticky=tk.W)
        self.attachments_listbox.grid(row=0, column=0, padx=(0, 10))
        self.attach_button.grid(row=0, column=1)

        self.prompt_label.grid(row=1, column=0, sticky=tk.W, padx=10)
        self.prompt_entry.grid(row=2, column=0, padx=10)

        self.submit_button.grid(row=3, column=0, pady=20)

    def attach_files(self):
        filepaths = filedialog.askopenfilenames(title="Choose files", filetypes=[("Word Documents", "*.docx")])
        for filepath in filepaths:
            self.attachments_listbox.insert(tk.END, filepath)

    def process_files(self):
        prompt = self.prompt_entry.get()
        files = self.attachments_listbox.get(0, tk.END)

        for filepath in files:
            try:
                processed_path = chatgpt.process_docx(filepath, prompt)
                self.display_processed_file(filepath, processed_path)
            except Exception as e:
                messagebox.showerror("Processing Error", str(e))

    def display_processed_file(self, original_path, processed_path):
        filename = os.path.basename(original_path)

        download_frame = ttk.Frame(self)
        label = ttk.Label(download_frame, text=f"Processed {filename}")
        download_button = ttk.Button(download_frame, text="Download", command=lambda p=processed_path: self.download_file(p))
        
        label.grid(row=0, column=0)
        download_button.grid(row=0, column=1)
        download_frame.grid(row=4 + list(self.download_boxes.keys()).index(filename) if filename in self.download_boxes else len(self.download_boxes), column=0, pady=5, padx=10)

        self.download_boxes[filename] = (label, download_button)

    def download_file(self, processed_path):
        dest_folder = os.path.expanduser('~/Downloads')
        shutil.copy2(processed_path, dest_folder)

        dest_path = os.path.join(dest_folder, os.path.basename(processed_path))
        filename = os.path.basename(processed_path)

        label, button = self.download_boxes[filename]
        label.config(text=f"{filename} (Downloaded)")
        messagebox.showinfo("File Downloaded", f"File saved to {dest_path}")

if __name__ == "__main__":
    root = ThemedTk(theme="arc")  # Using ThemedTk for consistency
    root.withdraw()
    app = ChatGPTWindow(master=root)
    app.mainloop()
