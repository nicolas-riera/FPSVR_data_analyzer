import customtkinter as ctk
import threading

from src.scan_data import ProcessFiles

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("FPSVR Data Analyzer")
        self.geometry("800x800")

        self.container = ctk.CTkFrame(master=self)
        self.container.pack(fill="both", expand=True)

        self.file_loading_progress_bar()

        self.after(100, self.start_thread)

    def start_thread(self):
        threading.Thread(target=self.file_loading).start()

    def file_loading(self):

        self.data = ProcessFiles(progress_callback=self.update_progress)
        self.data.run()

    def file_loading_progress_bar(self):
        self.progress = ctk.CTkProgressBar(self.container, width=400)
        self.progress.pack(pady=20)

        self.label = ctk.CTkLabel(self.container, text="Loading...")
        self.label.pack()

    def update_progress(self, progress, count, total):
        def _update():
            self.progress.set(progress)
            self.label.configure(text=f"{count}/{total}")
        self.after(0, _update) 