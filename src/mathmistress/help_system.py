"""Extracted help / success-display subsystem from GameplayScreen.

Self-contained cluster (7 methods, ~240 lines) sharing only ``self`` and the
``HelpDisplay`` / ``constants`` imports.  Extracted 2026-09-13 surgical-implementation
pass to satisfy plan OBJ-004 (reduce gameplay_screen.py below 1523 lines).
Every function takes ``self`` as its first argument so the thin wrappers in
``gameplay_screen.py`` can delegate with a single line.
"""

import logging
import traceback

from help_display import HelpDisplay
from constants import DEFAULT_HELP_TEXT


def provide_help(self):
    """Provide contextual help based on the current problem state and reveal next character."""
    logging.info("HELP BUTTON CLICKED: Starting help processing")
    
    try:
        # Set the flag to true since help button was clicked
        self.help_button_clicked = True
        
        # Make the solution canvas visible on first help click
        if not self.solution_canvas_visible:
            self.solution_canvas_visible = True
            logging.info("Making solution canvas visible now that help button was clicked")
            
        # STEP 1: Find the next character to reveal
        valid_positions = self.find_next_required_char()
        if valid_positions:
            # Get the first unrevealed character position
            next_pos = valid_positions[0]  # (line_idx, char_idx, char)
            line_idx, char_idx = next_pos[0], next_pos[1]
            
            # Reveal this character
            logging.info(f"Help button revealing character at position ({line_idx}, {char_idx})")
            self.reveal_char(line_idx, char_idx)
        
        # STEP 2: Draw solution lines if this is the first help click
        # This will make the text box visible only after help is clicked
        if hasattr(self, 'solution_symbol_display') and self.solution_symbol_display:
            self.draw_solution_lines()
        
        # STEP 3: Show explanatory text (existing functionality)
        # Force creation of help display if it doesn't exist
        if not hasattr(self, 'help_display') or self.help_display is None:
            logging.info("Help display not found - creating it now")
            self.help_display = HelpDisplay(
                self.solution_canvas,
                x=20,
                y=120
            )
        
        # Get current progress
        current_step = self._get_current_step_index()
        logging.info(f"Current step index: {current_step}")
        
        # Get text to display
        if current_step is not None and current_step < len(self.current_solution_steps):
            current_step_text = self.current_solution_steps[current_step]
            logging.info(f"Current step text: '{current_step_text}'")
            
            # Create a more immediate visual feedback that help is working
            self._flash_help_area()
            
            # Update help display with contextual information
            self.help_display.update_help_text(
                current_step_index=current_step,
                total_steps=len(self.current_solution_steps),
                step_text=current_step_text
            )
            
            # Make sure it's visible
            self.help_display.show()
            
            logging.info(f"Help provided for step {current_step}")
        else:
            # Fallback to symbol-based help
            symbols = set()
            for line in self.current_solution_steps:
                for char in line:
                    if char in "+-*/=×÷":
                        symbols.add(char)
            
            # Create a more immediate visual feedback
            self._flash_help_area()
            
            # Update help with symbol-based context
            self.help_display.update_help_text(symbols=list(symbols))
            
            # Make sure it's visible
            self.help_display.show()
            
            logging.info(f"Symbol-based help provided with symbols: {symbols}")
    except Exception as e:
        logging.error(f"Error providing help: {e}")
        import traceback
        logging.error(traceback.format_exc())

def _flash_help_area(self):
    """Create a visual flash on the help area to show button press registered."""
    try:
        if not hasattr(self, 'solution_canvas') or not self.solution_canvas.winfo_exists():
            return
            
        # Calculate position for the flash effect
        canvas_width = self.solution_canvas.winfo_width()
        flash_x = 20  # Same as help_display x
        flash_y = 120  # Same as help_display y
        flash_width = min(300, canvas_width - 40)  # Limited by canvas width
        flash_height = 80
        
        # Create a temporary highlight rectangle
        self.solution_canvas.create_rectangle(
            flash_x, flash_y,
            flash_x + flash_width, flash_y + flash_height,
            fill="#AAFFAA",  # Light green
            outline="#44AA44",
            stipple="gray50",
            tags="help_flash"
        )
        
        # Schedule removal of flash effect
        def remove_flash():
            try:
                if self.solution_canvas.winfo_exists():
                    self.solution_canvas.delete("help_flash")
            except:
                pass
                
        self.after(500, remove_flash)
        
    except Exception as e:
        logging.error(f"Error creating help flash effect: {e}")

def _get_current_step_index(self):
    """Determine which step the player is currently working on."""
    try:
        # If no solution steps or in transition, return a safe value
        if not self.current_solution_steps or hasattr(self, 'in_level_transition') and self.in_level_transition:
            return 0 # Return 0 instead of None for safer indexing
        
        # Find the first incomplete step
        for step_idx, step_text in enumerate(self.current_solution_steps):
            # Count visible characters in this step
            visible_count = sum(1 for char_idx in range(len(step_text)) 
                               if (step_idx, char_idx) in self.visible_chars)
            
            # If not all characters are visible, this is the current step
            if visible_count < len(step_text):
                return step_idx
        
        # If all steps are complete, return the last step
        return len(self.current_solution_steps) - 1 if self.current_solution_steps else 0
    
    except Exception as e:
        logging.error(f"Error determining current step: {e}")
        return 0 # Return 0 instead of None for safer indexing

def show_success_message(self):
    """Show a temporary success message on the solution canvas when level is complete."""
    try:
        if hasattr(self, 'solution_canvas') and self.solution_canvas.winfo_exists():
            # Delete any existing success message
            if hasattr(self, 'success_message_id'):
                self.solution_canvas.delete(self.success_message_id)
                
            # Get canvas dimensions
            canvas_width = self.solution_canvas.winfo_width()
            canvas_height = self.solution_canvas.winfo_height()
            
            # Create the success message
            self.success_message_id = self.solution_canvas.create_text(
                canvas_width / 2, 
                canvas_height / 2,
                text="Level Complete!",
                font=("Arial", 24, "bold"),
                fill="#00AA00",  # Green color
                tags="success_message"
            )
            
            # Add a glow effect
            self.success_glow_id = self.solution_canvas.create_oval(
                canvas_width / 2 - 120, 
                canvas_height / 2 - 40,
                canvas_width / 2 + 120, 
                canvas_height / 2 + 40,
                fill="#AAFFAA",
                outline="#00AA00",
                width=2,
                stipple="gray50",
                tags="success_message"
            )
            
            # Move glow behind text
            self.solution_canvas.tag_lower(self.success_glow_id, self.success_message_id)
            
            # Schedule cleanup after 4 seconds
            self.after(4000, self._clear_success_message)
            
            logging.info("Displayed level complete success message")
    except Exception as e:
        logging.error(f"Error displaying success message: {e}")
        
def _clear_success_message(self):
    """Clear the success message from the solution canvas."""
    try:
        if hasattr(self, 'solution_canvas') and self.solution_canvas.winfo_exists():
            self.solution_canvas.delete("success_message")
            
        # Clear the IDs
        if hasattr(self, 'success_message_id'):
            del self.success_message_id
        if hasattr(self, 'success_glow_id'):
            del self.success_glow_id
    except Exception as e:
        logging.error(f"Error clearing success message: {e}")

def _setup_help_display(self):
    """Set up the help display after a short delay to ensure solution_canvas exists."""
    try:
        if hasattr(self, 'solution_canvas') and self.solution_canvas.winfo_exists():
            # Initialize help display in Window B area
            self.help_display = HelpDisplay(
                self.solution_canvas,  # Use the solution canvas
                x=20,                  # Position near left edge
                y=120                  # Position below the help button
            )
            self.help_display.show()   # Show with default text
            
            # Force initial visibility
            self.help_display.current_help_text = DEFAULT_HELP_TEXT  # from constants
            self.help_display.update_display()
            
            logging.info("Help display initialized successfully")
        else:
            logging.warning("Could not initialize help display - solution_canvas not found or not ready")
            # Try again after a delay
            self.after(300, self._setup_help_display)
    except Exception as e:
        logging.error(f"Error setting up help display: {e}")
        import traceback
        logging.error(traceback.format_exc())

def _ensure_help_display_visible(self):
    """Make sure the help display is visible after initialization."""
    try:
        if hasattr(self, 'help_display') and self.help_display:
            logging.info("Ensuring help display is visible")
            self.help_display.update_display()
            self.help_display.show()
    except Exception as e:
        logging.error(f"Error making help display visible: {e}")
