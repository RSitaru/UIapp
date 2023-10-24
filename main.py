from ui.main_window import MainWindow

print("Running main.py...")

if __name__ == "__main__":
    print("Inside main block...")
    app = MainWindow()
    print("MainWindow instantiated...")
    app.mainloop()
    print("Exiting app...")
