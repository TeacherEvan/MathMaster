# gameplay_screen.py
import tkinter as tk
import random
import time
import logging
import math  # For math functions in gameplay animations
import json
import os
import traceback # Added import
from src.ui_components.feedback_manager import FeedbackManager # Added import
from lock_animation import LockAnimation # Import the lock animation class
from error_animation import ErrorAnimation # Import the new error animation class
from falling_symbols import FallingSymbols # Import the falling symbols manager
from WormsWindow_B import WormAnimation # Import the worm animation class
from window_b_solution_symbols import SolutionSymbolDisplay # Added import

# Import the problem sets from the module files
try:
    from Easy import problems as easy_problems
    from Medium import problems as medium_problems
    from MediumDivision import problems as division_problems
    from Help_Btn_Gameplay_Window_B import HelpButton  # Fixed import statement
    from Teleport_SymblDisplay_C_B import SymbolTeleportManager  # Fixed import name
    
    # Log successful import
    logging.info("Successfully imported all problem sets and Help Button")

    # Shuffle the lists right after import to ensure randomness across game starts
    random.shuffle(easy_problems)
    logging.info(f"Shuffled Easy problems. First few examples: {easy_problems[:3] if len(easy_problems) > 3 else easy_problems}")
    random.shuffle(medium_problems)
    logging.info(f"Shuffled Medium problems. First few examples: {medium_problems[:3] if len(medium_problems) > 3 else medium_problems}")
    random.shuffle(division_problems) # Assuming "medium too" refers to Division problems
    logging.info(f"Shuffled Division problems. First few examples: {division_problems[:3] if len(division_problems) > 3 else division_problems}")

except ImportError as e:
    logging.error(f"Error importing problem sets: {e}")
    # Fallback problems in case imports fail
    easy_problems = ["x + 5 = 12", "8 + x = 15", "10 + x - 4 = 16"]
    medium_problems = ["5x = 20", "7x = 49", "12x = 144"]
    division_problems = ["18 / x = 6", "x / 4 = 5", "9 / x = 3"]
    # Shuffle fallback lists as well for consistency
    random.shuffle(easy_problems)
    random.shuffle(medium_problems)
    random.shuffle(division_problems)
    logging.info("Used and shuffled fallback problem sets.")

# Map level names to problem sets
PROBLEMS = {
    "Easy": easy_problems,
    "Medium": medium_problems,
    "Division": division_problems
}

# Pre-calculated solution steps for common problem types
def generate_solution_steps(problem_input): # Renamed to avoid confusion
    """Generate solution steps for a given problem"""
    problem = str(problem_input).strip() # Ensure it's a string and stripped initially
    logging.info(f"[generate_solution_steps] Received raw input: '{problem_input}', Processed as: '{problem}'")

    # Secondary stripping for prefixes like "Problem X:"
    if ":" in problem and problem.lower().rfind("problem ") < problem.find(":"): # Check if "problem " is before ":"
        problem_part_after_colon = problem.split(":", 1)[1].strip()
        logging.info(f"[generate_solution_steps] Found ':' likely part of a prefix. Original: '{problem}', Extracted equation: '{problem_part_after_colon}'")
        problem = problem_part_after_colon
    elif problem.lower().startswith("problem "):
        # More robustly skip the "Problem X" part if no colon or colon is much later
        temp_problem = problem
        if ' ' in temp_problem:
            parts = temp_problem.split(' ', 2) # "Problem", "X", "equation"
            if len(parts) > 2 and parts[0].lower() == "problem" and parts[1].rstrip(':').isdigit():
                extracted_equation = parts[2].strip()
                logging.info(f"[generate_solution_steps] Found 'Problem X' prefix. Original: '{problem}', Extracted equation: '{extracted_equation}'")
                problem = extracted_equation
            elif len(parts) > 1 and parts[0].lower() == "problem": # e.g. "Problem equation"
                extracted_equation = parts[1].strip()
                logging.info(f"[generate_solution_steps] Found 'Problem' prefix. Original: '{problem}', Extracted equation: '{extracted_equation}'")
                problem = extracted_equation
            else:
                 logging.info(f"[generate_solution_steps] 'Problem ' prefix found but structure unclear. Using: '{problem}'")
        else:
            logging.info(f"[generate_solution_steps] 'Problem ' prefix found but structure unclear. Using: '{problem}'")


    logging.info(f"[generate_solution_steps] Problem after initial prefix stripping: '{problem}'")

    # If problem contains newlines (likely pre-formatted steps)
    if "\\n" in problem: # Check for literal \\n in string if problems are defined like "Step1\\nStep2"
        logging.info(f"[generate_solution_steps] Found literal '\\\\n' in problem. Splitting by '\\\\n'.")
        return [step.strip() for step in problem.split("\\n") if step.strip()]
    if "\n" in problem: # Check for actual newline characters
        logging.info(f"[generate_solution_steps] Found actual newline character in problem. Splitting by newline.")
        return [step.strip() for step in problem.split("\n") if step.strip()]

    logging.info(f"[generate_solution_steps] No newlines found. Proceeding to parse equation structure for: '{problem}'")

    original_problem_for_steps = problem # Keep a copy of the equation itself for the first step

    # General structure: ax + b = c, ax - b = c, x/a + b = c etc.
    # For now, let's focus on refining existing blocks and ensuring multiplication is robust.

    # Pattern: a + x - c = b or similar complex ones (ensure they are specific)
    # General check for patterns like: num + x - num = num  OR  x + num - num = num
    if ("+ x -" in problem.split("=")[0] or "x +" in problem.split("=")[0] and "-" in problem.split("=")[0]):
        logging.info(f"[generate_solution_steps] Checking complex +/- patterns for '{problem}'")
        
        equation_part = problem.split("=")[0].strip()
        result_part_str = problem.split("=")[1].strip()

        # Try to parse "a + x - c = b"
        # Example: 12 + x - 2 = 20
        if "+ x -" in equation_part: 
            logging.info(f"[generate_solution_steps] Attempting to parse as 'a + x - c = b' for '{equation_part}'")
            try:
                # Split around "+ x -" to get 'a' and 'c'
                parts = equation_part.split("+ x -")
                if len(parts) == 2:
                    a_str = parts[0].strip()
                    c_str = parts[1].strip()
                    a_val = int(a_str)
                    c_val = int(c_str)
                    b_val = int(result_part_str)
                    
                    # Steps: a + x - c = b  => x - c = b - a => x = b - a + c
                    step2_val = b_val - a_val
                    final_result = b_val - a_val + c_val
                    logging.info(f"[generate_solution_steps] Parsed '{problem}' as a + x - c = b -> a={a_val}, c={c_val}, b={b_val}. Result: {final_result}")
                    return [
                        original_problem_for_steps,
                        f"x - {c_val} = {b_val} - {a_val}", 
                        f"x - {c_val} = {step2_val}",
                        f"x = {step2_val} + {c_val}",
                        f"x = {final_result}"
                    ]
                else:
                    logging.warning(f"[generate_solution_steps] 'a + x - c = b' pattern for '{problem}' split yielded {len(parts)} parts, expected 2. Parts: {parts}")
            except (ValueError, IndexError) as e:
                logging.warning(f"[generate_solution_steps] Error parsing '{problem}' with 'a + x - c = b' specific pattern: {e}. Falling through.")

        # Try to parse "x + a - c = b"
        # Example: x + 12 - 2 = 20
        elif equation_part.startswith("x +") and "-" in equation_part: 
            logging.info(f"[generate_solution_steps] Attempting to parse as 'x + a - c = b' for '{equation_part}'")
            try:
                # Remove "x + " from the beginning, then split by "-"
                temp_eq = equation_part.replace("x +", "", 1).strip()
                parts = temp_eq.split("-", 1) # Should give [a, c]
                if len(parts) == 2:
                    a_str = parts[0].strip()
                    c_str = parts[1].strip()
                    a_val = int(a_str)
                    c_val = int(c_str)
                    b_val = int(result_part_str)
                    
                    # Steps: x + a - c = b => x - c = b - a => x = b - a + c
                    step2_val = b_val - a_val
                    final_result = b_val - a_val + c_val
                    logging.info(f"[generate_solution_steps] Parsed '{problem}' as x + a - c = b -> a={a_val}, c={c_val}, b={b_val}. Result: {final_result}")
                    return [
                        original_problem_for_steps, 
                        f"x - {c_val} = {b_val} - {a_val}",
                        f"x - {c_val} = {step2_val}",
                        f"x = {step2_val} + {c_val}",
                        f"x = {final_result}"
                    ]
                else:
                    logging.warning(f"[generate_solution_steps] 'x + a - c = b' pattern for '{problem}' split yielded {len(parts)} parts, expected 2. Parts: {parts}")
            except (ValueError, IndexError) as e:
                logging.warning(f"[generate_solution_steps] Error parsing '{problem}' with 'x + a - c = b' specific pattern: {e}. Falling through.")
        else:
            logging.info(f"[generate_solution_steps] Complex +/- pattern detected for '{problem}' but did not match 'a + x - c' or 'x + a - c' structure precisely.")

    # Pattern: Three terms added on LHS, one is x. e.g., a + b + x = c, a + x + b = c, x + a + b = c
    # This is checked before simple two-term addition.
    elif problem.count('+') == 2 and '=' in problem and 'x' in problem.split('=')[0] and '-' not in problem.split('=')[0] and '/' not in problem.split('=')[0]:
        logging.info(f"[generate_solution_steps] Checking three-term addition for '{problem}'")
        equation_part, result_part_str = problem.split('=', 1)
        equation_part = equation_part.strip()
        result_part_str = result_part_str.strip()

        try:
            result_val = int(result_part_str)
            terms_str = [t.strip() for t in equation_part.split('+')]

            if len(terms_str) == 3:
                x_term_index = -1
                num_parts_str = []
                # Assuming x is a standalone term, e.g., 'x', not '2x'
                # Coefficient handling for 'x' (e.g., '2x') is managed by multiplication rules.

                for i, term in enumerate(terms_str):
                    if term == 'x': # Simple check for 'x' as a whole term
                        x_term_index = i
                    else:
                        num_parts_str.append(term)
                
                if x_term_index != -1 and len(num_parts_str) == 2:
                    n1_str, n2_str = num_parts_str[0], num_parts_str[1]
                    n1 = int(n1_str)
                    n2 = int(n2_str)
                    sum_of_nums = n1 + n2
                    final_x_val = result_val - sum_of_nums

                    steps = [original_problem_for_steps]
                    # Step 2: Show grouping of numbers
                    if x_term_index == 0: # x + n1 + n2 = R
                        steps.append(f"x + ({n1} + {n2}) = {result_val}")
                        steps.append(f"x + {sum_of_nums} = {result_val}")
                    elif x_term_index == 1: # n1 + x + n2 = R
                        # Rearrange for clarity and consistency in steps
                        steps.append(f"x + ({n1} + {n2}) = {result_val}") 
                        steps.append(f"x + {sum_of_nums} = {result_val}")
                    else: # n1 + n2 + x = R (x_term_index == 2)
                        steps.append(f"({n1} + {n2}) + x = {result_val}")
                        steps.append(f"{sum_of_nums} + x = {result_val}")
                    
                    steps.append(f"x = {result_val} - {sum_of_nums}")
                    steps.append(f"x = {final_x_val}")
                    logging.info(f"[generate_solution_steps] Parsed three-term addition '{problem}' -> n1={n1}, n2={n2}, R={result_val}. Result: {final_x_val}")
                    return steps
                else:
                    logging.warning(f"[generate_solution_steps] Three-term addition pattern for '{problem}' parsed ambiguously or 'x' not standalone. Terms: {terms_str}, x_idx: {x_term_index}, Nums: {num_parts_str}")
            else:
                 logging.warning(f"[generate_solution_steps] Three-term addition pattern for '{problem}' split by '+' did not yield 3 parts as expected. Parts: {terms_str}")
        except ValueError as e:
            logging.warning(f"[generate_solution_steps] Error parsing three-term addition '{problem}': {e}. Falling through.")
    
    # Simple addition: x + a = b or a + x = b
    # Ensure these are checked *after* more complex forms like "x + a - c = b" or three-term additions.
    elif ("x +" in problem or "+ x" in problem) and "=" in problem and "-" not in problem.split("=")[0] and "/" not in problem.split("=")[0]: # Added check for '/'
        logging.info(f"[generate_solution_steps] Checking simple addition for '{problem}'")
        parts = problem.split("=")
        left_expr = parts[0].strip()
        right_val_str = parts[1].strip()
        try:
            b_val = int(right_val_str)
            a_val_str = ""
            if "x +" in left_expr : # x + a = b
                a_val_str = left_expr.replace("x +", "").strip()
            elif "+ x" in left_expr: # a + x = b
                a_val_str = left_expr.replace("+ x", "").strip()

            if a_val_str.isdigit():
                a_val = int(a_val_str)
                result = b_val - a_val
                logging.info(f"[generate_solution_steps] Parsed simple addition '{problem}' -> a={a_val}, b={b_val}")
                return [original_problem_for_steps, f"x = {b_val} - {a_val}", f"x = {result}"]
            else:
                logging.warning(f"[generate_solution_steps] Parsed simple addition for '{problem}' but 'a' part is not a digit: '{a_val_str}'. Falling through.")
        except ValueError as e:
            logging.warning(f"[generate_solution_steps] Error parsing simple addition '{problem}': {e}. Falling through.")
    
    # Direct assignment: x = value (should be fairly specific)
    if problem.strip().startswith("x =") or problem.strip().startswith("x=") :
        logging.info(f"[generate_solution_steps] Parsed '{problem}' as direct assignment.")
        # Potentially validate if RHS is a number, or just return as is if it's simple.
        # For now, if it's simple like "x = 10", one step is fine.
        # If it's "x = 10 + 5", it might need more, but current data seems to be "x = 10".
        return [original_problem_for_steps]

    # Division: x/a = b or a/x = b
    if ("x/" in problem or "/x" in problem) and "=" in problem:
        logging.info(f"[generate_solution_steps] Checking division for '{problem}'")
        parts = problem.split("=")
        left_expr = parts[0].strip()
        right_val_str = parts[1].strip()
        try:
            b_div_val = int(right_val_str) # This is 'b' in x/a=b or a/x=b
            if left_expr.startswith("x/"): # Pattern: x/a = b
                a_div_str = left_expr.replace("x/", "").strip()
                if a_div_str.isdigit():
                    a_div_val = int(a_div_str)
                    if a_div_val == 0:
                         logging.warning(f"[generate_solution_steps] Division by zero in x/a=b for '{problem}'.")
                         return [original_problem_for_steps, "Error: Division by zero"]
                    result = a_div_val * b_div_val
                    logging.info(f"[generate_solution_steps] Parsed x/a=b for '{problem}' -> a={a_div_val}, b={b_div_val}")
                    return [original_problem_for_steps, f"x = {b_div_val} × {a_div_val}", f"x = {result}"]
                else:
                    logging.warning(f"[generate_solution_steps] Denominator 'a' in x/a=b for '{problem}' is not a digit: '{a_div_str}'.")
            elif "/x" in left_expr: # Pattern: a/x = b
                a_div_str = left_expr.replace("/x", "").strip()
                if a_div_str.isdigit():
                    a_div_val = int(a_div_str)
                    if b_div_val == 0: # Avoid a / 0 = bx form
                        logging.warning(f"[generate_solution_steps] RHS 'b' is zero in a/x=b for '{problem}', leads to division by zero if solving for x.")
                        return [original_problem_for_steps, f"{a_div_val} = 0", "Error: Illogical equation"]
                    # a/x = b  => a = bx => x = a/b
                    result = a_div_val // b_div_val if a_div_val % b_div_val == 0 else a_div_val / b_div_val
                    logging.info(f"[generate_solution_steps] Parsed a/x=b for '{problem}' -> a={a_div_val}, b={b_div_val}")
                    return [original_problem_for_steps, f"{a_div_val} = {b_div_val}x", f"x = {a_div_val} ÷ {b_div_val}", f"x = {result}"]
                else:
                    logging.warning(f"[generate_solution_steps] Numerator 'a' in a/x=b for '{problem}' is not a digit: '{a_div_str}'.")
            else:
                logging.warning(f"[generate_solution_steps] Division pattern for '{problem}' not recognized as x/a or a/x. Left: '{left_expr}'")

        except ValueError as e:
            logging.warning(f"[generate_solution_steps] Error parsing division '{problem}': {e}. Falling through.")
    
    # Multiplication: ax=b or ax = b (ensure this is specific and doesn't overlap with x+..., x-...)
    # A simple check: contains 'x', contains '=', does not contain ops that would be handled by other rules.
    is_simple_mult = "x" in problem and "=" in problem and \
                     not any(op in problem.split("=")[0] for op in [" + ", " - ", "/"]) and \
                     not problem.split("=")[0].strip().startswith("x +") and \
                     not problem.split("=")[0].strip().startswith("+ x")
                     # Add more negative conditions if needed for specificity

    if is_simple_mult:
        logging.info(f"[generate_solution_steps] Attempting to parse as multiplication: '{problem}'")
        parts = problem.split("=")
        left = parts[0].strip()
        right = parts[1].strip()
        logging.info(f"[generate_solution_steps] Multiplication parts: left='{left}', right='{right}'")

        # Case: ax = b (e.g., "2x = 8", "x = 5" is handled by "x =" rule)
        # Need to ensure left is of form "ax" and not just "x"
        if "x" in left and left != "x": # Exclude simple "x=b" which is direct assignment
            coefficient_str = left.replace("x", "").strip()
            if coefficient_str.isdigit() and right.isdigit():
                a = int(coefficient_str)
                b = int(right)
                logging.info(f"[generate_solution_steps] Multiplication ax=b parsed: a={a}, b={b} for '{problem}'")
                if a == 0:
                    logging.warning(f"[generate_solution_steps] Coefficient 'a' is zero in '{problem}'.")
                    return [original_problem_for_steps, "Error: Coefficient is zero"]
                
                solution_val = b // a if b % a == 0 else b / a
                steps = [
                    original_problem_for_steps,
                    f"x = {b} ÷ {a}",
                    f"x = {solution_val}"
                ]
                logging.info(f"[generate_solution_steps] Returning steps for ax=b multiplication: {steps}")
                return steps
            else:
                logging.warning(f"[generate_solution_steps] For ax=b pattern '{problem}', coefficient or RHS not purely digits. Coeff_str: '{coefficient_str}', RHS: '{right}'. Falling through.")
        
        # Case: b = ax (e.g., "10 = 2x")
        elif "x" in right and right != "x":
            coefficient_str = right.replace("x", "").strip()
            if coefficient_str.isdigit() and left.isdigit(): # LHS is 'b'
                a_coeff = int(coefficient_str) # This is 'a' in ax=b
                b_val = int(left) # This is 'b' in ax=b
                logging.info(f"[generate_solution_steps] Multiplication b=ax parsed: a_coeff={a_coeff}, b_val={b_val} for '{problem}'")
                if a_coeff == 0:
                    logging.warning(f"[generate_solution_steps] Coefficient 'a_coeff' is zero in '{problem}'.")
                    return [original_problem_for_steps, "Error: Coefficient is zero"]

                solution_val = b_val // a_coeff if b_val % a_coeff == 0 else b_val / a_coeff
                steps = [
                    original_problem_for_steps,
                    f"{a_coeff}x = {b_val}", # Standardize
                    f"x = {b_val} ÷ {a_coeff}",
                    f"x = {solution_val}"
                ]
                logging.info(f"[generate_solution_steps] Returning steps for b=ax multiplication: {steps}")
                return steps
            else:
                logging.warning(f"[generate_solution_steps] For b=ax pattern '{problem}', coefficient or LHS not purely digits. Coeff_str: '{coefficient_str}', LHS: '{left}'. Falling through.")
        else:
            logging.warning(f"[generate_solution_steps] Multiplication general check hit for '{problem}', but specific ax=b or b=ax structure not matched or 'x' stands alone. Left='{left}', Right='{right}'. Falling through.")


    # Fallback if no specific parsing rule matched
    logging.warning(f"[generate_solution_steps] No specific parsing rule matched for '{original_problem_for_steps}'. Returning with 'Solution steps not available'.")
    return [original_problem_for_steps, "Solution steps not available (parser)."]

# Updated from placeholder to dynamic generation
SOLUTIONS = {}

# Falling symbols list moved to FallingSymbols class

class GameplayScreen(tk.Toplevel):
    def __init__(self, parent, level):
        super().__init__(parent)
        self.parent = parent
        self.current_level = level
        self.title(f"MathMaster - Level: {self.current_level}")
        self.geometry("1000x700") # Default size
        self.configure(bg="#1e1e1e")
        
        # Auto-save directory - needs to be initialized before clear_saved_game can be called
        self.save_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "saves")
        os.makedirs(self.save_dir, exist_ok=True)

        # Ensure a fresh start by clearing any saved game for this level upon initialization
        # This means launching a level from welcome_screen will always be a new problem.
        self.clear_saved_game() 
        logging.info(f"GameplayScreen for {self.current_level}: Cleared any existing save file to ensure fresh start from welcome screen.")
        
        # Add tracking for last problem to avoid repetition
        self.last_problems = []
        self.max_history = 3  # Remember last 3 problems to avoid repetition
        
        # We don't need saved_cracks here anymore as it's managed by ErrorAnimation
        
        # Set fullscreen immediately
        self.update_idletasks()  # Process any pending events
        self.state('zoomed')  # More reliable on Windows
        
        # Use different methods for fullscreen based on platform
        try:
            self.state('zoomed')  # Windows approach
        except:
            self.attributes('-fullscreen', True)  # Unix/Linux approach
        
        # Inherit parent size and position for proper scaling
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()
        parent_x = parent.winfo_x()
        parent_y = parent.winfo_y()
        
        # Apply parent's geometry (not needed in fullscreen, but kept for fallback)
        self.geometry(f"{parent_width}x{parent_height}+{parent_x}+{parent_y}")
        
        self.resizable(True, True)  # Allow resizing
        
        # Ensure visibility
        self.attributes('-alpha', 1.0)
        self.focus_force()
        
        # --- Game State Variables ---
        self.current_problem = ""
        self.current_solution_steps = []
        self.visible_chars = set() # Set of (line_idx, char_idx) tuples for revealed chars
        self.incorrect_clicks = 0
        self.max_incorrect_clicks = 20
        self.game_over = False
        # self.flash_ids = {} # To manage flashing effects - Will be managed by SolutionSymbolDisplay
        self.animation_after_id = None # For managing animation loop
        self.auto_save_after_id = None # For managing auto-save loop
        self.completed_line_indices_for_problem = set() # For lock animation logic
        self.lock_animation = None # Placeholder for LockAnimation instance
        self.error_animation = None # Placeholder for ErrorAnimation instance
        self.falling_symbols = None # Placeholder for FallingSymbols instance
        self.worm_animation = None # Placeholder for WormAnimation instance
        self.solution_symbol_display = None # Placeholder for SolutionSymbolDisplay instance
        
        # Track solution symbol data for worms
        self.solution_symbols_data_for_worms = [] # Renamed for clarity
        self.transported_by_worm_symbols = [] # Added to track symbols taken by worms
        self.currently_targeted_by_worm = None # Added for the rescue mechanic
        
        # Debug mode to print character details
        self.debug_mode = True

        # --- Layout ---
        self.create_layout() # This creates self.solution_canvas

        # Initialize SolutionSymbolDisplay after solution_canvas is created
        if hasattr(self, 'solution_canvas') and self.solution_canvas:
            self.solution_symbol_display = SolutionSymbolDisplay(self.solution_canvas, self)
        else:
            logging.error("CRITICAL: GameplayScreen - self.solution_canvas not created before SolutionSymbolDisplay initialization.")
            # Handle error appropriately, maybe raise exception or default

        # Initialize problem variables to empty state (can be useful, though problem load follows)
        self.current_problem = ""
        self.current_solution_steps = []
        self.visible_chars = set() 

        # Try to load saved state first, or load new problem for the session
        if not self.load_game_state():
            self.load_new_problem()
        else:
            # If a game state was loaded, and it's not game over, prepare the board
            if not self.game_over:
                # Cracks are usually cleared when a new problem loads or on game over.
                # For a loaded game, existing cracks might be relevant if we were to save/load them.
                # However, current save_game_state explicitly does not save cracks.
                # So, clearing them here or relying on load_new_problem/trigger_game_over to handle is fine.
                self.clear_all_cracks() # Ensure a clean start if loading a non-game-over state
        
        # --- Print Debug Info ---
        if self.debug_mode:
            self.print_solution_details()

        # --- Start Animation ---
        # Initialize falling symbols
        self.falling_symbols = FallingSymbols(self.symbol_canvas, list("0123456789Xx +-=÷×*/()"))
        
        # Delay starting animation slightly to allow canvas to initialize
        self.after(100, self.falling_symbols.start_animation)

        # Force fullscreen after initialization
        self.after(200, self._ensure_fullscreen)

        # --- Bindings ---
        self.bind("<Escape>", self.exit_game)
        self.bind("<Configure>", self.on_resize) # Handle resize
        # self.bind("<Map>", lambda event: self.refresh_cracks()) # refresh_cracks is more for game_over
        
        # Set up auto-save timer
        self.auto_save_interval = 10000  # 10 seconds
        self.schedule_auto_save()

        # Log gameplay screen start
        logging.info(f"Gameplay screen opened for level: {level}")

        # Ensure fullscreen once widgets are ready
        self.after(50, self.set_fullscreen)
        
        # Update lock dimensions after window setup is complete
        self.after(300, self._update_lock_dimensions)

        # Fix click event handling - ensure we have direct bindings to both canvases
        # Fix click event handling - ensure we have direct bindings to both canvases
        self.symbol_canvas.bind("<Button-1>", self.handle_canvas_c_click, add="+")
        self.solution_canvas.bind("<Button-1>", lambda e: None, add="+")  # Just to consume clicks
        
        # Initialize managers with proper coordinates
        self.teleport_manager = SymbolTeleportManager(
            self.symbol_canvas, 
            self.solution_canvas
        )
        
        # Update feedback manager with correct dimensions
        self.feedback_manager = FeedbackManager(
            self.symbol_canvas,
            self.symbol_canvas.winfo_width(),
            self.symbol_canvas.winfo_height()
        )
        
        # Initialize error animation for symbol canvas
        self.error_animation = ErrorAnimation(self.symbol_canvas)

        # Add a flash_ids dictionary to track animation timers for character flashing
        # self.flash_ids = {} # No longer needed here, SolutionSymbolDisplay handles its own

        # Initialize worm animation after other components are ready
        self.after(500, self._init_worm_animation)

    def _init_worm_animation(self):
        """Initializes the worm animation feature"""
        if not hasattr(self, 'solution_canvas') or not self.solution_canvas.winfo_exists():
            logging.error("Cannot initialize worm animation without solution_canvas.")
            return
            
        # Initialize the actual worm animation
        self.worm_animation = WormAnimation(
            self.solution_canvas,
            symbol_transport_callback=self.handle_symbol_transport,
            symbol_targeted_for_steal_callback=self.handle_symbol_targeted_for_steal
        )
        
        # Set up the list of symbols for worms to potentially target
        self.solution_symbols_data_for_worms = []
        
        # Start with animation paused - it will activate when first row is solved
        logging.info("Worm animation initialized but inactive until first row solved.")
        
        # Schedule delayed start of the symbol update mechanism
        # This delay gives the canvas time to be properly laid out and solution symbols to be drawn
        self.after(2000, self._update_worm_solution_symbols)  

    def handle_symbol_transport(self, symbol_id, char):
        """Handle callback when a worm transports a symbol to Window C"""
        logging.info(f"Symbol '{char}' (ID: {symbol_id}) transported by worm, will appear in Window C")
        
        # Find which line and char index this symbol represents from self.solution_symbols_data_for_worms
        transported_symbol_info = None
        original_line_idx, original_char_idx = -1, -1

        # The symbol_id from WormAnimation is the canvas item ID.
        # We need to find which (line_idx, char_idx) it corresponds to.
        # self.solution_symbols_data_for_worms contains dicts like:
        # {'id': canvas_item_id, 'char': char, 'line_idx': line_idx, 'char_idx': char_idx, ...}
        
        found_in_worm_data = False
        for symbol_data in self.solution_symbols_data_for_worms:
            if symbol_data.get('id') == symbol_id: # symbol_id is the canvas item id
                transported_symbol_info = symbol_data
                original_line_idx = symbol_data.get('line_idx')
                original_char_idx = symbol_data.get('char_idx')
                found_in_worm_data = True
                break
                
        if not found_in_worm_data or original_line_idx == -1 or original_char_idx == -1:
            logging.warning(f"Could not reliably find original (line, char) for transported symbol canvas ID {symbol_id} with char '{char}'. Worm data might be stale or ID mismatch.")
            # Attempt to find by char if it's unique and not yet transported - less reliable
            # This part can be complex to recover from if IDs don't match.
            # For now, we rely on the ID match.
            return
            
        logging.info(f"Found original position for symbol ID {symbol_id}: Line {original_line_idx}, Char {original_char_idx}")

        # Mark the character as 'hidden' or 'taken' in the solution display (Window B)
        # The SolutionSymbolDisplay draws based on self.visible_chars.
        # So, we remove it from visible_chars.
        if (original_line_idx, original_char_idx) in self.visible_chars:
            self.visible_chars.remove((original_line_idx, original_char_idx))
            logging.info(f"Removed ({original_line_idx},{original_char_idx}) from self.visible_chars.")
        
        # Trigger a redraw of Window B to reflect the symbol is gone (or appears as non-visible)
        if self.solution_symbol_display:
            self.solution_symbol_display.update_data(self.current_solution_steps, self.visible_chars)
            logging.info(f"Symbol '{char}' (L{original_line_idx}C{original_char_idx}) visually removed/hidden in Window B via SolutionSymbolDisplay update.")

            # Pulsate the spot where the symbol was taken, maybe with a different "empty" effect
            # For now, no specific effect on Window B for "taken", the symbol just disappears.
            # User request: "whenever a worm interacts with one It BRIGHTLY pulsates"
            # This pulsation should happen when the worm *targets* or *takes* the symbol.
            # Let's make it pulsate when taken for now with a specific color.
            self.solution_symbol_display.start_pulsation(
                original_line_idx, 
                original_char_idx, 
                pulse_color="#707070", # Darker pulse for "taken"
                base_color="#FFFFFF", # Base should be the invisible color
                duration=700, 
                pulses=2
            )


        # Create a copy of this character as a falling symbol in Window C
        if not hasattr(self, 'falling_symbols') or not self.falling_symbols:
            return
        
        # Manually create a new falling symbol
        x_pos = random.randint(50, self.symbol_canvas.winfo_width() - 50)
        new_symbol_data_for_falling_list = {
            'char': char,
            'x': x_pos,
            'y': 10,  # Near the top
            'id': None, # This will be populated by FallingSymbols when it creates the canvas item
            'size': 44,  # Match the size in FallingSymbols
            'is_transported_worm_symbol': True,
            'original_line_idx': original_line_idx,
            'original_char_idx': original_char_idx,
            'original_char_tag': f"sol_{original_line_idx}_{original_char_idx}"
        }
        
        # Add to falling symbols list
        self.falling_symbols.falling_symbols_on_screen.append(new_symbol_data_for_falling_list)

        # Add to our persistent list of symbols transported by worms
        self.transported_by_worm_symbols.append({
            'char': char,
            'original_line_idx': original_line_idx,
            'original_char_idx': original_char_idx,
            'original_char_tag': f"sol_{original_line_idx}_{original_char_idx}",
            'transported_at': time.time() # Optional: for later debugging or limits
        })
        
        logging.info(f"Symbol '{char}' (tag: {f"sol_{original_line_idx}_{original_char_idx}"}) added to falling symbols in Window C and tracked as worm-transported.")
        
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
    
    def _update_worm_solution_symbols(self):
        """Update the list of solution symbols for worm interaction"""
        if not hasattr(self, 'worm_animation') or not self.worm_animation or not self.solution_symbol_display:
            self.after(1000, self._update_worm_solution_symbols) # Try again
            return
            
        # Ensure solution_symbol_display has drawn symbols before trying to find them
        if not self.solution_symbol_display.character_positions:
            logging.info("Solution symbols not yet positioned. Will retry worm symbols update.")
            self.after(250, self._update_worm_solution_symbols) # Shortened retry from 1000ms
            return
            
        # Check if canvas is ready and has dimensions
        canvas_width, canvas_height = self.solution_symbol_display.get_canvas_dimensions()
        if canvas_width is None or canvas_height is None or canvas_width <= 1 or canvas_height <= 1:
            logging.info("Canvas not yet sized properly for worm solution symbols update. Will retry.")
            self.after(250, self._update_worm_solution_symbols) # Shortened retry from 1000ms
            return
            
        # Ensure solution_symbol_display has drawn symbols before trying to find them
        # This check is somewhat redundant due to the one above, but good for belt-and-suspenders
        if not self.solution_symbol_display.character_positions: # Check again, just in case.
            logging.info("Solution symbols (second check) not yet positioned. Will retry worm symbols update.")
            self.after(250, self._update_worm_solution_symbols) # Shortened retry from 1000ms
            return

        # Reset solution symbols list for worms
        self.solution_symbols_data_for_worms = []
        
        # Keep track of warnings to avoid log flooding
        missing_tags = set()
        found_tags = 0
        
        # Loop through all characters in current solution steps
        for line_idx, line in enumerate(self.current_solution_steps):
            for char_idx, char_val in enumerate(line):
                if not char_val.strip(): # Skip spaces for worm targeting
                    continue

                # Get precise coordinates for this symbol
                coords = self.solution_symbol_display.get_symbol_coordinates(line_idx, char_idx)
                
                # Get canvas item ID if available
                char_tag_text = f"ssd_{line_idx}_{char_idx}_text"
                items = []
                
                try:
                    items = self.solution_symbol_display.canvas.find_withtag(char_tag_text)
                except tk.TclError:
                    # Canvas might be in a transient state
                    pass
                
                # Check if we found a valid canvas item
                if items:
                    symbol_canvas_id = items[0]
                    found_tags += 1
                    
                    is_visible_to_player = (line_idx, char_idx) in self.visible_chars
                    
                    self.solution_symbols_data_for_worms.append({
                        'id': symbol_canvas_id,
                        'position': coords,
                        'char': char_val,
                        'line_idx': line_idx,
                        'char_idx': char_idx,
                        'visible_to_player': is_visible_to_player
                    })
                else:
                    # We may not have found a canvas item for this character
                    # but we still have valid coordinates from the SolutionSymbolDisplay
                    # Add it with a placeholder ID that the worm can still use for position targeting
                    if coords and coords[0] is not None and coords[1] is not None:
                        missing_tags.add(char_tag_text)
                        # Still add to worm data but with placeholder ID
                        self.solution_symbols_data_for_worms.append({
                            'id': -1,  # Placeholder ID
                            'position': coords,
                            'char': char_val,
                            'line_idx': line_idx,
                            'char_idx': char_idx,
                            'visible_to_player': (line_idx, char_idx) in self.visible_chars,
                            'is_placeholder': True  # Flag as placeholder to avoid operations requiring a real canvas ID
                        })

        # Log a summary of missing tags instead of individual messages
        if missing_tags:
            if len(self.solution_symbols_data_for_worms) == 0:
                logging.warning(f"No symbols found for worms. Canvas items may not be drawn yet. Will retry.")
                self.after(1000, self._update_worm_solution_symbols)
                return
            elif self.debug_mode:
                logging.warning(f"_update_worm_solution_symbols: Could not find {len(missing_tags)} canvas items, but found {found_tags} valid items")
        
        # Log success on finding all symbols
        if found_tags > 0 and not missing_tags and self.debug_mode:
            logging.info(f"_update_worm_solution_symbols: Successfully found all {found_tags} symbol canvas items")
            
        # Update worm animation with current symbols
        if self.worm_animation and hasattr(self.worm_animation, 'update_solution_symbols'):
            try:
                self.worm_animation.update_solution_symbols(self.solution_symbols_data_for_worms)
            except Exception as e:
                logging.error(f"Error updating worm solution symbols: {e}")
        
        # Schedule next update
        self.after(2000, self._update_worm_solution_symbols)  # Update every 2 seconds
    
    def _check_if_step_complete(self, line_idx):
        """Checks if all characters in a given solution step line are visible."""
        if line_idx < 0 or line_idx >= len(self.current_solution_steps):
            return False

        current_line = self.current_solution_steps[line_idx]
        # Consider only non-space characters for completion
        required_chars_count = sum(1 for char_idx, char_val in enumerate(current_line) if char_val.strip())
        
        visible_required_chars_count = 0
        for char_idx, char_val in enumerate(current_line):
            if char_val.strip() and (line_idx, char_idx) in self.visible_chars:
                visible_required_chars_count += 1
        
        is_complete = visible_required_chars_count >= required_chars_count
        
        if is_complete and line_idx not in self.completed_line_indices_for_problem: # Process only if newly completed
            self.completed_line_indices_for_problem.add(line_idx)
            logging.info(f"Step {line_idx + 1} ('{current_line}') is now complete.")

            # Stop any pulsation on symbols of this line if they were targeted
            if self.solution_symbol_display:
                for char_idx_loop in range(len(current_line)):
                     # This assumes pulsation_after_ids uses a specific key format
                    pulse_key = f"pulse_{line_idx}_{char_idx_loop}"
                    if pulse_key in self.solution_symbol_display.pulsation_after_ids:
                        self.solution_symbol_display.stop_specific_pulsation(pulse_key)


            if self.lock_animation:
                # This will be handled by _check_for_lock_visual_update which is called from reveal_char
                # self.lock_animation.unlock_next_part() # Avoid double-unlocking
                pass # Visual update handled elsewhere
            
            if self.feedback_manager:
                self.feedback_manager.show_feedback(f"Step {line_idx + 1} Unlocked!", 3000) # Changed "success" to 3000ms

            # Worm specific logic after a row is completed
            if self.worm_animation:
                if not self.worm_animation.animation_running:
                    logging.info("First row complete, starting worm animation and transport timer.")
                    self.worm_animation.start_animation(1) # Start with one worm
                    self._start_transport_timer() # Also start the transport timer logic
                else:
                    # If animation is already running (i.e., not the first row completed)
                    logging.info(f"Row {line_idx + 1} complete, adding a new worm.")
                    self.worm_animation.add_worm()
                
                # Call on_step_complete for speed boost logic etc.
                self.worm_animation.on_step_complete()

            self.check_level_complete() # Check if the entire level is complete
            return True
            
        return False # Step not complete or already processed

    def _start_transport_timer(self):
        """Starts the worm's symbol transport timer if conditions are met."""
        if hasattr(self, 'worm_animation') and self.worm_animation and self.worm_animation.animation_running:
            # Manually trigger the first transport
            self.worm_animation._transport_random_symbol()
            
            # Start the automatic timer for future transports
            self.worm_animation._schedule_symbol_transport()
            logging.info("Symbol transport timer started")

    def on_resize(self, event):
        """Handle window resize"""
        if event.widget == self: # Ensure the event is for the main Toplevel window
            # Use after_idle to ensure all resize operations are complete
            self.after_idle(self._process_resize)

    def _process_resize(self):
        """Actual resize processing logic"""
        self.redraw_game_elements()
        
        # Update lock dimensions when window is resized
        self._update_lock_dimensions()
        
        if hasattr(self, 'feedback_manager') and self.feedback_manager:
            if self.symbol_canvas.winfo_exists(): # Check if canvas exists
                self.feedback_manager.update_dimensions(self.symbol_canvas.winfo_width(), self.symbol_canvas.winfo_height())
                # self.feedback_manager.clear_feedback() # Clearing on resize might be too aggressive, let messages stay

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
        self.frame_b = tk.Frame(self, bg="#FFFFFF", bd=2, relief=tk.SUNKEN)
        self.frame_b.grid(row=0, column=2, sticky="nsew", padx=5, pady=5)
        self.frame_b.grid_columnconfigure(0, weight=1)
        
        # Configure rows for help button and solution lines
        self.frame_b.grid_rowconfigure(0, weight=0)  # Help button area
        self.frame_b.grid_rowconfigure(1, weight=1)  # Solution lines area

        # Add Help Button
        self.help_button = HelpButton(self.frame_b, self)

        # Canvas for Solution Lines
        self.solution_canvas = tk.Canvas(self.frame_b, bg="#FFFFFF", highlightthickness=0)
        self.solution_canvas.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

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
                self.after(50, lambda: self.solution_symbol_display.update_data(self.current_solution_steps, self.visible_chars))
                
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
        if self.game_over or not self.winfo_exists() or not self.falling_symbols: 
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
            revealed_color = "#336699"  # Standard revealed color

            logging.info(f"[SYMBOL_RETURN_DEBUG] Clicked '{clicked_char}' (transported). Original: L{original_line_idx}C{original_char_idx}, Tag: {original_char_tag}.")
            logging.info(f"[SYMBOL_RETURN_DEBUG] self.visible_chars BEFORE add: {self.visible_chars}")

            # Make it visible again in Window B
            try:
                self.visible_chars.add((original_line_idx, original_char_idx))
                logging.info(f"[SYMBOL_RETURN_DEBUG] self.visible_chars AFTER add: {self.visible_chars}")

                logging.info(f"[SYMBOL_RETURN_DEBUG] Calling solution_symbol_display.update_data to redraw Window B.")
                if self.solution_symbol_display:
                    self.solution_symbol_display.update_data(self.current_solution_steps, self.visible_chars)
                logging.info(f"[SYMBOL_RETURN_DEBUG] update_data finished. Attempting flash_char_green for L{original_line_idx}C{original_char_idx}.")
                
                # self.flash_char_green(original_char_tag, revealed_color) # Flash it # Old call
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
                
            # Add to visible chars
            self.visible_chars.add((line_idx, char_idx))
            
            # Ensure SolutionSymbolDisplay is synced with the new visible_chars state
            # This will redraw symbols, applying correct initial visibility and colors.
            if self.solution_symbol_display:
                self.solution_symbol_display.update_data(self.current_solution_steps, self.visible_chars)

            # Reveal character in canvas using SolutionSymbolDisplay
            # char_tag = f"sol_{line_idx}_{char_idx}" # Old tag
            # target_color = "#336699"  # A blue color for revealed characters # Old color
            
            try:
                if self.solution_symbol_display:
                    logging.info(f"[reveal_char] Preparing to call solution_symbol_display.reveal_symbol for ({line_idx}, {char_idx}) for char '{char_to_reveal_for_log}'.")
                    self.solution_symbol_display.reveal_symbol(line_idx, char_idx) # Uses its own red color
                    logging.info(f"[reveal_char] Successfully called reveal_symbol. Now flashing green using SolutionSymbolDisplay.")
                    
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
                logging.warning(f"[reveal_char] TclError during itemconfig/flash for char '{char_to_reveal_for_log}' tag '{f"sol_{line_idx}_{char_idx}"}' ({line_idx}, {char_idx}): {e}")
                
            # Check if this step is now complete
            self._check_if_step_complete(line_idx)
                
            # Update lock segment visuals if appropriate
            self._check_for_lock_visual_update()
            
            logging.info(f"[reveal_char] Successfully revealed character '{char_to_reveal_for_log}' (tag: {f"sol_{line_idx}_{char_idx}"}) at position ({line_idx}, {char_idx}).")
                    
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

    # The draw_crack_effect method has been moved to the ErrorAnimation class

    # The redraw_saved_cracks method has been moved to the ErrorAnimation class

    # The draw_shatter_effect method has been moved to the ErrorAnimation class

    def trigger_game_over(self):
        """Handle game over state"""
        logging.info("NOTICE: Game over functionality has been permanently removed")
        # This function is kept as a stub to maintain compatibility with any code that calls it
        # but it will not actually trigger any game over state
        return

    def reveal_all_remaining_red(self):
        """Reveals all hidden solution characters in red"""
        if not self.winfo_exists(): return
        logging.info("Revealing remaining solution steps in red.")
        for i, line in enumerate(self.current_solution_steps):
            for j, char in enumerate(line):
                if char.strip() and (i, j) not in self.visible_chars:
                    char_tag = f"sol_{i}_{j}"
                    try:
                        self.solution_canvas.itemconfig(char_tag, fill="#FF0000") # Red color
                    except tk.TclError:
                         logging.warning("TclError during reveal_all_remaining_red, likely window closed.")
                         return # Stop if canvas is gone
        self.visible_chars = set() # Clear visible list as game is over

    def show_level_failed_popup(self):
        """Displays the enhanced 'Level Failed' pop-up window"""
        if not self.winfo_exists(): return # Don't show if main window closed
        
        # Import the enhanced popup class
        from level_complete_popup import LevelCompletePopup
        
        # Create failure message based on current level
        if self.current_level == "Easy":
            subtitle = "Don't worry! Math takes practice. Would you like to try again?"
        elif self.current_level == "Medium":
            subtitle = "This level is challenging, but you're getting closer. Try again?"
        elif self.current_level == "Division":
            subtitle = "Division can be tricky. Ready to give it another shot?"
        else:
            subtitle = "Keep practicing - you'll solve it next time!"
        
        # Create and show the enhanced popup with red theme
        popup_manager = LevelCompletePopup(self)
        
        # Override colors for failure theme
        popup_manager.colors = {
            "background": "#1a0000",  # Very dark red
            "title": "#ff5d5d",       # Bright red
            "subtitle": "#ee9090",    # Light red
            "button_bg": "#4d0000",   # Dark red
            "button_fg": "#ffcccc",   # Very light red
            "button_hover": "#660000",  # Slightly brighter red
            "particle_colors": ["#ff5d5d", "#ee9090", "#ff0000", "#ff6666", "#cc3333"]
        }
        
        popup = popup_manager.show(
            title="Try Again?",
            subtitle=subtitle,
            callback_next=lambda: self.handle_popup_choice(None, "retry"),
            callback_level_select=lambda: self.handle_popup_choice(None, "level_select"),
            width=400,
            height=300
        )
        
        # Update button text
        for child in popup.winfo_children():
            if isinstance(child, tk.Canvas):
                for item in child.find_withtag("window"):
                    button_frame = child.itemcget(item, "window")
                    if button_frame:
                        for button in button_frame.winfo_children():
                            if button.cget("text") == "Next Problem":
                                button.config(text="Retry")
        
        # Wait for the popup to be closed
        self.wait_window(popup)

    def handle_popup_choice(self, popup, choice):
        """Handles the button clicks in level popups"""
        # Close the popup if it was provided and still exists
        if popup and popup.winfo_exists():
            popup.destroy()
            
        logging.info(f"Popup choice selected: {choice}")
        
        try:
            if choice == "retry":
                # Clear game state and load new problem
                self.clear_saved_game()
                self.clear_all_cracks()
                logging.info("Retry: About to load new problem")
                self.load_new_problem()
                self.game_over = False
                # Reset game state
                self.visible_chars = set()
                self.incorrect_clicks = 0
                
                # Re-initialize falling symbols animation
                if hasattr(self, 'falling_symbols') and self.falling_symbols:
                    self.falling_symbols.stop_animation()
                logging.info("Retry: Creating new falling symbols")
                self.falling_symbols = None
                self.falling_symbols = FallingSymbols(self.symbol_canvas, list("0123456789Xx +-=÷×*/()"))
                self.after(100, self.falling_symbols.start_animation)
                logging.info("Retry: Game state reset and new problem loaded")
            elif choice == "level_select":
                # Return to level select screen
                self.parent.deiconify()  # Show the parent (level select) window
                self.destroy()  # Close the gameplay window
                logging.info("Returning to level select screen")
            elif choice == "next":
                # Clear current game state
                self.clear_saved_game()
                self.clear_all_cracks()
                
                # Reset state variables
                self.game_over = False
                self.visible_chars = set()
                self.incorrect_clicks = 0
                self.currently_targeted_by_worm = None
                self.transported_by_worm_symbols = []  # Clear tracked worm symbols
                
                # Stop existing animation
                logging.info("Next: Stopping existing animations")
                if hasattr(self, 'falling_symbols') and self.falling_symbols:
                    self.falling_symbols.stop_animation()
                self.falling_symbols = None
                
                # Reset worm animation if it exists
                if hasattr(self, 'worm_animation') and self.worm_animation:
                    logging.info("Next: Stopping worm animation and clearing worms.")
                    self.worm_animation.stop_animation()
                    self.worm_animation.clear_worms() # Add this line
                    # Reset worm-specific state variables related to GameplayScreen
                    self.currently_targeted_by_worm = None
                    self.transported_by_worm_symbols = []
                    self.solution_symbols_data_for_worms = [] # This will be repopulated by _update_worm_solution_symbols
                    # Force re-initialization of worm animation data for the new problem
                    self.after(200, self._update_worm_solution_symbols) # Shortened delay from 500ms
                
                # Load new problem
                logging.info("Next: About to load new problem")
                self.load_new_problem()
                logging.info(f"Next: New problem loaded: '{self.current_problem}'")
                
                # Start new animation
                logging.info("Next: Creating new falling symbols")
                self.falling_symbols = FallingSymbols(self.symbol_canvas, list("0123456789Xx +-=÷×*/()"))
                self.after(100, self.falling_symbols.start_animation)
                logging.info("Starting next problem")
            else:
                logging.error(f"Unknown popup choice: {choice}")
        except Exception as e:
            logging.error(f"Error handling popup choice '{choice}': {str(e)}")
            logging.error(traceback.format_exc())
            # Try to recover by loading a new problem if possible
            try:
                logging.info("Attempting recovery from popup handling error")
                self.clear_saved_game()
                self.clear_all_cracks()
                self.game_over = False
                self.visible_chars = set()
                self.incorrect_clicks = 0
                self.currently_targeted_by_worm = None
                
                # Stop any existing animations
                if hasattr(self, 'falling_symbols') and self.falling_symbols:
                    self.falling_symbols.stop_animation()
                if hasattr(self, 'worm_animation') and self.worm_animation:
                    self.worm_animation.stop_animation()
                
                # Reinitialize and load
                self.load_new_problem()
                self.falling_symbols = FallingSymbols(self.symbol_canvas, list("0123456789Xx +-=÷×*/()"))
                self.after(100, self.falling_symbols.start_animation)
                logging.info("Recovered from error by loading new problem")
            except Exception as recovery_error:
                logging.error(f"Failed to recover from error: {str(recovery_error)}")
                logging.error(traceback.format_exc())
                # Last resort - return to level select
                if self.parent and self.parent.winfo_exists():
                    self.parent.deiconify()
                if self.winfo_exists():
                    self.destroy()

    def check_level_complete(self):
        """Check if all solution steps are completed"""
        if self.game_over:
            return

        # Count visible characters in each line
        all_lines_complete = True
        for line_idx, line in enumerate(self.current_solution_steps):
            line_complete = all((line_idx, char_idx) in self.visible_chars 
                               for char_idx in range(len(line)))
            
            if not line_complete:
                all_lines_complete = False
                break
                
        if all_lines_complete:
            logging.info("All steps completed! Level complete.")
            self.level_complete()
            return True
        return False

    def level_complete(self):
        """Handle level completion"""
        logging.info(f"Level {self.current_level} completed!")
        
        try:
            # Clear saved game file
            self.clear_saved_game()
            
            # Ensure lock is fully unlocked
            if self.lock_animation:
                try:
                    self.lock_animation.celebrate_problem_solved()
                except Exception as e:
                    logging.error(f"Error during lock celebration: {e}")
            
            # Stop gameplay-specific timers
            self.game_is_active = False
            
            # If worm animation exists, make them celebrate
            if hasattr(self, 'worm_animation') and self.worm_animation:
                try:
                    self.worm_animation.celebrate(duration=1000)
                except Exception as e:
                    logging.error(f"Error during worm celebration: {e}")
            
            # Remove any cracks from the error animation
            if self.error_animation:
                try:
                    self.error_animation.clear_all_cracks()
                except Exception as e:
                    logging.error(f"Error clearing cracks: {e}")
            
            # Reset worm targets and other states
            self.currently_targeted_by_worm = None
            
            # Display popup immediately
            logging.info("About to show level complete popup")
            self.show_level_complete_popup()
            
        except Exception as e:
            logging.error(f"Critical error in level_complete: {e}")
            logging.error(traceback.format_exc())
            # Try to show popup anyway as a last resort
            try:
                self.show_level_complete_popup()
            except Exception as popup_error:
                logging.error(f"Could not show level complete popup: {popup_error}")

    def show_level_complete_popup(self):
        """Displays the enhanced 'Level Complete' pop-up window"""
        if not self.winfo_exists(): return
        
        # Import the enhanced popup class
        from level_complete_popup import LevelCompletePopup
        
        # Create success message based on current level
        if self.current_level == "Easy":
            subtitle = "Great work! You've mastered the basics. Ready for a new challenge?"
        elif self.current_level == "Medium":
            subtitle = "Impressive skills! Your mathematical prowess is growing stronger."
        elif self.current_level == "Division":
            subtitle = "Excellent! You've conquered division problems with precision."
        else:
            subtitle = "Congratulations! You've solved the equation brilliantly."
        
        # Create and show the enhanced popup
        popup_manager = LevelCompletePopup(self)
        popup = popup_manager.show(
            title="Level Complete!",
            subtitle=subtitle,
            callback_next=lambda: self.handle_popup_choice(None, "next"),
            callback_level_select=lambda: self.handle_popup_choice(None, "level_select"),
            width=400,
            height=300
        )
        
        # Wait for the popup to close before continuing
        self.wait_window(popup)

    def exit_game(self, event=None):
        """Closes the gameplay screen"""
        logging.info("Escape pressed. Refreshing cracks before exiting.")
        self.refresh_cracks()
        self.after(300, lambda: (logging.info("Gameplay screen closed"), self.destroy()))

    def refresh_cracks(self):
        """Refresh the crack effects by clearing and redrawing them."""
        logging.info("Refreshing cracks on refresh event.")
        if not self.game_over:
            logging.info("Game not over; skipping crack refresh.")
            return
            
        # Only redraw cracks if game is over
        self.clear_all_cracks()
        if self.error_animation and self.game_over:
            self.error_animation.draw_shatter_effect()

    def get_hex_with_alpha(self, hex_color, alpha):
        """Convert a hex color and alpha value to a background-blended hex color"""
        try:
            # Extract RGB components from hex_color
            r_fg = int(hex_color[1:3], 16)
            g_fg = int(hex_color[3:5], 16)
            b_fg = int(hex_color[5:7], 16)

            # Get background color (assuming black for simplicity here, adjust if needed)
            # For more accuracy, could try to get the actual background widget color
            bg_color_rgb = self.winfo_rgb("#000000") # Assumes black background
            r_bg = bg_color_rgb[0] // 256
            g_bg = bg_color_rgb[1] // 256
            b_bg = bg_color_rgb[2] // 256

            # Alpha blending formula: R = R_fg * alpha + R_bg * (1 - alpha)
            r = int(r_fg * alpha + r_bg * (1 - alpha))
            g = int(g_fg * alpha + g_bg * (1 - alpha))
            b = int(b_fg * alpha + b_bg * (1 - alpha))

            # Clamp values to 0-255
            r = max(0, min(255, r))
            g = max(0, min(255, g))
            b = max(0, min(255, b))

            # Convert back to hex
            return f"#{r:02x}{g:02x}{b:02x}"
        except Exception as e:
             logging.error(f"Error in get_hex_with_alpha: {e}")
             return hex_color # Return original color on error

    def schedule_auto_save(self):
        """Schedule periodic auto-saving of game state"""
        if self.winfo_exists() and not self.game_over:
            self.save_game_state()
            # Cancel previous auto_save_after_id if it exists
            if hasattr(self, 'auto_save_after_id') and self.auto_save_after_id:
                self.after_cancel(self.auto_save_after_id)
            self.auto_save_after_id = self.after(self.auto_save_interval, self.schedule_auto_save)
        elif hasattr(self, 'auto_save_after_id') and self.auto_save_after_id:
            # If window doesn't exist or game is over, ensure any pending auto-save is cancelled.
            self.after_cancel(self.auto_save_after_id)
            self.auto_save_after_id = None
    
    def save_game_state(self):
        """Save the current game state to a file"""
        if self.game_over:
            # Clear save file when game is over
            self.clear_saved_game()
            return
            
        try:
            save_file = os.path.join(self.save_dir, f"save_{self.current_level}.json")
            
            # Prepare state data - ensure all data is JSON serializable
            state = {
                'level': self.current_level,
                'current_problem': self.current_problem,
                'current_solution_steps': [str(step) for step in self.current_solution_steps],
                'visible_chars': [[int(x), int(y)] for x, y in self.visible_chars],
                'incorrect_clicks': int(self.incorrect_clicks),
                'saved_cracks': []  # Don't save cracks as they might contain non-serializable data
            }
            
            # Save to file with proper formatting
            with open(save_file, 'w') as f:
                json.dump(state, f, indent=2)
                
            logging.info(f"Game state saved for level {self.current_level}")
        except Exception as e:
            logging.error(f"Error saving game state: {e}")
    
    def load_game_state(self):
        """Try to load a saved game state"""
        try:
            save_file = os.path.join(self.save_dir, f"save_{self.current_level}.json")
            
            if not os.path.exists(save_file):
                logging.info(f"No save file found for level {self.current_level}")
                return False
                
            with open(save_file, 'r') as f:
                state = json.load(f)
                
            # Restore state with proper type conversion
            self.current_level = str(state['level'])
            self.current_problem = str(state['current_problem'])
            self.current_solution_steps = [str(step) for step in state['current_solution_steps']]
            self.visible_chars = set((int(x), int(y)) for x, y in state['visible_chars'])
            self.incorrect_clicks = int(state['incorrect_clicks'])
            # Cracks are managed by the error_animation class now
            
            if self.incorrect_clicks < self.max_incorrect_clicks:
                self.clear_all_cracks()
            
            # Update UI with loaded state
            if ":" in self.current_problem:
                prefix, equation = self.current_problem.split(":", 1)
                self.problem_prefix_label.config(text=prefix.strip())
                self.problem_equation_label.config(text=equation.strip())
            else:
                self.problem_prefix_label.config(text="Problem")
                self.problem_equation_label.config(text=self.current_problem.strip())
            
            self.draw_solution_lines()
            
            logging.info(f"Game state loaded for level {self.current_level}")
            return True
        except Exception as e:
            logging.error(f"Error loading game state: {e}")
            return False
    
    def clear_saved_game(self):
        """Remove the saved game file when level is complete or failed"""
        try:
            save_file = os.path.join(self.save_dir, f"save_{self.current_level}.json")
            if os.path.exists(save_file):
                os.remove(save_file)
                logging.info(f"Removed save file for level {self.current_level}")
        except Exception as e:
            logging.error(f"Error removing save file: {e}")

    def clear_all_cracks(self):
        """Clears all cracks from both canvases"""
        # if hasattr(self, 'solution_canvas'): # Solution canvas cracks were not standard
            # self.solution_canvas.delete("crack")
        if hasattr(self, 'symbol_canvas'): # Symbol canvas (Window C) uses error_animation for cracks
            # self.symbol_canvas.delete("crack") # Old direct deletion
            pass # Now handled by error_animation.clear_all_cracks()

        if hasattr(self, 'error_animation') and self.error_animation:
            self.error_animation.clear_all_cracks() # This is for Window C (symbol_canvas)

    def destroy(self):
        """Clean up resources before destroying the window"""
        logging.info("Cleaning up gameplay screen resources before destruction")
        
        # Cancel any animation timers first
        if hasattr(self, 'animation_after_id') and self.animation_after_id:
            self.after_cancel(self.animation_after_id)
            self.animation_after_id = None
            
        # Cancel falling symbols animation timer
        if self.falling_symbols:
            self.falling_symbols.stop_animation()
            
        # Cancel worm animation timer
        if hasattr(self, 'worm_animation') and self.worm_animation:
            self.worm_animation.stop_animation()
            
        # Cancel auto-save timer
        if hasattr(self, 'auto_save_after_id') and self.auto_save_after_id:
            self.after_cancel(self.auto_save_after_id)
            self.auto_save_after_id = None
            
        # Cancel any flash timers - Now handled by SolutionSymbolDisplay
        # if hasattr(self, 'flash_ids'):
        #     for unique_key, timer_id_val in list(self.flash_ids.items()): # Iterate over a copy of items
        #         if timer_id_val:
        #             try:
        #                 self.after_cancel(timer_id_val)
        #             except Exception as e:
        #                 logging.warning(f"Error cancelling flash timer ID {timer_id_val} for key {unique_key}: {e}")
        #     self.flash_ids.clear() # Clear all tracked flash timers
        if self.solution_symbol_display:
            self.solution_symbol_display.stop_all_pulsations() # Ensure its animations are stopped
        
        # Manage save state more explicitly based on game_over status
        if self.game_over:
            # If game was over (e.g., level completed or failed and led to game_over state),
            # ensure the save file for this attempt is cleared.
            logging.info(f"Game is over. Clearing save file for level {self.current_level}.")
            self.clear_saved_game()
        else:
            # If game is not over (e.g., user exited mid-game),
            # save the current state for potential resumption.
            # Only save if the window still notionally exists (might be overly cautious here as destroy is happening)
            if self.winfo_exists(): 
                logging.info(f"Game not over. Saving state for level {self.current_level}.")
                self.save_game_state()
            else:
                # This case should ideally not be hit if destroy() is called on a valid window object
                logging.info(f"Game not over, but window does not exist. Skipping save for level {self.current_level}.")
            
        # Clear visual elements
        try:
            if hasattr(self, 'lock_animation') and self.lock_animation:
                self.lock_animation.clear_visuals()
                
            if hasattr(self, 'error_animation') and self.error_animation:
                self.error_animation.clear_all_cracks()
                
            if hasattr(self, 'feedback_manager') and self.feedback_manager:
                self.feedback_manager.clear_feedback()
        except Exception as e:
            logging.error(f"Error during visual cleanup: {e}")
            
        # Remove reference to teleport manager if it exists
        if hasattr(self, 'teleport_manager'):
            # The teleport_manager might not have a clear_particles method
            # Just remove the reference
            self.teleport_manager = None
            
        # Call parent class's destroy method
        logging.info("Calling tk.Toplevel.destroy()")
        super().destroy()
        logging.info("Gameplay screen destroyed.")

    def _ensure_fullscreen(self):
        """Ensure window is displayed in fullscreen mode"""
        try:
            # Try Windows approach first
            self.state('zoomed')
            logging.info("Window set to zoomed state")
        except Exception as e:
            # Fall back to -fullscreen attribute
            logging.info(f"Setting fullscreen: {e}")
            self.attributes('-fullscreen', True)
            
        # Ensure window has focus
        self.focus_force()

    def set_fullscreen(self):
        """Attempt to force fullscreen or maximized display across platforms using multiple methods."""
        self.update_idletasks()
        try:
            self.state('zoomed')
        except Exception as e:
            logging.error(f"state('zoomed') failed: {e}")
            try:
                self.attributes('-fullscreen', True)
            except Exception as e2:
                logging.error(f"attributes('-fullscreen') failed: {e2}")
                screen_width = self.winfo_screenwidth()
                screen_height = self.winfo_screenheight()
                self.geometry(f"{screen_width}x{screen_height}+0+0")

        # Ensure window has focus
        try:
            self.focus_force()
        except:
            pass

    def _is_symbol_match(self, clicked_char: str, required_char: str) -> bool:
        """Compare two symbols for equality, handling special cases and whitespace."""
        logging.info(f"[_is_symbol_match] Comparing clicked_char: '{clicked_char}' (ord: {ord(clicked_char) if len(clicked_char)==1 else 'N/A'}) with required_char: '{required_char}' (ord: {ord(required_char) if len(required_char)==1 else 'N/A'})")
        
        # Handle whitespace comparison
        if clicked_char.isspace() and required_char.isspace():
            logging.info(f"[_is_symbol_match] Whitespace match: True")
            return True
            
        # Normalize both characters for comparison
        import unicodedata
        clicked_norm = unicodedata.normalize('NFKC', clicked_char).strip()
        required_norm = unicodedata.normalize('NFKC', required_char).strip()
        logging.info(f"[_is_symbol_match] Normalized - clicked_norm: '{clicked_norm}' (len: {len(clicked_norm)}), required_norm: '{required_norm}' (len: {len(required_norm)})")

        # Direct match after normalization
        if clicked_norm == required_norm:
            logging.info(f"[_is_symbol_match] Result: True (Normalized direct match: '{clicked_norm}' == '{required_norm}')")
            return True
            
        # Special cases for mathematical operators
        # Using sets for cleaner checking
        multiplication_aliases = {'×', 'x', '*'}
        division_aliases = {'÷', '/', ':'}
        
        if clicked_norm in multiplication_aliases and required_norm in multiplication_aliases:
            logging.info(f"[_is_symbol_match] Result: True (Multiplication alias match: '{clicked_norm}' in {multiplication_aliases} and '{required_norm}' in {multiplication_aliases})")
            return True
        if clicked_norm in division_aliases and required_norm in division_aliases:
            logging.info(f"[_is_symbol_match] Result: True (Division alias match: '{clicked_norm}' in {division_aliases} and '{required_norm}' in {division_aliases})")
            return True
        # No specific alias for +, -, = as they are usually direct matches
            
        # Case-insensitive match for letters (already handled by normalization if letters are the same case)
        # This explicit check can be useful if normalization isn't enough for some specific letter cases.
        if clicked_norm.isalpha() and required_norm.isalpha():
            is_alpha_match = clicked_norm.lower() == required_norm.lower()
            logging.info(f"[_is_symbol_match] Result: {is_alpha_match} (Alpha case-insensitive match: '{clicked_norm.lower()}' == '{required_norm.lower()}')")
            return is_alpha_match
        
        logging.info(f"[_is_symbol_match] Result: False (No specific match type triggered for '{clicked_norm}' vs '{required_norm}')")
        return False

    def provide_help(self):
        """Automatically picks a correct character and reveals it."""
        if self.game_over:
            logging.info("Provide Help: Game is over, no help provided.")
            return

        if not self.current_solution_steps or not any(s.strip() for s in self.current_solution_steps):
            logging.warning("Provide Help: No valid solution steps loaded (problem might be empty or not loaded). Cannot provide help.")
            # Consider if a problem should be loaded here if this state is reached.
            # For now, just returning to avoid errors.
            return

        initial_revealable_chars = self.find_next_required_char()

        if not initial_revealable_chars:
            logging.info("Provide Help: No revealable characters found by find_next_required_char. Verifying level completion state.")
            # This could mean the level is genuinely complete, or find_next_required_char has an issue.
            self.after(10, self.check_level_complete) 
            return
        
        line_idx, char_idx, _ = initial_revealable_chars[0]
        
        try:
            char_to_reveal = self.current_solution_steps[line_idx][char_idx] # Get char for logging
            self.reveal_char(line_idx, char_idx)
            logging.info(f"Help used: Character '{char_to_reveal}' revealed at position ({line_idx}, {char_idx})")
            
            # After revealing, check again if the level is now complete
            remaining_chars_after_help = self.find_next_required_char()
            if not remaining_chars_after_help:
                logging.info("Provide Help: Revealing character via help seems to have completed the level. Verifying...")
                self.after(10, self.check_level_complete) 
            else:
                logging.info(f"Provide Help: Level not yet complete. {len(remaining_chars_after_help)} revealable chars remaining after help.")
            
            self.after(10, self.auto_reveal_spaces) # Auto-reveal spaces after help

        except IndexError:
             logging.error(f"Provide Help: IndexError for char at ({line_idx}, {char_idx}). Steps: {self.current_solution_steps}")
        except Exception as e:
            logging.error(f"Error providing help internally: {e}")

    def auto_reveal_spaces(self):
        """Automatically reveals space characters if they are next in the solution."""
        if self.game_over:
            return

        while True:
            next_required_chars = self.find_next_required_char()
            if not next_required_chars:
                # No more characters to reveal, check if level is complete
                self.after(10, self.check_level_complete)
                break

            # Check the first revealable character
            line_idx, char_idx, required_char = next_required_chars[0]

            if required_char.isspace():
                if self.debug_mode:
                    logging.info(f"Auto-revealing space at ({line_idx}, {char_idx})")
                self.reveal_char(line_idx, char_idx)
                # Loop again to see if the next char is also a space
            else:
                # Next character is not a space, stop auto-revealing
                break
        
        # After auto-revealing spaces, it's possible the level is complete
        # (e.g., if the solution was just "x = 1" and only spaces remained)
        # We already call check_level_complete if next_required_chars is empty.
        # If it's not empty, it means a non-space character is next, so no need for an extra check here.

    def get_solution_char_coords(self, line_idx, char_idx):
        """Calculate the exact coordinates for a character in the solution canvas.
        Delegates to SolutionSymbolDisplay.
        """
        if self.solution_symbol_display:
            return self.solution_symbol_display.get_symbol_coordinates(line_idx, char_idx)
        else:
            # Fallback if solution_symbol_display is not initialized (should not happen in normal operation)
            logging.warning("GameplayScreen.get_solution_char_coords called before solution_symbol_display was initialized.")
            canvas_width = self.solution_canvas.winfo_width() if hasattr(self, 'solution_canvas') and self.solution_canvas.winfo_exists() else 600
            canvas_height = self.solution_canvas.winfo_height() if hasattr(self, 'solution_canvas') and self.solution_canvas.winfo_exists() else 400
            return (canvas_width / 2, canvas_height / 2)

# --- Main execution (for testing) ---
if __name__ == "__main__":
    # Set up basic logging for testing
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    # Create a dummy root window for testing
    root = tk.Tk()
    root.title("MathMaster Launcher (Test)")
    root.geometry("300x200")

    def launch_game(level):
        root.withdraw() # Hide the launcher
        game_window = GameplayScreen(root, level)
        game_window.protocol("WM_DELETE_WINDOW", lambda: on_game_close(root, game_window))

    def on_game_close(root_win, game_win):
        game_win.destroy()
        try:
            root_win.deiconify() # Show launcher again
        except tk.TclError: pass # Ignore if root already destroyed

    tk.Label(root, text="Select Level to Test:", font=("Arial", 14)).pack(pady=10)

    tk.Button(root, text="Easy", command=lambda: launch_game("Easy")).pack(pady=5)
    tk.Button(root, text="Medium", command=lambda: launch_game("Medium")).pack(pady=5)
    tk.Button(root, text="Division", command=lambda: launch_game("Division")).pack(pady=5)

    root.mainloop()
    logging.info("=== MathMaster Test Launcher Closed ===")
