import tkinter as tk
import math
import random
import logging

class ErrorAnimation:
    """
    Class to handle error animations when incorrect symbols are selected.
    Creates and manages fractal-like crack effects on the canvas.
    """
    
    def __init__(self, canvas):
        """
        Initialize the error animation manager.
        
        Args:
            canvas: The canvas where cracks will be displayed
        """
        self.canvas = canvas
        self.saved_cracks = []
        self.visible = False
        
    def draw_crack_effect(self):
        """
        Draws a root-like crack with fractal branching patterns.
        Returns crack information that can be saved for redrawing.
        Sets the animation to visible.
        """
        if not self.canvas.winfo_exists():
            return None
            
        # Set visible flag to True when drawing a crack
        self.visible = True
        
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        if canvas_width <= 1 or canvas_height <= 1:
            return None

        # Generate random crack length with increased variability
        minus_count = random.randint(11, 61)
        crack_length = minus_count * 8

        def create_fractal_branch(start_x, start_y, length, angle, depth, width):
            """Recursively creates root-like branching patterns"""
            if length < 10 or depth > 4:
                return []  # Stop if too small or too deep
            
            # Calculate end point
            end_x = start_x + length * math.cos(angle)
            end_y = start_y + length * math.sin(angle)
            
            try:
                # Create main branch with randomly chosen color (blue or black)
                crack_color = "#000000" if random.random() < 0.5 else "#B0C4DE"
                branch_id = self.canvas.create_line(
                    start_x, start_y, end_x, end_y,
                    fill=crack_color,
                    width=width,
                    tags="crack",
                    capstyle=tk.ROUND,  # Rounded ends for organic look
                    joinstyle=tk.ROUND  # Rounded joints
                )
                
                branches = [{
                    'id': branch_id,
                    'coords': [start_x, start_y, end_x, end_y],
                    'width': width,
                    'color': crack_color,
                    'canvas': 'symbol'  # Always on symbol canvas
                }]
                
                # Create smaller branches with organic variation
                if depth < 4:  # Limit recursion depth
                    num_branches = random.randint(2, 3)
                    for _ in range(num_branches):
                        # Branch starts somewhere along the main branch
                        t = random.uniform(0.3, 0.7)
                        branch_start_x = start_x + t * (end_x - start_x)
                        branch_start_y = start_y + t * (end_y - start_y)
                        
                        # Randomize branch angles for organic look
                        angle_offset = random.uniform(math.pi/6, math.pi/3) * (1 if random.random() > 0.5 else -1)
                        new_angle = angle + angle_offset
                        
                        # Decrease length and width for each level
                        new_length = length * random.uniform(0.5, 0.7)
                        new_width = max(1, width * 0.7)
                        
                        # Recursively create sub-branches
                        branches.extend(create_fractal_branch(
                            branch_start_x, branch_start_y,
                            new_length, new_angle,
                            depth + 1, new_width
                        ))
                
                return branches
                
            except Exception as e:
                logging.error(f"Error creating fractal branch: {e}")
                return []

        try:
            # Start the main crack
            start_x = random.randint(0, canvas_width)
            start_y = random.randint(0, canvas_height)
            angle = random.uniform(0, 2 * math.pi)
            
            # Create the entire fractal pattern
            all_branches = create_fractal_branch(
                start_x, start_y,
                crack_length,
                angle,
                0,  # Initial depth
                random.uniform(2, 4)  # Initial width
            )
            
            # Store the crack info
            self.saved_cracks.append(all_branches)
            
            return all_branches
            
        except Exception as e:
            logging.error(f"Error drawing crack effect: {e}")
            return None

    def draw_shatter_effect(self):
        """Creates multiple cracks for game over effect and sets animation to visible"""
        if not self.canvas.winfo_exists():
            return
            
        # Set visible flag to True when drawing shatter effect
        self.visible = True
        
        # Create multiple cracks with lengths measured by minus count
        for _ in range(15):
            crack_info = self.draw_crack_effect()
            if not crack_info:  # If drawing failed, don't try to save it
                continue
                
        logging.info("Shatter effect displayed with proper crack visuals.")

    def redraw_saved_cracks(self):
        """Redraws all saved cracks after resize or other canvas changes"""
        if not self.canvas.winfo_exists() or not self.saved_cracks or not self.visible:
            return
            
        try:
            # Delete all existing cracks
            self.canvas.delete("crack")
            
            # Redraw each saved crack
            for crack_group in self.saved_cracks:
                if isinstance(crack_group, list):
                    for crack in crack_group:
                        try:
                            crack['id'] = self.canvas.create_line(
                                crack['coords'][0], crack['coords'][1],
                                crack['coords'][2], crack['coords'][3],
                                fill=crack['color'],
                                width=crack['width'],
                                tags="crack"
                            )
                        except (tk.TclError, Exception) as e:
                            logging.warning(f"Error redrawing crack: {e}")
        except Exception as e:
            logging.error(f"Error in redraw_saved_cracks: {e}")

    def clear_all_cracks(self):
        """Clears all cracks from the canvas and sets animation to invisible"""
        if self.canvas.winfo_exists():
            self.canvas.delete("crack")
        self.saved_cracks = []
        self.visible = False
    
    def get_saved_cracks(self):
        """Returns the current saved cracks data"""
        return self.saved_cracks
        
    def is_visible(self):
        """Returns whether the error animation is currently visible"""
        return self.visible and bool(self.saved_cracks) 