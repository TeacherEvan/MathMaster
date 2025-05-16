import tkinter as tk
import time
import os
import datetime
import logging
from gameplay_screen import GameplayScreen
from level_select_screen import LevelSelectScreen
from src.visual_components.welcome_screen import (
    BrainAnimation,
    MatrixBackground,
    MathSymbols,
    ProgressBar,
    TitleDisplay
)

# Set up logging
logging.basicConfig(
    filename='mathmaster.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Constants
FRAME_RATE = 48  # 20 frames per second
FRAME_DELAY = int(1000 / FRAME_RATE)  # Convert to milliseconds

# Math problems for background
MATH_PROBLEMS = [
    "x+5=10", "3y=9", "2z-4=8", 
    "7a+2=16", "b/3=5", "4c^2=64"
]

MATH_SYMBOLS = [
    "∫", "∑", "π", "√", "∞", "≠", "≤", "≥", 
    "÷", "×", "±", "θ", "Δ", "∂", "∇", "∝"
]

class WelcomeScreen(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("MathMaster")
        self.configure(bg="#000000")  # Solid black background as per blueprint
        
        # Log application start
        logging.info("MathMaster application started")
        
        # Make the window responsive and set default size
        self.geometry("800x600")
        self.minsize(600, 400)
        
        # Bind resize event
        self.bind("<Configure>", self.on_resize)
        
        # Track if user has clicked anywhere
        self.clicked = False
        self.bind("<Button-1>", self.on_click)
        
        # Timer variables
        self.start_time = time.time()
        self.timeout = 8  # seconds before auto-continue
        
        # Create canvas for drawing
        self.canvas = tk.Canvas(self, highlightthickness=0, bg="#000000")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Initialize visual components
        self.brain_animation = BrainAnimation(self.canvas)
        self.matrix_background = MatrixBackground(self.canvas, MATH_PROBLEMS)
        self.math_symbols = MathSymbols(self.canvas, MATH_SYMBOLS)
        self.progress_bar = ProgressBar(self.canvas)
        self.title_display = TitleDisplay(self.canvas)
        
        # Draw the initial content
        self.redraw()
        
        # Start animation
        self.animate()
        
        # Bind escape key to exit
        self.bind("<Escape>", self.exit_game)
    
    def on_resize(self, event):
        """Handle window resize"""
        if event.widget == self:
            # Redraw everything when window is resized
            self.redraw()
    
    def on_click(self, event):
        """Handle user click - transition to level selection"""
        if not self.clicked:  # Only respond if not already clicked
            logging.info("User clicked to continue")
            self.clicked = True
            # Use after to schedule the transition with a small delay to allow the UI to update
            self.after(100, self.schedule_transition)
    
    def check_timeout(self):
        """Check if timeout has occurred"""
        # Only proceed if not already clicked
        if self.clicked:
            return
            
        elapsed = time.time() - self.start_time
        if elapsed > self.timeout:
            logging.info("Auto-continue timeout reached")
            self.clicked = True  # Set clicked first to prevent multiple calls
            # Use after to schedule the transition with a small delay
            self.after(100, self.schedule_transition)
        else:
            # Update progress indicator
            progress = min(1.0, elapsed / self.timeout)
            self.progress_bar.draw(progress)
    
    def schedule_transition(self):
        """Schedule the transition to level select with proper state management"""
        logging.info("Scheduling transition to level select screen")
        self.open_level_select()

    def open_level_select(self):
        """Hides the welcome screen and opens the level select screen."""
        try:
            logging.info("Creating Level Select Screen")
            
            # Create the level select screen
            level_select_window = LevelSelectScreen(self)
            level_select_window.protocol("WM_DELETE_WINDOW", self.exit_game)
            
            # Position and show level select window first
            level_select_window.deiconify()
            level_select_window.update()
            
            # Then hide the welcome screen
            logging.info("Hiding welcome screen")
            self.withdraw()
            
            # Final updates to ensure proper display
            level_select_window.focus_force()
            level_select_window.update_idletasks()
            
            # Log success
            logging.info("Level select screen transition complete")
            
        except Exception as e:
            # Log the error
            logging.error(f"Failed to create level select screen: {e}")
            logging.exception("Transition error details:")

    def exit_game(self, event=None):
        """Exit the game"""
        logging.info("User exited the application.")
        self.destroy() # Destroy the root window (WelcomeScreen)

    def animate(self):
        """Animation loop"""
        if not self.clicked:
            try:
                # Check timeout if the user hasn't clicked/transitioned yet
                self.check_timeout()
                
                # Update visual elements
                self.math_symbols.update_positions()
                self.brain_animation.update_animation()
                
                # Schedule next frame
                self.after(FRAME_DELAY, self.animate)
            except Exception as e:
                if self.winfo_exists():
                    logging.error(f"Animation error: {e}")
                    print(f"Animation error: {e}")
                return
    
    def redraw(self):
        """Redraw all content on canvas"""
        # Clear canvas
        self.canvas.delete("all")
        
        # Get current dimensions
        width = self.winfo_width()
        height = self.winfo_height()
        
        # Ensure we have valid dimensions (avoid division by zero)
        if width <= 1 or height <= 1:
            # Window not yet fully initialized, wait for proper dimensions
            self.after(100, self.redraw)
            return
            
        # Draw Matrix-style background
        self.matrix_background.draw(width, height)
        
        # Draw math symbols
        self.math_symbols.create_elements(width, height)
        
        # Draw brain graphic
        self.brain_animation.draw_brain()
        
        # Draw title and text elements
        self.title_display.draw(width, height)
        
        # Draw progress bar (empty initially)
        self.progress_bar.draw(0)

    def _get_valid_stipple(self, opacity):
        """Convert opacity (0-1) to valid stipple pattern"""
        if opacity <= 0.12:
            return 'gray12'
        elif opacity <= 0.25:
            return 'gray25'
        elif opacity <= 0.50:
            return 'gray50'
        else:
            return 'gray75'

    def create_shockwave(self, center_x, center_y, radius, opacity):
        """Create a shockwave effect with proper opacity handling"""
        try:
            # Ensure opacity is between 0 and 1
            opacity = max(0, min(1, opacity))
            
            # Get valid stipple pattern
            stipple_pattern = self._get_valid_stipple(opacity)
            
            # Create the shockwave oval
            shockwave = self.canvas.create_oval(
                center_x - radius, center_y - radius,
                center_x + radius, center_y + radius,
                outline='#00ff00',  # Matrix-style green
                width=2,
                stipple=stipple_pattern
            )
            
            return shockwave
        except Exception as e:
            logging.error(f"Error creating shockwave: {e}")
            return None

if __name__ == "__main__":
    logging.info("=== MathMaster Application Started ===")
    app = WelcomeScreen()
    app.mainloop()
    logging.info("=== MathMaster Application Closed ===")
