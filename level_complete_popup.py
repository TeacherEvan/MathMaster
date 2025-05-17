import tkinter as tk
import random
import time
import math
import logging
from PIL import Image, ImageTk, ImageDraw, ImageFilter, ImageFont
import os

class LevelCompletePopup:
    """
    Enhanced popup window that appears when a level is completed.
    Features animated text, particle effects, and dynamic sizing.
    
    This popup is designed to be shown AFTER the lock animation in window A 
    has finished its celebration animation. The GameplayScreen class ensures
    proper timing by scheduling this popup after the lock animation completes.
    """
    
    def __init__(self, parent):
        """
        Initialize the popup window.
        
        Args:
            parent: The parent window
        """
        self.parent = parent
        self.popup = None
        self.particles = []
        self.animation_running = False
        
        # Visual theme colors
        self.colors = {
            "background": "#001a00",  # Very dark green
            "title": "#5dff5d",       # Bright green
            "subtitle": "#90ee90",    # Light green
            "button_bg": "#004d00",   # Dark green
            "button_fg": "#ccffcc",   # Very light green
            "button_hover": "#006600",  # Slightly brighter green
            "particle_colors": ["#5dff5d", "#90ee90", "#00ff00", "#66ff66", "#33cc33"]
        }
        
        # Load and prepare assets
        self.load_assets()
    
    def load_assets(self):
        """Load and prepare images, sounds, and other assets"""
        # Create paths to asset directories
        self.assets_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets")
        self.images_dir = os.path.join(self.assets_dir, "images")
        
        # Ensure the directories exist
        os.makedirs(self.assets_dir, exist_ok=True)
        os.makedirs(self.images_dir, exist_ok=True)

        # Cache for PhotoImage objects
        self.image_cache = {}
    
    def show(self, title="Level Complete!", subtitle="You've solved the math problem!", 
             callback_next=None, callback_level_select=None, width=400, height=300):
        """
        Display the popup window.
        
        Args:
            title: Main title to display
            subtitle: Secondary text to display
            callback_next: Function to call when "Next Problem" is clicked
            callback_level_select: Function to call when "Level Select" is clicked
            width: Width of the popup window
            height: Height of the popup window
        """
        if self.popup and self.popup.winfo_exists():
            self.popup.destroy()
            
        # Create popup window
        self.popup = tk.Toplevel(self.parent)
        self.popup.title("Success")
        self.popup.geometry(f"{width}x{height}")
        self.popup.configure(bg=self.colors["background"])
        self.popup.resizable(True, True)
        
        # Center the popup
        parent_x = self.parent.winfo_x() + (self.parent.winfo_width() // 2)
        parent_y = self.parent.winfo_y() + (self.parent.winfo_height() // 2)
        popup_x = parent_x - (width // 2)
        popup_y = parent_y - (height // 2)
        self.popup.geometry(f"+{popup_x}+{popup_y}")
        
        # Make popup modal
        self.popup.grab_set()
        self.popup.focus_set()
        self.popup.transient(self.parent)
        
        # Create main canvas for all drawing
        self.canvas = tk.Canvas(
            self.popup, 
            bg=self.colors["background"], 
            highlightthickness=0,
            width=width,
            height=height
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Set up window resize handling
        self.popup.bind("<Configure>", self.on_resize)
        
        # Create main content
        self.create_content(title, subtitle)
        
        # Create button frame
        button_frame = tk.Frame(self.canvas, bg=self.colors["background"])
        button_frame_window = self.canvas.create_window(
            width // 2, height - 70, 
            window=button_frame, 
            anchor=tk.CENTER
        )
        
        # Store callbacks for keyboard shortcuts
        self.callback_next = callback_next
        self.callback_level_select = callback_level_select
        
        # Create stylish buttons with icons for better navigation
        next_icon = "→ "  # Arrow icon
        level_icon = "⌂ "  # Home icon
        
        next_button = self.create_button(
            button_frame, 
            f"{next_icon}Next Problem", 
            lambda: self.handle_button_click(callback_next),
            index=0
        )
        next_button.grid(row=0, column=0, padx=10)
        
        level_select_button = self.create_button(
            button_frame, 
            f"{level_icon}Level Select", 
            lambda: self.handle_button_click(callback_level_select),
            index=1
        )
        level_select_button.grid(row=0, column=1, padx=10)
        
        # Add keyboard shortcuts
        self.popup.bind("<Return>", lambda e: self.handle_button_click(callback_next))  # Enter key for Next
        self.popup.bind("<Escape>", lambda e: self.handle_button_click(callback_level_select))  # Esc for Level Select
        
        # Add a small hint about keyboard shortcuts
        shortcuts_text = "Shortcuts: Enter = Next, Esc = Level Select"
        self.canvas.create_text(
            width // 2, 
            height - 20,
            text=shortcuts_text,
            font=("Arial", 8),
            fill=self.get_alpha_color(self.colors["subtitle"], 0.7),
            tags="shortcuts"
        )
        
        # Start animations
        self.start_animations()
        
        # Ensure popup stays on top
        self.popup.attributes('-topmost', True)
        self.popup.update()
        self.popup.attributes('-topmost', False)
        
        # Return the popup for reference
        return self.popup
    
    def create_content(self, title_text, subtitle_text):
        """Create the title, subtitle, and other content elements"""
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        
        # Create title with shadow effect
        self.title = self.canvas.create_text(
            width // 2 + 2, 
            height // 3 + 2, 
            text=title_text,
            font=("Arial", 24, "bold"),
            fill="#004d00",  # Shadow color
            tags="title_shadow"
        )
        
        self.title = self.canvas.create_text(
            width // 2, 
            height // 3, 
            text=title_text,
            font=("Arial", 24, "bold"),
            fill=self.colors["title"],
            tags="title"
        )
        
        # Create subtitle
        self.subtitle = self.canvas.create_text(
            width // 2,
            height // 2,
            text=subtitle_text,
            font=("Arial", 14),
            fill=self.colors["subtitle"],
            width=width-40,  # Wrap text if needed
            justify=tk.CENTER,
            tags="subtitle"
        )
        
        # Create decorative elements
        self.create_decorative_elements()
    
    def create_decorative_elements(self):
        """Create decorative visual elements"""
        # Get canvas dimensions with minimum size guarantees to prevent negative ranges
        width = max(100, self.canvas.winfo_width())
        height = max(100, self.canvas.winfo_height())
        
        # Create glowing border
        border_width = 2
        glow_steps = 2
        
        for i in range(glow_steps):
            alpha = 0.6 - (i * 0.2)  # Decreasing alpha for outer glow
            color = self.get_alpha_color(self.colors["title"], alpha)
            offset = i * 2 + border_width
            
            self.canvas.create_rectangle(
                offset, offset, 
                width - offset, height - offset,
                outline=color,
                width=border_width,
                tags="border"
            )
        
        # Create math symbols in background
        math_symbols = ["∫", "∑", "π", "√", "∞", "≠", "≤", "≥", "÷", "×", "±", "θ", "Δ"]
        
        # Only add decorative symbols if canvas is large enough
        if width > 60 and height > 60:
            for _ in range(7):
                symbol = random.choice(math_symbols)
                # Ensure valid ranges for random positions
                x = random.randint(20, max(21, width - 20))
                y = random.randint(20, max(21, height - 20))
                size = random.randint(12, 36)
                alpha = random.uniform(0.1, 0.3)
                color = self.get_alpha_color(self.colors["title"], alpha)
                
                self.canvas.create_text(
                    x, y, 
                    text=symbol,
                    font=("Arial", size),
                    fill=color,
                    tags="math_symbol"
                )
    
    def create_button(self, parent, text, command, index=0):
        """Create a styled button with hover effects"""
        button = tk.Button(
            parent,
            text=text,
            font=("Arial", 12, "bold"),
            bg=self.colors["button_bg"],
            fg=self.colors["button_fg"],
            relief=tk.FLAT,
            width=15,
            padx=10,
            pady=5,
            bd=0,
            activebackground=self.colors["button_hover"],
            activeforeground=self.colors["button_fg"],
            command=command
        )
        
        # Add hover effect
        button.bind("<Enter>", lambda e, b=button: self.on_button_hover(b, True))
        button.bind("<Leave>", lambda e, b=button: self.on_button_hover(b, False))
        
        return button
    
    def on_button_hover(self, button, is_hovering):
        """Handle button hover events"""
        if is_hovering:
            button.config(bg=self.colors["button_hover"])
        else:
            button.config(bg=self.colors["button_bg"])
    
    def handle_button_click(self, callback):
        """Handle button clicks and close the popup"""
        self.stop_animations()
        
        if callback:
            callback()
        
        if self.popup and self.popup.winfo_exists():
            self.popup.destroy()
    
    def start_animations(self):
        """Start all animations"""
        self.animation_running = True
        # self.animate_particles()  # Commented out to remove particles
        self.animate_text()
        self._animate_elements() # Start element animations
    
    def _animate_elements(self):
        """General animation loop for various small effects."""
        if not self.animation_running or not self.popup or not self.popup.winfo_exists():
            return

        # Example: Pulsate border glow intensity
        if hasattr(self, 'canvas'):
            border_items = self.canvas.find_withtag("border")
            glow_steps = 3 # Should match create_decorative_elements
            base_alpha = 0.6
            
            for i, item_id in enumerate(border_items):
                # Calculate dynamic alpha for pulsing effect
                # Using a time-based sine wave for smooth pulsing
                time_factor = time.time() * 2.0  # Speed of pulse
                pulse = (math.sin(time_factor + i * 0.5) + 1) / 2 # Ranges 0 to 1
                
                # Modulate base alpha with pulse
                dynamic_alpha = (base_alpha - (i * 0.2)) * (0.7 + 0.3 * pulse) # Ensure alpha stays reasonable
                dynamic_alpha = max(0.1, min(1.0, dynamic_alpha)) # Clamp alpha

                try:
                    color = self.get_alpha_color(self.colors["title"], dynamic_alpha)
                    self.canvas.itemconfig(item_id, outline=color)
                except tk.TclError:
                    pass # Item might be gone

        self.popup.after(50, self._animate_elements)

    def animate_particles(self):
        """Animate particles with various effects (movement, fade, etc.)"""
        # This method is now effectively disabled by not being called.
        # If we wanted to be absolutely sure, we could clear self.particles here or in init.
        # However, since create_particles is also not called from start_animations, 
        # self.particles should remain empty.

        # if not self.animation_running or not self.popup or not self.popup.winfo_exists():
        #     return

        # # Create new particles occasionally
        # if random.random() < 0.1 and len(self.particles) < 50: # Max 50 particles
        #     self.create_particle()
            
        # # Update existing particles
        # for particle in list(self.particles): # Iterate on a copy for safe removal
        #     try:
        #         # Move particle
        #         self.canvas.move(particle['id'], particle['vx'], particle['vy'])
                
        #         # Update particle lifetime and fade
        #         particle['life'] -= 1
        #         if particle['life'] <= 0:
        #             self.canvas.delete(particle['id'])
        #             self.particles.remove(particle)
        #             continue
                
        #         # Fade effect (adjust alpha)
        #         alpha = particle['life'] / particle['max_life']
        #         # Ensure alpha is between 0 and 1
        #         alpha = max(0, min(1, alpha))
                
        #         # Create color with new alpha (approximate for Tkinter)
        #         # This is a simplified way, proper alpha blending is complex in Tkinter
        #         base_color_hex = particle['color'].lstrip('#')
        #         r, g, b = tuple(int(base_color_hex[i:i+2], 16) for i in (0, 2, 4))
                
        #         # Blend with background (assuming self.colors["background"])
        #         bg_r, bg_g, bg_b = tuple(int(self.colors["background"].lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
                
        #         final_r = int(r * alpha + bg_r * (1 - alpha))
        #         final_g = int(g * alpha + bg_g * (1 - alpha))
        #         final_b = int(b * alpha + bg_b * (1 - alpha))
                
        #         # Clamp values to 0-255
        #         final_r = max(0, min(255, final_r))
        #         final_g = max(0, min(255, final_g))
        #         final_b = max(0, min(255, final_b))
                
        #         new_color = f"#{final_r:02x}{final_g:02x}{final_b:02x}"
        #         self.canvas.itemconfig(particle['id'], fill=new_color)
                
        #     except tk.TclError:
        #         # Particle might have been deleted
        #         if particle in self.particles:
        #             self.particles.remove(particle)
        
        # # Repeat animation
        # self.popup.after(30, self.animate_particles) # Approx 30 FPS
        pass # Method body effectively removed

    def create_particle(self):
        """Create a single particle with random properties"""
        # This method is now effectively disabled.
        # width = self.canvas.winfo_width()
        # height = self.canvas.winfo_height()
        
        # # Ensure canvas has valid dimensions before creating particles
        # if width <= 0 or height <= 0:
        #     return # Don't create particles if canvas not ready

        # x = random.randint(0, width)
        # y = random.randint(0, height)
        # size = random.randint(2, 5)
        # color = random.choice(self.colors["particle_colors"])
        
        # # Particle movement vector (random direction)
        # angle = random.uniform(0, 2 * math.pi)
        # speed = random.uniform(0.5, 1.5)
        # vx = math.cos(angle) * speed
        # vy = math.sin(angle) * speed
        
        # # Particle lifetime
        # max_life = random.randint(50, 150) # Number of frames
        
        # # Create particle on canvas
        # particle_id = self.canvas.create_oval(
        #     x - size, y - size, 
        #     x + size, y + size,
        #     fill=color, outline="", tags="particle"
        # )
        
        # self.particles.append({
        #     'id': particle_id,
        #     'x': x, 'y': y,
        #     'vx': vx, 'vy': vy,
        #     'size': size,
        #     'color': color,
        #     'life': max_life,
        #     'max_life': max_life
        # })
        pass # Method body effectively removed

    def animate_text(self):
        """Animate the title text pulsing effect"""
        if not self.animation_running or not self.popup or not self.popup.winfo_exists():
            return
            
        # Get current time for animation
        t = time.time() * 2
        scale = 1.0 + 0.05 * math.sin(t)
        
        # Apply scale to title
        self.canvas.itemconfig("title", font=("Arial", int(24 * scale), "bold"))
        self.canvas.itemconfig("title_shadow", font=("Arial", int(24 * scale), "bold"))
        
        # Continue animation
        self.popup.after(50, self.animate_text)
    
    def stop_animations(self):
        """Stop all running animations"""
        self.animation_running = False
    
    def on_resize(self, event):
        """Handle window resize events"""
        if event.widget == self.popup:
            width = event.width
            height = event.height
            
            # Reposition title and subtitle
            self.canvas.coords("title", width // 2, height // 3)
            self.canvas.coords("title_shadow", width // 2 + 2, height // 3 + 2)
            self.canvas.coords("subtitle", width // 2, height // 2)
            self.canvas.itemconfig("subtitle", width=width-40)
            
            # Update border
            self.canvas.delete("border")
            self.canvas.delete("math_symbol")
            self.create_decorative_elements()
            
            # Reposition button frame
            button_items = self.canvas.find_withtag("window")
            if button_items:
                self.canvas.coords(button_items[0], width // 2, height - 70)
                
            # Reposition keyboard shortcuts hint
            shortcuts_items = self.canvas.find_withtag("shortcuts")
            if shortcuts_items:
                self.canvas.coords(shortcuts_items[0], width // 2, height - 20)
    
    def get_alpha_color(self, hex_color, alpha):
        """Convert a hex color with alpha to an apparent hex color"""
        r = int(hex_color[1:3], 16)
        g = int(hex_color[3:5], 16)
        b = int(hex_color[5:7], 16)
        
        # Blend with background
        bg_color = self.colors["background"]
        bg_r = int(bg_color[1:3], 16)
        bg_g = int(bg_color[3:5], 16)
        bg_b = int(bg_color[5:7], 16)
        
        # Alpha blending formula
        r = int(r * alpha + bg_r * (1 - alpha))
        g = int(g * alpha + bg_g * (1 - alpha))
        b = int(b * alpha + bg_b * (1 - alpha))
        
        # Clamp values
        r = max(0, min(255, r))
        g = max(0, min(255, g))
        b = max(0, min(255, b))
        
        return f"#{r:02x}{g:02x}{b:02x}"

def show_demo():
    """Function to demonstrate the popup"""
    root = tk.Tk()
    root.title("Demo")
    root.geometry("800x600")
    root.configure(bg="#000")
    
    def next_action():
        print("Next Problem selected")
        
    def level_select_action():
        print("Level Select selected")
        
    def show_popup():
        popup = LevelCompletePopup(root)
        popup.show(
            title="Level Complete!",
            subtitle="You've solved the equation brilliantly! Your mathematical skills are improving.",
            callback_next=next_action,
            callback_level_select=level_select_action
        )
    
    # Create demo button
    btn = tk.Button(root, text="Show Popup", command=show_popup)
    btn.pack(pady=100)
    
    root.mainloop()

if __name__ == "__main__":
    show_demo() 