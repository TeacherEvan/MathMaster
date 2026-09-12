"""Extracted worm-animation subsystem from GameplayScreen.

Cluster of 4 methods (~304 lines) covering worm initialization, symbol
transport, targeted stealing, and solution-symbol updates.
Extracted 2026-09-13 surgical-implementation pass (plan OBJ-004).
All functions take ``self`` as first argument.
"""

import logging
import traceback

from WormsWindow_B import WormAnimation


def _init_worm_animation(self):
    """Initialize or recreate the worm animation system"""
    try:
        if not self.solution_canvas or not self.solution_canvas.winfo_exists():
            logging.warning("Solution canvas not ready for worm animation initialization. Retrying later.")
            # Retry after a short delay if we're not in transition
            if self.winfo_exists() and not getattr(self, 'in_level_transition', False):
                self.after(500, self._init_worm_animation)
            return

        # Get canvas dimensions with validation
        try:
            canvas_width = self.solution_canvas.winfo_width()
            canvas_height = self.solution_canvas.winfo_height()
        except tk.TclError:
            logging.warning("Canvas dimensions not available for worm animation. Retrying later.")
            if self.winfo_exists() and not getattr(self, 'in_level_transition', False):
                self.after(500, self._init_worm_animation)
            return
            
        # Skip if canvas dimensions aren't valid yet
        if canvas_width <= 1 or canvas_height <= 1:
            logging.info(f"Canvas dimensions not ready ({canvas_width}x{canvas_height}). Retrying worm animation.")
            if self.winfo_exists() and not getattr(self, 'in_level_transition', False):
                self.after(500, self._init_worm_animation)
            return

        logging.info("Initializing Worm Animation for GameplayScreen")
        
        # Clear any existing worm animation
        if hasattr(self, 'worm_animation') and self.worm_animation:
            try:
                self.worm_animation.stop_animation()
                self.worm_animation.clear_worms()
            except Exception as e:
                logging.warning(f"Error cleaning up old worm animation: {e}")
                
        # Create new worm animation instance
        self.worm_animation = WormAnimation(
            self.solution_canvas, 
            canvas_width=canvas_width, 
            canvas_height=canvas_height,
            symbol_transport_callback=self.handle_symbol_transport,
            symbol_targeted_for_steal_callback=self.handle_symbol_targeted_for_steal
        )
        
        # Reset worm-related state variables
        self.currently_targeted_by_worm = None
        self.solution_symbols_data_for_worms = []
        self.transported_by_worm_symbols = []
        
        logging.info("Worm Animation initialized and linked to callbacks successfully")
        
    except Exception as e:
        logging.error(f"Error initializing worm animation: {e}")
        import traceback
        logging.error(traceback.format_exc())
        # Don't retry on unexpected errors to avoid infinite loops

def handle_symbol_transport(self, transported_line_idx, transported_char_idx, transported_char):
    """Callback from WormAnimation when a symbol is successfully transported (stolen).
    Args:
        transported_line_idx (int): The original line index of the transported symbol.
        transported_char_idx (int): The original character index within the line of the transported symbol.
        transported_char (str): The character value of the transported symbol.
    """
    if not self.winfo_exists():
        logging.warning("GameplayScreen: handle_symbol_transport called but window no longer exists.")
        return

    logging.info(f"GameplayScreen: Received transport callback for char '{transported_char}' at L{transported_line_idx} C{transported_char_idx}")

    found_symbol_detail = None
    # detail_index = -1 # Not strictly needed if we operate on found_symbol_detail directly

    for detail in self.solution_char_details: # Iterate directly, no enumerate needed if index not used after find
        if detail.get('line_idx') == transported_line_idx and \
           detail.get('char_idx') == transported_char_idx:
            found_symbol_detail = detail
            break
    
    if found_symbol_detail:
        logging.info(f"Found matching symbol in solution_char_details: {found_symbol_detail}")
        original_canvas_id = found_symbol_detail.get('canvas_id')

        found_symbol_detail['transported_to_c'] = True
        found_symbol_detail['is_visible_on_b'] = False

        self.transported_solution_chars.append({
            'char': transported_char,
            'original_line': transported_line_idx,
            'original_char_idx': transported_char_idx,
            'original_canvas_id': original_canvas_id
        })

        if original_canvas_id and original_canvas_id != -1:
            try:
                if self.solution_canvas.winfo_exists() and original_canvas_id in self.solution_canvas.find_all():
                    self.solution_canvas.delete(original_canvas_id)
                    logging.info(f"Deleted canvas item {original_canvas_id} for transported symbol '{transported_char}' from Window B.")
            except tk.TclError as e:
                logging.warning(f"TclError deleting canvas_id {original_canvas_id} for transported char '{transported_char}': {e}")
        
        char_tuple_to_remove = (transported_line_idx, transported_char_idx)
        if char_tuple_to_remove in self.visible_chars:
            self.visible_chars.remove(char_tuple_to_remove)
            logging.info(f"Removed ({transported_line_idx}, {transported_char_idx}) from visible_chars.")

        if hasattr(self, 'solution_symbol_display') and self.solution_symbol_display:
            self.solution_symbol_display.mark_char_as_transported(transported_line_idx, transported_char_idx)

        self.incorrect_clicks += 1
        self._update_score_display()
        if hasattr(self, 'lock_animation') and self.lock_animation: # Check lock_animation exists
            self.lock_animation.shake_particles(intensity=0.5)

        if hasattr(self, 'error_anim_manager_c') and self.error_anim_manager_c:
            self.error_anim_manager_c.draw_crack_effect()

        # Add the stolen character to Window C as a falling symbol
        if hasattr(self, 'falling_symbols') and self.falling_symbols:
            x_pos_c = random.randint(50, self.canvas_c.winfo_width() - 50 if self.canvas_c.winfo_width() > 100 else 50)
            new_falling_symbol = {
                'char': transported_char,
                'x': x_pos_c,
                'y': 10, 
                'id': None, 
                'size': 44, 
                'is_transported': True, # Mark as transported
                'original_line_idx': transported_line_idx,
                'original_char_idx': transported_char_idx
            }
            self.falling_symbols.falling_symbols_on_screen.append(new_falling_symbol)
            logging.info(f"Added transported symbol '{transported_char}' to falling symbols in Window C.")

        logging.info(f"Symbol '{transported_char}' (L{transported_line_idx}, C{transported_char_idx}) processed as transported.")
        self.update_completion_percentage()
    else:
        logging.warning(
            f"Could not find matching symbol for transported char '{transported_char}' at L{transported_line_idx} C{transported_char_idx} in solution_char_details. "
            f"This might occur if solution_char_details was modified before callback completion."
        )
    # Worm animation scheduling is handled internally by WormAnimation class

    # Check if the transported symbol was the one targeted by player's help action
    if self.help_system and hasattr(self.help_system, 'currently_targeted_char_details'):
        if self.help_system.currently_targeted_char_details and \
           self.help_system.currently_targeted_char_details['line_idx'] == transported_line_idx and \
           self.help_system.currently_targeted_char_details['char_idx'] == transported_char_idx:
            logging.info("Symbol targeted by help system was transported by a worm. Resetting help target.")
            self.help_system.reset_help_target() # Reset help if the target is gone
    
    # self._update_score_display() # TODO: Implement or verify this method / Commented out due to AttributeError

    # Update worm animation with the new state of symbols
    self._update_worm_solution_symbols() # Refresh worm's view of symbols

def handle_symbol_targeted_for_steal(self, worm_id, symbol_data):
    """Callback from WormAnimation when a worm targets a symbol for stealing."""
    self.currently_targeted_by_worm = {
        'worm_id': worm_id,
        'symbol_data': symbol_data # Contains id, char, line_idx, char_idx of symbol in Window B
    }
    line_idx = symbol_data.get('line_idx')
    char_idx = symbol_data.get('char_idx')
    char_val = symbol_data.get('char')

    logging.info(f"Worm ID {worm_id} is targeting symbol: '{char_val}' (Canvas ID: {symbol_data.get('id')}) at L{line_idx}C{char_idx} for stealing.")
    
    # Make the targeted symbol pulsate
    if self.solution_symbol_display and line_idx is not None and char_idx is not None:
        # Determine base color (if visible, it's red, otherwise white)
        base_c = self.solution_symbol_display.text_color if (line_idx, char_idx) in self.visible_chars else "#FFFFFF"
        self.solution_symbol_display.start_pulsation(
            line_idx, 
            char_idx, 
            pulse_color="#FFA500", # Bright orange/yellow for targeting
            base_color=base_c,
            duration=1500, # Longer pulsation while targeted
            pulses=10 # Continuous pulsing
        )

def _update_worm_solution_symbols(self, initial_call=False):
    """Update the list of solution symbols for worm interaction"""
    # Skip updates if window doesn't exist or during transitions
    if not self.winfo_exists() or getattr(self, 'in_level_transition', False):
        logging.info("Skipping worm symbols update: window gone or in transition.")
        return
        
    # Initialize retry counter if needed
    if not hasattr(self, '_worm_update_retries'):
        self._worm_update_retries = 0
        
    # Limit excessive retries to avoid CPU overload
    if self._worm_update_retries > 3:  # Reduced from 5 to 3
        logging.warning(f"Too many worm update retries ({self._worm_update_retries}), delaying next update")
        if self.winfo_exists() and not getattr(self, 'in_level_transition', False):
            self.after(3000, self._reset_worm_update_retries)  # Increased delay
        return
        
    # Increment retry counter
    self._worm_update_retries += 1
    
    if not hasattr(self, 'worm_animation') or not self.worm_animation or not self.solution_symbol_display:
        if not initial_call and self.winfo_exists(): # Check again before scheduling
            self.after(1000, lambda: self._update_worm_solution_symbols(initial_call=False))
        else:
            logging.info("_update_worm_solution_symbols (initial_call or no reschedule): Components not ready.")
        return
        
    if not self.solution_canvas.winfo_exists():
        logging.warning("Solution canvas does not exist during worm symbol update.")
        return
        
    if not self.solution_symbol_display.character_positions:
        if self.winfo_exists(): # Check again before scheduling
            delay = 500 if initial_call else 250
            self.after(delay, lambda: self._update_worm_solution_symbols(initial_call=initial_call))
        return
        
    canvas_width, canvas_height = self.solution_symbol_display.get_canvas_dimensions()
    if canvas_width is None or canvas_height is None or canvas_width <= 1 or canvas_height <= 1:
        if self.winfo_exists(): # Check again before scheduling
            delay = 500 if initial_call else 250
            self.after(delay, lambda: self._update_worm_solution_symbols(initial_call=initial_call))
        return
    
    # OPTIMIZATION: After a level transition, wait a bit longer for canvas to be fully ready
    # This optimization is less critical now with the in_level_transition check at the start
    # but kept for robustness during the initial phase after transition completion.
    if hasattr(self, 'level_transition_timer') and self.level_transition_timer:
        time_since_transition = time.time() - self.level_transition_timer
        if time_since_transition < 1.0 and not self.in_level_transition: # Only if transition *just* finished
            logging.info(f"Recent level transition ({time_since_transition:.2f}s ago). Delaying worm symbol update.")
            if self.winfo_exists(): # Check again before scheduling
                self.after(200, lambda: self._update_worm_solution_symbols(initial_call=False))
            return
    
    self.solution_symbols_data_for_worms = []
    missing_tags = 0
    found_tags = 0
    
    try:
        # Iterate GameplayScreen's canonical solution_char_details
        for char_detail in self.solution_char_details:
            if not char_detail or char_detail.get('is_placeholder'):
                continue # Skip placeholders or empty details
            
            line_idx = char_detail['line_idx']
            char_idx = char_detail['char_idx']
            char_val = char_detail['char']

            # Get coordinates using SolutionSymbolDisplay's method which uses its character_positions cache or calculates
            coords = self.solution_symbol_display.get_symbol_coordinates(line_idx, char_idx)
            
            if not coords or coords[0] is None or coords[1] is None:
                # This might happen if SSD hasn't calculated positions yet for this specific char
                # logging.debug(f"_update_worm_solution_symbols: No coords from SSD for L{line_idx}C{char_idx}. Skipping.")
                continue
            
            # The canvas_id in char_detail is the source of truth for the drawn item ID
            symbol_canvas_id = char_detail.get('canvas_id') 
            is_visible_to_player = char_detail.get('is_visible_on_b', False)
            is_transported = char_detail.get('transported_to_c', False)

            if symbol_canvas_id and symbol_canvas_id != -1 and not is_transported:
                found_tags += 1 # Count as found if it has a canvas ID and isn't transported
                self.solution_symbols_data_for_worms.append({
                    'id': symbol_canvas_id,
                    'position': coords,
                    'char': char_val,
                    'line_idx': line_idx,
                    'char_idx': char_idx,
                    'visible_to_player': is_visible_to_player
                })
            elif not is_transported: # If no canvas_id but not transported, it's effectively missing for worms
                missing_tags += 1
                self.solution_symbols_data_for_worms.append({
                    'id': -1, # Mark as not on canvas / placeholder for worm logic
                    'position': coords,
                    'char': char_val,
                    'line_idx': line_idx,
                    'char_idx': char_idx,
                    'visible_to_player': is_visible_to_player,
                    'is_placeholder': True # Treat as placeholder if not drawn
                })
        
        if missing_tags > 0 and (self.debug_mode or initial_call):
            total_tags = missing_tags + found_tags
            logging.info(f"Worm symbols update: found {found_tags}/{total_tags} canvas items ({missing_tags} missing)")
        
        self.worm_animation.update_solution_symbols(self.solution_symbols_data_for_worms)
        self._worm_update_retries = 0
        
        # Only reschedule if not an initial call AND not in transition anymore
        if not initial_call and self.winfo_exists() and not getattr(self, 'in_level_transition', False):
            self.after(3000, lambda: self._update_worm_solution_symbols(initial_call=False))  # Increased from 2000 to 3000
            
    except Exception as e:
        logging.error(f"Error in _update_worm_solution_symbols: {e}")
        # Only reschedule if not an initial call AND not in transition anymore
        if not initial_call and self.winfo_exists() and not getattr(self, 'in_level_transition', False):
            self.after(3000, lambda: self._update_worm_solution_symbols(initial_call=False))  # Increased from 2000 to 3000
