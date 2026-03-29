import os
import json
from datetime import datetime
import time
import hashlib

from src.get_folder_path import HISTORY_DIR
from src.cache_path import get_cache_path

class ProcessFiles:
    def __init__(self, progress_callback=None):

        self.cache_manager("c")
        
        self.cache_manager("r")

        self.progress_callback = progress_callback

    def run(self):
        self.total_files = len([os.path.join(r, f) for r, _, files in os.walk(HISTORY_DIR) for f in files if f.endswith(".json")])

        if self.total_files == 0:
            if self.progress_callback:
                progress = 0
                self.progress_callback(progress, None, -1)
                return
            
        if self.total_files < len(self.file_cache): # avoid cache mismatch
            self.cache_manager(mode="cls")

        self.progress_file_count = 0

        for root, dirs, files in os.walk(HISTORY_DIR):

            for file in files:
                path = os.path.join(root, file)

                file_hash = self.get_file_hash(path)
                if path in self.file_cache and self.file_cache[path] == file_hash:
                    self.progress_file_count += 1
                    continue

                if file.endswith(".json"):
                    with open(path, "r", encoding="utf8") as f:
                        data = json.load(f)

                        if isinstance(data, dict) and "hmd" in data and "DateStart" in data and "DateEnd" in data and "app" in data:
                            start = datetime.fromisoformat(data["DateStart"])
                            end = datetime.fromisoformat(data["DateEnd"])
                            duration = self.processhmd(data["hmd"], start, end)

                            app = data["app"]
                            if app in self.game_time:
                                self.game_time[app] += duration
                            else:
                                self.game_time[app] = duration

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
                                    self.hardware_usage[cpu_name] = {"type": "CPU", "time": 0, "temps": []}
                                self.hardware_usage[cpu_name]["time"] += duration
                                for key in ["CPU_Tavg", "CPU_Tmax"]:
                                    if key in data and data[key] <= 120:
                                        self.hardware_usage[cpu_name]["temps"].append(data[key])

                            if "gpuSpeedVendor" in data:
                                gpu_name = data["gpuSpeedVendor"].strip()
                                if gpu_name not in self.hardware_usage:
                                    self.hardware_usage[gpu_name] = {"type": "GPU", "time": 0, "temps": []}
                                self.hardware_usage[gpu_name]["time"] += duration
                                for key in ["GPU_Tavg", "GPU_Tmax"]:
                                    if key in data and data[key] <= 120:
                                        self.hardware_usage[gpu_name]["temps"].append(data[key])

                            if "SteamVR" in data:
                                version = data["SteamVR"]
                                hmd = data["hmd"]
                                duration = (end - start).total_seconds()
                                if version not in self.steamvr_usage:
                                    self.steamvr_usage[version] = {}
                                if hmd in self.steamvr_usage[version]:
                                    self.steamvr_usage[version][hmd] += duration
                                else:
                                    self.steamvr_usage[version][hmd] = duration

                            if "TrackingSystem" in data:
                                tracking = data["TrackingSystem"]
                                self.tracking_usage[tracking] = self.tracking_usage.get(tracking, 0) + duration

                            if "OS" in data:
                                os_name = data["OS"]
                                self.os_usage[os_name] = self.os_usage.get(os_name, 0) + duration

                            if "hz" in data:
                                hz_val = data["hz"]
                                self.hz_usage[hz_val] = self.hz_usage.get(hz_val, 0) + duration

                    self.file_cache[path] = file_hash
                    self.progress_file_count += 1

                    if self.progress_callback:
                        progress = self.progress_file_count / self.total_files
                        self.progress_callback(progress, self.progress_file_count, self.total_files)

                time.sleep(0.0001) # so CPU can be free for CTK

        if self.progress_callback:
            progress = self.progress_file_count / self.total_files
            self.progress_callback(progress, self.progress_file_count, self.total_files)

        self.cache_manager("w") 

        print(f"""
        hmd_usage: {self.hmd_usage}
        game_time: {self.game_time}
        game_fps: {self.game_fps}
        cpu_temps_dict: {self.cpu_temps_dict}
        gpu_temps_dict: {self.gpu_temps_dict}
        hardware_usage: {self.hardware_usage}
        steamvr_usage: {self.steamvr_usage}
        tracking_usage: {self.tracking_usage}
        os_usage: {self.os_usage}
        hz_usage: {self.hz_usage}
        """) # debug only
    
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

                    self.file_cache = cache.get("files", {})
                    self.hmd_usage = cache.get("hmd_usage", {})
                    self.game_time = cache.get("game_time", {})
                    self.game_fps = cache.get("game_fps", {})
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
                    "files": self.file_cache,
                    "hmd_usage": self.hmd_usage,
                    "game_time": self.game_time,
                    "game_fps": self.game_fps,
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
    
    def processhmd(self, hmd, start, end):
        duration = (end - start).total_seconds()
        if hmd in self.hmd_usage:
            self.hmd_usage[hmd] += duration
        else:
            self.hmd_usage[hmd] = duration
        return duration
