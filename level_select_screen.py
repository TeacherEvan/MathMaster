import tkinter as tk
from tkinter import ttk # For themed widgets if needed later
import logging
import time  # Add missing import
import os # Import for file operations
from gameplay_screen import GameplayScreen

class LevelSelectScreen(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent # Keep a reference to the parent (WelcomeScreen)
        self.title("MathMaster - Level Selection")
        
        # Set to full screen immediately
        self.attributes('-fullscreen', True)
        
        self.configure(bg="#000000") # Black background
        self.resizable(True, True) # Allow resizing
        
        # Explicitly set visibility and focus
        self.attributes('-alpha', 1.0)
        self.focus_force()
        
        # Bind Escape key to exit
        self.bind("<Escape>", self.go_back)
        
        # --- Title ---
        title_label = tk.Label(
            self,
            text = "Select Difficulty Level",
            font = ("Courier New", 24, "bold"),
            fg = "#00FF00", # Green text
            bg = "#000000"  # Black background
        )
        title_label.pack(pady = 30)

        # --- Button Frame ---
        button_frame = tk.Frame(self, bg="#000000")
        button_frame.pack(pady=20, fill="x", padx=50)

        # --- Level Buttons ---
        # Button Style Configuration (Optional: use ttk for better styling)
        button_font = ("Courier New", 14, "bold")
        button_bg = "#001800" # Dark green background
        button_fg = "#00AA00" # Lighter green text
        button_active_bg = "#003300"
        button_active_fg = "#00FF00"
        button_width = 25 # Fixed width for alignment

        # Define levels
        # USER PREFERENCE: The third difficulty level MUST be displayed as "Medium too".
        # Do NOT change this display name.
        levels = [
            ("Easy", "Easy"),              # Display Text, Internal Level Name
            ("Medium", "Medium"),
            ("Medium too", "Division")     # Display "Medium too", internal logic uses "Division"
        ]

        for display_text, internal_level in levels:
            button = tk.Button(
                button_frame,
                text = display_text,
                font = button_font,
                bg = button_bg,
                fg = button_fg,
                activebackground = button_active_bg,
                activeforeground = button_active_fg,
                width = button_width,
                relief = tk.RAISED,
                bd = 2,
                command=lambda lvl=internal_level: self.start_level(lvl)
            )
            button.pack(pady=10) # Add padding between buttons

        # --- Back Button ---
        back_button = tk.Button(
            self,
            text="< Back to Welcome",
            font=("Courier New", 10),
            bg="#111111",
            fg="#CCCCCC",
            activebackground="#333333",
            activeforeground="#FFFFFF",
            command=self.go_back
        )
        back_button.pack(pady=20, side=tk.BOTTOM)

        logging.info("Level Select Screen opened.")

    def handle_game_window_close(self, game_window):
        """Handles the closure of the gameplay window and clears its save file."""
        logging.info(f"[LSS.handle_game_window_close] Called for game_window: {game_window}")
        level_to_clear = None
        path_to_save_dir = None

        try:
            if game_window and game_window.winfo_exists():
                logging.info(f"[LSS.handle_game_window_close] game_window exists.")
                # Try direct access first for logging
                try:
                    level_to_clear = game_window.current_level
                    path_to_save_dir = game_window.save_dir
                    logging.info(f"[LSS.handle_game_window_close] Directly accessed current_level: {level_to_clear}, save_dir: {path_to_save_dir}")
                except AttributeError:
                    logging.warning("[LSS.handle_game_window_close] AttributeError accessing current_level/save_dir directly from game_window.")
                    # Fallback to getattr, though direct access should work if attributes exist
                    level_to_clear = getattr(game_window, 'current_level', None)
                    path_to_save_dir = getattr(game_window, 'save_dir', None)
                    logging.info(f"[LSS.handle_game_window_close] Via getattr - current_level: {level_to_clear}, save_dir: {path_to_save_dir}")

                if level_to_clear and path_to_save_dir:
                    save_file = os.path.join(path_to_save_dir, f"save_{level_to_clear}.json")
                    logging.info(f"[LSS.handle_game_window_close] Target save file for deletion: {save_file}")
                    if os.path.exists(save_file):
                        logging.info(f"[LSS.handle_game_window_close] Save file exists. Attempting to remove.")
                        try:
                            os.remove(save_file)
                            logging.info(f"[LSS.handle_game_window_close] Successfully CLEARED save file: {save_file} for level {level_to_clear}.")
                        except Exception as e:
                            logging.error(f"[LSS.handle_game_window_close] Error REMOVING save file {save_file}: {e}")
                    else:
                        logging.info(f"[LSS.handle_game_window_close] No save file found at {save_file}. Deletion not needed/possible.")
                else:
                    logging.warning(f"[LSS.handle_game_window_close] Could not determine current_level ('{level_to_clear}') or save_dir ('{path_to_save_dir}') from game_window. Cannot clear save file.")

                game_window.destroy()
                logging.info(f"[LSS.handle_game_window_close] Gameplay window {game_window} destroyed.")
            else:
                logging.info(f"[LSS.handle_game_window_close] Gameplay window {game_window} was None or did not exist when trying to handle close.")
        except tk.TclError as e:
            logging.warning(f"[LSS.handle_game_window_close] TclError during game_window handling: {e}. Game window might have been already destroyed.")
            pass
        except Exception as e:
            logging.error(f"[LSS.handle_game_window_close] Unexpected error: {e}", exc_info=True)

        self.deiconify()
        self.focus_force()
        logging.info("[LSS.handle_game_window_close] Level Select Screen deiconified and focused.")

    def start_level(self, level):
        """Starts the gameplay screen for the selected level."""
        logging.info(f"User selected level: {level}")
        print(f"Starting level: {level}")
        self.withdraw() # Hide level select screen
        game_window = GameplayScreen(self, level) # Pass LevelSelectScreen as parent
        game_window.protocol("WM_DELETE_WINDOW", lambda: self.handle_game_window_close(game_window))


    def go_back(self, event=None):
        """Closes the level select screen and shows the welcome screen again."""
        logging.info("User returned to Welcome Screen from Level Select.")
        
        parent = self.parent # Save parent reference before destroying self
        
        self.destroy() # Destroy this window first
        
        try:
            if parent and parent.winfo_exists(): # Ensure parent is valid
                # Reset welcome screen properties
                parent.clicked = False
                parent.start_time = time.time()
                
                parent.deiconify() # Show the welcome screen again
                
                # Schedule animate after showing parent to avoid timeout race condition
                parent.after(100, parent.animate)
            else:
                logging.warning("Parent window (WelcomeScreen) was not valid or already closed when trying to go back.")
        except tk.TclError as e:
            logging.warning(f"TclError when trying to show WelcomeScreen: {e}. It might have been closed.")
        except Exception as e:
            logging.error(f"Unexpected error in go_back: {e}", exc_info=True)

# Example of how to test this screen directly (optional)
if __name__ == '__main__':
    # Create a dummy root window for testing
    root = tk.Tk()
    root.title("Launcher (Test)")
    root.geometry("100x50")
    # root.withdraw() # Hide the dummy root initially if LevelSelectScreen is the primary test window

    # Dummy Welcome Screen class for testing parentage
    class DummyWelcome(tk.Tk): # Inherit from Tk so it can be a parent
        def __init__(self):
            super().__init__() # Call superclass constructor
            self.title("Dummy Welcome")
            self.geometry("800x600")
            # No need to withdraw if it's just a conceptual parent for LevelSelectScreen
            self.clicked = False # Dummy attribute
            self.start_time = time.time() # Dummy attribute

        def on_game_close(self, gw): # Kept for potential direct test calls if needed
             print("DummyWelcome: Game window closed (stub)")
             if gw and gw.winfo_exists():
                 gw.destroy()
             # self.destroy() # Don't destroy dummy welcome, it's the root for test

        def animate(self):
             print("DummyWelcome: Animate (stub)")

        def exit_game(self, event=None): # Make it callable
            print("DummyWelcome: Exit game (stub)")
            self.quit() # Proper way to close mainloop for test

    dummy_welcome_parent = DummyWelcome() # This will be the main window for the test
    # Initially hide the dummy welcome if LevelSelectScreen is shown immediately
    dummy_welcome_parent.withdraw() 

    app = LevelSelectScreen(dummy_welcome_parent) 
    
    # Ensure LevelSelectScreen's close button behavior is defined for the test
    # Typically, this Toplevel might just close itself, or call a method on its parent.
    # For this test, let's make it re-show the dummy_welcome_parent or quit.
    def on_level_select_close():
        print("LevelSelectScreen closed. Quitting test.")
        dummy_welcome_parent.quit()

    app.protocol("WM_DELETE_WINDOW", on_level_select_close)
    
    # Show the LevelSelectScreen
    app.deiconify()

    dummy_welcome_parent.mainloop()
    print("Test mainloop ended.") 