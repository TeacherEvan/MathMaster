import tkinter as tk
import math
import random
import logging

class BrainAnimation:
    def __init__(self, canvas):
        self.canvas = canvas
        self.brain_size = 0.8  # Size multiplier
        self.brain_pulse_step = 0  # For pulsing animation
        self.brain_pulse_direction = 1  # Increasing = 1, decreasing = -1

    def update_animation(self):
        """Update the pulsing brain animation"""
        try:
            # Delete previous brain
            self.canvas.delete("brain")
            
            # Update pulse step
            self.brain_pulse_step += 0.1 * self.brain_pulse_direction
            
            # Reverse direction if reaching limits
            if self.brain_pulse_step >= 1.0:
                self.brain_pulse_direction = -1
            elif self.brain_pulse_step <= 0.0:
                self.brain_pulse_direction = 1
                
            # Redraw brain with new size
            self.draw_brain()
        except Exception as e:
            if self.canvas.winfo_exists():
                logging.error(f"Brain animation error: {e}")

    def draw_brain(self):
        """Draw a stylized "muscular, veiny brain" using tkinter canvas"""
        try:
            width = self.canvas.winfo_width()
            height = self.canvas.winfo_height()
            
            # Center coordinates
            center_x = width // 2
            center_y = height // 2 + 20  # Move slightly below center
            
            # Calculate brain size based on window
            max_size = min(width, height) * 0.3
            # Apply pulse effect (vary size by ±5%)
            pulse_factor = 1.0 + (self.brain_pulse_step * 0.1)  # 0-10% size variation
            size = max_size * self.brain_size * pulse_factor
            
            # Brain base color
            brain_color = "#FF7777"  # Pinkish red
            vein_color = "#7777FF"   # Bluish for veins
            
            # Draw brain hemispheres (left and right)
            # Left hemisphere
            left_x = center_x - size // 3
            self.canvas.create_oval(
                left_x - size//2, center_y - size//2,
                left_x + size//2, center_y + size//2,
                fill=brain_color, outline="#DD5555",
                width=2, tags="brain"
            )
            
            # Right hemisphere
            right_x = center_x + size // 3
            self.canvas.create_oval(
                right_x - size//2, center_y - size//2,
                right_x + size//2, center_y + size//2,
                fill=brain_color, outline="#DD5555",
                width=2, tags="brain"
            )
            
            # Draw some veins (wavy lines)
            for i in range(8):
                # Left hemisphere veins
                self.draw_vein(left_x, center_y, size//3, vein_color, i)
                # Right hemisphere veins
                self.draw_vein(right_x, center_y, size//3, vein_color, i+4)
                
            # Draw "muscular" bulges
            self.draw_brain_muscle(left_x, center_y, size//3, "#EE6666")
            self.draw_brain_muscle(right_x, center_y, size//3, "#EE6666")
                
            # Draw connecting part in the middle
            self.canvas.create_rectangle(
                center_x - size//3, center_y - size//4,
                center_x + size//3, center_y + size//4,
                fill=brain_color, outline="",
                tags="brain"
            )
            
            # Add a subtle glow effect
            for i in range(3, 0, -1):
                glow_alpha = 0.2 * i / 3
                glow_color = self._get_hex_with_alpha("#FFDDDD", glow_alpha)
                self.canvas.create_oval(
                    center_x - size * 0.8, center_y - size * 0.7,
                    center_x + size * 0.8, center_y + size * 0.7,
                    fill="", outline=glow_color,
                    width=i*2, tags="brain"
                )
        except Exception as e:
            if self.canvas.winfo_exists():
                logging.error(f"Error drawing brain: {e}")

    def draw_vein(self, center_x, center_y, size, color, seed):
        """Draw a single vein on the brain"""
        # Set random seed for consistent pattern
        random.seed(seed * 10)
        
        # Starting point
        x1 = center_x
        y1 = center_y
        
        # Create a wiggly line for the vein
        points = []
        for i in range(8):
            angle = random.uniform(0, 2 * math.pi)
            length = random.uniform(size * 0.1, size * 0.5)
            x2 = x1 + length * math.cos(angle)
            y2 = y1 + length * math.sin(angle)
            
            points.extend([x1, y1, x2, y2])
            x1, y1 = x2, y2
        
        # Draw the vein line
        self.canvas.create_line(
            points, fill=color, width=2,
            smooth=True, tags="brain"
        )

    def draw_brain_muscle(self, center_x, center_y, size, color):
        """Draw 'muscle bulges' on the brain to make it look strong"""
        for i in range(4):
            angle = i * math.pi / 2  # Evenly spaced around
            x = center_x + size * 0.7 * math.cos(angle)
            y = center_y + size * 0.7 * math.sin(angle)
            
            # Draw a small bulge
            self.canvas.create_oval(
                x - size * 0.25, y - size * 0.25,
                x + size * 0.25, y + size * 0.25,
                fill=color, outline="#CC5555",
                width=1, tags="brain"
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