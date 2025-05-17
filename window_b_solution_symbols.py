import tkinter as tk
import logging
import math

class SolutionSymbolDisplay:
    def __init__(self, canvas, gameplay_screen_ref):
        self.canvas = canvas
        self.gameplay_screen = gameplay_screen_ref # Reference to access things like debug_mode
        self.current_solution_steps = []
        self.visible_chars = set() # Set of (line_idx, char_idx)

        # Visual parameters - can be adjusted
        self.base_font_size = 22 # Original font size
        self.font_size_increase_factor = 1.3 # 30% increase
        self.current_font_size = int(self.base_font_size * self.font_size_increase_factor)
        
        self.base_char_width = 30 # Original char width, for reference in spacing calculations
        self.current_char_width_factor = 1.3 # Affects horizontal spacing
        
        self.text_color = "#FF0000"  # Bright Red
        self.shadow_color = "#550000" # Darker red for shadow
        self.shadow_offset = (2, 2)   # (x_offset, y_offset) for shadow

        self.max_lines_displayable = 8 # Max number of solution lines we'll attempt to draw

        # For pulsation effects
        self.pulsation_after_ids = {} # Stores after_ids for ongoing pulsations

        logging.info(f"SolutionSymbolDisplay initialized with font size: {self.current_font_size}")

    def update_data(self, solution_steps, visible_chars):
        """Update the data to be displayed."""
        self.current_solution_steps = solution_steps
        self.visible_chars = visible_chars
        # Redraw with new data
        self.draw_symbols()

    def get_canvas_dimensions(self):
        """Safely gets canvas dimensions, returns None if not ready."""
        if not self.canvas.winfo_exists():
            return None, None
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        if width <= 1 or height <= 1: # Canvas not ready
            return None, None
        return width, height

    def draw_symbols(self):
        """Draw the solution lines on the solution canvas with new visual requirements."""
        self.canvas.delete("solution_text_ssd") # Use a unique tag for this class
        self.canvas.delete("line_marker_ssd")

        canvas_width, canvas_height = self.get_canvas_dimensions()
        if canvas_width is None: # Canvas not ready
            self.canvas.after(50, self.draw_symbols) # Try again shortly
            return

        if not self.current_solution_steps:
            logging.info("SolutionSymbolDisplay: No solution steps to draw.")
            return

        # --- Dynamic Spacing Calculations ---
        num_steps_to_draw = min(len(self.current_solution_steps), self.max_lines_displayable)
        if num_steps_to_draw == 0:
            return

        # Vertical spacing: Distribute lines in the available 2/3 of canvas height
        top_offset_factor = 1/3  # Start drawing lines below the top 1/3
        drawing_area_height = canvas_height * (1 - top_offset_factor)
        
        # Calculate line_height: ensure enough space for font + some padding
        # Add 1 to num_steps_to_draw for spacing around the lines
        calculated_line_height = drawing_area_height / (num_steps_to_draw + 1)

        # Adjust font size if calculated_line_height is too small for current_font_size
        # Target a font height that's roughly 60-70% of the line_height
        target_font_height_for_sizing = calculated_line_height * 0.6
        effective_font_size = min(self.current_font_size, int(target_font_height_for_sizing))
        if effective_font_size <= 5: # Minimum readable font size
            effective_font_size = 6
            # If font size becomes too small, it means too many lines for the height.
            # For now, we proceed, but this could be a point for further heuristics if needed.

        # Horizontal character spacing (char_width)
        # This might need adjustment based on the longest line to prevent overflow,
        # but for a start, let's use a factor of the font size.
        # A common approximation for monospaced fonts is char_width = font_size * 0.6 to 0.8
        # Given base_char_width = 30 for font_size = 22, factor is ~1.36
        # Let's maintain a similar ratio or slightly more generous for the larger font.
        effective_char_width = int(effective_font_size * 1.5 * self.current_char_width_factor) # Adjusted factor
        
        font_config = ("Courier New", effective_font_size, "bold")
        
        logging.info(f"SolutionSymbolDisplay: Drawing {num_steps_to_draw} steps. Canvas: {canvas_width}x{canvas_height}. Line height: {calculated_line_height:.2f}. Font size: {effective_font_size}. Char width: {effective_char_width}")

        for i in range(num_steps_to_draw):
            if i >= len(self.current_solution_steps):
                break # Should not happen if num_steps_to_draw is correct

            line_text = self.current_solution_steps[i]
            if not line_text: # Skip empty lines
                continue

            # Y position for the line
            y_pos = (canvas_height * top_offset_factor) + (calculated_line_height * (i + 1))

            # Draw horizontal marker (underline) - subtle
            self.canvas.create_line(
                10, y_pos + effective_font_size * 0.7, # Position below text
                canvas_width - 10, y_pos + effective_font_size * 0.7,
                fill="#444444", # Darker gray for subtlety
                width=1,
                dash=(2, 2),
                tags=("line_marker_ssd",)
            )
            
            # Calculate starting X to center the text
            total_text_width = len(line_text) * effective_char_width
            x_start = (canvas_width - total_text_width) / 2
            if x_start < 10: x_start = 10 # Ensure some padding

            for j, char_val in enumerate(line_text):
                is_visible = (i, j) in self.visible_chars
                display_color = self.text_color if is_visible else "#FFFFFF" # White if not visible
                
                char_tag = f"ssd_{i}_{j}" # Unique tag prefix

                # Draw shadow first
                self.canvas.create_text(
                    x_start + (j * effective_char_width) + self.shadow_offset[0],
                    y_pos + self.shadow_offset[1],
                    text=char_val,
                    font=font_config,
                    fill=self.shadow_color,
                    anchor="w",
                    tags=("solution_text_ssd", char_tag, f"{char_tag}_shadow")
                )
                # Draw main text
                self.canvas.create_text(
                    x_start + (j * effective_char_width),
                    y_pos,
                    text=char_val,
                    font=font_config,
                    fill=display_color,
                    anchor="w",
                    tags=("solution_text_ssd", char_tag, f"{char_tag}_text")
                )
        if self.gameplay_screen.debug_mode:
             logging.info(f"SolutionSymbolDisplay: Drew {num_steps_to_draw} solution lines.")

    def reveal_symbol(self, line_idx, char_idx, color=None):
        """Reveals a specific symbol and applies a color."""
        if color is None:
            color = self.text_color
        
        char_tag_text = f"ssd_{line_idx}_{char_idx}_text"
        try:
            self.canvas.itemconfig(char_tag_text, fill=color)
            logging.info(f"SolutionSymbolDisplay: Revealed symbol ({line_idx},{char_idx}) with color {color}")
        except tk.TclError as e:
            logging.warning(f"SolutionSymbolDisplay: TclError revealing symbol ({line_idx},{char_idx}): {e}")

    def flash_symbol_color(self, line_idx, char_idx, flash_color, duration_ms, original_color=None):
        """Flashes a symbol with a specific color for a duration."""
        if original_color is None:
            original_color = self.text_color

        char_tag_text = f"ssd_{line_idx}_{char_idx}_text"
        char_tag_shadow = f"ssd_{line_idx}_{char_idx}_shadow" # Also flash shadow for consistency
        
        flash_shadow_color = self.adjust_color_brightness(flash_color, 0.5) # Make shadow darker version of flash

        # Unique key for managing this flash instance
        flash_key = f"flash_{line_idx}_{char_idx}"

        # Cancel any existing flash for this symbol
        if flash_key in self.pulsation_after_ids and self.pulsation_after_ids[flash_key]:
            self.canvas.after_cancel(self.pulsation_after_ids[flash_key])
            self.pulsation_after_ids[flash_key] = None

        try:
            self.canvas.itemconfig(char_tag_text, fill=flash_color)
            self.canvas.itemconfig(char_tag_shadow, fill=flash_shadow_color)

            def _reset_color():
                if self.canvas.winfo_exists():
                    try:
                        self.canvas.itemconfig(char_tag_text, fill=original_color)
                        # Re-apply original shadow color (could be dynamic if char wasn't visible)
                        # For now, assume original shadow if it was visible, else default shadow
                        # This part needs more robust handling if a character is flashed *before* reveal
                        is_char_visible = (line_idx, char_idx) in self.visible_chars
                        current_shadow_color = self.shadow_color if is_char_visible else self.adjust_color_brightness("#FFFFFF", 0.5) # Shadow for white
                        self.canvas.itemconfig(char_tag_shadow, fill=current_shadow_color)

                    except tk.TclError:
                        pass # Item might be gone
                if flash_key in self.pulsation_after_ids:
                    del self.pulsation_after_ids[flash_key]

            self.pulsation_after_ids[flash_key] = self.canvas.after(duration_ms, _reset_color)
        except tk.TclError as e:
            logging.warning(f"SolutionSymbolDisplay: TclError flashing symbol ({line_idx},{char_idx}): {e}")

    def start_pulsation(self, line_idx, char_idx, pulse_color="#FFFF00", base_color=None, duration=1000, pulses=3):
        """Makes a symbol pulsate brightly. Base color is its current revealed color."""
        if base_color is None:
            base_color = self.text_color # Assume it's revealed with the standard red

        char_tag_text = f"ssd_{line_idx}_{char_idx}_text"
        char_tag_shadow = f"ssd_{line_idx}_{char_idx}_shadow"
        
        pulse_shadow_color = self.adjust_color_brightness(pulse_color, 0.5)
        base_shadow_color = self.adjust_color_brightness(base_color, 0.5)

        pulse_key = f"pulse_{line_idx}_{char_idx}"

        # Cancel existing pulse for this symbol
        if pulse_key in self.pulsation_after_ids and self.pulsation_after_ids[pulse_key]:
            self.canvas.after_cancel(self.pulsation_after_ids[pulse_key])
        
        # Store current colors to revert if animation is interrupted or completes
        self.pulsation_after_ids[pulse_key] = {'base_text': base_color, 'base_shadow': base_shadow_color, 'timer': None}

        pulse_interval = duration // (pulses * 2) # Each pulse has an on and off state

        def _animate_pulse(count=0):
            if not self.canvas.winfo_exists() or pulse_key not in self.pulsation_after_ids:
                return # Stop if canvas gone or pulse cancelled

            is_on_state = count % 2 == 0
            
            current_text_color = pulse_color if is_on_state else base_color
            current_shadow_color = pulse_shadow_color if is_on_state else base_shadow_color

            try:
                self.canvas.itemconfig(char_tag_text, fill=current_text_color)
                self.canvas.itemconfig(char_tag_shadow, fill=current_shadow_color)
            except tk.TclError:
                if pulse_key in self.pulsation_after_ids: del self.pulsation_after_ids[pulse_key]
                return # Item likely gone

            if count < pulses * 2 -1:
                timer = self.canvas.after(pulse_interval, lambda: _animate_pulse(count + 1))
                if pulse_key in self.pulsation_after_ids: # Check if pulse_key still valid
                     self.pulsation_after_ids[pulse_key]['timer'] = timer
            else: # Animation finished
                # Ensure it ends on base color
                try:
                    self.canvas.itemconfig(char_tag_text, fill=base_color)
                    self.canvas.itemconfig(char_tag_shadow, fill=base_shadow_color)
                except tk.TclError: pass # Item might be gone
                if pulse_key in self.pulsation_after_ids:
                    del self.pulsation_after_ids[pulse_key]
        
        _animate_pulse()
        logging.info(f"SolutionSymbolDisplay: Started pulsation for symbol ({line_idx},{char_idx})")

    def stop_specific_pulsation(self, pulse_key):
        """Stops a specific pulsation animation and reverts the symbol to its base color."""
        if pulse_key in self.pulsation_after_ids:
            data = self.pulsation_after_ids[pulse_key]
            if isinstance(data, dict) and 'timer' in data and data['timer']:
                self.canvas.after_cancel(data['timer'])
                try:
                    # Revert to base color
                    # Extract line_idx, char_idx from key like "pulse_0_1"
                    _, line_idx_str, char_idx_str = pulse_key.split('_')
                    line_idx, char_idx = int(line_idx_str), int(char_idx_str)
                    char_tag_text = f"ssd_{line_idx}_{char_idx}_text"
                    char_tag_shadow = f"ssd_{line_idx}_{char_idx}_shadow"
                    if self.canvas.winfo_exists(): # Ensure canvas is still there
                        self.canvas.itemconfig(char_tag_text, fill=data['base_text'])
                        self.canvas.itemconfig(char_tag_shadow, fill=data['base_shadow'])
                    logging.info(f"SolutionSymbolDisplay: Stopped and reverted pulsation for {pulse_key}")
                except (tk.TclError, ValueError, AttributeError, KeyError) as e:
                    logging.warning(f"SolutionSymbolDisplay: Error reverting symbol color for {pulse_key} during specific stop: {e}")
            del self.pulsation_after_ids[pulse_key]
        else:
            logging.info(f"SolutionSymbolDisplay: No active pulsation found for key {pulse_key} to stop.")

    def stop_all_pulsations(self):
        """Stops all ongoing pulsation animations and reverts symbols to their original colors."""
        for key, data in list(self.pulsation_after_ids.items()):
            if isinstance(data, dict) and 'timer' in data and data['timer']: # Check for pulsation structure
                self.canvas.after_cancel(data['timer'])
                # Revert to base color if specified
                try:
                    # Extract line_idx, char_idx from key like "pulse_0_1"
                    _, line_idx_str, char_idx_str = key.split('_')
                    line_idx, char_idx = int(line_idx_str), int(char_idx_str)
                    char_tag_text = f"ssd_{line_idx}_{char_idx}_text"
                    char_tag_shadow = f"ssd_{line_idx}_{char_idx}_shadow"
                    self.canvas.itemconfig(char_tag_text, fill=data['base_text'])
                    self.canvas.itemconfig(char_tag_shadow, fill=data['base_shadow'])
                except (tk.TclError, ValueError, AttributeError) as e:
                    logging.warning(f"Error reverting symbol color for {key}: {e}")
            elif isinstance(data, str): # Simple flash timer ID
                 self.canvas.after_cancel(data)

        self.pulsation_after_ids.clear()
        logging.info("SolutionSymbolDisplay: Stopped all symbol pulsations.")

    def get_symbol_coordinates(self, line_idx, char_idx):
        """Calculate the exact coordinates for a character in the solution canvas.
           This is crucial for interactions like teleportation or worm targeting."""
        canvas_width, canvas_height = self.get_canvas_dimensions()
        if canvas_width is None:
            return canvas_width / 2 if canvas_width else 300, canvas_height / 2 if canvas_height else 200 # Fallback

        num_steps_to_draw = min(len(self.current_solution_steps), self.max_lines_displayable)
        if num_steps_to_draw == 0 or line_idx >= num_steps_to_draw :
             return canvas_width / 2, canvas_height / 2 # Fallback if line_idx is out of displayable range

        top_offset_factor = 1/3
        drawing_area_height = canvas_height * (1 - top_offset_factor)
        calculated_line_height = drawing_area_height / (num_steps_to_draw + 1)
        
        target_font_height_for_sizing = calculated_line_height * 0.6
        effective_font_size = min(self.current_font_size, int(target_font_height_for_sizing))
        if effective_font_size <= 5: effective_font_size = 6
        
        effective_char_width = int(effective_font_size * 1.5 * self.current_char_width_factor)

        # Y position for the line (center of the character vertically)
        y_center = (canvas_height * top_offset_factor) + (calculated_line_height * (line_idx + 1))
        
        # Ensure line_idx is within bounds before accessing current_solution_steps
        if line_idx < 0 or line_idx >= len(self.current_solution_steps):
            logging.error(f"SolutionSymbolDisplay: get_symbol_coordinates - line_idx {line_idx} out of bounds.")
            return canvas_width / 2, canvas_height / 2

        line_text = self.current_solution_steps[line_idx]
        
        if char_idx < 0 or char_idx >= len(line_text):
            logging.error(f"SolutionSymbolDisplay: get_symbol_coordinates - char_idx {char_idx} out of bounds for line.")
            return canvas_width / 2, canvas_height / 2

        total_text_width = len(line_text) * effective_char_width
        x_start_for_line = (canvas_width - total_text_width) / 2
        if x_start_for_line < 10: x_start_for_line = 10

        # X coordinate for the center of the character
        # The text is drawn with anchor="w", so char_x is the left edge.
        char_left_edge_x = x_start_for_line + (char_idx * effective_char_width)
        x_center = char_left_edge_x + (effective_char_width / 2)
        
        return x_center, y_center

    def adjust_color_brightness(self, hex_color, factor):
        """Adjusts brightness of a hex color. Factor < 1 darkens, > 1 lightens."""
        if not hex_color.startswith('#') or len(hex_color) != 7:
            return hex_color # Invalid format

        try:
            r = int(hex_color[1:3], 16)
            g = int(hex_color[3:5], 16)
            b = int(hex_color[5:7], 16)

            r = max(0, min(255, int(r * factor)))
            g = max(0, min(255, int(g * factor)))
            b = max(0, min(255, int(b * factor)))

            return f"#{r:02x}{g:02x}{b:02x}"
        except ValueError:
            return hex_color # Error in conversion

    def clear_all_visuals(self):
        """Clears all symbols and markers drawn by this class."""
        self.stop_all_pulsations()
        self.canvas.delete("solution_text_ssd")
        self.canvas.delete("line_marker_ssd")
        logging.info("SolutionSymbolDisplay: Cleared all visuals.")

    def handle_canvas_redraw_for_worms(self):
        """
        Called when GameplayScreen's draw_solution_lines (or equivalent) is called.
        Worms might be tracking symbols by their canvas ID. If these IDs change
        (e.g., because all symbols are redrawn), worms need to be updated.
        This function itself doesn't do much in SSD, as worms get data from GameplayScreen,
        but it's a placeholder for any direct state SSD might need to clear if worms
        were interacting with it more directly.
        The main thing is that GameplayScreen will call _update_worm_solution_symbols
        after SSD has redrawn, which will give worms new valid data.
        """
        # For now, this method primarily serves as a conceptual hook.
        # If SSD directly managed glows or other states that worms rely on by ID,
        # those would be cleared here.
        # Stop any ongoing animations like pulsations that might be tied to old symbol instances.
        self.stop_all_pulsations()
        logging.info("SolutionSymbolDisplay: Handling canvas redraw for worms (pulsations stopped).")

# Example usage (for testing within this file if needed)
if __name__ == '__main__':
    root = tk.Tk()
    root.geometry("600x400")
    
    # Mock GameplayScreen for testing reference
    class MockGameplayScreen:
        def __init__(self):
            self.debug_mode = True

    mock_gs = MockGameplayScreen()
    
    solution_canvas_test = tk.Canvas(root, bg="white", width=500, height=300)
    solution_canvas_test.pack(pady=20, expand=True, fill=tk.BOTH)
    
    display = SolutionSymbolDisplay(solution_canvas_test, mock_gs)
    
    test_solution_steps = [
        "x + 5 = 10",
        "x = 10 - 5",
        "x = 5",
        "CHECK:",
        "5 + 5 = 10",
        "10 = 10"
    ]
    test_visible_chars = set([(0,0), (0,1), (0,2), (1,0), (2,0), (2,1), (2,2), (2,3), (2,4)])

    def run_test_draw():
        display.update_data(test_solution_steps, test_visible_chars)

    def test_reveal():
        display.reveal_symbol(0, 4, "blue") # Reveal the '5' in blue
        display.reveal_symbol(1, 2) # Reveal the '='

    def test_flash():
        # Flash 'x' in first line
        display.flash_symbol_color(0, 0, "#00FF00", 500, original_color=display.text_color) 

    def test_pulsate():
        # Pulsate the final '5'
        display.start_pulsation(2, 4, pulse_color="#00FFFF", base_color=display.text_color, duration=1500, pulses=4)

    def test_pulsate_unrevealed():
        # Pulsate 'C' (not yet visible)
        display.start_pulsation(3,0, pulse_color="#FFA500", base_color="#FFFFFF", duration=2000, pulses=3)


    # Button to trigger drawing
    button_frame = tk.Frame(root)
    button_frame.pack()
    tk.Button(button_frame, text="Draw/Update Symbols", command=run_test_draw).pack(side=tk.LEFT)
    tk.Button(button_frame, text="Reveal Some", command=test_reveal).pack(side=tk.LEFT)
    tk.Button(button_frame, text="Flash 'x'", command=test_flash).pack(side=tk.LEFT)
    tk.Button(button_frame, text="Pulsate '5'", command=test_pulsate).pack(side=tk.LEFT)
    tk.Button(button_frame, text="Pulsate 'C'", command=test_pulsate_unrevealed).pack(side=tk.LEFT)


    # Initial draw after a short delay for canvas to be ready
    root.after(100, run_test_draw)
    
    root.mainloop() 