import customtkinter as ctk
from tkinter import ttk
import textwrap

class GraphUI(ctk.CTkFrame):
    def __init__(self, master, headers, data, on_back, label):
        super().__init__(master, fg_color="#333333")
        
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.on_back_callback = on_back
        self.headers = headers
        self.data = data

        style = ttk.Style()
        style.theme_use("default")
        
        style.layout("Treeview", [('Treeview.treearea', {'sticky': 'nswe'})])
        
        self.custom_row_height = 32
        
        style.configure("Treeview",
                        background="#2b2b2b",
                        foreground="#DCE4EE",
                        fieldbackground="#2b2b2b",
                        rowheight=self.custom_row_height,
                        borderwidth=0,
                        font=("Roboto", 10))

        style.configure("Treeview.Heading",
                        background="#1f538d",
                        foreground="white",
                        relief="flat",
                        padding=2,
                        font=("Roboto", 10, "bold"))

        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.grid(row=0, column=0, sticky="nsew", padx=15, pady=10)
        self.container.grid_columnconfigure(0, weight=1)
        self.container.grid_rowconfigure(1, weight=1)

        self.title_label = ctk.CTkLabel(self.container, text=label, font=("Roboto", 16, "bold"), anchor="center", text_color="white")
        self.title_label.grid(row=0, column=0, pady=(0, 10), sticky="ew")

        self.table_wrapper = ctk.CTkFrame(self.container, fg_color="#2b2b2b", corner_radius=10)
        self.table_wrapper.grid(row=1, column=0, sticky="nsew")
        self.table_wrapper.grid_columnconfigure(0, weight=1)
        self.table_wrapper.grid_rowconfigure(0, weight=1)

        self.tree = ttk.Treeview(self.table_wrapper, columns=headers, show='headings', selectmode="none")
        
        for i, col in enumerate(headers):
            self.tree.heading(col, text=col)
            if i == 0:
                width = 280
            else:
                width = 100
            self.tree.column(col, width=width, minwidth=width, anchor="center", stretch=True)

        self.tree.tag_configure("evenrow", background="#2b2b2b")
        self.tree.tag_configure("oddrow", background="#323232")

        for index, item in enumerate(self.data):
            processed_item = []
            for i, val in enumerate(item):
                val_str = str(val)
                if i == 0 and len(val_str) > 40:
                    val_str = "\n".join(textwrap.wrap(val_str, width=40))
                processed_item.append(val_str)
            
            tag = "evenrow" if index % 2 == 0 else "oddrow"
            self.tree.insert("", "end", values=processed_item, tags=(tag,))

        self.tree.bind("<Button-1>", lambda e: "break")
        self.tree.bind("<Motion>", lambda e: "break")

        self.v_scrollbar = ctk.CTkScrollbar(self.table_wrapper, orientation="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=self.v_scrollbar.set)
        
        self.tree.grid(row=0, column=0, sticky="nsew", padx=2, pady=2)
        self.v_scrollbar.grid(row=0, column=1, sticky="ns", padx=(0, 2), pady=2)

        self.back_button = ctk.CTkButton(self, text="Back", command=self.on_back_callback, width=120, height=28)
        self.back_button.grid(row=1, column=0, pady=15)

    def on_back_with_loading(self):
        self.on_back_callback()