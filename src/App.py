import customtkinter as ctk
import threading
import os

from src.scan_data import ProcessFiles
from src.MenuUI import MenuUI
from src.GraphUI import GraphUI

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("FPSVR Data Analyzer")
        self.geometry("800x800")
        self.after(201, lambda :self.iconbitmap(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "img", "logo.ico")))

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

        self.menu.pack_forget()
        
        match value:
            case 1:
                headers = ["VR Headset", "Total Usage"]
                data = [[h, App.format_duration(t)] for h, t in self.data.hmd_usage.items()]

            case 2:
                headers = ["Game", "Playtime", "Average FPS"]
                data = []

                for app, t in self.data.game_time.items():
                    avg_fps = self.data.game_fps[app]["total_fps"] / self.data.game_fps[app]["total_time"] if app in self.data.game_fps else 0
                    data.append([app, App.format_duration(t), f"{avg_fps:.2f}"])

            case 3:
                headers = ["Hardware", "Type", "Usage Time", "Average Temp (°C)", "Max Temp (°C)"]
                data = []
                for name, info in self.data.hardware_usage.items():
                    avg_temp = f"{sum(info['temps'])/len(info['temps']):.2f}" if info['temps'] else "N/A"
                    max_temp = f"{max(info['temps']):.2f}" if info['temps'] else "N/A"
                    usage_time = App.format_duration(info["time"])
                    data.append([name, info["type"], usage_time, avg_temp, max_temp])

            case 4:
                headers = ["SteamVR Version", "Most Used HMD", "Usage Time"]
                data = []

                for version, hmds in self.data.steamvr_usage.items():
                    most_used_hmd = max(hmds, key=hmds.get)
                    usage_time = App.format_duration(hmds[most_used_hmd])
                    data.append([version, most_used_hmd, usage_time])

            case 5:
                headers = ["Tracking System", "Total Usage"]
                data = [[k, App.format_duration(v)] for k, v in self.data.tracking_usage.items()]

            case 6:
                headers = ["Operating System", "Total Usage"]
                data = [[k, App.format_duration(v)] for k, v in self.data.os_usage.items()]

            case 7:
                headers = ["Refresh Rate (Hz)", "Total Usage"]
                data = [[k, App.format_duration(v)] for k, v in self.data.hz_usage.items()]
        
            case _:
                print("Menu Programming error") #debug only
                self.menu.pack(fill="both", expand=True, anchor="n")
                return

        self.graph_view = GraphUI(
            master=self.container, 
            headers=headers, 
            data=data, 
            on_back=self.show_menu 
        )
        self.graph_view.pack(fill="both", expand=True)

    def show_menu(self):
        if hasattr(self, 'graph_view'):
            self.graph_view.destroy()
        self.menu.pack(fill="both", expand=True, anchor="n")

    def refresh_data(self):
        self.status_container.destroy()
        self.file_loading_progress_bar()
        self.menu.refresh_btn.configure(state="disabled")
        self.menu.disable_buttons()

        self.data.cache_manager(mode="cls")
        self.after(300, self.start_thread)

    @staticmethod
    def format_duration(seconds):
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        return f"{hours}h {minutes}m {secs}s"
