import customtkinter as ctk
from CTkTable import CTkTable
import threading
import time

class GraphUI(ctk.CTkFrame):
    def __init__(self, master, headers, data, on_back, label):
        super().__init__(master, fg_color="#333333")
        
        self.grid_rowconfigure(0, weight=1)  
        self.grid_rowconfigure(1, weight=0)  
        self.grid_columnconfigure(0, weight=1)

        self.on_back_callback = on_back
        self.label = label
        self.headers = headers
        self.data = data

        self.progress = ctk.CTkProgressBar(self, width=300)
        self.progress.grid(row=0, column=0, padx=20, pady=20)
        self.progress.set(0)

        self.back_button = ctk.CTkButton(
            self, 
            text="Retour", 
            command=self.on_back_with_loading,
            width=140,
            height=30
        )
        self.back_button.grid(row=1, column=0, pady=20, sticky="s")

        threading.Thread(target=self.loading_process, daemon=True).start()

    def loading_process(self):
        total_steps = len(self.data)
        
        if total_steps > 0:
            for i in range(min(total_steps, 100)): # On limite le suivi à 100 paliers
                time.sleep(0.005) # Petit délai pour laisser l'UI respirer
                progress_value = (i + 1) / min(total_steps, 100)
                self.after(0, lambda v=progress_value: self.progress.set(v))

        self.after(10, self.display_final_table)

    def display_final_table(self):
        self.progress.grid_forget()
        self.show_table(self.headers, self.data)

    def show_table(self, headers, data):
        all_values = [headers] + data
        
        self.table_container = ctk.CTkScrollableFrame(self, label_text=self.label)
        self.table_container.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        self.table = CTkTable(
            master=self.table_container,
            values=all_values,
            header_color="#1f538d",
            hover_color="#4a4a4a"
        )
        self.table.pack(expand=True, fill="both")

    def on_back_with_loading(self):
        self.back_button.configure(state="disabled", text="...")

        if hasattr(self, 'table_container'):
            self.table_container.grid_forget()

        self.progress.grid(row=0, column=0, padx=20, pady=20)
        self.progress.configure(mode="indeterminate")
        self.progress.start()

        self.after(100, self.perform_final_back)

    def perform_final_back(self):
        self.progress.stop()
        self.on_back_callback()