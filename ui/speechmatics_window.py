import tkinter as tk
from tkinter import ttk, filedialog
import shutil
from models import speechmatics

class SpeechmaticsWindow(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.title("Fereastra Speechmatics")
        self.geometry("600x400")

        self.attachments = []

        self.add_button = ttk.Button(self, text="Adaugă Atașamente", command=self.add_attachment)
        self.add_button.pack(pady=20)

        self.transcribe_button = ttk.Button(self, text="Transcriere", command=self.transcribe_attachments)
        self.transcribe_button.pack(pady=20)

    def add_attachment(self):
        file_path = filedialog.askopenfilename(filetypes=[('Audio Files', '*.wav;*.mp3')])
        if not file_path:
            return
        attachment = Attachment(self, file_path)
        attachment.pack(fill=tk.X, padx=20, pady=5)
        self.attachments.append(attachment)

    def transcribe_attachments(self):
        for attachment in self.attachments:
            callback = lambda result, attach=attachment: attach.set_status("completed")
            progress_callback = lambda progress, attach=attachment: attach.set_status("started", progress=progress)
        
            speechmatics.transcribe_audio_threaded(attachment.file_path, callback, progress_callback)

class Attachment(ttk.Frame):
    def __init__(self, parent, file_path):
        super().__init__(parent)
        self.file_path = file_path

        self.label = ttk.Label(self, text=file_path)
        self.label.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.status_canvas = tk.Canvas(self, width=100, height=20, bg="white")
        self.status_canvas.pack(side=tk.RIGHT, padx=5)
        self.rectangle = self.status_canvas.create_rectangle(5, 5, 95, 15, fill="grey")

        self.download_button = ttk.Button(self, text="Download", command=self.download_file, state=tk.DISABLED)
        self.download_button.pack(side=tk.RIGHT, padx=5)

    def set_status(self, status, progress=0):
        if status == "not started":
            self.status_canvas.itemconfig(self.rectangle, fill="grey")
        elif status == "started":
            fill_width = progress  # 0 to 100
            self.status_canvas.coords(self.rectangle, 5, 5, 5 + fill_width, 15)
            self.status_canvas.itemconfig(self.rectangle, fill="blue")
        elif status == "completed":
            self.status_canvas.coords(self.rectangle, 5, 5, 95, 15)
            self.status_canvas.itemconfig(self.rectangle, fill="green")
            self.download_button.config(state=tk.NORMAL)

    def download_file(self):
        save_path = filedialog.asksaveasfilename(initialfile=self.file_path.split('/')[-1],
                                                 filetypes=[('Audio Files', '*.wav;*.mp3')])
        if not save_path:
            return
        shutil.copy(self.file_path, save_path)

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    window = SpeechmaticsWindow(master=root)
    window.mainloop()
