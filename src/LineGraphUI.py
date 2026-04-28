import customtkinter as ctk


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

        self.back_button = ctk.CTkButton(
            self,
            text="Back",
            command=self.on_back,
            width=120
        )
        self.back_button.pack(pady=15)

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

        for i, (date, hours, hmd) in enumerate(self.data_points):
            x = left_margin + i * spacing
            y = top_margin + graph_height - (hours / max_y) * graph_height
            coords.append((x, y, date, hours, hmd))

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

        for x, y, date, hours, hmd in coords:
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
                text=date,
                fill="white",
                font=("Arial", 10)
            )

            if hours > 0:
                if x > width - 120:
                    text_x = x - 15
                    anchor = "se"
                else:
                    text_x = x + 15
                    anchor = "sw"

                self.canvas.create_text(
                    text_x,
                    y - 20,
                    text=hmd,
                    fill="#00BFFF",
                    font=("Arial", 9, "italic"),
                    anchor=anchor
                )

                self.canvas.create_text(
                    text_x,
                    y - 5,
                    text=f"{hours:.2f}h",
                    fill="white",
                    font=("Arial", 10, "bold"),
                    anchor=anchor
                )