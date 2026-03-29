# Important Note 
### This branch is here as a archival purpose, if you still want to use the older CLI version. It won't be updated and contributions on this branch won't be accepted.

---

# FPSVR Data Analyzer

![pythonversion](https://img.shields.io/badge/python-3.10+-blue)

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

This is a Python CLI utility for displaying aggregated FPSVR history data.

## Features

This utility displays:

- Usage time per VR Headset, SteamVR Version, Tracking System, OS and Refresh Rate
- Game Playtime and Average FPS
- CPU/GPU Usage and Temperatures

## Usage

Note : This tool assumes that you're on Windows. It has not been tested on Linux and may not even work.

Download the utility from the [releases](https://github.com/nicolas-riera/FPSVR_data_analyzer/releases/tag/1.1) and execute it.

You can navigate with numbers and by pressing on Enter.

## Run and Build from source

### Requirements
- Python **3.10+**
- PyInstaller -> ```python -m pip install pyinstaller```

### Run

From the root folder, run :

```bash
python vrstats.py
```

### Build

To build the game (in .exe for Windows, in .app on MacOs, and as a binary file on Linux), use pyinstaller :

```bash
pyinstaller vrstats.py --onefile --icon=img/logo.ico --name "FPSVR Data Analyzer" 
```


