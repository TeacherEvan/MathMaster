import tkinter as tk
import random
import logging
import time

class FallingSymbols:
    """Handles the falling symbols animation and interaction in Window C of the game."""
    
    def __init__(self, canvas, symbols_list=None):
        """
        Initialize the falling symbols manager.
        
        Args:
            canvas: The tkinter canvas where symbols will be drawn
            symbols_list: Optional list of symbols to use (defaults to numbers, operators, etc.)
        """
        self.canvas = canvas
        self.falling_symbols_on_screen = []  # List of symbol objects/dictionaries
        self.animation_after_id = None  # For managing animation loop
        self.symbols_list = symbols_list or list("0123456789Xx +-=÷×*/()")
        self.game_over = False
        self.generation_rate = 0.60  # 60% chance to generate a new symbol
        logging.info(f"FallingSymbols instance {id(self)} created. Initial generation_rate: {self.generation_rate}. Symbols list length: {len(self.symbols_list)}")
        
    def animate_falling_symbols(self):
        """Manages the animation loop for falling symbols"""
        if self.game_over or not self.canvas.winfo_exists(): 
            if self.animation_after_id:
                self.canvas.after_cancel(self.animation_after_id)
                self.animation_after_id = None
            return

        try:
            self.update_falling_symbols()
            self.draw_falling_symbols()
            if self.animation_after_id:  # Clear previous before setting new
                self.canvas.after_cancel(self.animation_after_id)
            self.animation_after_id = self.canvas.after(50, self.animate_falling_symbols)  # Adjust speed (milliseconds)
        except Exception as e:
            if self.animation_after_id:
                self.canvas.after_cancel(self.animation_after_id)
                self.animation_after_id = None
            if self.canvas.winfo_exists():
                logging.error(f"Falling symbol animation error: {e}")
                print(f"Falling symbol animation error: {e}")

    def update_falling_symbols(self):
        """Updates positions and generates new symbols"""
        if not self.canvas.winfo_exists(): 
            return  # Check if window exists

        canvas_height = self.canvas.winfo_height()
        canvas_width = self.canvas.winfo_width()

        if canvas_height <= 1 or canvas_width <= 1: 
            return  # Canvas not ready

        # 7.7 seconds to fall from top to bottom (10% slower than original 7 seconds)
        fall_speed = canvas_height / (7.7 * 20)  # Pixels per 50ms interval for 7.7 sec fall

        # Move existing symbols
        next_symbols = []
        for symbol_info in self.falling_symbols_on_screen:
            symbol_info['y'] += fall_speed
            if symbol_info['y'] < canvas_height + symbol_info['size']:  # Keep if still visible
                next_symbols.append(symbol_info)
            else:
                # Symbol reached bottom, delete its canvas item if it exists
                try:
                    if symbol_info.get('id'):
                        self.canvas.delete(symbol_info['id'])
                except tk.TclError:  # Handle case where item might already be deleted
                    pass
        self.falling_symbols_on_screen = next_symbols

        # Add new symbols based on generation rate
        if random.random() < self.generation_rate:
            char = random.choice(self.symbols_list)
            x_pos = random.randint(20, canvas_width - 20)
            
            # Check if new symbol overlaps with existing ones spawned near the top
            spawn_margin = 30  # minimum horizontal gap
            can_spawn = True
            for symbol_info in self.falling_symbols_on_screen:
                if symbol_info['y'] < 50:  # Only check symbols near the top
                    if abs(symbol_info['x'] - x_pos) < spawn_margin:
                        can_spawn = False
                        break
            if can_spawn:
                new_symbol = {
                    'char': char,
                    'x': x_pos,
                    'y': 0,
                    'id': None,  # Canvas item ID
                    'size': 44  # Doubled size from 22 to 44
                }
                self.falling_symbols_on_screen.append(new_symbol)

    def draw_falling_symbols(self):
        """Draw all falling symbols on the canvas"""
        if not self.canvas.winfo_exists(): 
            return  # Check if window exists
        
        try:
            # Clear all existing symbols
            self.canvas.delete("falling_symbol")
            
            # Draw each symbol
            for symbol_info in self.falling_symbols_on_screen:
                # Create text with larger font size
                symbol_id = self.canvas.create_text(
                    symbol_info['x'],
                    symbol_info['y'],
                    text=symbol_info['char'],
                    font=("Courier New", 44, "bold"),  # Size 44
                    fill="#00FF00",
                    tags="falling_symbol"
                )
                symbol_info['id'] = symbol_id
        except tk.TclError:
            # Handle case where canvas is destroyed
            pass
    
    def clear_symbols(self):
        """Clear all falling symbols from the screen"""
        self.falling_symbols_on_screen = []
        if self.canvas.winfo_exists():
            self.canvas.delete("falling_symbol")
    
    def start_animation(self):
        """Start the falling symbols animation"""
        self.game_over = False
        self.animate_falling_symbols()
    
    def stop_animation(self):
        """Stop the falling symbols animation"""
        self.game_over = True
        if self.animation_after_id and self.canvas.winfo_exists():
            self.canvas.after_cancel(self.animation_after_id)
            self.animation_after_id = None
    
    def get_symbol_at_position(self, x, y, hit_radius=12):
        """
        Find the symbol at the given position.
        
        Args:
            x: X coordinate
            y: Y coordinate
            hit_radius: Radius around point to check for symbols (increased by 20%)
            
        Returns:
            (symbol_info, symbol_index) or (None, -1) if no symbol found
        """
        if not self.canvas.winfo_exists():
            return None, -1
            
        clicked_items = self.canvas.find_overlapping(
            x - hit_radius, y - hit_radius,
            x + hit_radius, y + hit_radius
        )
        
        if not clicked_items:
            return None, -1
        
        # Find the closest item to the click point
        closest_item = None
        closest_distance = float('inf')
        
        for item_id in clicked_items:
            try:
                bbox = self.canvas.bbox(item_id)
                if not bbox:
                    continue
                    
                # Calculate center of the item
                item_center_x = (bbox[0] + bbox[2]) / 2
                item_center_y = (bbox[1] + bbox[3]) / 2
                
                # Calculate distance to click
                distance = ((x - item_center_x)**2 + (y - item_center_y)**2)**0.5
                
                if distance < closest_distance:
                    closest_distance = distance
                    closest_item = item_id
            except Exception as e:
                logging.error(f"Error during item bounds calculation: {e}")
                continue
        
        if not closest_item:
            return None, -1
        
        # Find the symbol info for this item
        for i, symbol_info in enumerate(self.falling_symbols_on_screen):
            if symbol_info.get('id') == closest_item:
                return symbol_info, i
        
        return None, -1
    
    def remove_symbol(self, symbol_index):
        """Remove a symbol from tracking by index"""
        if 0 <= symbol_index < len(self.falling_symbols_on_screen):
            # Get ID before removing from list
            symbol_id = self.falling_symbols_on_screen[symbol_index].get('id')
            
            # Remove from list
            del self.falling_symbols_on_screen[symbol_index]
            
            # Delete the canvas item
            if symbol_id and self.canvas.winfo_exists():
                try:
                    self.canvas.delete(symbol_id)
                except tk.TclError:
                    pass
                    
    def set_symbols_list(self, symbols_list):
        """Update the list of symbols that can appear"""
        self.symbols_list = symbols_list 

    def reduce_generation_rate(self):
        """Slow down the symbol generation rate during level completion.
        This is called when a level is complete to gradually reduce visual clutter
        without abruptly stopping all animations.
        """
        # We don't immediately stop the animation, but make it generate fewer symbols
        # This creates a nice visual effect for level completion
        try:
            # Reduce the generation rate to 10%
            self.generation_rate = 0.10
            
            # Clear most existing symbols but keep a few for visual effect
            if len(self.falling_symbols_on_screen) > 5:
                # Keep just a few symbols
                keep_indices = random.sample(range(len(self.falling_symbols_on_screen)), 5)
                for i in sorted(range(len(self.falling_symbols_on_screen)), reverse=True):
                    if i not in keep_indices:
                        symbol_id = self.falling_symbols_on_screen[i].get('id')
                        if symbol_id and self.canvas.winfo_exists():
                            try:
                                self.canvas.delete(symbol_id)
                            except tk.TclError:
                                pass
            
                # Update the list to only keep selected symbols
                self.falling_symbols_on_screen = [self.falling_symbols_on_screen[i] for i in keep_indices]
            
            logging.info("Reduced falling symbols generation rate for level completion")
        except Exception as e:
            logging.error(f"Error reducing symbol generation rate: {e}")
        
        # The generation rate reduction happens naturally since update_falling_symbols
        # will now have a reduced chance to generate new symbols 