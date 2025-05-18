import tkinter as tk
import logging

class HelpButton:
    def __init__(self, parent, gameplay_screen):
        self.parent = parent
        self.gameplay_screen = gameplay_screen
        self.create_help_button()
        
    def create_help_button(self):
        """Creates the help button with guaranteed functionality"""
        # Direct frame creation and explicit positioning
        self.button_frame = tk.Frame(self.parent, bg="#FFFFFF", width=200, height=80)
        self.button_frame.pack(side=tk.TOP, pady=10, fill=tk.X)
        self.button_frame.pack_propagate(False)  # Force fixed size
        
        # Create the help button as a direct Button widget with explicit handling
        self.help_btn = tk.Button(
            self.button_frame,
            text="HELP",
            font=("Courier New", 18, "bold"),
            bg="#4CAF50",  # Green color
            fg="white",
            command=self._direct_help_handler,  # Use a simplified direct handler
            relief=tk.RAISED,
            bd=5,  # Thicker border
            width=15,
            height=2
        )
        self.help_btn.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)
        
        # Bind additional events for redundancy
        self.help_btn.bind("<Button-1>", self._click_handler)
        
        # Log creation
        logging.info("Help button created with DIRECT FUNCTIONALITY")
        print("HELP BUTTON CREATED: Should be fully functional now")
    
    def _click_handler(self, event):
        """Directly handle click event"""
        logging.info("Help button clicked via event binding")
        print("HELP BUTTON CLICKED via event binding")
        self._direct_help_handler()
        return "break"  # Prevent event propagation
        
    def _direct_help_handler(self):
        """Simplified direct help handler"""
        logging.info("DIRECT HELP HANDLER CALLED")
        print("HELP BUTTON ACTIVATED: Direct handler called")
        
        # Visual indication the button was pressed
        self.help_btn.config(relief=tk.SUNKEN)
        self.parent.after(200, lambda: self.help_btn.config(relief=tk.RAISED))
        
        # Call actual help functions
        try:
            if self.gameplay_screen:
                # Call direct functions on the gameplay screen
                if hasattr(self.gameplay_screen, "algebra_helper") and self.gameplay_screen.algebra_helper:
                    print("Using algebra_helper to provide help")
                elif hasattr(self.gameplay_screen, "provide_help") and callable(self.gameplay_screen.provide_help):
                    print("Using gameplay_screen.provide_help() method")
                    self.gameplay_screen.provide_help()
                else:
                    # Emergency fallback - create a direct help popup
                    self._create_help_popup()
        except Exception as e:
            logging.error(f"Error providing help: {e}")
            print(f"ERROR in help button: {e}")
            # Fallback to direct popup
            self._create_help_popup()
    
    def _create_help_popup(self):
        """Emergency fallback - create a direct help popup"""
        popup = tk.Toplevel(self.parent)
        popup.title("Algebra Help")
        popup.geometry("400x300")
        popup.config(bg="#FFFFDD")
        
        # Add help content
        tk.Label(popup, text="Algebra Help", font=("Arial", 16, "bold"), bg="#FFFFDD").pack(pady=10)
        
        help_text = """
        Algebra Rules:
        
        1. Addition Rule: Add the same value to both sides
        2. Subtraction Rule: Subtract the same value from both sides
        3. Multiplication Rule: Multiply both sides by the same value
        4. Division Rule: Divide both sides by the same value
        
        To solve for x, isolate the variable on one side of the equation.
        """
        
        tk.Label(popup, text=help_text, font=("Arial", 12), justify=tk.LEFT, 
                 bg="#FFFFDD", wraplength=380).pack(pady=10, padx=20)
        
        # Close button
        tk.Button(popup, text="Close", font=("Arial", 12, "bold"), 
                 command=popup.destroy, bg="#FF2222", fg="white").pack(pady=10)
                 
        # Force to front
        popup.lift()
        popup.focus_force() 