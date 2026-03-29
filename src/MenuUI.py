import customtkinter as ctk


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
        self.subtitle.pack(pady=(0, 25))

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
            text="Refresh Data",
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