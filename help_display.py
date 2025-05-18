import tkinter as tk
import logging
from algebra_helper import AlgebraHelper

class HelpDisplay:
    """
    Displays contextual help text in Window B below the help button.
    The text explains algebra rules based on the current step.
    """
    
    def __init__(self, parent_canvas, x=None, y=None, width=None, height=None):
        """
        Initialize the help display component.
        
        Args:
            parent_canvas: The canvas where the help text will be displayed (Window B)
            x, y: The position of the top-left corner of the help text box
            width, height: The dimensions of the help text box
        """
        self.canvas = parent_canvas
        self.algebra_helper = AlgebraHelper()
        self.help_text_id = None
        self.help_box_id = None
        
        # Default position and size if not specified
        self.x = x or 10  # Default x position
        self.y = y or 50  # Default y position (below help button)
        self.width = width or parent_canvas.winfo_width() - 20  # Default width
        self.height = height or 80  # Increased height for better visibility
        
        # Track window resizing
        self.canvas.bind("<Configure>", self.on_resize)
        
        # Improved text properties
        self.font = ("Arial", 11, "italic bold")  # CHANGED: bigger font, bold added
        self.text_color = "#000000"  # CHANGED: Black for better contrast
        self.bg_color = ""  # Transparent background so it's invisible by default
        self.is_visible = False  # Track visibility state
        
        # Initialize with default text
        self.current_help_text = "Algebra Help: Click Help button for assistance."
        
    def on_resize(self, event=None):
        """Handle canvas resize events."""
        # Update dimensions based on parent canvas
        if event:
            self.width = event.width - 20
        self.update_display()
        
    def update_display(self):
        """Update the help text display on the canvas."""
        try:
            # Clear previous text if it exists
            if self.help_text_id:
                self.canvas.delete(self.help_text_id)
            if self.help_box_id:
                self.canvas.delete(self.help_box_id)
                
            if self.is_visible:
                # Create a visible background box
                self.help_box_id = self.canvas.create_rectangle(
                    self.x, self.y,
                    self.x + self.width, self.y + self.height,
                    fill=self.bg_color, outline="#44AA44", width=2
                )
                
                # Add new text with word wrapping
                self.help_text_id = self.canvas.create_text(
                    self.x + 10, self.y + 10,  # Increased padding
                    text=self.current_help_text,
                    font=self.font,
                    fill=self.text_color,
                    anchor="nw",
                    width=self.width - 20  # Allow for wrapping
                )
                
                # Move the text to the top layer
                self.canvas.tag_raise(self.help_text_id)
            
        except Exception as e:
            logging.error(f"Error updating help display: {e}")
            
    def update_help_text(self, current_step_index=None, total_steps=None, step_text=None, symbols=None):
        """
        Update the help text based on the current problem state.
        
        Args:
            current_step_index: The index of the current step
            total_steps: Total number of steps in the solution
            step_text: The text of the current step
            symbols: List of symbols involved in the current step
        """
        try:
            new_help_text = None
            
            # Generate help text based on step information
            if current_step_index is not None and total_steps is not None and step_text:
                new_help_text = self.algebra_helper.get_help_for_steps(
                    current_step_index, total_steps, step_text
                )
            # Or generate based on symbols
            elif symbols:
                new_help_text = self.algebra_helper.get_help_for_symbols(symbols)
            
            # Update text if we have new text
            if new_help_text:
                self.current_help_text = new_help_text
                self.update_display()
                
        except Exception as e:
            logging.error(f"Error updating help text: {e}")
            
    def show(self):
        """Show the help display."""
        self.is_visible = True
        self.update_display()
        
    def hide(self):
        """Hide the help display."""
        self.is_visible = False
        if self.help_text_id:
            self.canvas.delete(self.help_text_id)
            self.help_text_id = None
        if self.help_box_id:
            self.canvas.delete(self.help_box_id)
            self.help_box_id = None
            
    def set_position(self, x, y):
        """Set a new position for the help text."""
        self.x = x
        self.y = y
        self.update_display()

# For testing
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Help Display Test")
    root.geometry("400x300")
    
    canvas = tk.Canvas(root, bg="white")
    canvas.pack(fill=tk.BOTH, expand=True)
    
    # Add a mock help button
    help_button = tk.Button(root, text="Help")
    help_button_window = canvas.create_window(10, 10, anchor="nw", window=help_button)
    
    # Create and show help display
    help_display = HelpDisplay(canvas)
    help_display.show()
    
    # Test updating help text after 2 seconds
    root.after(2000, lambda: help_display.update_help_text(
        current_step_index=0, 
        total_steps=3, 
        step_text="x + 5 = 12"
    ))
    
    # Test updating with symbols after 4 seconds
    root.after(4000, lambda: help_display.update_help_text(
        symbols=['+', '=', 'x']
    ))
    
    root.mainloop() 