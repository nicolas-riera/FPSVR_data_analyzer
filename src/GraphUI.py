import customtkinter as ctk
from tkinter import ttk, filedialog, messagebox
import datetime
import csv
import json
import textwrap
import os

class GraphUI(ctk.CTkFrame):
    def __init__(self, master, headers, data, on_back, label):
        super().__init__(master, fg_color="#333333")
        
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.on_back_callback = on_back
        self.headers = headers
        self.data = data
        self.graphlabel = label

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
            elif "Usage Period" in col :
                width = 220
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

        self.bottom_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.bottom_frame.grid(row=1, column=0, pady=15)

        self.back_button = ctk.CTkButton(
            self.bottom_frame, 
            text="Back", 
            command=self.on_back_callback, 
            width=120, 
            height=28,
            fg_color="#444444",
            hover_color="#555555"
        )
        self.back_button.pack(side="left", padx=10)

        self.graph_btn = ctk.CTkButton(
            self.bottom_frame, 
            text="Show Graph", 
            command=self.toggle_graph_view, 
            width=100
        )
        self.graph_btn.pack(side="right", padx=10)

        self.export_button = ctk.CTkButton(
            self.bottom_frame, 
            text="Export", 
            command=self.export_data, 
            width=120, 
            height=28,
            fg_color="#2a9d8f",
            hover_color="#21867a"
        )
        self.export_button.pack(side="left", padx=10)

    def on_back_with_loading(self):
        self.on_back_callback()

    def export_data(self):
        if not self.data:
            return

        name_to_clean = self.graphlabel.replace("/", "_").replace("&", "and")
        
        clean_label = "".join([
            c for c in name_to_clean 
            if c.isalnum() or c in (' ', '_', '-')
        ]).strip()
        
        while "  " in clean_label:
            clean_label = clean_label.replace("  ", " ")

        now = datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S")
        default_filename = f"{clean_label}_{now}"

        file_path = filedialog.asksaveasfilename(
            initialfile=default_filename,
            defaultextension=".csv",
            filetypes=[("CSV File", "*.csv"), ("JSON File", "*.json")],
            title="Export Data"
        )

        if not file_path:
            return

        try:
            if file_path.endswith(".json"):
                export_dict = [dict(zip(self.headers, row)) for row in self.data]
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(export_dict, f, indent=4, ensure_ascii=False)
            
            else:
                with open(file_path, "w", newline="", encoding="utf-8-sig") as f:
                    writer = csv.writer(f, delimiter=";")
                    writer.writerow(self.headers)
                    writer.writerows(self.data)

            messagebox.showinfo("Export Successful", f"Data exported as {os.path.basename(file_path)}")
        
        except Exception as e:
            messagebox.showerror("Export Error", f"An error occurred: {e}")

    def toggle_graph_view(self):
        if hasattr(self, 'canvas_container') and self.canvas_container.winfo_manager():
            self.canvas_container.grid_forget()
            self.table_wrapper.grid(row=1, column=0, sticky="nsew") 
            self.graph_btn.configure(text="Show Graph")
        else:
            self.table_wrapper.grid_forget() 
            self.show_histogram() 
            self.graph_btn.configure(text="Show Table")

    def show_histogram(self):
        if hasattr(self, 'canvas_container'):
            self.canvas_container.grid(row=1, column=0, sticky="nsew")
        else:
            self.canvas_container = ctk.CTkFrame(self.container, fg_color="#2b2b2b", corner_radius=10)
            self.canvas_container.grid(row=1, column=0, sticky="nsew")
            self.canvas_container.grid_columnconfigure(0, weight=1)
            self.canvas_container.grid_rowconfigure(0, weight=1)

            self.canvas = ctk.CTkCanvas(self.canvas_container, bg="#2b2b2b", highlightthickness=0)
            self.scrollbar = ctk.CTkScrollbar(self.canvas_container, orientation="vertical", command=self.canvas.yview)
            self.canvas.configure(yscrollcommand=self.scrollbar.set)

            self.canvas.grid(row=0, column=0, sticky="nsew", padx=(2,0), pady=2)
            self.scrollbar.grid(row=0, column=1, sticky="ns", padx=(0,2), pady=2)

            self.canvas.bind("<MouseWheel>", self._on_mousewheel)
            self.canvas_container.bind("<MouseWheel>", self._on_mousewheel)
        
        self.after(100, self.draw_logic)

    def _on_mousewheel(self, event):
        try:
            if not self.canvas.winfo_exists():
                return
                
            sr = self.canvas.cget("scrollregion")
            if sr:
                _, _, _, total_h = map(int, sr.split())
                if total_h <= self.canvas.winfo_height():
                    return
            
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        except Exception:
            pass 

    def draw_logic(self):
        self.update()
        w = self.canvas.winfo_width()
        if not self.data or w < 50: return

        def parse_dur(v):
            s = str(v).lower().replace(',', '.')
            try:
                if 'h' in s:
                    pts = s.split('h')
                    return float(pts[0].strip()) + (float(pts[1].split('m')[0].strip())/60 if 'm' in pts[1] else 0)
                return float("".join(c for c in s if c.isdigit() or c in ".-"))
            except: return 0

        val_idx = 1
        priority = ["total usage", "playtime", "usage time", "usage %", "total"]
        for p in priority:
            for i, h in enumerate(self.headers):
                if p in h.lower():
                    val_idx = i
                    break
            else: continue
            break

        parsed = [{"l": str(r[0]), "rv": str(r[val_idx]), "nv": parse_dur(r[val_idx])} for r in self.data]
        parsed.sort(key=lambda x: x["nv"], reverse=True)

        line_height = 45 
        total_h = max(len(parsed) * line_height + 40, self.canvas.winfo_height())
        self.canvas.delete("all")
        self.canvas.configure(scrollregion=(0, 0, w, total_h))

        m_left, m_right = 180, 120
        draw_w = w - m_left - m_right
        max_v = max([x["nv"] for x in parsed]) if parsed and max([x["nv"] for x in parsed]) > 0 else 1

        PODIUM_COLORS = {
            0: "#FFD700",  
            1: "#C0C0C0", 
            2: "#CD7F32"  
        }

        LIGHT_BLUE = "#009FD4" 
        
        TEXT_WHITE = "#DCE4EE"

        for i, item in enumerate(parsed):
            y_mid = 30 + (i * line_height)
            bar_w = (item["nv"] / max_v) * draw_w if max_v > 0 else 0
            
            bar_color = PODIUM_COLORS.get(i, LIGHT_BLUE)
            
            y0, y1 = y_mid - 10, y_mid + 10
            self.canvas.create_rectangle(m_left, y0, m_left + bar_w, y1, 
                                       fill=bar_color, outline="")
            
            name_txt = item["l"] if len(item["l"]) < 25 else item["l"][:22] + "..."
            self.canvas.create_text(m_left - 10, y_mid, text=name_txt, fill=TEXT_WHITE, 
                                   anchor="e", font=("Roboto", 10))
            
            val_x = m_left + bar_w + 8
            if val_x > w - 10: val_x = w - 10
            
            self.canvas.create_text(val_x, y_mid, text=item["rv"], fill=bar_color, 
                                   anchor="w", font=("Roboto", 10, "bold"))