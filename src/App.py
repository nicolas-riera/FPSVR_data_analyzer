import customtkinter as ctk
import threading
import os

from src.scan_data import ProcessFiles
from src.MenuUI import MenuUI
from src.GraphUI import GraphUI
from src.ressource_path import resource_path

class App(ctk.CTk):
    def __init__(self, version):
        super().__init__()

        self.title("FPSVR Data Analyzer")
        self.geometry("800x800")
        self.after(201, lambda :self.iconbitmap(resource_path(os.path.join("img", "logo.ico"))))

        self.version = version

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
        self.title("FPSVR Data Analyzer - Retriving and processing data...")
        t = threading.Thread(target=self.file_loading)
        t.daemon = True 
        t.start()

    def file_loading(self):
        self.data = ProcessFiles(version=self.version, progress_callback=self.update_progress)
        self.data.run()
        if self.label.cget("text") != "Please wait...":
            self.after(1500, self.destroy_loading_widgets)

    def file_loading_progress_bar(self):

        self.status_container = ctk.CTkFrame(self.container, height=40, fg_color="#333333")
        self.status_container.pack(side="bottom", fill="x")
        self.status_container.pack_propagate(False)

        self.version_label = ctk.CTkLabel(
            self,
            text=f"v{self.version}" if hasattr(self, "version") else "v?",
            font=ctk.CTkFont(size=12),
            text_color="gray",
            fg_color="#333333"
        )

        self.version_label.place(relx=1.0, rely=1.0, anchor="se", x=-10, y=-5)

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

        self.menu.refresh_btn.configure(state="normal", text="Refresh Data")

    def update_progress(self, progress, count, total):
        def _update():
            self.progress.set(progress)
            if total != -1:
                self.label.configure(text=f"{count}/{total}")
                if count == total:

                    highlights = self.calculate_highlights()

                    self.menu.enable_buttons()
                    self.menu.update_last_played(self.data.last_session)
                    self.menu.update_highlights(highlights)
                    self.title("FPSVR Data Analyzer")
            else:
                self.label.configure(text="Data Not Found...")  
                self.title("FPSVR Data Analyzer - Data Not Found") 
             
        self.after(0, _update) 
        
    # Main Menu
    def handle_selection(self, value):

        self.menu.pack_forget()
        self.version_label.place_forget()
        
        match value:
            case 1:
                self.graphlabel = "VR Headset Usage"
                headers = ["VR Headset", "Resolution", "Usage Period", "Total Usage"]
                data = []

                for hmd_name, stats in self.data.hmd_usage.items():
                    resolutions = stats.get('resolutions', {})
                    if resolutions:
                        most_used_res = max(resolutions.items(), key=lambda x: x[1])[0]
                    else:
                        most_used_res = "N/A"

                    if stats['first_seen'] == stats['last_seen']:
                        date_range = stats['first_seen']
                    else:
                        date_range = f"{stats['first_seen']} -> {stats['last_seen']}"
                    
                    data.append([
                        hmd_name, 
                        most_used_res, 
                        date_range, 
                        App.format_duration(stats["duration"])
                    ])

            case 2:
                self.graphlabel = "Game Playtime & Avg FPS"
                headers = ["Game", "Playtime", "Average FPS"]
                data = []

                for app, t in self.data.game_time.items():
                    avg_fps = self.data.game_fps[app]["total_fps"] / self.data.game_fps[app]["total_time"] if app in self.data.game_fps else 0
                    data.append([app, App.format_duration(t), f"{avg_fps:.2f}"])

            case 3:
                self.graphlabel = "CPU / GPU Usage & Temps"
                headers = ["Hardware", "Type", "Usage Time", "Avg Temp", "Max Temp"]
                data = []
                for name, info in self.data.hardware_usage.items():
                    avg_temp = f"{sum(info['temps'])/len(info['temps']):.2f}" if info['temps'] else "N/A"
                    max_temp = f"{max(info['temps']):.2f}" if info['temps'] else "N/A"
                    usage_time = App.format_duration(info["time"])
                    data.append([name, info["type"], usage_time, avg_temp, max_temp])

            case 4:
                self.graphlabel = "SteamVR Version Usage"
                headers = ["SteamVR Version", "Most Used HMD", "Usage Period", "Usage Time"]
                data = []

                for version, hmds in self.data.steamvr_usage.items():
                    most_used_hmd = max(hmds, key=lambda x: hmds[x]["duration"])
                    
                    total_sec = sum(h["duration"] for h in hmds.values())
                    first_day = min(h["first_seen"] for h in hmds.values())
                    last_day = max(h["last_seen"] for h in hmds.values())
                    
                    date_range = first_day if first_day == last_day else f"{first_day} -> {last_day}"
                    usage_time = App.format_duration(total_sec)
                    
                    data.append([version, most_used_hmd, date_range, usage_time])

            case 5:
                self.graphlabel = "Tracking System Usage"
                headers = ["Tracking System", "Total Usage"]
                data = [[k, App.format_duration(v)] for k, v in self.data.tracking_usage.items()]

            case 6:
                self.graphlabel = "OS Usage"
                headers = ["Operating System", "Usage Period", "Total Usage"]
                data = []
                
                for os_name, stats in self.data.os_usage.items():
                    if stats['first_seen'] == stats['last_seen']:
                        date_range = stats['first_seen']
                    else:
                        date_range = f"{stats['first_seen']} -> {stats['last_seen']}"
                    data.append([
                        os_name, 
                        date_range, 
                        App.format_duration(stats["duration"])
                    ])

            case 7:
                self.graphlabel = "Refresh Rate Usage"
                headers = ["Refresh Rate (Hz)", "Total Usage"]
                data = [[k, App.format_duration(v)] for k, v in self.data.hz_usage.items()]
        
            case _:
                self.graphlabel = "???"
                print("Menu Programming error") #debug only
                self.menu.pack(fill="both", expand=True, anchor="n")
                return

        self.title(f"FPSVR Data Analyzer - {self.graphlabel}")
        self.graph_view = GraphUI(
            master=self.container, 
            headers=headers, 
            data=data, 
            on_back=self.show_menu,
            label=self.graphlabel
        )
        self.graph_view.pack(fill="both", expand=True)

    def show_menu(self):
        self.title("FPSVR Data Analyzer")
        if hasattr(self, 'graph_view'):
            self.graph_view.destroy()
        self.menu.pack(fill="both", expand=True, anchor="n")
        self.version_label.place(relx=1.0, rely=1.0, anchor="se", x=-10, y=-5)

    def refresh_data(self):
        self.status_container.destroy()
        self.file_loading_progress_bar()
        self.menu.refresh_btn.configure(state="disabled", text="...")
        self.menu.update_last_played("Refreshing signal")
        self.menu.update_highlights("Refreshing signal")
        self.menu.disable_buttons()

        self.data.cache_manager(mode="cls")
        self.after(300, self.start_thread)

    @staticmethod
    def format_duration(seconds):
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        return f"{hours}h {minutes}m {secs}s"
    
    @staticmethod
    def truncate_text(text, max_chars=50):
        if len(text) > max_chars:
            return text[:max_chars-3] + "..."
        return text
    
    def calculate_highlights(self):
        total_sessions = len(self.data.file_cache)
        total_sec = sum(self.data.game_time.values())
        formatted_time = App.format_duration(total_sec)
        sessions_time_display = f"{total_sessions} sessions\n{formatted_time}"
        sessions_time_display = App.truncate_text(sessions_time_display, 50)

        if self.data.hmd_usage:
            hmd_entry = max(self.data.hmd_usage.items(), key=lambda x: x[1]['duration'])
            hmd_name = App.truncate_text(hmd_entry[0], 25) 
            hmd_dur = App.format_duration(hmd_entry[1]['duration'])
            top_hmd = f"{hmd_name}\n{hmd_dur.split(' ')[0]} {hmd_dur.split(' ')[1]}"
        else:
            top_hmd = "N/A"

        if self.data.game_time:
            full_name = max(self.data.game_time.items(), key=lambda x: x[1])[0]
            top_game = App.truncate_text(full_name, 45)
            
            fps_info = self.data.game_fps.get(full_name, {"total_fps": 0, "total_time": 1})
            top_game_fps = f"{fps_info['total_fps'] / fps_info['total_time']:.1f}"
        else:
            top_game = "N/A"
            top_game_fps = "0"

        return {
            "total_sessions": sessions_time_display,
            "top_hmd": top_hmd,
            "top_game": f"{top_game}\n{top_game_fps} FPS avg"
        }
