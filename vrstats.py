# Librairies

import os
import json
from datetime import datetime
import ctypes
from ctypes import wintypes
from time import sleep

# Variables

art = r"""
  _____ ____  ______     ______     ____        _              
 |  ___|  _ \/ ___\ \   / /  _ \   |  _ \  __ _| |_ __ _       
 | |_  | |_) \___ \ \ \ / /| |_) |  | | | |/ _` | __/ _` |      
 |  _| |  __/ ___) | \ V / |  _ <   | |_| | (_| | || (_| |      
 |_|   |_|   |____/   \_/  |_| \_\  |____/ \__,_|\__\__,_|      
                                                                
     _                _                      
    / \   _ __   __ _| |_   _ _______ _ __   
   / _ \ | '_ \ / _` | | | | |_  / _ \ '__|  
  / ___ \| | | | (_| | | |_| |/ /  __/ |     
 /_/   \_\_| |_|\__,_|_|\__, /___\___|_|     
                        |___/                
"""

CSIDL_PERSONAL = 5  
SHGFP_TYPE_CURRENT = 0

buf = ctypes.create_unicode_buffer(wintypes.MAX_PATH)
ctypes.windll.shell32.SHGetFolderPathW(None, CSIDL_PERSONAL, None, SHGFP_TYPE_CURRENT, buf)

documents_path = buf.value
HISTORY_DIR = os.path.join(documents_path, "fpsVR", "History")

hmd_usage = {}
game_time = {}
game_fps = {}
cpu_temps_dict = {}
gpu_temps_dict = {}
hardware_usage = {}
steamvr_usage = {}
tracking_usage = {}
os_usage = {}
hz_usage = {}

# Functions

def processhmd(hmd, start, end):
    duration = (end - start).total_seconds()
    if hmd in hmd_usage:
        hmd_usage[hmd] += duration
    else:
        hmd_usage[hmd] = duration
    return duration

def format_duration(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    return f"{hours}h {minutes}m {secs}s"

def display_table(headers, data):
    col_widths = []
    for i in range(len(headers)):
        max_col = len(str(headers[i]))
        for row in data:
            max_col = max(max_col, len(str(row[i])))
        col_widths.append(max_col + 2)  

    def top_separator():
        print("┌" + "┬".join("─" * w for w in col_widths) + "┐")

    def middle_separator():
        print("├" + "┼".join("─" * w for w in col_widths) + "┤")

    def bottom_separator():
        print("└" + "┴".join("─" * w for w in col_widths) + "┘")

    top_separator()
    print("│" + "│".join(str(headers[i]).center(col_widths[i]) for i in range(len(headers))) + "│")
    middle_separator()

    for row in data:
        print("│" + "│".join(str(row[i]).center(col_widths[i]) for i in range(len(row))) + "│")

    bottom_separator()


# Main program

print("\033[?25l", end="", flush=True)
os.system("cls")
print(art)
sleep(1.5)

print("\nRetriving and processing data...")

total_files = len([os.path.join(r, f) for r, _, files in os.walk(HISTORY_DIR) for f in files if f.endswith(".json")])

progress_file_count = 0

for root, dirs, files in os.walk(HISTORY_DIR):

    for file in files:
        path = os.path.join(root, file)
        if file.endswith(".json"):
            with open(path, "r", encoding="utf8") as f:
                data = json.load(f)

                if isinstance(data, dict) and "hmd" in data and "DateStart" in data and "DateEnd" in data and "app" in data:
                    start = datetime.fromisoformat(data["DateStart"])
                    end = datetime.fromisoformat(data["DateEnd"])
                    duration = processhmd(data["hmd"], start, end)

                    app = data["app"]
                    if app in game_time:
                        game_time[app] += duration
                    else:
                        game_time[app] = duration

                    if "framesused" in data and "stime" in data and data["stime"] > 0:
                        fps_session = data["framesused"] / data["stime"]
                        if app in game_fps:
                            game_fps[app]["total_fps"] += fps_session * duration
                            game_fps[app]["total_time"] += duration
                        else:
                            game_fps[app] = {"total_fps": fps_session * duration, "total_time": duration}

                    if "cpu" in data:
                        cpu_name = data["cpu"].strip()
                        if cpu_name not in hardware_usage:
                            hardware_usage[cpu_name] = {"type": "CPU", "time": 0, "temps": []}
                        hardware_usage[cpu_name]["time"] += duration
                        for key in ["CPU_Tavg", "CPU_Tmax"]:
                            if key in data and data[key] <= 120:
                                hardware_usage[cpu_name]["temps"].append(data[key])

                    if "gpuSpeedVendor" in data:
                        gpu_name = data["gpuSpeedVendor"].strip()
                        if gpu_name not in hardware_usage:
                            hardware_usage[gpu_name] = {"type": "GPU", "time": 0, "temps": []}
                        hardware_usage[gpu_name]["time"] += duration
                        for key in ["GPU_Tavg", "GPU_Tmax"]:
                            if key in data and data[key] <= 120:
                                hardware_usage[gpu_name]["temps"].append(data[key])

                    if "SteamVR" in data:
                        version = data["SteamVR"]
                        hmd = data["hmd"]
                        duration = (end - start).total_seconds()
                        if version not in steamvr_usage:
                            steamvr_usage[version] = {}
                        if hmd in steamvr_usage[version]:
                            steamvr_usage[version][hmd] += duration
                        else:
                            steamvr_usage[version][hmd] = duration

                    if "TrackingSystem" in data:
                        tracking = data["TrackingSystem"]
                        tracking_usage[tracking] = tracking_usage.get(tracking, 0) + duration

                    if "OS" in data:
                        os_name = data["OS"]
                        os_usage[os_name] = os_usage.get(os_name, 0) + duration

                    if "hz" in data:
                        hz_val = data["hz"]
                        hz_usage[hz_val] = hz_usage.get(hz_val, 0) + duration

            progress_file_count += 1

            bar_length = 40
            progress = progress_file_count / total_files
            filled_length = int(bar_length * progress)
            bar = "#" * filled_length + "-" * (bar_length - filled_length)
            print(f"\r|{bar}| {progress_file_count}/{total_files}", end="")

# Menu loop

while 1:

    os.system("cls")

    if not hmd_usage and not game_time and not game_fps:
        print("Data not found...")
        sleep(3)
        break
    
    print("\033[?25h", end="", flush=True)
    
    usr_choice = input(
    "Which data do you want to see:\n"
    "1. Usage per VR Headset\n"
    "2. Game Playtime and Average FPS\n"
    "3. CPU/GPU Usage and Temperatures\n"
    "4. Usage by SteamVR Version\n"
    "5. Usage by Tracking System\n"
    "6. Usage by OS\n"
    "7. Usage by Refresh Rate\n"
    "0. Exit\n"
    )

    os.system("cls")

    print("\033[?25l", end="", flush=True)

    match usr_choice:
        case "1":
            headers = ["VR Headset", "Total Usage"]
            data = [[h, format_duration(t)] for h, t in hmd_usage.items()]

            print("VR headsets with time usage:")
            display_table(headers, data)
            input("\nPress Enter to go back")

        case "2":
            headers = ["Game", "Playtime", "Average FPS"]
            data = []

            for app, t in game_time.items():
                avg_fps = game_fps[app]["total_fps"] / game_fps[app]["total_time"] if app in game_fps else 0
                data.append([app, format_duration(t), f"{avg_fps:.2f}"])
            
            print("Game playtime and average FPS:")
            display_table(headers, data)
            input("\nPress Enter to go back")

        case "3":
            headers = ["Hardware", "Type", "Usage Time", "Average Temp (°C)", "Max Temp (°C)"]
            data_temps = []
            for name, info in hardware_usage.items():
                avg_temp = f"{sum(info['temps'])/len(info['temps']):.2f}" if info['temps'] else "N/A"
                max_temp = f"{max(info['temps']):.2f}" if info['temps'] else "N/A"
                usage_time = format_duration(info["time"])
                data_temps.append([name, info["type"], usage_time, avg_temp, max_temp])
            
            print("CPU/GPU Usage and Temperatures:")
            display_table(headers, data_temps)
            input("\nPress Enter to go back")

        case "4":
            headers = ["SteamVR Version", "Most Used HMD", "Usage Time"]
            data_versions = []

            for version, hmds in steamvr_usage.items():
                most_used_hmd = max(hmds, key=hmds.get)
                usage_time = format_duration(hmds[most_used_hmd])
                data_versions.append([version, most_used_hmd, usage_time])

            print("Most used VR headset per SteamVR version:")
            display_table(headers, data_versions)
            input("\nPress Enter to go back")

        case "5":
            headers = ["Tracking System", "Total Usage"]
            data_tracking = [[k, format_duration(v)] for k, v in tracking_usage.items()]

            print("Usage by Tracking System:")
            display_table(headers, data_tracking)
            input("\nPress Enter to go back")

        case "6":
            headers = ["Operating System", "Total Usage"]
            data_os = [[k, format_duration(v)] for k, v in os_usage.items()]

            print("Usage by Operating System:")
            display_table(headers, data_os)
            input("\nPress Enter to go back")

        case "7":
            headers = ["Refresh Rate (Hz)", "Total Usage"]
            data_hz = [[k, format_duration(v)] for k, v in hz_usage.items()]

            print("Usage by Refresh Rate (Hz):")
            display_table(headers, data_hz)
            input("\nPress Enter to go back")
        
        case "0":
            break
    
        case _:
            continue