import tkinter as tk
import random
import logging

class MathSymbols:
    def __init__(self, canvas, symbols):
        self.canvas = canvas
        self.symbols = symbols
        self.math_elements = []

    def create_elements(self, width, height):
        """Create math symbols in the background"""
        # Create math symbols if not already created
        if not self.math_elements:
            # Create symbols
            for _ in range(20):
                symbol = random.choice(self.symbols)
                x = random.randint(0, width)
                y = random.randint(0, height)
                size = random.randint(14, 36)
                speed_x = random.uniform(-1, 1)
                speed_y = random.uniform(-1, 1)
                opacity = random.uniform(0.1, 0.4)
                
                element = {
                    'text': symbol,
                    'x': x,
                    'y': y,
                    'size': size,
                    'speed_x': speed_x,
                    'speed_y': speed_y,
                    'opacity': opacity,
                    'id': None
                }
                
                self.math_elements.append(element)
        
        # Draw all math elements
        for element in self.math_elements:
            # Delete previous instance if exists
            if element['id'] is not None:
                self.canvas.delete(element['id'])
            
            # Draw new instance
            color = self._get_hex_with_alpha("#00FF00", element['opacity'])
            element['id'] = self.canvas.create_text(
                element['x'], element['y'],
                text=element['text'],
                font=("Courier New", element['size']),
                fill=color
            )

    def update_positions(self):
        """Update positions of math symbols"""
        if not self.math_elements:
            return
            
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        
        # Update positions
        for element in self.math_elements:
            if 'id' not in element or element['id'] is None:
                continue
                
            element['x'] += element['speed_x']
            element['y'] += element['speed_y']
            
            # Bounce off edges
            if element['x'] < 0 or element['x'] > width:
                element['speed_x'] *= -1
            if element['y'] < 0 or element['y'] > height:
                element['speed_y'] *= -1
            
            # Update position on canvas
            try:
                self.canvas.coords(element['id'], element['x'], element['y'])
            except:
                # Element may have been deleted, skip it
                pass

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