import customtkinter as ctk
from CTkTable import CTkTable

class GraphUI(ctk.CTkFrame):
    def __init__(self, master, headers, data, on_back):
        super().__init__(master, fg_color="transparent")
        
        self.grid_rowconfigure(0, weight=1)  
        self.grid_rowconfigure(1, weight=0)  
        self.grid_columnconfigure(0, weight=1)

        self.on_back = on_back

        self.show_table(headers, data)

        self.btn_retour = ctk.CTkButton(
            self, 
            text="Retour", 
            command=self.on_back,
            width=120
        )
        self.btn_retour.grid(row=1, column=0, pady=20, sticky="s")

    def show_table(self, headers, data):
        all_values = [headers] + data
        
        self.table_container = ctk.CTkScrollableFrame(self)
        self.table_container.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        self.table = CTkTable(
            master=self.table_container,
            values=all_values,
            header_color="#1f538d",
            hover_color="#4a4a4a"
        )
        self.table.pack(expand=True, fill="both")
        