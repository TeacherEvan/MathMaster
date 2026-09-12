"""Extracted canvas-interaction subsystem from GameplayScreen.

Cluster of 14 methods (~972 lines) covering layout, symbol matching,
click handling, character reveal, and crack/error-visual management.
Extracted 2026-09-13 surgical-implementation pass (plan OBJ-004).
All functions take ``self`` as first argument.
"""

import logging
import traceback

from error_animation import ErrorAnimation


def _is_symbol_match(self, clicked_char, expected_char):
    """
    Check if a clicked symbol matches the expected character.
    Uses Unicode normalization and handles special cases.
    
    Args:
        clicked_char: The character that was clicked
        expected_char: The character that's expected in the solution
        
    Returns:
        bool: True if the characters match, False otherwise
    """
    import unicodedata
    
    # Normalize both strings to ensure consistent comparison
    clicked_norm = unicodedata.normalize('NFKC', clicked_char)
    expected_norm = unicodedata.normalize('NFKC', expected_char)
    
    # Direct match after normalization
    if clicked_norm == expected_norm:
        logging.info(f"Direct match: '{clicked_char}' == '{expected_char}'")
        return True
        
    # Handle special cases - multiplication
    if (clicked_norm in ['x', 'X', '×', '*'] and 
        expected_norm in ['x', 'X', '×', '*']):
        logging.info(f"Multiplication match: '{clicked_char}' matches '{expected_char}'")
        return True
        
    # Handle special cases - division
    if (clicked_norm in ['/', '÷'] and 
        expected_norm in ['/', '÷']):
        logging.info(f"Division match: '{clicked_char}' matches '{expected_char}'")
        return True
        
    # Handle special case - minus and en-dash/em-dash
    if (clicked_norm in ['-', '–', '—'] and 
        expected_norm in ['-', '–', '—']):
        logging.info(f"Dash match: '{clicked_char}' matches '{expected_char}'")
        return True
        
    # No match found
    logging.info(f"No match: '{clicked_char}' != '{expected_char}'")
    return False

def redraw_game_elements(self):
    """Redraw elements that depend on window size"""
    # Redraw solution lines using the new display class
    if self.solution_symbol_display:
        self.solution_symbol_display.update_data(self.current_solution_steps, self.visible_chars)
    
    # Redraw saved cracks using the error animation
    if self.error_animation:
        self.error_animation.redraw_saved_cracks()
    # Optionally redraw falling symbols if their spawn area changes significantly
    # self.draw_falling_symbols() # Might cause flicker, test needed
    if hasattr(self, 'symbol_canvas') and self.symbol_canvas.winfo_exists():
        s_width = self.symbol_canvas.winfo_width()
        s_height = self.symbol_canvas.winfo_height()
        if hasattr(self, 'feedback_manager') and self.feedback_manager:
            self.feedback_manager.update_dimensions(s_width, s_height)
            # No need to clear feedback here, it has a timeout or is cleared on game state changes

def create_layout(self):
    """Creates the three-window layout"""
    # Configure row/column weights for responsiveness
    self.grid_rowconfigure(0, weight=1)
    self.grid_columnconfigure(0, weight=25) # Window A ~25%
    self.grid_columnconfigure(1, weight=1)  # Separator
    self.grid_columnconfigure(2, weight=40) # Window B ~40%
    self.grid_columnconfigure(3, weight=1)  # Separator
    self.grid_columnconfigure(4, weight=35) # Window C ~35%

    # --- Window A (Problem Display) ---
    self.frame_a = tk.Frame(self, bg="#111111", bd=2, relief=tk.SUNKEN)
    self.frame_a.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
    self.frame_a.grid_columnconfigure(0, weight=1)
    # Configure rows for problem prefix, equation, and lock animation in center
    self.frame_a.grid_rowconfigure(0, weight=0)  # Problem Prefix Label
    self.frame_a.grid_rowconfigure(1, weight=0)  # Problem Equation Label
    self.frame_a.grid_rowconfigure(2, weight=1)  # Lock Animation Canvas (centered)

    # Problem Prefix Label
    self.problem_prefix_label = tk.Label(
        self.frame_a, text="Problem",
        font=("Courier New", 34, "bold"),
        fg="#00FF00", bg="#111111"
    )
    self.problem_prefix_label.grid(row=0, column=0, padx=10, pady=(10,5), sticky="n")

    # Problem Equation Label (now at row 1)
    self.problem_equation_label = tk.Label(
        self.frame_a, text="Loading...",
        font=("Courier New", 34, "bold"),
        fg="#00FF00", bg="#111111",
        wraplength=200  # Adjust as needed based on frame width
    )
    self.problem_equation_label.grid(row=1, column=0, padx=10, pady=(5,10), sticky="new") # sticky includes e,w
    self.frame_a.bind("<Configure>", lambda e: self.problem_equation_label.config(wraplength=e.width-20))

    # No spacer needed as the lock canvas will take center position

    # Lock Animation Canvas - Using responsive sizing
    self.lock_canvas = tk.Canvas(self.frame_a, bg="#111111", highlightthickness=0)
    self.lock_canvas.grid(row=2, column=0, pady=(10,15), sticky="nsew") # Center position in row 2
    
    # Initial lock animation with placeholder values
    # The actual size will be set properly in the _update_lock_dimensions method
    self.lock_animation = LockAnimation(
        self.lock_canvas, 
        x=50, 
        y=50, 
        size=100,
        level_name=self.current_level  # Pass the current level name
    )
    
    # Bind the frame resize event to update lock dimensions
    self.frame_a.bind("<Configure>", self._update_lock_dimensions)

    # --- Separator 1 ---
    sep1 = tk.Frame(self, width=2, bg="#00FF00")
    sep1.grid(row=0, column=1, sticky="ns")

    # --- Window B (Solution Steps) ---
    # Modified: Changed bd to 0, removed the green border, made bg white
    self.frame_b = tk.Frame(self, bg="#FFFFFF", bd=0, relief=tk.FLAT)
    self.frame_b.grid(row=0, column=2, sticky="nsew", padx=5, pady=5)
    self.frame_b.grid_columnconfigure(0, weight=1)
    
    # Configure rows for help button and solution lines
    self.frame_b.grid_rowconfigure(0, weight=0)  # Help button area - fixed height
    self.frame_b.grid_rowconfigure(1, weight=1)  # Solution lines area - expandable
    
    # Create a dedicated container frame for the help button to ensure visibility
    # Ensure this container does not have a visible border or distracting background
    self.help_button_container = tk.Frame(self.frame_b, bg="#FFFFFF", bd=0, relief=tk.FLAT) # Ensure bg matches frame_b and no border
    self.help_button_container.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
    self.help_button_container.grid_propagate(False)  # Force fixed height
    
    # Add Help Button to the container
    print("Creating help button...")
    try:
        self.help_button = HelpButton(self.help_button_container, self) # Pass self.help_button_container
        print("Help button created successfully!")
    except Exception as e:
        print(f"ERROR creating help button: {e}")
        logging.error(f"Failed to create help button: {e}")

    # Canvas for Solution Lines
    # Ensure solution_canvas also has no border and matches the frame_b background
    self.solution_canvas = tk.Canvas(self.frame_b, bg="#FFFFFF", highlightthickness=0, bd=0, relief=tk.FLAT)
    self.solution_canvas.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
    
    # Make the solution canvas completely invisible initially (0% opacity)
    self.solution_canvas.config(bg="#FFFFFF")
    self.solution_canvas_visible = False
    
    # Set a flag to track if help button has been clicked
    self.help_button_clicked = False

    # --- Separator 2 ---
    sep2 = tk.Frame(self, width=2, bg="#00FF00")
    sep2.grid(row=0, column=3, sticky="ns")

    # --- Window C (Symbol Interaction) ---
    self.frame_c = tk.Frame(self, bg="#050505", bd=2, relief=tk.SUNKEN)
    self.frame_c.grid(row=0, column=4, sticky="nsew", padx=5, pady=5)
    self.frame_c.grid_rowconfigure(0, weight=1)
    self.frame_c.grid_columnconfigure(0, weight=1)

    self.symbol_canvas = tk.Canvas(self.frame_c, bg="#050505", highlightthickness=0)
    self.symbol_canvas.grid(row=0, column=0, sticky="nsew")
    
    # Bind click handler for the symbol canvas only
    self.symbol_canvas.bind("<Button-1>", self.handle_canvas_c_click)
    
    # Initialize teleport manager after both canvases are created
    self.teleport_manager = SymbolTeleportManager(self.symbol_canvas, self.solution_canvas)

def _update_lock_dimensions(self, event=None):
    """Update lock canvas and animation dimensions based on parent frame size"""
    if not hasattr(self, 'frame_a') or not self.frame_a.winfo_exists():
        return
        
    # Get the current dimensions of frame_a
    frame_width = self.frame_a.winfo_width()
    frame_height = self.frame_a.winfo_height()
    
    # Skip if dimensions aren't valid yet
    if frame_width <= 1 or frame_height <= 1:
        return
        
    # Calculate available space for lock (considering the problem labels in rows 0 and 1)
    problem_prefix_height = self.problem_prefix_label.winfo_height()
    problem_equation_height = self.problem_equation_label.winfo_height()
    padding_height = 40  # Account for padding between elements
    
    available_height = frame_height - problem_prefix_height - problem_equation_height - padding_height
    
    # Calculate appropriate lock canvas dimensions (80% of available width, 90% of available height)
    lock_canvas_width = int(frame_width * 0.8)
    lock_canvas_height = int(available_height * 0.9)
    
    # Ensure minimum dimensions
    lock_canvas_width = max(lock_canvas_width, 100)
    lock_canvas_height = max(lock_canvas_height, 120)
    
    # Calculate appropriate lock size
    # Original factor was 0.7, then 0.35. New factor is 0.35 * 0.9 = 0.315
    lock_size = int(min(lock_canvas_width, lock_canvas_height) * 0.315) # Further 10% reduction
    lock_size = max(lock_size, 30) # Ensure a minimum reasonable lock size (e.g., 30px, adjusted from 40)
    
    # Configure the canvas dimensions
    self.lock_canvas.config(width=lock_canvas_width, height=lock_canvas_height)
    
    # If lock animation exists, recreate it with new dimensions
    if hasattr(self, 'lock_animation') and self.lock_animation:
        # Store current state if needed
        unlocked_parts = self.lock_animation.unlocked_parts if hasattr(self.lock_animation, 'unlocked_parts') else 0
        
        # Clear existing animation
        self.lock_animation.clear_visuals()
        
        # Create new animation with appropriate size
        self.lock_animation = LockAnimation(
            self.lock_canvas, 
            x=lock_canvas_width/2, 
            y=lock_canvas_height * 0.65, # Moved south by 15% of canvas height (0.5 + 0.15 = 0.65)
            size=lock_size,
            level_name=self.current_level
        )
        
        # Restore state if needed
        for _ in range(unlocked_parts):
            self.lock_animation.unlock_next_part()
            
    # Update the problem equation wraplength while we're here
    self.problem_equation_label.config(wraplength=frame_width-20)

def load_new_problem(self):
    """Loads a random problem for the selected level"""
    logging.info(f"Attempting to load new problem for level: {self.current_level}")
    
    self.solution_char_details.clear() # Clear details from previous problem

    if self.current_level not in PROBLEMS:
        logging.error(f"Invalid level: {self.current_level}")
        self.problem_prefix_label.config(text="Error")
        self.problem_equation_label.config(text="Invalid level selected.")
        self.current_problem = ""
        self.current_solution_steps = []
        if self.solution_symbol_display:
            self.solution_symbol_display.update_data([], set())
        return
        
    if not PROBLEMS[self.current_level]:
        logging.error(f"No problems found for level: {self.current_level}")
        self.problem_prefix_label.config(text="Error")
        self.problem_equation_label.config(text="No equations available for this level.")
        self.current_problem = ""
        self.current_solution_steps = []
        if self.solution_symbol_display:
            self.solution_symbol_display.update_data([], set())
        return

    self.clear_all_cracks()  # Clear any existing cracks
    
    # Clear falling symbols
    if self.falling_symbols:
        self.falling_symbols.clear_symbols()
        self.falling_symbols.generation_rate = 0.60 # Reset generation rate
        logging.info("Falling symbols cleared and generation rate reset.")
        
    self.completed_line_indices_for_problem.clear() # Reset for new problem
    if self.lock_animation:
        self.lock_animation.reset()
    
    if self.solution_symbol_display: # Clear previous symbols from new display
        self.solution_symbol_display.clear_all_visuals()

    available_problems = PROBLEMS[self.current_level]
    logging.info(f"Available problems for {self.current_level}: {len(available_problems)}")
    
    # Filter out recently used problems AND any empty/whitespace-only problem strings
    fresh_problems = [p.strip() for p in available_problems if p.strip() and p not in self.last_problems]
    logging.info(f"Fresh problems available: {len(fresh_problems)}")
    
    if not fresh_problems:
        # If all fresh problems were used or were empty, try from all available non-empty problems (excluding last one if possible)
        logging.warning(f"No fresh problems available for {self.current_level}, using full problem set")
        fresh_problems = [p.strip() for p in available_problems if p.strip() and (not self.last_problems or p != self.last_problems[-1])]
        
        if not fresh_problems:
             # This means ALL problems for the level are empty/whitespace or only one bad one repeats
             logging.error(f"All problems for level {self.current_level} are empty or have been used. Cannot load new problem.")
             self.problem_prefix_label.config(text="Error")
             self.problem_equation_label.config(text=f"No valid problems for {self.current_level}.")
             self.current_problem = "" # Ensure problem state is cleared
             self.current_solution_steps = []
             if self.solution_symbol_display:
                 self.solution_symbol_display.update_data([], set())
             return
    
    try:
        self.current_problem = random.choice(fresh_problems)
        # self.current_problem should already be stripped from list comprehension, but strip again to be safe.
        self.current_problem = self.current_problem.strip()
        logging.info(f"Selected problem: '{self.current_problem}'")
        
        # Update last_problems history to prevent immediate repetition in the same session
        if self.current_problem: # Only add if a valid problem was chosen
            self.last_problems.append(self.current_problem)
            if len(self.last_problems) > self.max_history:
                self.last_problems.pop(0)
        
        # Final check if problem is somehow still empty (should be caught by list comprehensions)
        if not self.current_problem:
            logging.error(f"Load New Problem: Selected an empty problem string for level '{self.current_level}' despite filtering.")
            self.problem_prefix_label.config(text="Error")
            self.problem_equation_label.config(text="Problem loading failed.")
            self.current_solution_steps = [] # Clear steps
            if self.solution_symbol_display:
                self.solution_symbol_display.update_data([], set())
            return
        
        # Format the problem text - split at colon
        display_text = self.current_problem
        if ":" in display_text:
            prefix, equation = display_text.split(":", 1)
            self.problem_prefix_label.config(text=prefix.strip())
            self.problem_equation_label.config(text=equation.strip())
        else:
            # For problems without a colon, only show the equation part, not the full solution step if it matches
            # If the first solution step is identical to the problem, only show the problem as the equation
            solution_steps = generate_solution_steps(display_text)
            if solution_steps and solution_steps[0].strip() == display_text.strip():
                self.problem_prefix_label.config(text="Problem")
                self.problem_equation_label.config(text=display_text.strip())
            else:
                # Fallback: show as before
                self.problem_prefix_label.config(text="Problem")
                self.problem_equation_label.config(text=display_text.strip())

        # Reset game state for new problem
        self.visible_chars = set()
        self.incorrect_clicks = 0
        self.game_over = False

        # Ensure current_solution_steps is empty before generating new ones
        self.current_solution_steps = [] 

        # Get and prepare solution steps
        self.current_solution_steps = generate_solution_steps(self.current_problem)
        logging.info(f"Generated {len(self.current_solution_steps)} solution steps")

        # Populate solution_char_details based on the generated steps
        self.solution_char_details = [] # Ensure it's empty before populating
        for line_idx, step_text in enumerate(self.current_solution_steps):
            for char_idx, char_val in enumerate(step_text):
                self.solution_char_details.append({
                    'line_idx': line_idx,
                    'char_idx': char_idx,
                    'char': char_val,
                    'canvas_id': None,  # Will be updated by SolutionSymbolDisplay
                    'is_visible_on_b': False, # Initially not visible
                    'transported_to_c': False,
                    'is_placeholder': char_val.isspace() # Mark spaces as placeholders
                })
        
        # Detailed logging for generated solution steps
        if self.debug_mode:
            logging.info(f"--- Generated Solution Steps for '{self.current_problem}' ---")
            if self.current_solution_steps:
                for i, step_text in enumerate(self.current_solution_steps):
                    logging.info(f"  Step {i}: '{step_text}' (Length: {len(step_text)})")
                logging.info(f"Total steps generated: {len(self.current_solution_steps)}")
            else:
                logging.info("  No solution steps were generated.")
            logging.info("-----------------------------------------------------")
            
        # Ensure redraw happens after canvas is sized and data is ready
        if self.solution_symbol_display:
            # Force complete clear of previous symbols before drawing new ones
            self.solution_symbol_display.clear_all_visuals()
            logging.info("Explicitly cleared Window B before drawing new problem")
            
            # Ensure the canvas is ready and sized before drawing
            # if hasattr(self.solution_symbol_display, 'canvas') and self.solution_symbol_display.canvas.winfo_exists():
            #     self.solution_symbol_display.canvas.update_idletasks() # Intentionally removed
            
            self.after(50, lambda: self.solution_symbol_display.update_data(self.current_solution_steps, self.visible_chars))
            
            # Schedule the first update for worm symbols after drawing is likely initiated
            # This replaces the one previously in handle_popup_choice
            # if hasattr(self, '_update_worm_solution_symbols'): # REMOVED - Now handled by SSD callback
            #    self.after(500, self._update_worm_solution_symbols) # Give some time for drawing
        
        self.after(100, self.auto_reveal_spaces) # Auto-reveal initial spaces
    except Exception as e:
        logging.error(f"Error loading new problem: {str(e)}")
        logging.error(traceback.format_exc())
        self.problem_prefix_label.config(text="Error")
        self.problem_equation_label.config(text="Problem loading failed.")
        self.current_problem = ""
        self.current_solution_steps = []
        if self.solution_symbol_display:
            self.solution_symbol_display.update_data([], set())

def draw_solution_lines(self):
    """
    This method now delegates drawing to the SolutionSymbolDisplay class.
    It ensures data is passed correctly.
    """
    try:
        # Skip drawing if help button hasn't been clicked yet
        if not hasattr(self, 'help_button_clicked') or not self.help_button_clicked:
            logging.info("Skipping solution lines drawing - help button not clicked yet.")
            # Still call the callback to prevent any hanging processes
            if hasattr(self, 'drawing_complete_callback') and callable(self.drawing_complete_callback):
                self.drawing_complete_callback()
            return
        
        # Notify worm animation about canvas redraw to clear its state related to old symbol IDs/glows
        # This should happen BEFORE new symbols are drawn and new data is sent to worms.
        if hasattr(self, 'worm_animation') and self.worm_animation:
            self.worm_animation.handle_solution_canvas_redraw() # Worms clear their internal state
        
        # New: Call the new class to draw symbols
        if self.solution_symbol_display:
            # Make sure SolutionSymbolDisplay also knows about potential redraws for its own state (like pulsations)
            self.solution_symbol_display.handle_canvas_redraw_for_worms() # SSD clears its pulsations
            self.solution_symbol_display.update_data(self.current_solution_steps, self.visible_chars)
        
        if self.debug_mode:
            logging.info(f"GameplayScreen: Delegated drawing of {len(self.current_solution_steps)} solution steps to SolutionSymbolDisplay.")
            
    except Exception as e:
        logging.error(f"Error in GameplayScreen.draw_solution_lines (delegating): {e}")
        import traceback
        logging.error(traceback.format_exc())

def print_solution_details(self):
    """Print detailed info about the solution steps for debugging"""
    logging.info("=== DEBUG: Solution Steps Details ===")
    print("\n=== DEBUG: Solution Steps Details ===")
    
    # First log the basic information about each step
    for i, step in enumerate(self.current_solution_steps):
        logging.info(f"Step {i}: '{step}' (len={len(step)})")
        print(f"Step {i}: '{step}' (len={len(step)})")
        # Print character by character details
        for j, char in enumerate(step):
            char_repr = repr(char)
            char_ord = ord(char) if len(char) == 1 else None
            logging.info(f"  Char {j}: '{char}' (repr={char_repr}, ord={char_ord})")
            print(f"  Char {j}: '{char}' (repr={char_repr}, ord={char_ord})")
    
    # Display information about what the solution is actually showing
    logging.info("\nCurrent solution completion state:")
    print("\nCurrent solution completion state:")
    for i, step in enumerate(self.current_solution_steps):
        visible_count = 0
        total_count = len(step)
        for j, _ in enumerate(step):
            if (i, j) in self.visible_chars:
                visible_count += 1
        
        completion_percentage = (visible_count / total_count * 100) if total_count > 0 else 0
        logging.info(f"Step {i}: {visible_count}/{total_count} chars visible ({completion_percentage:.1f}%)")
        print(f"Step {i}: {visible_count}/{total_count} chars visible ({completion_percentage:.1f}%)")
        
    logging.info("=====================================")
    print("=====================================\n")

def find_next_required_char(self):
    """
    Returns a list of all (line_idx, char_idx) positions that are still invisible
    and can be revealed in ANY order within the current solution step. 
    Solution steps must be completed in sequence.
    """
    if self.debug_mode:
        logging.info("===== FINDING NEXT REQUIRED CHAR =====")
        # Print the current visible characters for debugging
        logging.info(f"Current visible chars: {self.visible_chars}")
    
    valid_positions = []
    
    # Iterate through all steps to find the first incomplete one
    for step_idx, step in enumerate(self.current_solution_steps):
        if not step:  # Skip empty steps
            if self.debug_mode:
                logging.info(f"Step {step_idx} is empty, skipping")
            continue
            
        # Check if this step is complete
        step_complete = True
        missing_chars = []
        
        for char_idx, char in enumerate(step):
            if (step_idx, char_idx) not in self.visible_chars:
                step_complete = False
                missing_chars.append((char_idx, char))
        
        if self.debug_mode:
            if step_complete:
                logging.info(f"Step {step_idx} is complete")
            else:
                logging.info(f"Step {step_idx} is incomplete. Missing chars: {missing_chars}")
        
        # If this step is incomplete, it's the active step
        if not step_complete:
            if self.debug_mode:
                logging.info(f"Active step is {step_idx}")
            
            # Return all valid positions for this step
            for char_idx, char in enumerate(step):
                if (step_idx, char_idx) not in self.visible_chars:
                    valid_positions.append((step_idx, char_idx, char))
                    if self.debug_mode:
                        if char.isspace():
                            logging.info(f"Found unrevealed space at ({step_idx}, {char_idx})")
                        else:
                            logging.info(f"Found unrevealed char at ({step_idx}, {char_idx}): '{char}' (ord={ord(char)})")
            
            # We found our active step, no need to check further steps
            break
    
    if self.debug_mode:
        if not valid_positions:
            logging.info("No more unrevealed characters found - all steps complete")
        else:
            logging.info(f"Valid positions: {[(p[0], p[1], repr(p[2])) for p in valid_positions]}")
        logging.info("========================================")
        
    return valid_positions

def handle_canvas_c_click(self, event):
    """Handles clicks specifically on the symbol canvas (Window C)"""
    # Ignore clicks during transitions or if game is over
    if hasattr(self, 'in_level_transition') and self.in_level_transition:
        logging.info("Click ignored during level transition")
        return
        
    if self.game_over or not self.winfo_exists(): 
        return

    # Safety check for falling_symbols - prevent NoneType errors
    if not hasattr(self, 'falling_symbols') or not self.falling_symbols:
        logging.warning("Click ignored - falling_symbols not initialized")
        return

    # Log raw click coordinates for debugging
    if self.debug_mode:
        logging.info(f"Raw click at ({event.x}, {event.y}) on symbol canvas")

    # Get canvas coordinates
    canvas = self.symbol_canvas  # Always use symbol_canvas for this handler
    click_x = canvas.canvasx(event.x)
    click_y = canvas.canvasy(event.y)
    click_pos = (click_x, click_y)

    # Get the clicked symbol using the falling_symbols manager
    clicked_symbol_info, symbol_index = self.falling_symbols.get_symbol_at_position(click_x, click_y)
    
    if not clicked_symbol_info:
        if self.debug_mode:
            logging.info(f"No symbols found at click position {click_pos}")
        return

    clicked_char = clicked_symbol_info['char']
    if self.debug_mode:
        logging.info(f"User clicked symbol: '{clicked_char}' at position {click_pos}")
        logging.info(f"Symbol has ID: {clicked_symbol_info.get('id')}")

    # --- NEW: Check for Intervention Attempt First --- 
    if self.currently_targeted_by_worm:
        targeted_info = self.currently_targeted_by_worm
        targeted_symbol_data_B = targeted_info['symbol_data'] # Data for symbol in Window B
        
        # Check if the clicked character in Window C matches the character the worm is targeting in Window B
        if clicked_char == targeted_symbol_data_B.get('char'):
            logging.info(f"Potential intervention: Clicked '{clicked_char}' matches worm-targeted char. Attempting for symbol at L{targeted_symbol_data_B.get('line_idx')}C{targeted_symbol_data_B.get('char_idx')}.")

            # Stop pulsation of the targeted symbol in Window B as an action is being taken
            if self.solution_symbol_display:
                self.solution_symbol_display.stop_specific_pulsation(f"pulse_{targeted_symbol_data_B.get('line_idx')}_{targeted_symbol_data_B.get('char_idx')}")

            intervention_successful = False # Default to false
            if hasattr(self, 'worm_animation') and self.worm_animation:
                intervention_successful = self.worm_animation.attempt_intervention_kill(
                    targeted_info['worm_id'], 
                    targeted_symbol_data_B.get('id') # Canvas ID of the symbol in Window B worm was targeting
                )

            if intervention_successful:
                logging.info(f"Intervention successful! Worm {targeted_info['worm_id']} exploded.")
                
                # Get details of the symbol in Window B that was targeted
                line_idx_B = targeted_symbol_data_B.get('line_idx')
                char_idx_B = targeted_symbol_data_B.get('char_idx')
                # The canvas item targeted_symbol_data_B.get('id') was deleted by attempt_intervention_kill

                # Trigger teleport effect for the clicked symbol from C to B's spot
                if hasattr(self, 'teleport_manager') and self.teleport_manager and clicked_symbol_info.get('id') is not None:
                    target_coords_B = self.get_solution_char_coords(line_idx_B, char_idx_B)
                    self.teleport_manager.teleport_symbol(
                        clicked_symbol_info.get('id'), # ID of the symbol clicked in Window C
                        start_pos=click_pos, # Original click position in Window C
                        end_pos=target_coords_B, # Target position in Window B
                        is_correct=True # Visual cue for a positive action
                    )
                    logging.info(f"Teleport effect triggered for symbol {clicked_symbol_info.get('id')} from C to B.")
                
                # Remove the clicked symbol from Window C's falling symbols list
                if symbol_index != -1: # Ensure symbol_index is valid from get_symbol_at_position
                    self.falling_symbols.remove_symbol(symbol_index)
                    logging.info(f"Removed clicked symbol (original index {symbol_index}, char '{clicked_char}') from Window C list.")

                # Mark character in Window B as visible and redraw to show it
                self.visible_chars.add((line_idx_B, char_idx_B))
                # self.draw_solution_lines() # This will redraw, creating the new char visual # Old call
                if self.solution_symbol_display:
                    self.solution_symbol_display.update_data(self.current_solution_steps, self.visible_chars)
                logging.info(f"Marked L{line_idx_B}C{char_idx_B} as visible and redrew solution lines for Window B replacement.")

            else: # Intervention failed
                logging.info(f"Intervention attempt for worm {targeted_info['worm_id']} failed (likely too late or target mismatch). Clicked char '{clicked_char}'. Worm target char '{targeted_symbol_data_B.get('char')}'.")
            
            # This targeting event has been processed (intervention attempted, successfully or not)
            self.currently_targeted_by_worm = None
            
            return # Click action handled as an intervention attempt
    # --- END NEW INTERVENTION LOGIC ---

    # Check if this symbol was transported by a worm and can be returned
    if clicked_symbol_info.get('is_transported_worm_symbol'):
        original_line_idx = clicked_symbol_info['original_line_idx']
        original_char_idx = clicked_symbol_info['original_char_idx']
        original_char_tag = clicked_symbol_info['original_char_tag']
        "#336699"  # Standard revealed color (unused local removed by pyflakes pass)

        logging.info(f"[SYMBOL_RETURN_DEBUG] Clicked '{clicked_char}' (transported). Original: L{original_line_idx}C{original_char_idx}, Tag: {original_char_tag}.")
        logging.info(f"[SYMBOL_RETURN_DEBUG] self.visible_chars BEFORE add: {self.visible_chars}")

        # Make it visible again in Window B
        try:
            self.visible_chars.add((original_line_idx, original_char_idx))
            logging.info(f"[SYMBOL_RETURN_DEBUG] self.visible_chars AFTER add: {self.visible_chars}")

            logging.info("[SYMBOL_RETURN_DEBUG] Calling solution_symbol_display.update_data to redraw Window B.")
            if self.solution_symbol_display:
                self.solution_symbol_display.update_data(self.current_solution_steps, self.visible_chars)
            logging.info(f"[SYMBOL_RETURN_DEBUG] update_data finished. Attempting flash_char_green for L{original_line_idx}C{original_char_idx}.")
            
            # self.flash_char_green(original_char_tag, "#336699") # Flash it # Old call
            if self.solution_symbol_display:
                self.solution_symbol_display.flash_symbol_color(
                    original_line_idx, 
                    original_char_idx, 
                    flash_color="#22DD22", # Green flash
                    duration_ms=300,
                    original_color=self.solution_symbol_display.text_color # Revert to SSD's red
                )
            logging.info(f"[SYMBOL_RETURN_DEBUG] flash_symbol_color for L{original_line_idx}C{original_char_idx} apparently successful.")

            # Remove from falling symbols in Window C
            self.falling_symbols.remove_symbol(symbol_index)

            # Remove from our tracking list of transported_by_worm_symbols
            # Find and remove the specific symbol from the tracking list
            for i, entry in enumerate(self.transported_by_worm_symbols):
                if entry['original_char_tag'] == original_char_tag:
                    self.transported_by_worm_symbols.pop(i)
                    logging.info(f"Removed {original_char_tag} from transported_by_worm_symbols list.")
                    break
            
            # Potentially trigger a check if the step/level is now complete, though re-adding a char might not complete a new step
            self._check_if_step_complete(original_line_idx) 
            self._check_for_lock_visual_update()

        except tk.TclError as e:
            logging.error(f"TclError returning worm-transported symbol {original_char_tag} to Window B: {e}")
        except Exception as e:
            logging.error(f"Error returning worm-transported symbol {original_char_tag} to Window B: {e}")
        return # This click action is complete, do not proceed to normal symbol matching

    try:
        # Get all possible character positions that could be clicked
        valid_positions = self.find_next_required_char()
            
        if self.debug_mode:
            if not valid_positions:
                logging.info("No valid positions found for current step")
            else:
                logging.info(f"Valid positions found: {valid_positions}")
                for pos in valid_positions:
                    logging.info(f"Expected char: '{pos[2]}' (repr={repr(pos[2])}, ord={ord(pos[2])})")

        # Check if the clicked symbol matches any of the expected characters
        expected_position = None
        for pos in valid_positions:
            try:
                match_result = self._is_symbol_match(clicked_char, pos[2])
                if self.debug_mode:
                    logging.info(f"Match test: '{clicked_char}' vs '{pos[2]}' = {match_result}")
                
                if match_result:
                    expected_position = pos
                    if self.debug_mode:
                        logging.info(f"Match found! Clicked '{clicked_char}' matches required '{pos[2]}'")
                    break
            except Exception as e:
                logging.error(f"Error during symbol match: {e}")
                continue

        if expected_position:
            line_idx, char_idx, required_char = expected_position
            
            # Stop pulsation if this was the character targeted by a worm
            if self.currently_targeted_by_worm and \
               self.currently_targeted_by_worm['symbol_data'].get('line_idx') == line_idx and \
               self.currently_targeted_by_worm['symbol_data'].get('char_idx') == char_idx:
                if self.solution_symbol_display:
                    self.solution_symbol_display.stop_specific_pulsation(f"pulse_{line_idx}_{char_idx}")
                self.currently_targeted_by_worm = None # Target resolved
            
            # Calculate target position in solution canvas
            try:
                target_coords = self.get_solution_char_coords(line_idx, char_idx)
                
                logging.info(f"Correct symbol '{clicked_char}' selected, revealing at ({line_idx}, {char_idx})")
                self.reveal_char(line_idx, char_idx)
                
                # Use precise coordinates for teleportation
                self.teleport_manager.teleport_symbol(
                    clicked_symbol_info.get('id'),
                    start_pos=click_pos,
                    end_pos=target_coords,
                    is_correct=True
                )
                
                # Remove the symbol from tracking
                if symbol_index != -1:
                    self.falling_symbols.remove_symbol(symbol_index)

                # Check for level completion
                self.check_level_complete() # Check first, then auto-reveal
                self.after(10, self.auto_reveal_spaces) # Auto-reveal subsequent spaces
            except Exception as e:
                logging.error(f"Error during correct symbol handling: {e}")
        else:
            # Handle incorrect selection
            if self.debug_mode:
                logging.info(f"No match found for clicked symbol '{clicked_char}'")
                
            self.teleport_manager.teleport_symbol(
                clicked_symbol_info.get('id'),
                start_pos=click_pos,
                end_pos=click_pos,  # Stay in place for incorrect
                is_correct=False
            )

            self.incorrect_clicks += 1
            # Use the error animation for incorrect clicks
            if self.error_animation:
                self.error_animation.draw_crack_effect()

            # Game over functionality permanently removed as per user request
            # Players should never be penalized for making mistakes
    except Exception as e:
        logging.error(f"Critical error in handle_canvas_c_click: {e}")
        import traceback
        logging.error(traceback.format_exc())

def reveal_char(self, line_idx, char_idx):
    """Reveal a character in the solution steps"""
    try:
        # Skip if game is over
        if self.game_over:
            logging.info(f"[reveal_char] Ignoring reveal_char call for ({line_idx}, {char_idx}) because game is over.")
            return
    
        # Skip if line_idx or char_idx out of bounds
        if line_idx < 0 or line_idx >= len(self.current_solution_steps):
            logging.error(f"[reveal_char] Invalid line_idx {line_idx}, max is {len(self.current_solution_steps)-1}. current_solution_steps: {self.current_solution_steps}")
            return
            
        current_line = self.current_solution_steps[line_idx]
        if char_idx < 0 or char_idx >= len(current_line):
            logging.error(f"[reveal_char] Invalid char_idx {char_idx} for line {line_idx} ('{current_line}'), max is {len(current_line)-1}.")
            return
        
        char_to_reveal_for_log = current_line[char_idx] if char_idx < len(current_line) else ""
        logging.info(f"[reveal_char] Attempting to reveal char '{char_to_reveal_for_log}' (ord: {ord(char_to_reveal_for_log) if len(char_to_reveal_for_log)==1 else 'N/A'}) at ({line_idx}, {char_idx}).")

        # Skip if already visible
        if (line_idx, char_idx) in self.visible_chars:
            logging.info(f"[reveal_char] Character '{char_to_reveal_for_log}' at ({line_idx}, {char_idx}) is ALREADY in self.visible_chars. Skipping reveal.")
            return
            
        # Add to visible chars set (for legacy checks or simple visibility tracking)
        self.visible_chars.add((line_idx, char_idx))

        # Update the canonical solution_char_details list
        for detail in self.solution_char_details:
            if detail['line_idx'] == line_idx and detail['char_idx'] == char_idx:
                detail['is_visible_on_b'] = True
                detail['transported_to_c'] = False # Ensure it's not marked as transported
                # canvas_id will be updated by SolutionSymbolDisplay._create_character
                break
        
        # Ensure SolutionSymbolDisplay is synced with the new visible_chars state
        if self.solution_symbol_display:
            self.solution_symbol_display.update_data(self.current_solution_steps, self.visible_chars)

        # Reveal character in canvas using SolutionSymbolDisplay
        # char_tag = f"sol_{line_idx}_{char_idx}" # Old tag
        # target_color = "#336699"  # A blue color for revealed characters # Old color
        
        try:
            if self.solution_symbol_display:
                logging.info(f"[reveal_char] Preparing to call solution_symbol_display.reveal_symbol for ({line_idx}, {char_idx}) for char '{char_to_reveal_for_log}'.")
                self.solution_symbol_display.reveal_symbol(line_idx, char_idx) # Uses its own red color
                logging.info("[reveal_char] Successfully called reveal_symbol. Now flashing green using SolutionSymbolDisplay.")
                
                # Flash the character green briefly using SolutionSymbolDisplay
                self.solution_symbol_display.flash_symbol_color(
                    line_idx, 
                    char_idx, 
                    flash_color="#22DD22", # Green flash
                    duration_ms=300,
                    original_color=self.solution_symbol_display.text_color # Revert to SSD's red
                )
            
            # Trigger character-themed particle formation for significant characters
            if self.lock_animation and char_to_reveal_for_log in "0123456789+-=xX":
                self.lock_animation.react_to_character_reveal(char_to_reveal_for_log)
        
        except tk.TclError as e:
            _tag = f"sol_{line_idx}_{char_idx}"
            logging.warning(f"[reveal_char] TclError during itemconfig/flash for char '{char_to_reveal_for_log}' tag '{_tag}' ({line_idx}, {char_idx}): {e}")
            
        # Check if this step is now complete
        self._check_if_step_complete(line_idx)
            
        # Update lock segment visuals if appropriate
        self._check_for_lock_visual_update()
        
        _tag = f"sol_{line_idx}_{char_idx}"
        logging.info(f"[reveal_char] Successfully revealed character '{char_to_reveal_for_log}' (tag: {_tag}) at position ({line_idx}, {char_idx}).")
                
        # Log completion percentage for this line
        total_chars_in_line = len(current_line)
        visible_chars_in_line = sum(1 for i in range(total_chars_in_line) if (line_idx, i) in self.visible_chars)
        logging.info(f"[reveal_char] Step {line_idx} is now {visible_chars_in_line}/{total_chars_in_line} complete ({visible_chars_in_line/total_chars_in_line*100:.1f}%). Visible chars overall: {len(self.visible_chars)}")
                
        # If this step is complete, log that and what the next step will be
        if visible_chars_in_line == total_chars_in_line:
            logging.info(f"[reveal_char] Step {line_idx} ('{self.current_solution_steps[line_idx]}') is now COMPLETE!")
            
            if line_idx + 1 < len(self.current_solution_steps):
                logging.info(f"[reveal_char] Next step will be {line_idx + 1}: '{self.current_solution_steps[line_idx+1] if (line_idx+1) < len(self.current_solution_steps) else 'N/A'}'")
            
    except Exception as e:
        logging.error(f"[reveal_char] Critical error in reveal_char for ({line_idx}, {char_idx}): {e}")
        traceback.print_exc()

    # After revealing, update help text if needed
    try:
        if hasattr(self, 'help_display') and self.help_display is not None:
            self.help_display.update_help_text(
                current_step_index=line_idx,
                total_steps=len(self.current_solution_steps),
                step_text=self.current_solution_steps[line_idx]
            )
    except Exception as e:
        logging.error(f"Error updating help display during reveal_char: {e}")

def _check_for_lock_visual_update(self):
    """Check if we should update the lock animation based on completed steps"""
    try:
        if not self.lock_animation:
            return
            
        num_distinct_completed_steps = len(self.completed_line_indices_for_problem)
        
        # If we have completed more steps than parts unlocked, unlock the next part
        if self.lock_animation.unlocked_parts < self.lock_animation.total_parts and \
           num_distinct_completed_steps > self.lock_animation.unlocked_parts:
            
            self.lock_animation.unlock_next_part()
            logging.info(f"[LockAnimation] Unlocked part. Total distinct steps completed: {num_distinct_completed_steps}. Lock parts now visually unlocked: {self.lock_animation.unlocked_parts}")
    except Exception as e:
        logging.error(f"Error updating lock visuals: {e}")
        
def flash_char_green(self, tag, original_color):
    """Makes a character flash bright green when correctly revealed.
    DEPRECATED: Functionality moved to SolutionSymbolDisplay.flash_symbol_color()
    Kept for compatibility if any old direct calls exist, but should be removed later.
    """
    logging.warning("DEPRECATED GameplayScreen.flash_char_green called. Use SolutionSymbolDisplay.flash_symbol_color.")
    # Try to parse tag "sol_{line_idx}_{char_idx}"
    try:
        parts = tag.split('_')
        if len(parts) == 3 and parts[0] == 'sol':
            line_idx, char_idx = int(parts[1]), int(parts[2])
            if self.solution_symbol_display:
                target_original_color = self.solution_symbol_display.text_color # Default to SSD's red
                # If the original_color passed was different, it implies a special case.
                # For now, the new system flashes green then reverts to SSD's standard red.
                self.solution_symbol_display.flash_symbol_color(line_idx, char_idx, "#22DD22", 300, target_original_color)
                return
    except Exception:
        logging.error(f"Could not parse deprecated flash_char_green tag: {tag}")

    # Fallback to old logic if parsing failed or no solution_symbol_display
    if not self.winfo_exists(): 
        return
        
    try:
        # Flash the character green
        flash_color = "#22DD22"
        # logging.info(f"Flashing tag {tag} to {flash_color}, will return to {original_color}") # Old logging

        # Create a unique ID for this flash to avoid conflicts with after_cancel
        # flash_id = f"flash_{tag}_{time.time()}" # Old flash_id management
        # self.flash_ids[flash_id] = True
        
        self.solution_canvas.itemconfig(tag, fill=flash_color)
        
        # Schedule reset back to black after 300ms
        def reset_color():
            # if self.winfo_exists() and flash_id in self.flash_ids: # Check key presence before del # Old
            if self.winfo_exists():
                try:
                    self.solution_canvas.itemconfig(tag, fill=original_color)
                except tk.TclError:
                    pass # Item might be gone
                # finally: # Old
                    # Always remove the flash_id from tracking once its timer has executed or attempted
                    # del self.flash_ids[flash_id]
                    
        # self.flash_ids[flash_id] = self.after(300, reset_color) # Store the timer ID with the unique key #Old
        self.after(300, reset_color) 
        
    except tk.TclError:
        # Item might be gone already
        pass

def reset_char_color(self, tag, color):
    """Resets character color after flashing.
    DEPRECATED: Functionality moved to SolutionSymbolDisplay.
    """
    logging.warning("DEPRECATED GameplayScreen.reset_char_color called.")
    if not self.winfo_exists(): return
    try:
        # logging.info(f"[reset_char_color] Resetting tag '{tag}' to color '{color}'.") # Old
        self.solution_canvas.itemconfig(tag, fill=color)
        # logging.info(f"[reset_char_color] Successfully set tag '{tag}' to '{color}'.") # Old
        # if tag in self.flash_ids: # Old
            # del self.flash_ids[tag] # Clean up flash ID # Old
    except tk.TclError as e:
         logging.warning(f"[reset_char_color DEPRECATED] TclError for tag '{tag}' (color: {color}): {e}.")
         # if tag in self.flash_ids: del self.flash_ids[tag] # Old
         pass

def clear_all_cracks(self):
    """Clear all crack effects from the error animation"""
    if hasattr(self, 'error_animation') and self.error_animation:
        self.error_animation.clear_all_cracks()
        logging.info("Cleared all crack effects")
        