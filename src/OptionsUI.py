import customtkinter as ctk

class OptionsUI(ctk.CTkFrame):
    def __init__(self, master, callbacks, config, **kwargs):
        super().__init__(master, **kwargs)

        self.callbacks = callbacks
        self.config = config

        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.pack(expand=True, fill="both", padx=40, pady=40)

        self.title = ctk.CTkLabel(
            self.container,
            text="Options",
            font=ctk.CTkFont(size=28, weight="bold")
        )
        self.title.pack(pady=(0, 20), fill="x", anchor="center")

        self.temp_frame = ctk.CTkFrame(self.container, fg_color="#2b2b2b", corner_radius=12)
        self.temp_frame.pack(pady=10, fill="x")

        self.temp_label = ctk.CTkLabel(
            self.temp_frame,
            text="Temperature Unit",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#ffffff"
        )
        self.temp_label.pack(side="left", padx=20, pady=20)

        current_unit = self.config.get("temp_unit", "°C")

        self.temp_switch = ctk.CTkSegmentedButton(
            self.temp_frame,
            values=["°C", "°F"],
            font=ctk.CTkFont(size=14, weight="bold"),
            width=120,
            height=35,
            command=self.on_temp_unit_change
        )
        self.temp_switch.pack(side="right", padx=20, pady=20)
        self.temp_switch.set(current_unit)

        self.update_frame = ctk.CTkFrame(self.container, fg_color="#2b2b2b", corner_radius=12)
        self.update_frame.pack(pady=10, fill="x")

        self.update_label = ctk.CTkLabel(
            self.update_frame,
            text="Check for Updates on Startup",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#ffffff"
        )
        self.update_label.pack(side="left", padx=20, pady=20)

        current_update_setting = self.config.get("check_updates", True)

        self.update_switch = ctk.CTkSwitch(
            self.update_frame,
            text="",
            width=60,
            command=self.on_update_setting_change
        )
        self.update_switch.pack(side="right", padx=20, pady=20)
        
        if current_update_setting:
            self.update_switch.select()
        else:
            self.update_switch.deselect()

        self.action_frame = ctk.CTkFrame(self.container, fg_color="transparent")
        self.action_frame.pack(side="bottom", pady=(25, 0))

        self.back_btn = ctk.CTkButton(
            self.action_frame,
            text="Back",
            width=180,
            height=40,
            fg_color="#4f5d75",
            hover_color="#2d3748",
            corner_radius=10,
            command=self.callbacks.get("on_back")
        )
        self.back_btn.pack(side="left", padx=10)

        self.pack(fill="both", expand=True)

    def on_temp_unit_change(self, value):
        self.config["temp_unit"] = value
        if "on_unit_change" in self.callbacks:
            self.callbacks["on_unit_change"](value)

    def on_update_setting_change(self):
        value = bool(self.update_switch.get())
        self.config["check_updates"] = value
        if "on_update_setting_change" in self.callbacks:
            self.callbacks["on_update_setting_change"](value)