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
        self.last_played_label.pack(pady=(0, 20))

        self.btn_frame = ctk.CTkFrame(self.container, fg_color="transparent")
        self.btn_frame.pack()

        self.create_button("VR Headset Usage", 1)
        self.create_button("Game Playtime & Avg FPS", 2)
        self.create_button("CPU / GPU Usage & Temps", 3)
        self.create_button("SteamVR Version Usage", 4)
        self.create_button("Tracking System Usage", 5)
        self.create_button("OS Usage", 6)
        self.create_button("Refresh Rate Usage", 7)

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

    def create_button(self, text, value):
        btn = ctk.CTkButton(
            self.btn_frame,
            text=text,
            width=320,         
            height=42,         
            corner_radius=12,    
            font=ctk.CTkFont(size=14),
            command=lambda: self.on_select(value),
            state="disabled"
        )
        btn.pack(pady=6)
        self.buttons.append(btn)

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
        