import tkinter as tk

class TitleDisplay:
    def __init__(self, canvas):
        self.canvas = canvas

    def draw(self, width, height):
        """Draw title, subtitle, description and credits"""
        # Draw title with glow effect
        title_font_size = max(36, min(width // 15, 60))
        
        # Glow effect (multiple layers with decreasing opacity)
        for i in range(5, 0, -1):
            self.canvas.create_text(
                width // 2, height // 4,
                text="Math Master",
                font=("Courier New", title_font_size, "bold"),
                fill=self._get_hex_with_alpha("#00FF00", 0.1 * i),
                tags="title"
            )
        
        # Main title
        self.canvas.create_text(
            width // 2, height // 4,
            text="Math Master",
            font=("Courier New", title_font_size, "bold"),
            fill="#00FF00",
            tags="title"
        )
        
        # Draw subtitle
        subtitle_font_size = max(14, min(width // 35, 28))
        self.canvas.create_text(
            width // 2, height // 4 + title_font_size,
            text="Educational Mathematics Challenge",
            font=("Courier New", subtitle_font_size),
            fill="#CCFFCC",
            tags="subtitle"
        )
        
        # Draw brief description
        desc_font_size = max(10, min(width // 60, 16))
        self.canvas.create_text(
            width // 2, height // 4 + title_font_size + subtitle_font_size,
            text="Master algebra through interactive puzzles and challenges",
            font=("Courier New", desc_font_size),
            fill="#AAFFAA",
            tags="description"
        )
        
        # Credits
        credit_font_size = max(10, min(width // 70, 14))
        self.canvas.create_text(
            width // 2, height - 20,
            text="Created by Teacher Evan",
            font=("Courier New", credit_font_size, "italic"),
            fill="#00AA00"
        )

    def _get_hex_with_alpha(self, hex_color, alpha):
        """Convert a hex color and alpha value to a hex color"""
        # Extract RGB components
        r = int(hex_color[1:3], 16)
        g = int(hex_color[3:5], 16)
        b = int(hex_color[5:7], 16)
        
        # Apply alpha
        r = int(r * alpha + (1 - alpha) * self.canvas.winfo_rgb("#000000")[0]/256)
        g = int(g * alpha + (1 - alpha) * self.canvas.winfo_rgb("#000000")[1]/256)
        b = int(b * alpha + (1 - alpha) * self.canvas.winfo_rgb("#000000")[2]/256)
        
        # Convert back to hex
        return f"#{r:02x}{g:02x}{b:02x}" 