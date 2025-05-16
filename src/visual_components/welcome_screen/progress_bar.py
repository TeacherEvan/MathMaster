import tkinter as tk

class ProgressBar:
    def __init__(self, canvas):
        self.canvas = canvas

    def draw(self, progress):
        """Draw progress bar with the given progress value (0.0 to 1.0)"""
        # Remove old progress bar
        self.canvas.delete("progress_fill")
        
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        progress_width = min(400, width * 0.6)
        
        # Draw progress bar outline if it doesn't exist
        self.canvas.delete("progress_outline")
        self.canvas.create_rectangle(
            width // 2 - progress_width // 2,
            height * 0.9 - 10,
            width // 2 + progress_width // 2,
            height * 0.9 + 10,
            outline="#00AA00",
            width=2,
            tags="progress_outline"
        )
        
        # Draw filled portion
        filled_width = progress_width * progress
        self.canvas.create_rectangle(
            width // 2 - progress_width // 2,
            height * 0.9 - 10,
            width // 2 - progress_width // 2 + filled_width,
            height * 0.9 + 10,
            fill="#00FF00",
            outline="",
            tags="progress_fill"
        ) 