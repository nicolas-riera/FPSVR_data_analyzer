# Librairies

import os
import json
from datetime import datetime
import ctypes
from ctypes import wintypes
from time import sleep


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