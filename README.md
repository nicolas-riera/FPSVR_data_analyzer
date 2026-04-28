# FPSVR Data Analyzer

![pythonversion](https://img.shields.io/badge/python-3.10+-blue)
![ctk](https://img.shields.io/badge/customtkinter-required-yellow)

```
  _____ ____  _______     ______     ____        _              
 |  ___|  _ \/ ___ \ \   / /  _ \   |  _ \  __ _| |_ __ _       
 | |_  | |_) \___ \ \ \ / /| |_) |  | | | |/ _` | __/ _` |      
 |  _| |  __/ ___) | \ V / |  _ <   | |_| | (_| | || (_| |      
 |_|   |_|   |____/   \_/  |_| \_\  |____/ \__,_|\__\__,_|      
                                                                
     _                _                      
    / \   _ __   __ _| |_   _ _______ _ __   
   / _ \ | '_ \ / _` | | | | |_  / _ \ '__|  
  / ___ \| | | | (_| | | |_| |/ /  __/ |     
 /_/   \_\_| |_|\__,_|_|\__, /___\___|_|     
                        |___/                
```

This is a Python utility for displaying aggregated FPSVR history data.  
It uses [CustomTkinter](https://github.com/tomschimansky/customtkinter) as its graphical interface framework.

## Features

This utility displays:

- Usage time per VR Headset, SteamVR Version, Tracking System, OS and Refresh Rate
- Game Playtime and Average FPS
- CPU/GPU Usage and Temperatures
- Recent Sessions Data

## Usage

Note : This tool assumes that you're on Windows. It has not been tested on Linux and may not even work.

Download the utility from the [releases](https://github.com/nicolas-riera/FPSVR_data_analyzer/releases/latest), extract it and then execute ```FPSVR Data Analyser.exe```.

## Run and Build from source

### Requirements
- Python **3.10+**
- PyInstaller
- CustomTkinter

Install dependencies with :

```bash
python -m pip install -r requirements.txt
```

### Run

From the root folder, run :

```bash
python main.py
```

### Build

To build the program (in .exe for Windows, in .app on MacOs, and as a binary file on Linux), you need first to get the location of customtkiner:

```bash
pip show customtkinter
```

Then, copy the location and paste it in this pyinstaller command :

```bash
pyinstaller main.py --onedir --add-data "{path_to_customtkinter}/customtkinter;customtkinter/" --add-data "img;img" --noconsole --name "FPSVR Data Analyzer" --icon=img/logo.ico
```
