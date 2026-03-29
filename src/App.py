import customtkinter as ctk
import threading
import os

from src.scan_data import ProcessFiles
from src.MenuUI import MenuUI

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("")
        self.geometry("800x800")

        self.container = ctk.CTkFrame(master=self)
        self.container.pack(fill="both", expand=True)
        
        self.file_loading_progress_bar()

        self.after(300, self.start_thread)

        self.menu = MenuUI(
            self.container,
            on_select=self.handle_selection,
            on_refresh=self.refresh_data
        )
        self.menu.pack(fill="both", expand=True, anchor="n")

    # Data loading
    def start_thread(self):
        t = threading.Thread(target=self.file_loading)
        t.daemon = True 
        t.start()

    def file_loading(self):
        self.data = ProcessFiles(progress_callback=self.update_progress)
        self.data.run()
        if self.label.cget("text") != "Please wait...":
            self.after(1500, self.destroy_loading_widgets)

    def file_loading_progress_bar(self):

        self.status_container = ctk.CTkFrame(self.container, height=40, fg_color="#333333")
        self.status_container.pack(side="bottom", fill="x")
        self.status_container.pack_propagate(False)

        self.bottom_frame = ctk.CTkFrame(self.status_container, fg_color="transparent")
        self.bottom_frame.pack(side="bottom", anchor="w", padx=10, pady=10)

        self.bottom_frame.grid_columnconfigure(0, weight=0)
        self.bottom_frame.grid_columnconfigure(1, weight=0)

        self.progress = ctk.CTkProgressBar(self.bottom_frame, width=300)
        self.progress.grid(row=0, column=0, sticky="w")
        self.progress.set(0)

        self.label = ctk.CTkLabel(self.bottom_frame, text="Please wait...")
        self.label.grid(row=0, column=1, padx=(10, 0), sticky="w")

    def destroy_loading_widgets(self):
        self.progress.destroy()
        self.label.destroy()
        self.bottom_frame.destroy()

        self.menu.refresh_btn.configure(state="normal")

    def update_progress(self, progress, count, total):
        def _update():
            self.progress.set(progress)
            if total != -1:
                self.label.configure(text=f"{count}/{total}")
                if count == total:
                    self.menu.enable_buttons()
            else:
                self.label.configure(text="Data Not Found...")   
             
        self.after(0, _update) 
        
    # Main Menu
    def handle_selection(self, value):
        print(value)

    def refresh_data(self):
        self.status_container.destroy()
        self.file_loading_progress_bar()
        self.menu.refresh_btn.configure(state="disabled")
        self.menu.disable_buttons()

        self.data.cache_manager(mode="cls")
        self.after(300, self.start_thread)