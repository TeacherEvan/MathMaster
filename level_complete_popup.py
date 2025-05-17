import tkinter as tk
import os

class LevelCompletePopup:
    """
    Simplified popup window that appears when a level is completed.
    Minimizes visual effects to prevent game slowdown.
    """
    
    def __init__(self, parent):
        """
        Initialize the popup window.
        
        Args:
            parent: The parent window
        """
        self.parent = parent
        self.popup = None
        
        # Visual theme colors
        self.colors = {
            "background": "#001a00",  # Very dark green
            "title": "#5dff5d",       # Bright green
            "subtitle": "#90ee90",    # Light green
            "button_bg": "#004d00",   # Dark green
            "button_fg": "#ccffcc",   # Very light green
            "button_hover": "#006600"  # Slightly brighter green
        }
    
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
        
        # Create frame for content
        content_frame = tk.Frame(self.popup, bg=self.colors["background"])
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Create title
        title_label = tk.Label(
            content_frame,
            text=title,
            font=("Arial", 24, "bold"),
            fg=self.colors["title"],
            bg=self.colors["background"]
        )
        title_label.pack(pady=(20, 10))
        
        # Create subtitle
        subtitle_label = tk.Label(
            content_frame,
            text=subtitle,
            font=("Arial", 14),
            fg=self.colors["subtitle"],
            bg=self.colors["background"],
            wraplength=width-60
        )
        subtitle_label.pack(pady=(0, 30))
        
        # Create button frame
        button_frame = tk.Frame(content_frame, bg=self.colors["background"])
        button_frame.pack(pady=10)
        
        # Store callbacks for keyboard shortcuts
        self.callback_next = callback_next
        self.callback_level_select = callback_level_select
        
        # Create buttons
        next_button = tk.Button(
            button_frame,
            text="Next Problem",
            bg=self.colors["button_bg"],
            fg=self.colors["button_fg"],
            font=("Arial", 12),
            relief=tk.RAISED,
            borderwidth=2,
            padx=15,
            pady=5,
            command=lambda: self.handle_button_click(callback_next)
        )
        next_button.grid(row=0, column=0, padx=10)
        
        level_select_button = tk.Button(
            button_frame,
            text="Level Select",
            bg=self.colors["button_bg"],
            fg=self.colors["button_fg"],
            font=("Arial", 12),
            relief=tk.RAISED,
            borderwidth=2,
            padx=15,
            pady=5,
            command=lambda: self.handle_button_click(callback_level_select)
        )
        level_select_button.grid(row=0, column=1, padx=10)
        
        # Add keyboard shortcuts
        self.popup.bind("<Return>", lambda e: self.handle_button_click(callback_next))  # Enter key for Next
        self.popup.bind("<Escape>", lambda e: self.handle_button_click(callback_level_select))  # Esc for Level Select
        
        # Add a small hint about keyboard shortcuts
        shortcuts_label = tk.Label(
            content_frame,
            text="Shortcuts: Enter = Next, Esc = Level Select",
            font=("Arial", 8),
            fg=self.colors["subtitle"],
            bg=self.colors["background"]
        )
        shortcuts_label.pack(side=tk.BOTTOM, pady=5)
        
        # Ensure popup stays on top
        self.popup.attributes('-topmost', True)
        self.popup.update()
        self.popup.attributes('-topmost', False)
        
        # Return the popup for reference
        return self.popup
        
    def handle_button_click(self, callback):
        """Handle button click event"""
        if callable(callback):
            callback()
        # No more animations to clean up, so we can just destroy the popup
        if self.popup and self.popup.winfo_exists():
            self.popup.destroy()

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