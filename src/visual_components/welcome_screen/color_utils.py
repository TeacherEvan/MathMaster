import tkinter as tk

class ColorUtils:
    @staticmethod
    def get_hex_with_alpha(canvas, hex_color, alpha):
        """Convert a hex color and alpha value to a hex color"""
        # Extract RGB components
        r = int(hex_color[1:3], 16)
        g = int(hex_color[3:5], 16)
        b = int(hex_color[5:7], 16)
        
        # Apply alpha
        r = int(r * alpha + (1 - alpha) * canvas.winfo_rgb("#000000")[0]/256)
        g = int(g * alpha + (1 - alpha) * canvas.winfo_rgb("#000000")[1]/256)
        b = int(b * alpha + (1 - alpha) * canvas.winfo_rgb("#000000")[2]/256)
        
        # Convert back to hex
        return f"#{r:02x}{g:02x}{b:02x}" 