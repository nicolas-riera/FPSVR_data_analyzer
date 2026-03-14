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
    
    usr_choice = input("Which data do you want to see:\n1. VR headsets with time usage\n2. Game playtime and average FPS\n0. Exit\n")

    os.system("cls")

    print("\033[?25l", end="", flush=True)

    match usr_choice:
        case "1":
            print("VR headsets with time usage:")
            for h, t in hmd_usage.items():
                print(f"- {h} : {format_duration(t)}")
            input("\nPress Enter to go back")
        case "2":
            print("Game playtime and average FPS:")
            for app, t in game_time.items():
                avg_fps = game_fps[app]["total_fps"] / game_fps[app]["total_time"] if app in game_fps else 0
                print(f"- {app} : {format_duration(t)} | FPS moyen : {avg_fps:.2f}")
            input("\nPress Enter to go back")
        
        case "0":
            break
    
        case _:
            continue