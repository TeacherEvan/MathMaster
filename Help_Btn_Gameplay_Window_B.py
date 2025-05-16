import tkinter as tk
import logging

class HelpButton:
    def __init__(self, parent, gameplay_screen):
        self.parent = parent
        self.gameplay_screen = gameplay_screen
        self.create_help_button()
        
    def create_help_button(self):
        """Creates the help button"""
        self.button_frame = tk.Frame(self.parent, bg="#FFFFFF")
        self.button_frame.grid(row=0, column=0, pady=10)
        
        # Create the help button
        self.help_btn = tk.Button(
            self.button_frame,
            text="HELP",
            font=("Courier New", 18, "bold"),
            bg="#4CAF50",  # Green color
            fg="white",
            command=self.provide_help,
            width=15,
            height=2
        )
        self.help_btn.pack(pady=5)
    
    def provide_help(self):
        """Delegates help functionality to gameplay screen"""
        if self.gameplay_screen and hasattr(self.gameplay_screen, 'provide_help'):
            self.help_btn.config(state='disabled')  # Prevent multiple rapid clicks
            self.gameplay_screen.provide_help()
            # Re-enable button after a short delay
            self.gameplay_screen.after(100, lambda: self.help_btn.config(state='normal')) 