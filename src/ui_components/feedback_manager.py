import tkinter as tk

class FeedbackManager:
    def __init__(self, canvas, width, height):
        self.canvas = canvas
        self.width = width
        self.height = height
        self.feedback_text_id = None
        self.feedback_bg_id = None

    def show_feedback(self, message, duration=3000):
        """Displays a feedback message on the canvas for a certain duration."""
        if self.feedback_text_id:
            self.canvas.delete(self.feedback_text_id)
        if self.feedback_bg_id:
            self.canvas.delete(self.feedback_bg_id)

        # Position feedback at the bottom center
        x = self.width / 2
        y = self.height - 50  # Adjust as needed

        # Create a semi-transparent background for the text
        text_bbox = self.canvas.bbox(self.canvas.create_text(x, y, text=message, font=("Arial", 14), fill="white"))
        if text_bbox:
             # Add padding
            x1, y1, x2, y2 = text_bbox
            padding = 10
            self.feedback_bg_id = self.canvas.create_rectangle(
                x1 - padding, y1 - padding, x2 + padding, y2 + padding,
                fill="#333333",  # Dark gray background
                outline="#555555", # Slightly lighter border
                stipple="gray50" # Make it a bit transparent
            )
            self.canvas.tag_raise(self.feedback_bg_id) # Ensure bg is behind text if created after, otherwise lower

        self.feedback_text_id = self.canvas.create_text(
            x, y,
            text=message,
            font=("Arial", 16, "bold"),
            fill="#FFFF00",  # Bright yellow for visibility
            justify=tk.CENTER,
            anchor=tk.S # Anchor to the south (bottom) of the text
        )
        self.canvas.tag_raise(self.feedback_text_id) # ensure text is on top

        # Schedule message removal
        self.canvas.after(duration, self.clear_feedback)

    def clear_feedback(self):
        """Clears the feedback message from the canvas."""
        if self.feedback_text_id:
            try:
                self.canvas.delete(self.feedback_text_id)
            except tk.TclError:
                pass # Item might already be deleted
            self.feedback_text_id = None
        if self.feedback_bg_id:
            try:
                self.canvas.delete(self.feedback_bg_id)
            except tk.TclError:
                pass # Item might already be deleted
            self.feedback_bg_id = None

    def update_dimensions(self, width, height):
        """Updates the dimensions if the canvas resizes."""
        self.width = width
        self.height = height
        # If feedback is active, you might want to reposition it
        # For now, we'll let it be cleared or recreated on next show_feedback

    def get_dimensions(self):
        """Returns the current dimensions of the canvas."""
        return self.width, self.height

    def get_feedback_text_id(self):
        """Returns the ID of the feedback text."""
        return self.feedback_text_id

    def get_feedback_bg_id(self):
        """Returns the ID of the feedback background."""
        return self.feedback_bg_id 