import os
import json
from datetime import datetime
import ctypes
from ctypes import wintypes
from time import sleep

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
steamvr_usage = {}

print("\033[?25l", end="", flush=True)

os.system("cls")

print("Retriving and processing data...")

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
                        for key in ["CPU_Tavg", "CPU_Tmax"]:
                            if key in data and data[key] <= 120:
                                cpu_temps_dict.setdefault(cpu_name, []).append(data[key])

                    if "gpuSpeedVendor" in data:
                        gpu_name = data["gpuSpeedVendor"].strip()
                        for key in ["GPU_Tavg", "GPU_Tmax"]:
                            if key in data and data[key] <= 120:
                                gpu_temps_dict.setdefault(gpu_name, []).append(data[key])

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

            progress_file_count += 1

            bar_length = 40
            progress = progress_file_count / total_files
            filled_length = int(bar_length * progress)
            bar = "#" * filled_length + "-" * (bar_length - filled_length)
            print(f"\r|{bar}| {progress_file_count}/{total_files}", end="")

while 1:

    os.system("cls")

    if not hmd_usage and not game_time and not game_fps:
        print("Data not found...")
        sleep(3)
        break
    
    print("\033[?25h", end="", flush=True)
    
    usr_choice = input(
    "Which data do you want to see:\n"
    "1. VR headsets with time usage\n"
    "2. Game playtime and average FPS\n"
    "3. CPU/GPU temperatures by hardware\n"
    "4. SteamVR Version usage\n"
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
            headers = ["Hardware", "Type", "Average Temp (°C)", "Max Temp (°C)"]
            data_temps = []
            for name, temps in cpu_temps_dict.items():
                data_temps.append([name, "CPU", f"{sum(temps)/len(temps):.2f}", f"{max(temps):.2f}"])
            for name, temps in gpu_temps_dict.items():
                data_temps.append([name, "GPU", f"{sum(temps)/len(temps):.2f}", f"{max(temps):.2f}"])

            print("CPU/GPU Temperatures by hardware:")
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
        
        case "0":
            break
    
        case _:
            continue