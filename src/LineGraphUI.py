import customtkinter as ctk
from tkinter import filedialog, messagebox
import datetime
import csv
import json
import os

class LineGraphUI(ctk.CTkFrame):
    def __init__(self, master, x_label, y_label, data_points, title, on_back):
        super().__init__(master)

        self.x_label = x_label
        self.y_label = y_label
        self.data_points = data_points
        self.title = title
        self.on_back = on_back

        self.configure(fg_color="#333333")

        self.title_label = ctk.CTkLabel(
            self,
            text=self.title,
            font=("Roboto", 16, "bold"), 
            text_color="white"
        )
        self.title_label.pack(pady=(20, 10))

        self.canvas_width = 760
        self.canvas_height = 600

        self.canvas_border = ctk.CTkFrame(
            self,
            corner_radius=10,
            fg_color="#2b2b2b"
        )
        self.canvas_border.pack(padx=20, pady=10)

        self.canvas = ctk.CTkCanvas(
            self.canvas_border,
            width=self.canvas_width,
            height=self.canvas_height,
            bg="#2b2b2b",
            highlightthickness=0,
            bd=0
        )

        self.canvas.pack(fill="both", expand=True, padx=5, pady=5)

        self.button_container = ctk.CTkFrame(self, fg_color="transparent")
        self.button_container.pack(pady=20)

        self.back_button = ctk.CTkButton(
            self.button_container,
            text="Back",
            command=self.on_back,
            width=120
        )
        self.back_button.pack(side="left", padx=10)

        self.export_button = ctk.CTkButton(
            self.button_container, 
            text="Export Data", 
            command=self.export_data, 
            width=120,
            fg_color="#2a9d8f",
            hover_color="#21867a"
        )
        self.export_button.pack(side="left", padx=10)

        self.draw_graph()

    def draw_graph(self):
        self.canvas.delete("all")

        width = self.canvas_width
        height = self.canvas_height

        left_margin = 70
        right_margin = 40
        top_margin = 50
        bottom_margin = 80

        graph_width = width - left_margin - right_margin
        graph_height = height - top_margin - bottom_margin

        self.canvas.create_line(
            left_margin,
            top_margin,
            left_margin,
            top_margin + graph_height,
            fill="gray",
            width=2
        )

        self.canvas.create_line(
            left_margin,
            top_margin + graph_height,
            left_margin + graph_width,
            top_margin + graph_height,
            fill="gray",
            width=2
        )

        values = [point[1] for point in self.data_points]
        raw_max_y = max(values) if values else 1

        if raw_max_y <= 1:
            max_y = 1
        elif raw_max_y <= 2:
            max_y = 2
        elif raw_max_y <= 5:
            max_y = 5
        elif raw_max_y <= 10:
            max_y = 10
        else:
            max_y = int(raw_max_y) + 1

        steps = 5

        for i in range(steps + 1):
            value = (max_y / steps) * i
            y = top_margin + graph_height - (value / max_y) * graph_height

            self.canvas.create_line(
                left_margin - 5,
                y,
                left_margin,
                y,
                fill="gray"
            )

            self.canvas.create_text(
                left_margin - 10,
                y,
                text=f"{int(value)}",
                fill="white",
                font=("Arial", 9),
                anchor="e"
            )

        self.canvas.create_text(
            width / 2,
            height - 25,
            text=self.x_label,
            fill="white",
            font=("Arial", 11, "bold")
        )

        self.canvas.create_text(
            25,
            height / 2,
            text=self.y_label,
            fill="white",
            font=("Arial", 11, "bold"),
            angle=90
        )

        num_points = len(self.data_points)
        spacing = graph_width / (num_points - 1) if num_points > 1 else graph_width

        coords = []

        for i, (label_x, value_y, detail) in enumerate(self.data_points):
            x = left_margin + i * spacing
            y = top_margin + graph_height - (value_y / max_y) * graph_height
            coords.append((x, y, label_x, value_y, detail))

        for i in range(len(coords) - 1):
            x1, y1, _, _, _ = coords[i]
            x2, y2, _, _, _ = coords[i + 1]

            self.canvas.create_line(
                x1,
                y1,
                x2,
                y2,
                fill="#00BFFF",
                width=2
            )

        for x, y, label_x, value_y, detail in coords:
            self.canvas.create_oval(
                x - 3,
                y - 3,
                x + 3,
                y + 3,
                fill="gold",
                outline="gold"
            )

            self.canvas.create_text(
                x,
                top_margin + graph_height + 20,
                text=label_x,
                fill="white",
                font=("Arial", 10)
            )

            if value_y > 0:
                if x > width - 120:
                    text_x = x - 15
                    anchor = "se"
                else:
                    text_x = x + 15
                    anchor = "sw"

                self.canvas.create_text(
                    text_x,
                    y - 20,
                    text=detail,
                    fill="#00BFFF",
                    font=("Arial", 9, "italic"),
                    anchor=anchor
                )

                unit = "h" if "Hours" in self.y_label else "°C" if "°C" in self.y_label else ""
                val_text = f"{value_y:.2f}{unit}" if unit else f"{value_y:.1f}"

                self.canvas.create_text(
                    text_x,
                    y - 5,
                    text=val_text,
                    fill="white",
                    font=("Arial", 10, "bold"),
                    anchor=anchor
                )

    def export_data(self):
        if not self.data_points:
            return

        clean_label = "".join([c for c in self.title if c.isalnum() or c in (' ', '_', '-')]).strip().replace(" ", "_")
        now = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        default_filename = f"Export_{clean_label}_{now}"

        file_path = filedialog.asksaveasfilename(
            initialfile=default_filename,
            defaultextension=".csv",
            filetypes=[("CSV File", "*.csv"), ("JSON File", "*.json")],
            title="Export Graph Data"
        )

        if not file_path:
            return

        try:
            headers = [self.x_label, self.y_label, "Details"]
            
            if file_path.endswith(".json"):
                export_list = [
                    {self.x_label: p[0], self.y_label: p[1], "Details": p[2]} 
                    for p in self.data_points
                ]
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(export_list, f, indent=4, ensure_ascii=False)
            
            else:
                with open(file_path, "w", newline="", encoding="utf-8-sig") as f:
                    writer = csv.writer(f, delimiter=";")
                    writer.writerow(headers)
                    writer.writerows(self.data_points)

            messagebox.showinfo("Export Successful", f"File saved:\n{os.path.basename(file_path)}")
        
        except Exception as e:
            messagebox.showerror("Export Error", f"An error occurred: {e}")