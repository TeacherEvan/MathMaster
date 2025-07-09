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

        # Position feedback slightly higher and centered
        x = self.width / 2
        y = self.height - 70  # Moved up a bit

        # Determine colors based on message content (simple check for "Unlocked")
        is_positive = "unlocked" in message.lower() or "complete" in message.lower()
        
        bg_fill = "#2E7D32" if is_positive else "#C62828"  # Dark Green for positive, Dark Red for negative/other
        bg_outline = "#4CAF50" if is_positive else "#E53935" # Brighter Green/Red for outline
        text_fill = "#FFFFFF" # White text

        # Create a temporary text item to get bounding box for background sizing
        # Use a slightly larger font for bbox calculation to ensure padding
        temp_font_for_bbox = ("Courier New", 18, "bold")
        try:
            temp_text_item = self.canvas.create_text(x, y, text=message, font=temp_font_for_bbox, fill="white", anchor=tk.S)
            text_bbox = self.canvas.bbox(temp_text_item)
            self.canvas.delete(temp_text_item) # Delete temporary item
        except tk.TclError:
            text_bbox = None # Canvas might be gone

        if text_bbox:
            x1, y1, x2, y2 = text_bbox
            padding = 15 # Increased padding
            
            self.feedback_bg_id = self.canvas.create_rectangle(
                x1 - padding, y1 - padding, x2 + padding, y2 + padding,
                fill=bg_fill,
                outline=bg_outline,
                width=2 # Thicker outline
            )
            self.canvas.tag_lower(self.feedback_bg_id)

        # Create the actual feedback text
        try:
            self.feedback_text_id = self.canvas.create_text(
                x, y,
                text=message,
                font=("Courier New", 16, "bold"), # Changed font
                fill=text_fill,
                justify=tk.CENTER,
                anchor=tk.S # Anchor to the south (bottom) of the text, position y is bottom
            )
            if self.feedback_bg_id: # Ensure text is on top of the background if bg exists
                 self.canvas.tag_raise(self.feedback_text_id, self.feedback_bg_id)
            else: # Otherwise, just raise it generally
                 self.canvas.tag_raise(self.feedback_text_id)
        except tk.TclError: 
            self.feedback_text_id = None # Canvas might be gone

        # Schedule message removal
        if self.feedback_text_id or self.feedback_bg_id: # Only schedule if something was created
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