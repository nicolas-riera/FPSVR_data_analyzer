import customtkinter as ctk
from datetime import datetime, timezone

class MenuUI(ctk.CTkFrame):
    def __init__(self, master, on_select, on_refresh, **kwargs):
        super().__init__(master, **kwargs)

        self.on_select = on_select
        self.on_refresh = on_refresh

        self.buttons = []

        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.pack(expand=True)

        self.title = ctk.CTkLabel(
            self.container,
            text="FPSVR Data Analyzer",
            font=ctk.CTkFont(size=28, weight="bold")
        )
        self.title.pack(pady=(20, 5))

        self.subtitle = ctk.CTkLabel(
            self.container,
            text="Which data do you want to see?",
            font=ctk.CTkFont(size=16)
        )
        self.subtitle.pack(pady=(0, 0))

        self.last_played_label = ctk.CTkLabel(
            self.container,
            text="...", 
            font=ctk.CTkFont(size=12, slant="italic"),
            text_color="#aaaaaa"
        )
        self.last_played_label.pack(pady=(0, 0))

        self.highlights_frame = ctk.CTkFrame(self.container, fg_color="transparent")
        self.highlights_frame.pack(pady=10, fill="x")

        self.stat_blocks = []
        for i in range(3):
            block = ctk.CTkFrame(self.highlights_frame, fg_color="#2b2b2b", corner_radius=10, height=100)
            block.grid(row=0, column=i, padx=5, sticky="nsew")
            
            block.pack_propagate(False) 

            label = ctk.CTkLabel(
                block, 
                text="...", 
                font=ctk.CTkFont(size=11, weight="bold"), 
                text_color="#888888"
            )
            label.pack(pady=(12, 0), fill="x") 
            
            value = ctk.CTkLabel(
                block, 
                text="---", 
                font=ctk.CTkFont(size=12, weight="bold"),
                wraplength=220, 
                justify="center"
            )
            value.pack(pady=(0, 5), padx=10, fill="both", expand=True)
            
            self.stat_blocks.append({"label": label, "value": value})

        self.btn_frame = ctk.CTkFrame(self.container, fg_color="transparent")
        self.btn_frame.pack(pady=10)

        menu_items = [
            ("VR Headset Usage", 1),
            ("Game Playtime & Avg FPS", 2),
            ("CPU / GPU Usage & Temps", 3),
            ("SteamVR Version Usage", 4),
            ("Tracking System Usage", 5),
            ("OS Usage", 6),
            ("Refresh Rate Usage", 7)
        ]

        for i, (text, value) in enumerate(menu_items):
            row = i // 2  
            col = i % 2 
            
            btn = ctk.CTkButton(
                self.btn_frame,
                text=text,
                width=240,       
                height=42,
                corner_radius=12,
                font=ctk.CTkFont(size=14),
                command=lambda v=value: self.on_select(v), 
                state="disabled"
            )
            btn.grid(row=row, column=col, padx=8, pady=6)
            self.buttons.append(btn)

        self.action_frame = ctk.CTkFrame(self.container, fg_color="transparent")
        self.action_frame.pack(pady=(25, 10))

        self.refresh_btn = ctk.CTkButton(
            self.action_frame,
            text="...",
            width=180,
            height=40,
            fg_color="#2a9d8f",
            hover_color="#21867a",
            corner_radius=10,
            command=self.on_refresh,
            state="disabled"
        )
        self.refresh_btn.pack(pady=5)

        self.exit_btn = ctk.CTkButton(
            self.action_frame,
            text="Exit",
            width=180,
            height=40,
            fg_color="#e63946",
            hover_color="#b02a37",
            corner_radius=10,
            command=master.quit
        )
        self.exit_btn.pack(pady=5)

        self.pack(fill="both", expand=True)

    def enable_buttons(self):
        for btn in self.buttons:
            btn.configure(state="normal")

    def disable_buttons(self):
        for btn in self.buttons:
            btn.configure(state="disabled")

    def update_last_played(self, last_session_dict):
        if last_session_dict and "app" in last_session_dict:
            app = last_session_dict["app"]
            date = last_session_dict["date"]
            self.last_played_label.configure(
                text=f"Last played: {app} - {MenuUI.get_relative_time(date)}."
            )
        elif last_session_dict == "Refreshing signal":
            self.last_played_label.configure(text="...")
        else:
            self.last_played_label.configure(text="No recent session found")

    def update_highlights(self, stats_dict):
        if stats_dict == "Refreshing signal":
            for i in range(3):
                self.stat_blocks[i]["label"].configure(text="...")
                self.stat_blocks[i]["value"].configure(text="---")
            return
        
        self.stat_blocks[0]["label"].configure(text="SESSIONS / TOTAL TIME")
        self.stat_blocks[0]["value"].configure(text=stats_dict['total_sessions'])

        self.stat_blocks[1]["label"].configure(text="MOST USED HEADSET")
        self.stat_blocks[1]["value"].configure(text=stats_dict['top_hmd'])

        self.stat_blocks[2]["label"].configure(text="TOP GAME & PERF")
        self.stat_blocks[2]["value"].configure(text=stats_dict['top_game'])

    def get_relative_time(date_str):
        if not date_str:
            return "Never"
        
        past = datetime.fromisoformat(date_str)
        
        if past.tzinfo is not None:
            now = datetime.now(timezone.utc)
            past = past.astimezone(timezone.utc)
        else:
            now = datetime.now()

        diff = now - past
        seconds = diff.total_seconds()
        
        if seconds < 60:
            return "Just now"
        elif seconds < 3600:
            minutes = int(seconds // 60)
            return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
        elif seconds < 86400:
            hours = int(seconds // 3600)
            return f"{hours} hour{'s' if hours > 1 else ''} ago"
        elif seconds < 604800:
            days = int(seconds // 86400)
            return f"{days} day{'s' if days > 1 else ''} ago"
        elif seconds < 2629746: 
            weeks = int(seconds // 604800)
            return f"{weeks} week{'s' if weeks > 1 else ''} ago"
        elif seconds < 31556952: 
            months = int(seconds // 2629746)
            return f"{months} month{'s' if months > 1 else ''} ago"
        else: 
            years = int(seconds // 31556952)
            return f"{years} year{'s' if years > 1 else ''} ago"
        