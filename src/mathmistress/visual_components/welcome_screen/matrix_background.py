import tkinter as tk
import random

class MatrixBackground:
    def __init__(self, canvas, math_problems):
        self.canvas = canvas
        self.math_problems = math_problems

    def draw(self, width, height):
        """Draw Matrix-style background with falling code and semi-transparent algebraic problems"""
        # Draw falling code (vertical lines of characters)
        for x in range(0, width, 30):
            # Determine line length and starting position
            line_length = random.randint(5, 20)
            start_y = random.randint(0, height)
            
            # Draw each character in the line
            for i in range(line_length):
                char = random.choice("01")
                y = (start_y + i * 20) % height
                alpha = 0.1 + (0.2 * random.random())
                color = self._get_hex_with_alpha("#00FF00", alpha)
                
                self.canvas.create_text(
                    x, y,
                    text=char,
                    font=("Courier New", 12),
                    fill=color
                )
        
        # Draw semi-transparent algebraic problems
        for problem in self.math_problems:
            x = random.randint(0, width)
            y = random.randint(0, height)
            size = random.randint(14, 24)
            
            self.canvas.create_text(
                x, y,
                text=problem,
                font=("Courier New", size),
                fill=self._get_hex_with_alpha("#00FF00", 0.2)
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