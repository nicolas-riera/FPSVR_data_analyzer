import customtkinter as ctk
import threading
import os
from collections import Counter
import statistics
import requests
import webbrowser
from tkinter import messagebox
from datetime import datetime, timedelta
import platform

if platform.system() == "Windows":
    import winsound
else:
    winsound = None

from src.scan_data import ProcessFiles
from src.MenuUI import MenuUI
from src.GraphUI import GraphUI
from src.LineGraphUI import LineGraphUI
from src.ressource_path import resource_path

class App(ctk.CTk):
    def __init__(self, version):
        super().__init__()

        self.title("FPSVR Data Analyzer")
        self.geometry("800x800")
        ctk.set_appearance_mode("dark")
        self.after(201, lambda :self.iconbitmap(resource_path(os.path.join("img", "logo.ico"))))
        self.resizable(False, False)

        self.version = version

        self.container = ctk.CTkFrame(master=self)
        self.container.pack(fill="both", expand=True)
        
        self.file_loading_progress_bar()

        self.check_updates_async()

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
            # Global data
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

                for app, stats in self.data.game_time.items():
                    if isinstance(stats, dict):
                        duration = stats["duration"]
                        avg_fps = self.data.game_fps[app]["total_fps"] / self.data.game_fps[app]["total_time"] if app in self.data.game_fps else 0
                        data.append([app, App.format_duration(duration), f"{avg_fps:.2f}"])

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

            # Recent data
            case -1:
                self.graphlabel = "VR Headset Usage - Last 7 Days"
                self.x_label = "Date"
                self.y_label = "Hours"

                now_dt = datetime.now().date()

                stats_map = {
                    now_dt - timedelta(days=i): {"hours": 0, "hmds": set()}
                    for i in range(6, -1, -1)
                }

                for hmd_name, hmd_stats in self.data.hmd_usage.items():
                    history = hmd_stats.get("history", {})

                    for date_str, duration in history.items():
                        log_date = datetime.fromisoformat(date_str).date()

                        if log_date in stats_map:
                            stats_map[log_date]["hours"] += duration / 3600
                            stats_map[log_date]["hmds"].add(hmd_name)

                graph_data = [
                    (
                        day.strftime("%m-%d"),
                        round(info["hours"], 2),
                        ", ".join(info["hmds"])
                    )
                    for day, info in stats_map.items()
                ]

            case -2:
                self.graphlabel = "Game Playtime - Last 7 Days"
                self.x_label = "Date"
                self.y_label = "Hours"

                now_dt = datetime.now().date()

                stats_map = {
                    now_dt - timedelta(days=i): {"hours": 0, "games": set()}
                    for i in range(6, -1, -1)
                }

                for game_name, game_stats in self.data.game_time.items():
                    if isinstance(game_stats, dict):
                        history = game_stats.get("history", {})
                        for date_str, duration in history.items():
                            log_date = datetime.fromisoformat(date_str).date()
                            if log_date in stats_map:
                                stats_map[log_date]["hours"] += duration / 3600
                                stats_map[log_date]["games"].add(game_name)

                graph_data = [
                    (
                        day.strftime("%m-%d"),
                        round(info["hours"], 2),
                        ", ".join(list(info["games"])[:3]) + ("..." if len(info["games"]) > 3 else "")
                    )
                    for day, info in stats_map.items()
                ]

            case -3:
                self.graphlabel = "Avg Session Length - Last 7 Months"
                self.x_label = "Month"
                self.y_label = "Hours" 

                now = datetime.now()
                months = []
                for i in range(6, -1, -1):
                    total_m = (now.year * 12 + (now.month - 1)) - i
                    year, m_idx = divmod(total_m, 12)
                    months.append(f"{year}-{m_idx + 1:02d}")

                graph_data = []
                for m_str in months:
                    sessions = self.data.monthly_sessions.get(m_str, [])
                    if sessions:
                        avg_hours = (sum(sessions) / len(sessions)) / 3600
                        graph_data.append((
                            m_str, 
                            round(avg_hours, 2), 
                            ""
                        ))
                    else:
                        graph_data.append((m_str, 0, "No data"))

            case -4:
                self.graphlabel = "Recent CPU Temperatures - Last 7 Days"
                self.x_label = "Date"
                self.y_label = "°C"

                now_dt = datetime.now().date()
                stats_map = {now_dt - timedelta(days=i): [] for i in range(6, -1, -1)}

                for name, info in self.data.hardware_usage.items():
                    if info.get("type") == "CPU":
                        for date_str, temps in info.get("history", {}).items():
                            log_date = datetime.fromisoformat(date_str).date()
                            if log_date in stats_map:
                                stats_map[log_date].extend(temps)

                graph_data = [
                    (
                        day.strftime("%m/%d"),
                        round(sum(v)/len(v), 1) if v else 0,
                        ""
                    )
                    for day, v in stats_map.items()
                ]

            case -5: 
                self.graphlabel = "Recent GPU Temperatures - Last 7 Days"
                self.x_label = "Date"
                self.y_label = "°C"

                now_dt = datetime.now().date()
                stats_map = {now_dt - timedelta(days=i): [] for i in range(6, -1, -1)}

                for name, info in self.data.hardware_usage.items():
                    if info.get("type") == "GPU":
                        for date_str, temps in info.get("history", {}).items():
                            log_date = datetime.fromisoformat(date_str).date()
                            if log_date in stats_map:
                                stats_map[log_date].extend(temps)

                graph_data = [
                    (
                        day.strftime("%m/%d"),
                        round(sum(v)/len(v), 1) if v else 0,
                        ""
                    )
                    for day, v in stats_map.items()
                ]
        
            #debug only
            case _:
                self.graphlabel = "???"
                print("Menu Programming error") #debug only
                self.menu.pack(fill="both", expand=True, anchor="n")
                return

        self.title(f"FPSVR Data Analyzer - {self.graphlabel}")

        if value > 0:
            self.graph_view = GraphUI(
                master=self.container, 
                headers=headers, 
                data=data, 
                on_back=self.show_menu,
                label=self.graphlabel
            )
        elif value < 0:
            self.graph_view = LineGraphUI(
                master=self.container,
                x_label=self.x_label,
                y_label=self.y_label,
                data_points=graph_data,
                title=self.graphlabel,
                on_back=self.show_menu
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
        total_sec = sum(game["duration"] for game in self.data.game_time.values() if isinstance(game, dict))
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
            full_name = max(self.data.game_time.items(), key=lambda x: x[1]['duration'] if isinstance(x[1], dict) else 0)[0]
            top_game = App.truncate_text(full_name, 45)
            
            fps_info = self.data.game_fps.get(full_name, {"total_fps": 0, "total_time": 1})
            top_game_fps = f"{fps_info['total_fps'] / fps_info['total_time']:.1f}"
        else:
            top_game = "N/A"
            top_game_fps = "0"

        record = self.data.longest_session
        max_dur = App.format_duration(record["duration"])
        max_game = App.truncate_text(record["app"], 20)
        max_date = record["date"]

        longest_display = f"{max_dur} on {max_game}\n({max_date})"

        hours = self.data.session_hours
        days = self.data.session_days
        total_sessions = len(hours)

        if total_sessions < 5:
            return {"player_profile": "Data Gathering..."}

        counts = Counter(hours)
        peak_h = counts.most_common(1)[0][0]
        
        def f_ampm(h):
            return f"{12 if h%12==0 else h%12}{'AM' if h%24<12 else 'PM'}"
        
        time_slot = f"{f_ampm(peak_h)}-{f_ampm(peak_h+3)}"

        unique_days = len(set(days))
        wknd_ratio = sum(1 for d in days if d >= 5) / total_sessions
        night_ratio = sum(1 for h in hours if h >= 22 or h <= 4) / total_sessions
        morning_ratio = sum(1 for h in hours if 5 <= h <= 10) / total_sessions

        std_dev = statistics.stdev(hours) if total_sessions > 1 else 10

        if total_sessions > 1000 and unique_days >= 6:
            arch = "Legendary Addict"
        elif night_ratio > 0.6:
            arch = "Vampire Dweller"
        elif morning_ratio > 0.5:
            arch = "Early Bird"
        elif wknd_ratio > 0.75:
            arch = "Weekend Smasher"
        elif wknd_ratio < 0.15:
            arch = "Professional Grinder"
        elif 0.4 <= wknd_ratio <= 0.6:
            arch = "Social Nomad"
        else:
            arch = "Casual Wanderer"

        if std_dev < 2.5:
            trait = "Clockwork"
        elif std_dev > 6:
            trait = "Chaos"
        else:
            trait = "Steady"

        intensity = "High" if total_sessions / unique_days > 5 else "Light"
        
        profile_str = f"{arch}\n{time_slot} | {trait} ({intensity})"

        significant_durations = [d for d in self.data.all_session_durations if d > 900]
        
        if significant_durations:
            avg_sec = sum(significant_durations) / len(significant_durations)
            typical_sec = statistics.median(significant_durations)
            
            avg_disp = App.format_duration(avg_sec)
            typical_disp = App.format_duration(typical_sec)
            
            endurance_str = f"Avg: {avg_disp}\nTypical: {typical_disp}"
        else:
            endurance_str = "No Long Sessions"

        return {
            "total_sessions": sessions_time_display,
            "top_hmd": top_hmd,
            "top_game": f"{top_game}\n{top_game_fps} FPS avg",
            "longest_session_display": longest_display,
            "player_profile": profile_str,
            "endurance": endurance_str
        }
    
    def check_updates_async(self):
        t = threading.Thread(target=self._fetch_github_version, daemon=True)
        t.start()

    def _fetch_github_version(self):

        url = f"https://api.github.com/repos/nicolas-riera/FPSVR_data_analyzer/releases/latest"

        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                latest_tag = data['tag_name']
                
                remote_v = latest_tag.lstrip('v')
                local_v = str(self.version).lstrip('v')

                if remote_v > local_v:
                    new_text = f"v{self.version} (Update v{latest_tag} available!)"
                    self.after(0, lambda: self.version_label.configure(text=new_text, text_color="#FFCC00"))
                    self.after(0, lambda: self.show_update_popup(latest_tag, data['html_url']))
                elif remote_v < local_v: # debug only
                    print(f"Remote version : {remote_v}")
                    print(f"Local version : {local_v}")
        except Exception as e:
            print(f"Update check failed: {e}") # debug only

    def show_update_popup(self, new_version, url):

        if winsound:
            try:
                winsound.PlaySound("SystemAsterisk", winsound.SND_ALIAS | winsound.SND_ASYNC)
            except Exception:
                pass

        title = "Update Available"
        message = f"A new version ({new_version}) is available!\n\nWould you like to open the download page?"
        
        if messagebox.askyesno(title, message):
            webbrowser.open(url)