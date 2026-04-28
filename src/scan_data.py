import os
import json
from datetime import datetime
import time
import hashlib

from src.get_folder_path import HISTORY_DIR
from src.cache_path import get_cache_path

class ProcessFiles:
    def __init__(self, version=None, progress_callback=None):

        self.cache_manager("c")
        
        self.cache_manager("r")

        self.version = version
        self.progress_callback = progress_callback

    def run(self):
        self.total_files = len([os.path.join(r, f) for r, _, files in os.walk(HISTORY_DIR) for f in files if f.endswith(".json")])

        if self.total_files == 0:
            if self.progress_callback:
                progress = 0
                self.progress_callback(progress, None, -1)
                return
            
        try :
            if self.total_files < len(self.file_cache) or self.version != self.cache_version: # avoid cache mismatch
                self.cache_manager(mode="cls")
        except:
            self.cache_manager(mode="cls")

        self.progress_file_count = 0

        for root, dirs, files in os.walk(HISTORY_DIR):

            for file in files:
                path = os.path.join(root, file)

                file_hash = self.get_file_hash(path)
                if path in self.file_cache and self.file_cache[path] == file_hash:
                    self.progress_file_count += 1
                    if self.total_files >= 10 :
                        if self.progress_callback and self.progress_file_count % (self.total_files // 10) == 0:
                            progress = self.progress_file_count / self.total_files
                            self.progress_callback(progress, self.progress_file_count, self.total_files)
                    else:
                        progress = self.progress_file_count / self.total_files
                        self.progress_callback(progress, self.progress_file_count, self.total_files)
                    continue

                if file.endswith(".json"):
                    with open(path, "r", encoding="utf8") as f:
                        data = json.load(f)

                        if isinstance(data, dict) and "hmd" in data and "DateStart" in data and "DateEnd" in data and "app" in data:
                            start = datetime.fromisoformat(data["DateStart"])
                            end = datetime.fromisoformat(data["DateEnd"])
                            session_date = start.strftime("%Y-%m-%d")
                            session_month = start.strftime("%Y-%m")

                            bx = data.get("baseX", 0)
                            by = data.get("baseY", 0)

                            duration = self.processhmd(data["hmd"], start, end, bx, by)

                            if session_month not in self.monthly_sessions:
                                self.monthly_sessions[session_month] = []
                            self.monthly_sessions[session_month].append(duration)

                            self.all_session_durations.append(duration)
                            self.session_hours.append(start.hour)
                            self.session_days.append(start.weekday())

                            if duration > self.longest_session["duration"]:
                                self.longest_session = {
                                    "duration": duration,
                                    "app": data["app"],
                                    "date": start.strftime("%Y-%m-%d")
                                }

                            app = data["app"]
                            current_date = start.strftime("%Y-%m-%d")

                            if app not in self.game_time:
                                self.game_time[app] = {
                                    "duration": duration,
                                    "history": {current_date: duration}
                                }
                            else:
                                if isinstance(self.game_time[app], (int, float)):
                                    self.game_time[app] = {
                                        "duration": self.game_time[app] + duration,
                                        "history": {current_date: duration}
                                    }
                                else:
                                    self.game_time[app]["duration"] += duration
                                    self.game_time[app]["history"][current_date] = self.game_time[app]["history"].get(current_date, 0) + duration

                            current_session_date_str = data["DateStart"] 

                            if not self.last_session or current_session_date_str > self.last_session.get("date", ""):
                                self.last_session = {
                                    "app": app,
                                    "date": current_session_date_str, 
                                }

                            if "framesused" in data and "stime" in data and data["stime"] > 0:
                                fps_session = data["framesused"] / data["stime"]
                                if app in self.game_fps:
                                    self.game_fps[app]["total_fps"] += fps_session * duration
                                    self.game_fps[app]["total_time"] += duration
                                else:
                                    self.game_fps[app] = {"total_fps": fps_session * duration, "total_time": duration}

                            if "cpu" in data:
                                cpu_name = data["cpu"].strip()
                                if cpu_name not in self.hardware_usage:
                                    self.hardware_usage[cpu_name] = {"type": "CPU", "time": 0, "temps": [], "history": {}}
                                
                                self.hardware_usage[cpu_name]["time"] += duration
                                
                                if session_date not in self.hardware_usage[cpu_name]["history"]:
                                    self.hardware_usage[cpu_name]["history"][session_date] = []

                                for key in ["CPU_Tavg", "CPU_Tmax"]:
                                    if key in data and data[key] <= 120:
                                        val = data[key]
                                        self.hardware_usage[cpu_name]["temps"].append(val)
                                        self.hardware_usage[cpu_name]["history"][session_date].append(val)

                            if "gpuSpeedVendor" in data:
                                gpu_name = data["gpuSpeedVendor"].strip()
                                if gpu_name not in self.hardware_usage:
                                    self.hardware_usage[gpu_name] = {"type": "GPU", "time": 0, "temps": [], "history": {}}
                                
                                self.hardware_usage[gpu_name]["time"] += duration
                                
                                if session_date not in self.hardware_usage[gpu_name]["history"]:
                                    self.hardware_usage[gpu_name]["history"][session_date] = []

                                for key in ["GPU_Tavg", "GPU_Tmax"]:
                                    if key in data and data[key] <= 120:
                                        val = data[key]
                                        self.hardware_usage[gpu_name]["temps"].append(val)
                                        self.hardware_usage[gpu_name]["history"][session_date].append(val)

                            if "SteamVR" in data:
                                version = str(data["SteamVR"])
                                hmd = data["hmd"]
                                duration = (end - start).total_seconds()
                                current_date = start.strftime("%Y-%m-%d") 

                                if version not in self.steamvr_usage:
                                    self.steamvr_usage[version] = {}
                                
                                if hmd not in self.steamvr_usage[version]:
                                    self.steamvr_usage[version][hmd] = {
                                        "duration": duration,
                                        "first_seen": current_date,
                                        "last_seen": current_date
                                    }
                                else:
                                    entry = self.steamvr_usage[version][hmd]
                                    entry["duration"] += duration
                                    if current_date < entry["first_seen"]: entry["first_seen"] = current_date
                                    if current_date > entry["last_seen"]: entry["last_seen"] = current_date

                            if "TrackingSystem" in data:
                                tracking = data["TrackingSystem"]
                                self.tracking_usage[tracking] = self.tracking_usage.get(tracking, 0) + duration

                            if "OS" in data:
                                os_name = data["OS"]
                                current_date = start.strftime("%Y-%m-%d")

                                if os_name not in self.os_usage:
                                    self.os_usage[os_name] = {
                                        "duration": 0,
                                        "first_seen": current_date,
                                        "last_seen": current_date
                                    }
                                
                                entry = self.os_usage[os_name]
                                entry["duration"] += duration
                                if current_date < entry["first_seen"]: entry["first_seen"] = current_date
                                if current_date > entry["last_seen"]: entry["last_seen"] = current_date

                            if "hz" in data:
                                hz_val = str(data["hz"])
                                self.hz_usage[hz_val] = self.hz_usage.get(hz_val, 0) + duration

                    self.file_cache[path] = file_hash
                    self.progress_file_count += 1

                    if self.progress_callback:
                        progress = self.progress_file_count / self.total_files
                        self.progress_callback(progress, self.progress_file_count, self.total_files)

                time.sleep(0.0001) # so CPU can be free for CTK

        if self.progress_callback:
            if self.total_files != 0 :
                progress = self.progress_file_count / self.total_files      
            else :
                progress = 0
            self.progress_callback(progress, self.progress_file_count, self.total_files)

        self.cache_manager("w") 

        # print(f"""
        # hmd_usage: {self.hmd_usage}
        # game_time: {self.game_time}
        # game_fps: {self.game_fps}
        # cpu_temps_dict: {self.cpu_temps_dict}
        # gpu_temps_dict: {self.gpu_temps_dict}
        # hardware_usage: {self.hardware_usage}
        # steamvr_usage: {self.steamvr_usage}
        # tracking_usage: {self.tracking_usage}
        # os_usage: {self.os_usage}
        # hz_usage: {self.hz_usage}
        # """) # debug only
    
    def cache_manager(self, mode):
        path = get_cache_path("cache.json")
        match mode:
            case "c":
                if not os.path.exists(path):
                    os.makedirs(os.path.dirname(path), exist_ok=True)
                    with open(path, "w", encoding="utf-8") as f:
                        json.dump({}, f)
            
            case "r":
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        cache = json.load(f)

                    self.cache_version = cache.get("version", {})
                    self.file_cache = cache.get("files", {}) 
                    self.all_session_durations = cache.get("all_session_durations", [])
                    self.monthly_sessions = cache.get("monthly_sessions", {}) 
                    self.session_hours = cache.get("session_hours", [])
                    self.session_days = cache.get("session_days", [])
                    self.last_session = cache.get("last_session", {})
                    self.hmd_usage = cache.get("hmd_usage", {})
                    self.game_time = cache.get("game_time", {})
                    self.game_fps = cache.get("game_fps", {})
                    self.longest_session = cache.get("longest_session", {"duration": 0, "app": "N/A", "date": "N/A"})
                    self.cpu_temps_dict = cache.get("cpu_temps_dict", {})
                    self.gpu_temps_dict = cache.get("gpu_temps_dict", {})
                    self.hardware_usage = cache.get("hardware_usage", {})
                    self.steamvr_usage = cache.get("steamvr_usage", {})
                    self.tracking_usage = cache.get("tracking_usage", {})
                    self.os_usage = cache.get("os_usage", {})
                    self.hz_usage = cache.get("hz_usage", {})

                except json.JSONDecodeError:
                    print("Exception : Cache Error ; Recreating new cache.") # Debug only
                    with open(path, "w", encoding="utf-8") as f:
                        json.dump({}, f)

            case "w":
                cache = {
                    "version": self.version,
                    "files": self.file_cache,
                    "last_session": self.last_session,
                    "all_session_durations": self.all_session_durations,
                    "monthly_sessions": self.monthly_sessions,
                    "session_hours": self.session_hours,
                    "session_days": self.session_days,
                    "hmd_usage": self.hmd_usage,
                    "game_time": self.game_time,
                    "game_fps": self.game_fps,
                    "longest_session": self.longest_session,
                    "cpu_temps_dict": self.cpu_temps_dict,
                    "gpu_temps_dict": self.gpu_temps_dict,
                    "hardware_usage": self.hardware_usage,
                    "steamvr_usage": self.steamvr_usage,
                    "tracking_usage": self.tracking_usage,
                    "os_usage": self.os_usage,
                    "hz_usage": self.hz_usage
                }

                with open(path, "w", encoding="utf8") as f:
                    json.dump(cache, f, indent=4)  

            case "cls":
                if not os.path.exists(path):
                    os.makedirs(os.path.dirname(path), exist_ok=True)
                with open(path, "w", encoding="utf-8") as f:
                    json.dump({}, f)
                self.cache_manager(mode="r")
            case _:
                print("Cache programming error.") #debug only   

    def get_file_hash(self, path):
        h = hashlib.sha256()

        with open(path, "rb") as f:
            while chunk := f.read(8192):
                h.update(chunk)

        return h.hexdigest()
    
    def processhmd(self, hmd, start, end, bx=0, by=0):
        duration = (end - start).total_seconds()
        current_date = start.strftime("%Y-%m-%d")
        res_key = f"{bx}x{by}" if bx > 0 and by > 0 else None

        if hmd not in self.hmd_usage:
            self.hmd_usage[hmd] = {
                "duration": duration,
                "first_seen": current_date,
                "last_seen": current_date,
                "resolutions": {res_key: 1} if res_key else {}, 
                "history": {current_date: duration}
            }
        else:
            entry = self.hmd_usage[hmd]
            if isinstance(entry, dict):
                entry["duration"] += duration
                if current_date < entry["first_seen"]: entry["first_seen"] = current_date
                if current_date > entry["last_seen"]: entry["last_seen"] = current_date
                
                if res_key:
                    if "resolutions" not in entry:
                        entry["resolutions"] = {}
                    entry["resolutions"][res_key] = entry["resolutions"].get(res_key, 0) + 1

                if "history" not in entry:
                    entry["history"] = {}

                entry["history"][current_date] = (
                    entry["history"].get(current_date, 0) + duration
                )
            else:
                self.hmd_usage[hmd] = {
                    "duration": entry + duration,
                    "first_seen": current_date,
                    "last_seen": current_date,
                    "resolutions": {res_key: 1} if res_key else {},
                    "history": {current_date: duration}
                }
                
        return duration
