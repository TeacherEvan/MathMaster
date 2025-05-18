import tkinter as tk
import logging
import math
import time

class SolutionSymbolDisplay:
    def __init__(self, canvas, gameplay_screen_ref, drawing_complete_callback=None):
        self.canvas = canvas
        self.gameplay_screen = gameplay_screen_ref # Reference to access things like debug_mode
        self.drawing_complete_callback = drawing_complete_callback # Store the callback

        # Visual parameters - can be adjusted
        self.base_font_size = 22 # Original font size
        self.font_size_increase_factor = 1.3 # 30% increase
        self.current_font_size = int(self.base_font_size * self.font_size_increase_factor)
        
        self.base_char_width = 30 # Original char width, for reference in spacing calculations
        self.current_char_width_factor = 1.3 # Affects horizontal spacing
        
        self.text_color = "#D40000"  # "Beautiful Red" for revealed text
        self.shadow_color = self._calculate_shadow_color(self.text_color, -0.4) # Darker red for shadow
        self.shadow_offset = (2, 2)   # (x_offset, y_offset) for shadow

        self.max_lines_displayable = 8 # Max number of solution lines we'll attempt to draw

        # For pulsation effects
        self.pulsation_after_ids = {} # Stores after_ids for ongoing pulsations

        logging.info(f"SolutionSymbolDisplay initialized with font size: {self.current_font_size}")

        self.font_size = 20  # Base font size
        self.unrevealed_color = "#FFFFFF"  # White for unrevealed characters
        self.unrevealed_outline_color = "#FFFFFF" # White outline for unrevealed
        self.font_family = "Courier New"
        self.font = (self.font_family, self.font_size, "bold")
        self.char_width = 0  # Will be calculated
        self.line_height_multiplier = 1.5  # Adjusted line height multiplier
        self.drawn_symbol_items = {} # Stores {(line_idx, char_idx, 'text'/'shadow'): item_id}
        self.visible_chars_cache = set() # Cache visible_chars to optimize drawing checks
        self.current_solution_steps_cache = [] # Cache solution steps

        # Calculate character width once
        self._calculate_char_width()

    def _calculate_shadow_color(self, base_hex_color, factor):
        r = int(base_hex_color[1:3], 16)
        g = int(base_hex_color[3:5], 16)
        b = int(base_hex_color[5:7], 16)
        r = max(0, min(255, int(r * (1 + factor))))
        g = max(0, min(255, int(g * (1 + factor))))
        b = max(0, min(255, int(b * (1 + factor))))
        return f"#{r:02x}{g:02x}{b:02x}"

    def update_data(self, solution_steps, visible_chars):
        """Update the data to be displayed.
        Now relies on gameplay_screen.solution_char_details as the source of truth.
        solution_steps and visible_chars are passed for context but drawing decisions
        are primarily based on gameplay_screen.solution_char_details.
        """
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

    def _calculate_char_width(self):
        # Create a temporary item to measure character width
        if not self.canvas.winfo_exists():
            # If canvas isn't ready, defer or use a default. For now, default.
            self.char_width = self.font_size * 0.6 # Estimate
            return

        try:
            temp_text = self.canvas.create_text(0, 0, text="M", font=self.font, anchor=tk.NW)
            bbox = self.canvas.bbox(temp_text)
            if bbox:
                self.char_width = bbox[2] - bbox[0]
            else:
                self.char_width = self.font_size * 0.6 # Fallback if bbox fails
            self.canvas.delete(temp_text)
        except tk.TclError:
            self.char_width = self.font_size * 0.6 # Fallback if canvas interaction fails

        if self.char_width == 0: # Ensure it's never zero
            self.char_width = self.font_size * 0.6
        logging.info(f"Calculated char_width: {self.char_width} for font_size: {self.font_size}")

    def draw_symbols(self):
        """Draw the solution lines on the solution canvas with new visual requirements."""
        self.clear_all_visuals() # Clear old symbols first
        
        # Use solution_char_details from gameplay_screen directly
        solution_details_list = self.gameplay_screen.solution_char_details
        
        if not solution_details_list or not self.canvas.winfo_exists():
            if hasattr(self, 'drawing_complete_callback') and callable(self.drawing_complete_callback):
                self.drawing_complete_callback()
            return

        canvas_width, canvas_height = self.get_canvas_dimensions()
        
        if canvas_width is None or canvas_height is None:
            if self.canvas.winfo_exists():
                self.canvas.after(100, self.draw_symbols)
            return

        # Determine number of lines from the details list by finding unique line_idx
        if not solution_details_list: # Should be caught by earlier check, but good for safety
            if hasattr(self, 'drawing_complete_callback') and callable(self.drawing_complete_callback):
                self.drawing_complete_callback() # Call if no lines to draw
            return

        line_indices = sorted(list(set(d['line_idx'] for d in solution_details_list if d)))
        num_lines = len(line_indices)
        if num_lines == 0:
            if hasattr(self, 'drawing_complete_callback') and callable(self.drawing_complete_callback):
                self.drawing_complete_callback()
            return

        max_line_len = 0
        # Calculate max_line_len based on characters per line from solution_details_list
        chars_per_line = {}
        for detail in solution_details_list:
            if detail:
                chars_per_line[detail['line_idx']] = chars_per_line.get(detail['line_idx'], 0) + 1
        if chars_per_line: # Check if chars_per_line is not empty
             max_line_len = max(chars_per_line.values()) if chars_per_line else 1 # Max chars in any single line
        else: # Fallback if no character details are present (e.g., empty problem)
            max_line_len = 1

        if max_line_len == 0: max_line_len = 1

        available_height_for_font = canvas_height / num_lines
        dynamic_font_size_h = int(available_height_for_font / self.line_height_multiplier * 0.8)

        estimated_char_width_at_dynamic_font_size = max_line_len * (dynamic_font_size_h * 0.6)
        
        if estimated_char_width_at_dynamic_font_size > canvas_width * 0.9 and max_line_len > 0:
            dynamic_font_size_w = int((canvas_width * 0.9) / (max_line_len * 0.6))
        else:
            dynamic_font_size_w = dynamic_font_size_h

        self.font_size = max(10, min(dynamic_font_size_h, dynamic_font_size_w, 35))
        self.font = (self.font_family, self.font_size, "bold")
        self._calculate_char_width()

        line_spacing = self.font_size * self.line_height_multiplier
        total_text_height = num_lines * line_spacing
        start_y = (canvas_height - total_text_height) / 2 + line_spacing / 2

        shadow_offset_x = int(self.font_size * 0.05)
        shadow_offset_y = int(self.font_size * 0.05)

        self.character_positions = {}
        
        # Group details by line
        lines_data = {}
        for detail in solution_details_list:
            if detail: # Ensure detail is not None
                if detail['line_idx'] not in lines_data:
                    lines_data[detail['line_idx']] = []
                lines_data[detail['line_idx']].append(detail)

        for line_idx in line_indices: # Iterate through sorted unique line indices
            line_details = lines_data.get(line_idx, [])
            if not line_details: continue

            # Sort characters within the line by char_idx to ensure correct order
            line_details.sort(key=lambda d: d['char_idx'])
            
            # Calculate total width for this specific line
            current_line_width = sum(self.char_width for d in line_details if d and not d.get('is_placeholder', False)) # only count non-placeholders for width

            current_x = (canvas_width - current_line_width) / 2
            current_y = start_y + (line_idx * line_spacing) - (self.font_size / 2)

            for detail_idx, detail in enumerate(line_details):
                if not detail: continue # Skip if detail is None
                char_center_x = current_x + self.char_width / 2
                char_center_y = current_y + self.font_size / 2
                self.character_positions[(detail['line_idx'], detail['char_idx'])] = (char_center_x, char_center_y)
                
                if not detail.get('is_placeholder', False): # Only advance x for actual characters
                     current_x += self.char_width
        
        drawn_symbols_count = 0
        for detail in solution_details_list:
            if detail and detail.get('is_visible_on_b') and not detail.get('transported_to_c') and not detail.get('is_placeholder'):
                self._create_character(detail['line_idx'], detail['char_idx'], detail['char'])
                drawn_symbols_count +=1
        
        if self.gameplay_screen.debug_mode:
            logging.info(f"SolutionSymbolDisplay: Drew {drawn_symbols_count} visible symbols. Font size: {self.font_size}. Char width: {self.char_width}.")

        if hasattr(self, 'drawing_complete_callback') and callable(self.drawing_complete_callback):
            self.drawing_complete_callback()

    def _create_character(self, line_idx, char_idx, char):
        """Create a visible character (text and shadow) on the canvas and update GameplayScreen's solution_char_details."""
        if (line_idx, char_idx) not in self.character_positions:
            logging.warning(f"No position info for character at {line_idx}, {char_idx}")
            return

        text_center_x, text_center_y = self.character_positions[(line_idx, char_idx)]
        shadow_offset_x = int(self.font_size * 0.05)
        shadow_offset_y = int(self.font_size * 0.05)
        
        text_tag = f"ssd_{line_idx}_{char_idx}_text"
        shadow_tag = f"ssd_{line_idx}_{char_idx}_shadow"
        
        shadow_id = self.canvas.create_text(
            text_center_x + shadow_offset_x,
            text_center_y + shadow_offset_y,
            text=char, font=self.font, fill=self.shadow_color,
            anchor=tk.CENTER, tags=(shadow_tag, "solution_text_ssd")
        )
        
        text_id = self.canvas.create_text(
            text_center_x, text_center_y,
            text=char, font=self.font, fill=self.text_color,
            anchor=tk.CENTER, tags=(text_tag, "solution_text_ssd")
        )

        # Store in local cache for quick access (e.g., by get_symbol_coordinates)
        self.drawn_symbol_items[(line_idx, char_idx, 'text')] = text_id
        self.drawn_symbol_items[(line_idx, char_idx, 'shadow')] = shadow_id

        # Update the canonical list in GameplayScreen
        for detail in self.gameplay_screen.solution_char_details:
            if detail and detail['line_idx'] == line_idx and detail['char_idx'] == char_idx:
                detail['canvas_id'] = text_id # Store the main text_id
                detail['is_visible_on_b'] = True # Mark as drawn/visible
                # Ensure 'shadow_canvas_id' is also stored if needed elsewhere, or handle shadow deletion via tags
                break
    
    def _update_symbol_appearance(self, line_idx, char_idx):
        """Updates a symbol's appearance based on visibility flags in GameplayScreen.solution_char_details."""
        # Find the detail in GameplayScreen's list
        char_detail = None
        for detail in self.gameplay_screen.solution_char_details:
            if detail and detail['line_idx'] == line_idx and detail['char_idx'] == char_idx:
                char_detail = detail
                break
        
        if not char_detail:
            return

        is_visible_in_gs = char_detail.get('is_visible_on_b', False)
        is_transported_in_gs = char_detail.get('transported_to_c', False)
        is_placeholder_in_gs = char_detail.get('is_placeholder', False)
        
        # Determine if the symbol *should* be drawn on canvas B
        should_be_drawn_on_b = is_visible_in_gs and not is_transported_in_gs and not is_placeholder_in_gs

        # Check if it *is* currently drawn (by checking its canvas_id in the detail itself)
        is_currently_drawn_on_b = char_detail.get('canvas_id') is not None

        if should_be_drawn_on_b:
            if not is_currently_drawn_on_b:
                self._create_character(line_idx, char_idx, char_detail['char'])
            # If it should be drawn and is drawn, color/appearance is handled by _create_character or flash/pulse
        else: # Should NOT be drawn
            if is_currently_drawn_on_b:
                self._remove_character_from_canvas_and_gs_details(line_idx, char_idx)
    
    def _remove_character_from_canvas_and_gs_details(self, line_idx, char_idx):
        """Remove a character from the canvas AND update its state in GameplayScreen.solution_char_details."""
        char_detail_to_update = None
        for detail_in_list in self.gameplay_screen.solution_char_details:
            if detail_in_list and detail_in_list['line_idx'] == line_idx and detail_in_list['char_idx'] == char_idx:
                char_detail_to_update = detail_in_list
                break

        if char_detail_to_update and char_detail_to_update.get('canvas_id') is not None:
            text_id_to_delete = char_detail_to_update['canvas_id']
            # Construct shadow tag based on text tag or find shadow_id if stored
            shadow_tag_to_delete = f"ssd_{line_idx}_{char_idx}_shadow" # Assuming tag structure

            try:
                if text_id_to_delete: # Check if text_id_to_delete is not None
                    self.canvas.delete(text_id_to_delete)
                # Delete shadow by tag; more robust if shadow_id wasn't stored separately in detail
                shadow_items = self.canvas.find_withtag(shadow_tag_to_delete)
                for item_id in shadow_items:
                    self.canvas.delete(item_id)

            except tk.TclError:
                pass # Item might already be gone
            finally:
                # Update GameplayScreen's list
                char_detail_to_update['canvas_id'] = None
                char_detail_to_update['is_visible_on_b'] = False # Explicitly mark as not visible on B
                # transported_to_c flag is managed by GameplayScreen directly when transport occurs

    def reveal_symbol(self, line_idx, char_idx, color=None):
        """Ensures a symbol is created on canvas if it should be visible, and updates GameplayScreen's details."""
        # Find the detail in GameplayScreen's list to get the character and update flags
        char_detail_to_reveal = None
        for detail in self.gameplay_screen.solution_char_details:
            if detail and detail['line_idx'] == line_idx and detail['char_idx'] == char_idx:
                char_detail_to_reveal = detail
                break
        
        if not char_detail_to_reveal:
            logging.warning(f"Cannot reveal symbol at ({line_idx},{char_idx}): details not found in GameplayScreen list.")
            return

        # If it's a placeholder (space), do nothing visually here
        if char_detail_to_reveal.get('is_placeholder'):
            # GameplayScreen.reveal_char handles visibility flags, SSD doesn't draw placeholders
            return

        # Mark as visible in GameplayScreen's canonical list (this might be redundant if GS.reveal_char already does it)
        # However, this method is often called by GS.reveal_char, so ensuring it's set here is fine.
        char_detail_to_reveal['is_visible_on_b'] = True
        char_detail_to_reveal['transported_to_c'] = False # Ensure it's not marked as transported if being revealed

        # Create the character on canvas if it's not already there (canvas_id is None)
        if char_detail_to_reveal.get('canvas_id') is None:
            self._create_character(line_idx, char_idx, char_detail_to_reveal['char'])
        
        # Color change is handled by flash_symbol_color, not directly here for reveal.
        # If a specific 'color' was passed, it's likely from an old call pattern.
        # Modern flashing for reveal is handled by GameplayScreen calling flash_symbol_color.

    def flash_symbol_color(self, line_idx, char_idx, flash_color, duration_ms, original_color=None):
        """Flashes a symbol's color temporarily."""
        was_created_for_flash = False
        # Use gameplay_screen.current_solution_steps for bounds checking
        if (line_idx, char_idx, 'text') not in self.drawn_symbol_items:
            if line_idx < len(self.gameplay_screen.current_solution_steps):
                line = self.gameplay_screen.current_solution_steps[line_idx]
                if char_idx < len(line):
                    self._create_character(line_idx, char_idx, line[char_idx])
                    was_created_for_flash = True
                else:
                    logging.warning(f"Flash: Cannot flash symbol at ({line_idx},{char_idx}): char_idx out of bounds")
                    return
            else:
                logging.warning(f"Flash: Cannot flash symbol at ({line_idx},{char_idx}): line_idx out of bounds")
                return
        
        text_id = self.drawn_symbol_items.get((line_idx, char_idx, 'text'))
        shadow_id = self.drawn_symbol_items.get((line_idx, char_idx, 'shadow'))
        
        if not text_id:
            logging.warning(f"Flash: Text item for ({line_idx},{char_idx}) not found after creation attempt.")
            return
        
        shadow_flash_color = self._calculate_shadow_color(flash_color, -0.4)
        
        # Unique key for this flash
        flash_key = f"flash_{line_idx}_{char_idx}_{time.time()}"
        
        current_flash_ids = getattr(self, '_flash_after_ids', {})
        setattr(self, '_flash_after_ids', current_flash_ids)
        
        # Record if this was flash-created for proper cleanup
        if was_created_for_flash:
            current_flash_ids[f"{flash_key}_was_created"] = True
        
        try:
            self.canvas.itemconfig(text_id, fill=flash_color)
            if shadow_id:
                self.canvas.itemconfig(shadow_id, fill=shadow_flash_color)
            
            def _reset_after_flash():
                if not self.canvas.winfo_exists():
                    return
                
                # Check visibility based on gameplay_screen.solution_char_details
                detail_to_check = next((d for d in self.gameplay_screen.solution_char_details if d['line_idx'] == line_idx and d['char_idx'] == char_idx), None)
                should_stay_visible_gs = detail_to_check.get('is_visible_on_b', False) if detail_to_check else False
                
                if should_stay_visible_gs:
                    # Just reset to standard red color
                    final_color = original_color if original_color else self.text_color
                    final_shadow = self._calculate_shadow_color(final_color, -0.4)
                    try:
                        self.canvas.itemconfig(text_id, fill=final_color)
                        if shadow_id:
                            self.canvas.itemconfig(shadow_id, fill=final_shadow)
                    except tk.TclError:
                        pass  # Item might be gone
                else:
                    # Was flash-created and needs to be removed after flash
                    was_created = current_flash_ids.pop(f"{flash_key}_was_created", False)
                    if was_created:
                        self._remove_character(line_idx, char_idx)
                
                # Clean up flash key
                if flash_key in current_flash_ids:
                    del current_flash_ids[flash_key]
            
            # Schedule reset after duration
            current_flash_ids[flash_key] = self.canvas.after(duration_ms, _reset_after_flash)
            
        except tk.TclError as e:
            logging.warning(f"TclError during flash for ({line_idx},{char_idx}): {e}")
            if flash_key in current_flash_ids:
                del current_flash_ids[flash_key]

    def start_pulsation(self, line_idx, char_idx, pulse_color="#FFFF00", base_color=None, duration=1000, pulses=3):
        """Starts a pulsation effect on a symbol."""
        was_created_for_pulse = False
        # Use gameplay_screen.current_solution_steps for bounds checking
        if (line_idx, char_idx, 'text') not in self.drawn_symbol_items:
            if line_idx < len(self.gameplay_screen.current_solution_steps):
                line = self.gameplay_screen.current_solution_steps[line_idx]
                if char_idx < len(line):
                    self._create_character(line_idx, char_idx, line[char_idx])
                    was_created_for_pulse = True
                else:
                    logging.warning(f"Pulsate: Cannot pulsate symbol at ({line_idx},{char_idx}): char_idx out of bounds")
                    return
            else:
                logging.warning(f"Pulsate: Cannot pulsate symbol at ({line_idx},{char_idx}): line_idx out of bounds")
                return
        
        text_id = self.drawn_symbol_items.get((line_idx, char_idx, 'text'))
        shadow_id = self.drawn_symbol_items.get((line_idx, char_idx, 'shadow'))
        
        if not text_id:
            logging.warning(f"Pulsate: Text item for ({line_idx},{char_idx}) not found after creation attempt.")
            return

        pulse_key = f"pulse_{line_idx}_{char_idx}"
        # Cancel existing pulse
        if pulse_key in self.pulsation_after_ids and self.pulsation_after_ids[pulse_key]:
            try:
                self.canvas.after_cancel(self.pulsation_after_ids[pulse_key])
            except:
                pass
        
        # Record if this was created for pulsation
        if was_created_for_pulse:
            self.pulsation_after_ids[f"{pulse_key}_was_created"] = True
        
        is_visible = (line_idx, char_idx) in self.visible_chars_cache
        
        # Determine base color
        if base_color is None:
            if is_visible:
                actual_base_text_color = self.text_color
                actual_base_shadow_color = self.shadow_color
            else:
                # For a symbol that will be removed after pulsation,
                # use the visible colors during pulsation
                actual_base_text_color = self.text_color
                actual_base_shadow_color = self.shadow_color
        else:
            actual_base_text_color = base_color
            actual_base_shadow_color = self._calculate_shadow_color(base_color, -0.4)
        
        pulse_shadow_color = self._calculate_shadow_color(pulse_color, -0.4)
        delay = duration // (pulses * 2)
        
        def _animate_pulse(count=0):
            if not self.canvas.winfo_exists() or pulse_key not in self.pulsation_after_ids:
                return # Cancelled or canvas gone
            
            if count >= pulses * 2:
                # Pulsation complete
                # Check visibility based on gameplay_screen.solution_char_details
                detail_to_check = next((d for d in self.gameplay_screen.solution_char_details if d['line_idx'] == line_idx and d['char_idx'] == char_idx), None)
                should_stay_visible_gs = detail_to_check.get('is_visible_on_b', False) if detail_to_check else False
                
                if should_stay_visible_gs:
                    # Update appearance to standard visible state
                    try:
                        self.canvas.itemconfig(text_id, fill=self.text_color)
                        if shadow_id:
                            self.canvas.itemconfig(shadow_id, fill=self.shadow_color)
                    except tk.TclError:
                        pass # Item might be gone
                else:
                    # Was created just for pulsation, remove it
                    was_created = self.pulsation_after_ids.pop(f"{pulse_key}_was_created", False)
                    if was_created:
                        self._remove_character(line_idx, char_idx)
                
                # Clean up
                if pulse_key in self.pulsation_after_ids:
                    del self.pulsation_after_ids[pulse_key]
                
                return
            
            try:
                if count % 2 == 0:
                    # Pulse to highlight color
                    if text_id:
                        self.canvas.itemconfig(text_id, fill=pulse_color)
                    if shadow_id:
                        self.canvas.itemconfig(shadow_id, fill=pulse_shadow_color)
                else:
                    # Return to base color
                    if text_id:
                        self.canvas.itemconfig(text_id, fill=actual_base_text_color)
                    if shadow_id:
                        self.canvas.itemconfig(shadow_id, fill=actual_base_shadow_color)
                
                # Schedule next pulse frame
                self.pulsation_after_ids[pulse_key] = self.canvas.after(
                    delay, lambda: _animate_pulse(count + 1))
                
            except tk.TclError as e:
                logging.warning(f"TclError during pulsation for ({line_idx},{char_idx}): {e}")
                if pulse_key in self.pulsation_after_ids:
                    del self.pulsation_after_ids[pulse_key]
        
        # Start pulsation
        self.pulsation_after_ids[pulse_key] = self.canvas.after(0, lambda: _animate_pulse(0))

    def stop_specific_pulsation(self, pulse_key_or_line_idx, char_idx_if_line=None):
        """Stops a specific pulsation and handles cleanup."""
        pulse_key_to_stop = ""
        line_idx_for_revert = -1
        char_idx_for_revert = -1
        
        if char_idx_if_line is not None:
            # Called with (line_idx, char_idx)
            pulse_key_to_stop = f"pulse_{pulse_key_or_line_idx}_{char_idx_if_line}"
            line_idx_for_revert = pulse_key_or_line_idx
            char_idx_for_revert = char_idx_if_line
        else:
            # Called with full key string
            pulse_key_to_stop = pulse_key_or_line_idx
            try:
                parts = pulse_key_to_stop.split('_')
                if len(parts) == 3 and parts[0] == 'pulse':
                    line_idx_for_revert = int(parts[1])
                    char_idx_for_revert = int(parts[2])
            except ValueError:
                logging.error(f"Could not parse coordinates from pulse_key: {pulse_key_to_stop}")
                return
        
        # Cancel the pulse timer
        if pulse_key_to_stop in self.pulsation_after_ids:
            timer_id = self.pulsation_after_ids.pop(pulse_key_to_stop)
            if timer_id:
                try:
                    self.canvas.after_cancel(timer_id)
                except:
                    pass
        
        # Check if the symbol should remain visible
        if line_idx_for_revert != -1 and char_idx_for_revert != -1:
            # Check visibility based on gameplay_screen.solution_char_details
            detail_to_check = next((d for d in self.gameplay_screen.solution_char_details if d['line_idx'] == line_idx_for_revert and d['char_idx'] == char_idx_for_revert), None)
            should_stay_visible_gs = detail_to_check.get('is_visible_on_b', False) if detail_to_check else False
            
            if should_stay_visible_gs:
                # Update to standard visible appearance
                text_id = self.drawn_symbol_items.get((line_idx_for_revert, char_idx_for_revert, 'text'))
                shadow_id = self.drawn_symbol_items.get((line_idx_for_revert, char_idx_for_revert, 'shadow'))
                
                if text_id or shadow_id:
                    try:
                        if text_id:
                            self.canvas.itemconfig(text_id, fill=self.text_color)
                        if shadow_id:
                            self.canvas.itemconfig(shadow_id, fill=self.shadow_color)
                    except tk.TclError:
                        pass # Item might be gone
            else:
                # Was created for pulsation, now remove it
                was_created_key = f"{pulse_key_to_stop}_was_created"
                was_created = self.pulsation_after_ids.pop(was_created_key, False)
                
                if was_created:
                    self._remove_character(line_idx_for_revert, char_idx_for_revert)

    def stop_all_pulsations(self):
        """Stops all pulsations and handles cleanup."""
        pulse_keys = [k for k in self.pulsation_after_ids.keys() if k.startswith('pulse_') and not k.endswith('_was_created')]
        
        for key in pulse_keys:
            self.stop_specific_pulsation(key)
        
        # Clear any remaining timer IDs and flags
        self.pulsation_after_ids.clear()

    def get_symbol_coordinates(self, line_idx, char_idx):
        """Calculate the exact coordinates for a character in the solution canvas.
           This is crucial for interactions like teleportation or worm targeting."""
        # First check if the character is already drawn on the canvas, and use its actual position
        if (line_idx, char_idx, 'text') in self.drawn_symbol_items:
            text_id = self.drawn_symbol_items[(line_idx, char_idx, 'text')]
            try:
                bbox = self.canvas.bbox(text_id)
                if bbox:
                    center_x = (bbox[0] + bbox[2]) / 2
                    center_y = (bbox[1] + bbox[3]) / 2
                    logging.info(f"Using actual position for symbol at ({line_idx}, {char_idx}): ({center_x}, {center_y})")
                    return center_x, center_y
            except tk.TclError:
                # Item might not exist anymore, fall back to calculation
                logging.warning(f"TclError getting bbox for drawn symbol at ({line_idx}, {char_idx}), falling back to stored position")
                pass
        
        # Next, try checking for canvas item by tag as a fallback
        try:
            text_tag = f"ssd_{line_idx}_{char_idx}_text"
            items = self.canvas.find_withtag(text_tag)
            if items:
                bbox = self.canvas.bbox(items[0])
                if bbox:
                    center_x = (bbox[0] + bbox[2]) / 2
                    center_y = (bbox[1] + bbox[3]) / 2
                    logging.info(f"Found symbol by tag at ({line_idx}, {char_idx}): ({center_x}, {center_y})")
                    return center_x, center_y
        except tk.TclError:
            logging.warning(f"TclError getting bbox by tag for symbol at ({line_idx}, {char_idx})")
            pass
                
        # Check if we have a stored position
        if (line_idx, char_idx) in self.character_positions:
            center_x, center_y = self.character_positions[(line_idx, char_idx)]
            logging.info(f"Using stored position for symbol at ({line_idx}, {char_idx}): ({center_x}, {center_y})")
            return center_x, center_y
        
        # Do a fresh calculation if all else fails
        logging.warning(f"No position info found for ({line_idx}, {char_idx}), calculating from scratch")
        canvas_width, canvas_height = self.get_canvas_dimensions()
        if canvas_width is None or canvas_height is None:
            logging.error(f"Canvas dimensions not available for coordinate calculation at ({line_idx}, {char_idx})")
            return canvas_width / 2 if canvas_width else 300, canvas_height / 2 if canvas_height else 200 # Fallback

        num_steps_to_draw = min(len(self.gameplay_screen.current_solution_steps), self.max_lines_displayable)
        if num_steps_to_draw == 0 or line_idx >= num_steps_to_draw:
            logging.error(f"Line index {line_idx} is out of displayable range (max: {num_steps_to_draw})")
            return canvas_width / 2, canvas_height / 2 # Fallback if line_idx is out of displayable range

        # Ensure line_idx is within bounds before accessing current_solution_steps
        if line_idx < 0 or line_idx >= len(self.gameplay_screen.current_solution_steps):
            logging.error(f"SolutionSymbolDisplay: get_symbol_coordinates - line_idx {line_idx} out of bounds.")
            return canvas_width / 2, canvas_height / 2

        line_text = self.gameplay_screen.current_solution_steps[line_idx]
        
        if char_idx < 0 or char_idx >= len(line_text):
            logging.error(f"SolutionSymbolDisplay: get_symbol_coordinates - char_idx {char_idx} out of bounds for line.")
            return canvas_width / 2, canvas_height / 2

        # Calculate appropriate spacing
        top_offset_factor = 1/3
        drawing_area_height = canvas_height * (1 - top_offset_factor)
        calculated_line_height = drawing_area_height / (num_steps_to_draw + 1)
        
        target_font_height_for_sizing = calculated_line_height * 0.6
        effective_font_size = min(self.current_font_size, int(target_font_height_for_sizing))
        if effective_font_size <= 5: effective_font_size = 6
        
        effective_char_width = int(effective_font_size * 1.5 * self.current_char_width_factor)

        # Y position for the line (center of the character vertically)
        y_center = (canvas_height * top_offset_factor) + (calculated_line_height * (line_idx + 1))

        total_text_width = len(line_text) * effective_char_width
        x_start_for_line = (canvas_width - total_text_width) / 2
        if x_start_for_line < 10: x_start_for_line = 10

        # X coordinate for the center of the character
        char_left_edge_x = x_start_for_line + (char_idx * effective_char_width)
        x_center = char_left_edge_x + (effective_char_width / 2)
        
        # Save this calculated position for future reference
        self.character_positions[(line_idx, char_idx)] = (x_center, y_center)
        
        logging.info(f"Calculated position for symbol at ({line_idx}, {char_idx}): ({x_center}, {y_center})")
        return x_center, y_center

    def clear_all_visuals(self):
        """Clears all symbols and markers drawn by this class."""
        self.stop_all_pulsations()
        self.canvas.delete("solution_text_ssd")
        self.canvas.delete("line_marker_ssd")
        logging.info("SolutionSymbolDisplay: Cleared all visuals.")

    def mark_char_as_transported(self, line_idx, char_idx):
        """
        Marks a character as transported to Window C.
        This updates its state in gameplay_screen.solution_char_details
        and removes its visual representation from this canvas (Canvas B).
        """
        char_detail_to_update = None
        for detail in self.gameplay_screen.solution_char_details:
            if detail and detail['line_idx'] == line_idx and detail['char_idx'] == char_idx:
                char_detail_to_update = detail
                break

        if char_detail_to_update:
            # Update state in the canonical list
            char_detail_to_update['transported_to_c'] = True
            char_detail_to_update['is_visible_on_b'] = False # No longer visible on Canvas B
            
            # Remove from canvas B if it was drawn
            # Its canvas_id is stored in the detail itself
            text_id_to_delete = char_detail_to_update.get('canvas_id')
            shadow_tag_to_delete = f"ssd_{line_idx}_{char_idx}_shadow" # Assuming tag structure

            if text_id_to_delete:
                try:
                    self.canvas.delete(text_id_to_delete)
                except tk.TclError:
                    logging.warning(f"mark_char_as_transported: TclError deleting text_id {text_id_to_delete} for ({line_idx},{char_idx})")
                    pass # Item might already be gone
            
            # Delete shadow by tag
            shadow_items = self.canvas.find_withtag(shadow_tag_to_delete)
            for item_id in shadow_items:
                try:
                    self.canvas.delete(item_id)
                except tk.TclError:
                    logging.warning(f"mark_char_as_transported: TclError deleting shadow_item {item_id} for ({line_idx},{char_idx})")
                    pass # Item might already be gone

            # Clear canvas_id as it's no longer on this canvas
            char_detail_to_update['canvas_id'] = None
            
            # Clean from local drawn_symbol_items cache as well
            if (line_idx, char_idx, 'text') in self.drawn_symbol_items:
                del self.drawn_symbol_items[(line_idx, char_idx, 'text')]
            if (line_idx, char_idx, 'shadow') in self.drawn_symbol_items:
                del self.drawn_symbol_items[(line_idx, char_idx, 'shadow')]

            logging.info(f"SolutionSymbolDisplay: Marked char ({line_idx},{char_idx}) as transported. Visuals removed from Canvas B.")
        else:
            logging.warning(f"SolutionSymbolDisplay: mark_char_as_transported - Could not find char detail for ({line_idx},{char_idx}) to mark as transported.")

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