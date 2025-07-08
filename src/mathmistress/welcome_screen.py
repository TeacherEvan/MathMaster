import tkinter as tk
import time
import os
import datetime
import logging
import math  # Added for pulsating calculations
from gameplay_screen import GameplayScreen
from level_select_screen import LevelSelectScreen
from stoic_quotes import get_random_quote
from src.visual_components.welcome_screen import (
    MatrixBackground,
    MathSymbols,
    ProgressBar
)
from math_master_logo_art import draw_algebra_logo # Added import for the logo

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
        
        # Make the window full screen
        self.attributes('-fullscreen', True)
        
        # Bind resize event
        self.bind("<Configure>", self.on_resize)
        
        # Track if user has clicked anywhere
        self.clicked = False
        self.bind("<Button-1>", self.on_click)
        
        # Create the main layout
        self.create_layout()
        
        # Initialize visual components
        self.matrix_background = MatrixBackground(self.canvas, MATH_PROBLEMS)
        self.math_symbols = MathSymbols(self.canvas, MATH_SYMBOLS)
        self.progress_bar = ProgressBar(self.canvas)
        
        # Use specific Marcus Aurelius quote instead of random
        self.stoic_quote = "If it is not right, do not do it; if it is not true, do not say it. - Marcus Aurelius"
        self.quote_pulse_phase = 0.0  # For pulsating effect
        self.algebra_pulse_phase = 0.0  # For Algebra text pulsating effect
        self.quote_pulse_timer = None  # For tracking the pulse animation
        
        # Draw the initial content
        self.redraw()
        
        # Start animation
        self.animate()
        
        # Bind escape key to exit
        self.bind("<Escape>", self.exit_game)
    
    def create_layout(self):
        """Creates the layout for the welcome screen"""
        # Create canvas for drawing
        self.canvas = tk.Canvas(self, highlightthickness=0, bg="#000000")
        self.canvas.pack(fill=tk.BOTH, expand=True)
    
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
        
        # Clean up the quote pulse timer
        if hasattr(self, 'quote_pulse_timer') and self.quote_pulse_timer:
            self.after_cancel(self.quote_pulse_timer)
            self.quote_pulse_timer = None
        
        self.destroy() # Destroy the root window (WelcomeScreen)

    def animate(self):
        """Animation loop"""
        if not self.clicked:
            try:
                # Update visual elements
                self.math_symbols.update_positions()
                
                # Update Algebra text pulsating effect with faster and more pronounced pulsing
                self.algebra_pulse_phase = (self.algebra_pulse_phase + 0.08) % (2 * math.pi)  # Increased speed
                self.redraw()  # Redraw to update the pulsating effect
                
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
        
        # Draw "MATH MASTER" title at the top
        title_font_size = max(24, min(width // 20, 36))
        # Double the title size by multiplying by 2
        title_font_size = title_font_size * 2
        
        # Create title with glowing effect
        for i in range(3, 0, -1):  # Create layers for glow effect
            glow_alpha = 0.3 * i / 3
            glow_color = self._get_hex_with_alpha("#00FF00", glow_alpha)
            self.canvas.create_text(
                width // 2, (height // 4) - title_font_size * 0.1,  # Only MATH MASTER moved 10% higher
                text="MATH MASTER",
                font=("Courier New", title_font_size, "bold"),
                fill=glow_color,
                tags="title_glow"
            )

        # --- Enhanced 3D/Shading Effect for MATH MASTER ---
        title_x = width // 2
        title_y = (height // 4) - title_font_size * 0.1
        
        # 1. Darker shadow layer (further offset)
        shadow_offset_x_deep = 3
        shadow_offset_y_deep = 3
        dark_green_shadow = "#004400" # Very dark green
        self.canvas.create_text(
            title_x + shadow_offset_x_deep,
            title_y + shadow_offset_y_deep,
            text="MATH MASTER",
            font=("Courier New", title_font_size, "bold"),
            fill=dark_green_shadow,
            tags="title_deep_shadow"
        )

        # 2. Mid-tone shadow layer (less offset)
        shadow_offset_x_mid = 1
        shadow_offset_y_mid = 1
        mid_green_shadow = "#006600" # Medium dark green
        self.canvas.create_text(
            title_x + shadow_offset_x_mid,
            title_y + shadow_offset_y_mid,
            text="MATH MASTER",
            font=("Courier New", title_font_size, "bold"),
            fill=mid_green_shadow,
            tags="title_mid_shadow"
        )
        # --- End of Enhanced 3D/Shading Effect ---
        
        # Main title text with black outline for depth (drawn around the original position)
        for offset in [(1, 1), (-1, 1), (1, -1), (-1, -1)]:
            self.canvas.create_text(
                title_x + offset[0], title_y + offset[1],  # Use title_x, title_y
                text="MATH MASTER",
                font=("Courier New", title_font_size, "bold"),
                fill="#000000",  # Black outline
                tags="title_outline"
            )
        
        # Main title text (top layer)
        self.canvas.create_text(
            title_x, title_y,  # Use title_x, title_y
            text="MATH MASTER",
            font=("Courier New", title_font_size, "bold"),
            fill="#00FF00",  # Matrix green
            tags="title"
        )
        
        # Draw "Algebra" text below with pulsating effect - REVERTED TO ORIGINAL POSITION
        algebra_font_size = int(title_font_size * 0.7)  # 70% of title size
        pulse_intensity = 0.5 * (math.sin(self.algebra_pulse_phase) + 1) / 2  # Increased range to 0 to 0.5
        algebra_alpha = 0.3 + pulse_intensity  # Base 30% opacity + pulsating effect (more transparent)
        
        # Create gold glow effect behind Algebra text - BACK TO ORIGINAL POSITION
        for i in range(5, 0, -1):  # Increased layers for more pronounced glow
            glow_alpha = (algebra_alpha * 0.4) * i / 5  # Reduced base alpha for gold glow
            glow_color = self._get_hex_with_alpha("#FFD700", glow_alpha)  # Gold color
            self.canvas.create_text(
                width // 2, height // 4 + 30,  # REVERTED - no additional_offset
                text="Algebra",
                font=("Courier New", algebra_font_size + (i * 2), "bold"),  # Increasing size for each layer
                fill=glow_color,
                tags="algebra_gold_glow"
            )
        
        # Black outline for Algebra text - BACK TO ORIGINAL POSITION
        for offset in [(1, 1), (-1, 1), (1, -1), (-1, -1)]:
            self.canvas.create_text(
                width // 2 + offset[0], height // 4 + 30 + offset[1],  # REVERTED - no additional_offset
                text="Algebra",
                font=("Courier New", algebra_font_size, "bold"),
                fill="#000000",  # Black outline
                tags="algebra_outline"
            )
        
        # Main Algebra text - BACK TO ORIGINAL POSITION
        self.canvas.create_text(
            width // 2, height // 4 + 30,  # REVERTED - no additional_offset
            text="Algebra",
            font=("Courier New", algebra_font_size, "bold"),
            fill=self._get_hex_with_alpha("#00FF00", algebra_alpha),
            tags="algebra"
        )
        
        # --- START INSERTED CODE FOR ALGEBRA LOGO ---
        # Calculate properties for Algebra text bottom
        # algebra_y_center is height // 4 + 30
        # algebra_font_size is already defined from title_font_size calculation
        algebra_text_visual_height_for_logo = algebra_font_size # Approximation for single-line text height
        algebra_bbox_bottom_for_logo = (height // 4 + 30) + (algebra_text_visual_height_for_logo / 2)

        # Calculate properties for Stoic Quote top (mirroring later calculations for accurate spacing)
        # Quote font size calculation (mirrors lines 300-303 of original file structure)
        _original_calc_size_quote_logo = max(10, min(width // 60, 16))
        _current_q_font_size_logo = int(_original_calc_size_quote_logo * 0.9)
        _actual_q_font_size_logo = int(_current_q_font_size_logo * 1.1) # This is the quote_font_size

        _quote_width_for_logo_calc = width * 0.8
        if _quote_width_for_logo_calc <= 0: _quote_width_for_logo_calc = 1 # Avoid division by zero

        _main_quote_text_for_logo_calc = self.stoic_quote
        if " - " in self.stoic_quote:
            _main_quote_text_for_logo_calc = self.stoic_quote.rsplit(" - ", 1)[0]

        _main_quote_y_for_logo_calc = height // 2 + 20 # Center Y of the quote block

        # Estimate height of main quote text (mirrors lines 329-331 of original file structure)
        if _actual_q_font_size_logo > 0: # Ensure font size is positive
            # Ensure _quote_width_for_logo_calc is not zero before division
            if _quote_width_for_logo_calc == 0: _quote_width_for_logo_calc = 1 
            _main_quote_num_lines_for_logo = (len(_main_quote_text_for_logo_calc) * _actual_q_font_size_logo * 0.6) / _quote_width_for_logo_calc
            if _main_quote_num_lines_for_logo == 0: _main_quote_num_lines_for_logo = 1 # Avoid issues with zero height for very short quotes
            _main_quote_estimated_height_for_logo = _main_quote_num_lines_for_logo * _actual_q_font_size_logo * 1.2
        else: # Fallback if font size calculation led to zero or negative
            _main_quote_estimated_height_for_logo = 0.0 # Set to 0 if font size is not positive

        _main_quote_bbox_top_for_logo = _main_quote_y_for_logo_calc - (_main_quote_estimated_height_for_logo / 2)

        available_vertical_space_for_logo = _main_quote_bbox_top_for_logo - algebra_bbox_bottom_for_logo
        
        MIN_LOGO_TARGET_PIXEL_HEIGHT = 30.0 # Minimum target height for the logo to be drawn

        if available_vertical_space_for_logo * 0.82 >= MIN_LOGO_TARGET_PIXEL_HEIGHT:
            logo_target_pixel_height = available_vertical_space_for_logo * 0.82
            
            LOGO_HEIGHT_TO_BASE_SIZE_RATIO = 1.5578 
            if LOGO_HEIGHT_TO_BASE_SIZE_RATIO <= 0: 
                LOGO_HEIGHT_TO_BASE_SIZE_RATIO = 1.0 # Prevent division by zero/negative

            logo_base_size = logo_target_pixel_height / LOGO_HEIGHT_TO_BASE_SIZE_RATIO
            
            MIN_LOGO_BASE_SIZE = 10.0 
            if logo_base_size >= MIN_LOGO_BASE_SIZE :
                logo_center_x = width // 2
                logo_center_y = algebra_bbox_bottom_for_logo + (available_vertical_space_for_logo / 2)
                
                # Assuming draw_algebra_logo is imported (e.g., from math_master_logo_art import draw_algebra_logo)
                draw_algebra_logo(
                    self.canvas,
                    logo_center_x,
                    logo_center_y,
                    logo_base_size,
                    self._get_hex_with_alpha
                )
        # --- END INSERTED CODE FOR ALGEBRA LOGO ---

        # Add creator credit below Algebra - POSITIONED AT BOTTOM CENTER
        original_font_size = max(12, min(width // 40, 20))
        credit_font_size = original_font_size // 2  # Exactly 50% of original size
        self.canvas.create_text(
            width // 2, height - credit_font_size - 20,  # Centered horizontally, near bottom
            text="Created By Teacher Evan (Ewaldt Botha)",
            font=("Helvetica", credit_font_size, "bold italic"),
            fill=self._get_hex_with_alpha("#88FF88", 0.5),  # 50% transparent
            tags="creator_credit"
        )

        # Draw stoic quote in the center (moved down slightly)
        # Original: quote_font_size = max(10, min(width // 60, 16))
        # Current (reduced by 10%): original_calculated_size = max(10, min(width // 60, 16)); quote_font_size = int(original_calculated_size * 0.9)
        # New (10% bigger than current):
        original_calculated_size = max(10, min(width // 60, 16))
        current_quote_font_size = int(original_calculated_size * 0.9) # This is the base for the 10% increase
        quote_font_size = int(current_quote_font_size * 1.21) # Increased by 10% from current (0.9 * 1.21 ≈ 1.089)

        quote_width = width * 0.8  # Use 80% of the width for the quote

        # Split quote into main part and author
        main_quote_text = self.stoic_quote
        author_text = ""
        if " - " in self.stoic_quote:
            parts = self.stoic_quote.rsplit(" - ", 1)
            main_quote_text = parts[0]
            author_text = " - " + parts[1]

        # Calculate vertical position for the main quote
        main_quote_y = height // 2 + 20

        # Black outline for main quote text for better definition
        for offset in [(1, 1), (-1, 1), (1, -1), (-1, -1), (0, 2), (2, 0), (-2, 0), (0, -2)]:
            self.canvas.create_text(
                width // 2 + offset[0], main_quote_y + offset[1], # Use main_quote_y
                text=main_quote_text, # Use main_quote_text
                font=("Helvetica", quote_font_size, "italic"),
                fill="#000000",
                width=quote_width,
                justify=tk.CENTER,
                tags="quote_outline"
            )
        
        # Create the main quote text 
        main_quote_id = self.canvas.create_text(
            width // 2, main_quote_y, # Use main_quote_y
            text=main_quote_text, # Use main_quote_text
            font=("Helvetica", quote_font_size, "italic"),
            fill=self._get_hex_with_alpha("#FFD700", 0.35),  # Gold with 65% transparency
            width=quote_width,
            justify=tk.CENTER,
            tags="stoic_quote"
        )

        # Draw Author Text if available
        if author_text:
            author_font_size = int(quote_font_size * 1.2) # 20% larger than the main quote's font size
            
            # Estimate height of main quote text to position author below it
            # This is an approximation. A more precise way would be to use canvas.bbox(main_quote_id)
            # but that requires the item to be drawn and might cause a flicker if updated.
            # For simplicity, we'll use font size as a proxy.
            main_quote_num_lines = (len(main_quote_text) * quote_font_size * 0.6) / quote_width # Approximate lines
            main_quote_estimated_height = main_quote_num_lines * quote_font_size * 1.2 # Approx height with line spacing
            
            author_y = main_quote_y + (main_quote_estimated_height / 2) + (author_font_size / 2) + 10 # Add some padding

            # Black outline for author text
            for offset in [(1, 1), (-1, 1), (1, -1), (-1, -1), (0, 2), (2, 0), (-2, 0), (0, -2)]:
                self.canvas.create_text(
                    width // 2 + offset[0], author_y + offset[1],
                    text=author_text,
                    font=("Helvetica", author_font_size, "italic"),
                    fill="#000000",
                    width=quote_width,
                    justify=tk.CENTER,
                    tags="author_outline"
                )

            # Create the author text
            self.canvas.create_text(
                width // 2, author_y,
                text=author_text,
                font=("Helvetica", author_font_size, "italic"),
                fill=self._get_hex_with_alpha("#FFD700", 0.35),  # Same color as quote
                width=quote_width, # Use same width constraint
                justify=tk.CENTER, # Center author
                tags="stoic_author"
            )
        
        # Add "Click to continue" text below the quote
        # Original: instruction_font_size = max(10, min(width // 60, 16))
        # Reduced by 10%:
        original_calculated_size = max(10, min(width // 60, 16))
        instruction_font_size = int(original_calculated_size * 0.9)
        
        # Add black outline to instruction text
        for offset in [(1, 1), (-1, 1), (1, -1), (-1, -1)]:
            self.canvas.create_text(
                width // 2 + offset[0], height // 2 + 120 + offset[1],
                text="Click to continue",
                font=("Helvetica", instruction_font_size),
                fill="#000000",
                tags="instruction_outline"
            )
        
        self.canvas.create_text(
            width // 2, height // 2 + 120,
            text="Click to continue",
            font=("Helvetica", instruction_font_size),
            fill="#AAFFAA",
            tags="instruction"
        )

    def _get_hex_with_alpha(self, hex_color, alpha):
        """Convert a hex color and alpha value to a hex color with the specified transparency"""
        try:
            # Extract RGB components
            r = int(hex_color[1:3], 16)
            g = int(hex_color[3:5], 16)
            b = int(hex_color[5:7], 16)
            
            # Apply alpha against black background
            r = int(r * alpha)
            g = int(g * alpha)
            b = int(b * alpha)
            
            # Convert back to hex
            return f"#{r:02x}{g:02x}{b:02x}"
        except Exception as e:
            logging.error(f"Error in color conversion: {e}")
            return hex_color  # Return original color on error

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
