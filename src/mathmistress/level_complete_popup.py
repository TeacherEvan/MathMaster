import tkinter as tk
from tkinter import ttk
import logging
import time
import math

class LevelCompletePopup:
    def __init__(self, parent):
        self.parent = parent
        self.popup_window = None
        self.animation_ids = []
        self.particles = []
        self.animation_running = False
        print("DEBUG: LevelCompletePopup initialized with parent:", parent)

    def show(self, title="Level Complete", subtitle="Congratulations!", callback_next=None, callback_level_select=None, width=450, height=300):
        print(f"DEBUG: LevelCompletePopup.show() called with title='{title}', subtitle='{subtitle}'")
        if self.popup_window and self.popup_window.winfo_exists():
            self.popup_window.lift()
            return self.popup_window

        self.popup_window = tk.Toplevel(self.parent)
        self.popup_window.title(title)
        self.popup_window.transient(self.parent) # Keep popup on top of parent
        self.popup_window.grab_set() # Modal behavior

        # Calculate position to center on parent
        parent_x = self.parent.winfo_x()
        parent_y = self.parent.winfo_y()
        parent_width = self.parent.winfo_width()
        parent_height = self.parent.winfo_height()
        
        x = parent_x + (parent_width - width) // 2
        y = parent_y + (parent_height - height) // 2
        self.popup_window.geometry(f"{width}x{height}+{x}+{y}")
        self.popup_window.resizable(False, False)
        print(f"DEBUG: Popup window created with dimensions {width}x{height} at position {x},{y}")

        # Matrix theme dark background
        self.popup_window.configure(bg="#000000")
        
        # Setup canvas for animations and content
        self.canvas = tk.Canvas(self.popup_window, bg="#000000", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Create matrix background effect
        self.create_matrix_background()
        
        # Style for buttons with matrix theme
        s = ttk.Style()
        s.configure('Matrix.TButton', 
                    font=('Courier New', 12, 'bold'), 
                    padding=10, 
                    borderwidth=1, 
                    foreground='#00FF00', 
                    background='#000000')
        
        s.map('Matrix.TButton',
              foreground=[('active', '#FFFFFF'), ('pressed', '#FFFFFF')],
              background=[('active', '#003300'), ('pressed', '#002200')])

        # Display title with glow effect
        self._create_title(title, width//2, height//4)
        
        # Display subtitle with fade-in effect
        if subtitle:
            self._create_subtitle(subtitle, width//2, height//2 - 20)
        
        # Create button frame
        button_frame = tk.Frame(self.popup_window, bg="#000000")
        button_frame.place(relx=0.5, rely=0.75, anchor='center', width=width-40)
        
        def on_next():
            logging.info("'Next Level' chosen from level complete popup.")
            print("DEBUG: Next Level button clicked")
            self._stop_animations()
            if callback_next:
                callback_next()
            self.close()

        def on_level_select():
            logging.info("'Level Select' chosen from level complete popup.")
            print("DEBUG: Level Select button clicked")
            self._stop_animations()
            if callback_level_select:
                callback_level_select()
            self.close()

        # Next level button with green glow
        next_button = ttk.Button(button_frame, text="Next Level", command=on_next, style='Matrix.TButton', width=15)
        next_button.pack(side=tk.LEFT, padx=10, expand=True)
        self._add_button_glow(next_button)

        # Level select button with blue glow
        level_select_button = ttk.Button(button_frame, text="Level Select", command=on_level_select, style='Matrix.TButton', width=15)
        level_select_button.pack(side=tk.RIGHT, padx=10, expand=True)
        self._add_button_glow(level_select_button)
        
        # Start particle animation
        self.animation_running = True
        self._animate_particles()
        
        self.popup_window.focus_set()
        self.popup_window.lift()
        self.popup_window.attributes("-topmost", True)
        self.popup_window.after(100, lambda: self.popup_window.attributes("-topmost", False))
        
        # Bind escape key
        self.popup_window.bind("<Escape>", lambda e: self.close())
        
        print("DEBUG: Popup window setup complete and returning")
        return self.popup_window
    
    def create_matrix_background(self):
        """Creates a Matrix-style raining code background"""
        # Create digital rain elements
        width = self.popup_window.winfo_width()
        height = self.popup_window.winfo_height()
        
        # Ensure we have valid dimensions (avoid division by zero)
        if width <= 1 or height <= 1:
            # Window not yet fully initialized
            self.popup_window.after(100, self.create_matrix_background)
            return
            
        for x in range(0, width, 15):
            # Random starting points and speeds
            y = -height if x % 30 == 0 else -20 * (x % 15)
            speed = 2 + (x % 5)
            color = "#00" + self._get_hex_value(150 + (x % 105)) + "00"  # Green variations
            
            char_id = self.canvas.create_text(
                x, y, 
                text=self._get_random_matrix_char(), 
                font=("Courier New", 10), 
                fill=color,
                tags="matrix_rain"
            )
            
            # Schedule animation
            self.popup_window.after(10 * (x % 20), lambda i=char_id, s=speed: self._animate_matrix_char(i, s))
    
    def _get_hex_value(self, value):
        """Convert a value 0-255 to hex string"""
        hex_val = hex(value)[2:]
        return hex_val.zfill(2)
    
    def _get_random_matrix_char(self):
        """Return a random character for the matrix rain effect"""
        import random
        chars = "0123456789MATRIX"
        return random.choice(chars)
    
    def _animate_matrix_char(self, char_id, speed):
        """Animate a single matrix character"""
        if not self.animation_running or not self.popup_window.winfo_exists():
            return
            
        # Move the character down
        self.canvas.move(char_id, 0, speed)
        
        # Get current position
        pos = self.canvas.coords(char_id)
        if not pos:
            return
            
        height = self.popup_window.winfo_height()
        
        # If character is off screen, reset it
        if pos[1] > height + 10:
            import random
            new_y = -20
            new_x = pos[0]
            self.canvas.coords(char_id, new_x, new_y)
            self.canvas.itemconfig(char_id, text=self._get_random_matrix_char())
        
        # Continue animation
        self.popup_window.after(50, lambda: self._animate_matrix_char(char_id, speed))
    
    def _create_title(self, title_text, x, y):
        """Create title with glow effect"""
        # Create layers for glow effect
        for i in range(3, 0, -1):
            glow_factor = i / 3
            offset = 2 * (3 - i)
            
            glow_id = self.canvas.create_text(
                x, y + offset,
                text=title_text,
                font=("Courier New", 24, "bold"),
                fill=f"#00{self._get_hex_value(int(255 * glow_factor))}00",
                tags="title_glow"
            )
            self.animation_ids.append(glow_id)
        
        # Main title text
        title_id = self.canvas.create_text(
            x, y,
            text=title_text,
            font=("Courier New", 24, "bold"),
            fill="#00FF00",
            tags="title"
        )
        self.animation_ids.append(title_id)
        
        # Animate title
        self._pulse_title()
    
    def _pulse_title(self):
        """Create a pulsing effect for the title"""
        if not self.animation_running or not self.popup_window.winfo_exists():
            return
            
        # Get all title elements
        title_ids = self.canvas.find_withtag("title")
        glow_ids = self.canvas.find_withtag("title_glow")
        
        # Calculate pulse factor based on time
        pulse = (math.sin(time.time() * 4) + 1) / 2  # Value between 0 and 1
        
        # Update main title
        for title_id in title_ids:
            green_val = int(200 + 55 * pulse)
            self.canvas.itemconfig(title_id, fill=f"#00{self._get_hex_value(green_val)}00")
        
        # Update glow
        for i, glow_id in enumerate(glow_ids):
            factor = (i+1) / len(glow_ids) * pulse
            green_val = int(100 + 155 * factor)
            self.canvas.itemconfig(glow_id, fill=f"#00{self._get_hex_value(green_val)}00")
        
        # Continue animation
        self.popup_window.after(50, self._pulse_title)
    
    def _create_subtitle(self, subtitle_text, x, y):
        """Create subtitle with fade-in effect"""
        subtitle_id = self.canvas.create_text(
            x, y,
            text=subtitle_text,
            font=("Courier New", 12),
            fill="#00FF00",
            width=self.popup_window.winfo_width() - 60,
            justify=tk.CENTER,
            tags="subtitle"
        )
        self.animation_ids.append(subtitle_id)
        
        # Start with transparent
        self.canvas.itemconfig(subtitle_id, fill="#000000")
        
        # Animate fade in
        self._fade_in_subtitle(subtitle_id, 0)
    
    def _fade_in_subtitle(self, subtitle_id, step):
        """Fade in the subtitle gradually"""
        if not self.animation_running or not self.popup_window.winfo_exists():
            return
            
        green_val = min(255, int(step * 25.5))
        self.canvas.itemconfig(subtitle_id, fill=f"#00{self._get_hex_value(green_val)}00")
        
        if step < 10:
            self.popup_window.after(50, lambda: self._fade_in_subtitle(subtitle_id, step + 1))
    
    def _add_button_glow(self, button):
        """Add a gentle glow effect around buttons"""
        import random
        
        # Get button position relative to canvas
        x = button.winfo_rootx() - self.canvas.winfo_rootx() + button.winfo_width()//2
        y = button.winfo_rooty() - self.canvas.winfo_rooty() + button.winfo_height()//2
        
        # Create particles around the button
        for _ in range(5):
            particle = {
                'x': x + random.randint(-button.winfo_width()//2, button.winfo_width()//2),
                'y': y + random.randint(-button.winfo_height()//2, button.winfo_height()//2),
                'size': random.randint(2, 4),
                'speed': random.uniform(0.2, 0.5),
                'angle': random.uniform(0, 2 * math.pi),
                'alpha': random.uniform(0.5, 0.9)
            }
            self.particles.append(particle)
    
    def _animate_particles(self):
        """Animate glowing particles around buttons"""
        if not self.animation_running or not self.popup_window.winfo_exists():
            return
            
        # Clear previous particles
        self.canvas.delete("particle")
        
        # Draw and update all particles
        for p in self.particles:
            # Create particle
            alpha = min(1.0, p['alpha'])
            color = f"#00{self._get_hex_value(int(255 * alpha))}00"
            
            self.canvas.create_oval(
                p['x'] - p['size'], p['y'] - p['size'],
                p['x'] + p['size'], p['y'] + p['size'],
                fill=color, outline="", tags="particle"
            )
            
            # Update position for next frame
            p['x'] += math.cos(p['angle']) * p['speed']
            p['y'] += math.sin(p['angle']) * p['speed']
            
            # Slightly modify angle for organic movement
            p['angle'] += math.sin(time.time() * 2) * 0.05
            
            # Keep particles within bounds
            width = self.popup_window.winfo_width()
            height = self.popup_window.winfo_height()
            
            if p['x'] < 0 or p['x'] > width or p['y'] < 0 or p['y'] > height:
                import random
                # Reset to a random position at the edge
                edge = random.randint(0, 3)  # 0: top, 1: right, 2: bottom, 3: left
                if edge == 0:  # top
                    p['x'] = random.randint(0, width)
                    p['y'] = 0
                elif edge == 1:  # right
                    p['x'] = width
                    p['y'] = random.randint(0, height)
                elif edge == 2:  # bottom
                    p['x'] = random.randint(0, width)
                    p['y'] = height
                else:  # left
                    p['x'] = 0
                    p['y'] = random.randint(0, height)
                
                # Update angle to move toward center
                p['angle'] = math.atan2(height/2 - p['y'], width/2 - p['x'])
                p['alpha'] = random.uniform(0.5, 0.9)
        
        # Continue animation
        self.popup_window.after(50, self._animate_particles)
    
    def _stop_animations(self):
        """Stop all animations"""
        self.animation_running = False
        for anim_id in self.animation_ids:
            self.canvas.delete(anim_id)
        self.animation_ids = []
    
    def close(self):
        """Close the popup window"""
        self._stop_animations()
        if self.popup_window and self.popup_window.winfo_exists():
            self.popup_window.destroy()
            self.popup_window = None
            if self.parent and self.parent.winfo_exists():
                 self.parent.grab_release() # Correctly release grab
                 self.parent.focus_set() # Return focus to parent
