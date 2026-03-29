import os
import json
from datetime import datetime
import time

from src.get_folder_path import HISTORY_DIR

class ProcessFiles:
    def __init__(self, progress_callback=None):
        
        self.hmd_usage = {}
        self.game_time = {}
        self.game_fps = {}
        self.cpu_temps_dict = {}
        self.gpu_temps_dict = {}
        self.hardware_usage = {}
        self.steamvr_usage = {}
        self.tracking_usage = {}
        self.os_usage = {}
        self.hz_usage = {}

        self.progress_callback = progress_callback

    def run(self):
        self.total_files = len([os.path.join(r, f) for r, _, files in os.walk(HISTORY_DIR) for f in files if f.endswith(".json")])

        self.progress_file_count = 0

        for root, dirs, files in os.walk(HISTORY_DIR):

            for file in files:
                path = os.path.join(root, file)
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

                    self.progress_file_count += 1

                    if self.progress_callback:
                        progress = self.progress_file_count / self.total_files
                        self.progress_callback(progress, self.progress_file_count, self.total_files)

                time.sleep(0.0001) # so CPU can be free for CTK
                        
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
        """)
    
    
    def processhmd(self, hmd, start, end):
        duration = (end - start).total_seconds()
        if hmd in self.hmd_usage:
            self.hmd_usage[hmd] += duration
        else:
            self.hmd_usage[hmd] = duration
        return duration

    @staticmethod
    def format_duration(seconds):
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        return f"{hours}h {minutes}m {secs}s"



