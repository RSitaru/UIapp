import tkinter as tk
from tkinter import ttk
from ttkthemes import ThemedTk
from ui.chatgpt_window import ChatGPTWindow
from ui.speechmatics_window import SpeechmaticsWindow

class MainWindow(ThemedTk):
    def __init__(self):
        super().__init__(theme="arc")
        
        # Set window title
        self.title("Selector Model AI")
        
        # Set the window size and position
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        window_width = int(screen_width * 0.4)
        window_height = int(screen_height * 0.4)
        position_x = int((screen_width / 2) - (window_width / 2))
        position_y = int((screen_height / 2) - (window_height / 2))
        self.geometry(f"{window_width}x{window_height}+{position_x}+{position_y}")

        # Configure ttk style for button font
        style = ttk.Style()
        style.configure("TButton", font=("Arial", 16))

        # Adding a frame that holds the buttons
        self.frame = ttk.Frame(self, padding="20")
        self.frame.pack(fill=tk.BOTH, expand=True)

        # Create and position the ChatGPT button
        chatgpt_btn = ttk.Button(self.frame, text="Comunică cu ChatGPT", command=self.show_chatgpt_window)
        chatgpt_btn.pack(pady=20, padx=20, expand=True, fill=tk.BOTH)

        # Create and position the Speechmatics button
        speechmatics_btn = ttk.Button(self.frame, text="Folosește Speechmatics", command=self.show_speechmatics_window)
        speechmatics_btn.pack(pady=20, padx=20, expand=True, fill=tk.BOTH)

    def show_chatgpt_window(self):
        ChatGPTWindow(self)  # Parent of ChatGPTWindow is this MainWindow

    def show_speechmatics_window(self):
        SpeechmaticsWindow(self)  # Similarly for Speechmatics
