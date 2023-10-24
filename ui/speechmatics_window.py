import tkinter as tk
from tkinter import ttk, filedialog
from models import speechmatics
import shutil


class SpeechmaticsWindow(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.title("Fereastra Speechmatics")
        self.geometry("600x400")

        self.attachments = []

        # Create an "Adaugă Atașamente" button to add attachments
        self.add_button = ttk.Button(self, text="Adaugă Atașamente", command=self.add_attachment)
        self.add_button.pack(pady=20)

        # Create a "Transcriere" button to start the transcription process
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

        # Download button
        self.download_button = ttk.Button(self, text="Download", command=self.download_file, state=tk.DISABLED)  # Initially disabled
        self.download_button.pack(side=tk.RIGHT, padx=5)

        # Status rectangle
        self.status_canvas = tk.Canvas(self, width=100, height=20, bg="white")
        self.status_canvas.pack(side=tk.RIGHT, padx=5)
        self.rectangle = self.status_canvas.create_rectangle(5, 5, 5, 15, fill="grey")
        self.progress_text = self.status_canvas.create_text(50, 10, text="0%", anchor=tk.CENTER)  # Center text

    def set_status(self, status, progress=0):
        if status == "not started":
            self.status_canvas.itemconfig(self.rectangle, fill="grey")
            self.status_canvas.itemconfig(self.progress_text, text="0%")
        elif status == "started":
            fill_width = progress  # 0 to 99
            self.status_canvas.coords(self.rectangle, 5, 5, 5 + fill_width, 15)
            self.status_canvas.itemconfig(self.rectangle, fill="blue")
            self.status_canvas.itemconfig(self.progress_text, text=f"{progress}%")
        elif status == "completed":
            self.status_canvas.coords(self.rectangle, 5, 5, 95, 15)
            self.status_canvas.itemconfig(self.rectangle, fill="green")
            self.status_canvas.itemconfig(self.progress_text, text="100%")
            self.download_button.config(state=tk.NORMAL, style='TButton')  # Enable the download button and change style

    def download_file(self):
        save_path = filedialog.asksaveasfilename(initialfile=self.file_path.split('/')[-1],
                                                 filetypes=[('Audio Files', '*.wav;*.mp3')])
        if not save_path:
            return
        # Copy the processed file to the save_path (assuming the processed file is the same as the original for this example)
        shutil.copy(self.file_path, save_path)


if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    window = SpeechmaticsWindow(master=root)
    window.mainloop()
