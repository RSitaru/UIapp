import tkinter as tk
from tkinter import ttk, filedialog
from models import speechmatics

class SpeechmaticsWindow(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master=master)

        self.title("Fereastră Speechmatics")

        # Set size and center window
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        window_width = int(screen_width * 0.4)
        window_height = int(screen_height * 0.4)
        
        position_x = (screen_width // 2) - (window_width // 2)
        position_y = (screen_height // 2) - (window_height // 2)
        
        self.geometry(f"{window_width}x{window_height}+{position_x}+{position_y}")

        # Attachment Field
        self.attachment_btn = ttk.Button(self, text="Adaugă Atașamente", command=self.add_attachments)
        self.attachment_btn.pack(pady=10, padx=20)

        self.attachments_frame = ttk.Frame(self)
        self.attachments_frame.pack(pady=10, padx=20, fill=tk.X)
        
        self.attachments = []

        # Submit Button
        self.submit_btn = ttk.Button(self, text="Transcriere", command=self.submit)
        self.submit_btn.pack(pady=20)

    def add_attachments(self):
        file_paths = filedialog.askopenfilenames(filetypes=[("Audio Files", "*.mp3;*.wav")])
        for file_path in file_paths:
            if file_path and len(self.attachments) < 10:  # Maximum of 10 attachments
                attachment = Attachment(self.attachments_frame, file_path)
                attachment.pack(fill=tk.X)
                self.attachments.append(attachment)
                if len(self.attachments) == 10:
                    break

    def submit(self):
        # Handle attachments
        for attachment in self.attachments:
            # TODO: Send each attachment as a separate request
            # For demonstration, we'll just print the file path for now
            print(attachment.file_path)

class Attachment(ttk.Frame):
    def __init__(self, parent, file_path):
        super().__init__(parent)
        self.file_path = file_path

        self.label = ttk.Label(self, text=file_path)
        self.label.pack(side=tk.LEFT)

        # Small font for loading and cost details
        small_font = ("Arial", 10)

        # Loading and cost icons can be added here
        # Currently adding a dummy label as a placeholder
        self.info_label = ttk.Label(self, text="Loading... | $0.00", font=small_font)
        self.info_label.pack(side=tk.RIGHT)

        # The logic for updating the loading status and cost can be added in this class

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    window = SpeechmaticsWindow(master=root)
    window.mainloop()
