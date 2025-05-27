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
try:
    from lock_animation_improved import LockAnimation # Import the improved lock animation class
    logging.info("Using improved lock animation")
except ImportError:
    from lock_animation import LockAnimation # Fallback to original lock animation class
    logging.info("Using original lock animation (improved version not found)")
from error_animation import ErrorAnimation # Import the new error animation class
from falling_symbols import FallingSymbols # Import the falling symbols manager
from WormsWindow_B import WormAnimation # Import the worm animation class
from window_b_solution_symbols import SolutionSymbolDisplay # Added import
from stoic_quotes import get_random_quote
from help_display import HelpDisplay

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

        self.in_level_transition = False  # Initialize the attribute here

        # Auto-save directory - needs to be initialized before clear_saved_game can be called
        self.save_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "saves")
        os.makedirs(self.save_dir, exist_ok=True)
        
        # Timer tracking for better cleanup during transitions
        self.active_timers = set()  # Track all active after() calls

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
        self.solution_char_details = [] # Initialize solution_char_details
        self.animation_after_id = None # For managing animation loop
        self.auto_save_after_id = None # For managing auto-save loop
        self.transported_solution_chars = [] # Initialize list for transported chars
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
        
        # Initialize stoic quote early to ensure it's available for add_stoic_quote_watermark
        self.stoic_quote = get_random_quote()
        
        # Stats manager for tracking performance (initialize as None)
        self.stats_manager = None
        
        # Track if help button has been clicked
        self.help_button_clicked = False

        # --- Layout ---
        self.create_layout() # This creates self.solution_canvas

        # Initialize SolutionSymbolDisplay after solution_canvas is created
        if hasattr(self, 'solution_canvas') and self.solution_canvas:
            self.solution_symbol_display = SolutionSymbolDisplay(
                self.solution_canvas, 
                self,
                drawing_complete_callback=self._on_ssd_drawing_complete # Pass the callback
            )
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
        
        # Set level start time for tracking completion time
        self.level_start_time = time.time()

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

        # Initialize help display (use direct initialization instead of delayed)
        try:
            logging.info("Directly initializing help display during __init__")
            self.help_display = HelpDisplay(
                self.solution_canvas,  # Use the solution canvas
                x=20,                  # Position near left edge 
                y=120                  # Position below the help button
            )
            self.help_display.current_help_text = "Click HELP button for algebra assistance" 
            # Don't show help display or text until help button is clicked
            # self.after(800, self._ensure_help_display_visible) # Comment out to hide initially
        except Exception as e:
            logging.error(f"Error during initial help display setup: {e}")
            # Fall back to delayed initialization if direct initialization fails
            self.after(1000, self._setup_help_display)

    def _on_ssd_drawing_complete(self):
        """Called when SolutionSymbolDisplay completes drawing"""
        logging.info("SolutionSymbolDisplay drawing complete callback received.")
        
        # Attempt to add stoic quote as watermark on solution_canvas
        self.add_stoic_quote_watermark()
            
        # Notify worm animation about available symbols - THIS IS THE PRIMARY TRIGGER after drawing
        if hasattr(self, '_update_worm_solution_symbols') and callable(self._update_worm_solution_symbols):
            # Ensure not in transition before starting the update loop
            if not self.in_level_transition:
                self._update_worm_solution_symbols(initial_call=True)
            else:
                logging.info("SSD drawing complete, but still in level transition. Worm symbol update deferred.")
    
    def add_stoic_quote_watermark(self):
        """Add a transparent stoic quote to window B (solution_canvas)"""
        if not hasattr(self, 'stoic_quote_id') and self.solution_canvas.winfo_exists():
            canvas_width = self.solution_canvas.winfo_width()
            canvas_height = self.solution_canvas.winfo_height()
            
            if canvas_width <= 1 or canvas_height <= 1:
                # Canvas not ready, try again later
                self.after(100, self.add_stoic_quote_watermark)
                return
                
            # Increase font size and adjust width to prevent overflow
            font_size = max(14, min(canvas_width // 30, 20))  # Increased from max 14 to max 20
            quote_width = canvas_width * 0.9  # Increased from 0.8 to 0.9 for better scaling
            
            # Limit quote length to prevent overflow
            max_chars_per_line = canvas_width // (font_size // 2)
            displayed_quote = self.stoic_quote
            if len(displayed_quote) > max_chars_per_line * 3:  # Limit to roughly 3 lines
                displayed_quote = displayed_quote[:max_chars_per_line * 3 - 3] + "..."
            
            # Create transparent quote text - positioned at bottom with padding
            bottom_padding = 40  # Ensures it stays away from bottom edge
            self.stoic_quote_id = self.solution_canvas.create_text(
                canvas_width // 2,
                canvas_height - bottom_padding,  # Adjusted from fixed 30 to dynamic padding
                text=displayed_quote,
                font=("Helvetica", font_size, "italic"),
                fill=self.get_hex_with_alpha("#FFFFFF", 0.2),  # Slightly more visible (0.15 -> 0.2)
                width=quote_width,
                justify=tk.CENTER,
                tags="stoic_quote_watermark"
            )
            
            # Send to back so it doesn't interfere with other elements
            self.solution_canvas.tag_lower(self.stoic_quote_id)
            logging.info(f"Added stoic quote watermark to Window B (font size: {font_size})")
            
            # Ensure quote stays within boundaries by checking its boundaries after creation
            quote_bbox = self.solution_canvas.bbox(self.stoic_quote_id)
            if quote_bbox:
                quote_height = quote_bbox[3] - quote_bbox[1]
                # If quote is too big and might overflow outside bottom of canvas
                if quote_bbox[3] > canvas_height - 10:  # 10px safety margin
                    # Reposition higher on canvas
                    new_y = canvas_height - quote_height//2 - 15
                    self.solution_canvas.coords(self.stoic_quote_id, canvas_width // 2, new_y)
                    logging.info(f"Repositioned stoic quote to prevent overflow: {new_y}px from top")
    
    def _init_worm_animation(self):
        if not self.solution_canvas or not self.solution_canvas.winfo_exists():
            logging.warning("Solution canvas not ready for worm animation initialization.")
            return

        logging.info("Initializing Worm Animation for GameplayScreen")
        self.worm_animation = WormAnimation(
            self.solution_canvas, 
            canvas_width=self.solution_canvas.winfo_width(), 
            canvas_height=self.solution_canvas.winfo_height(),
            symbol_transport_callback=self.handle_symbol_transport, # Signature now (line_idx, char_idx, char)
            symbol_targeted_for_steal_callback=self.handle_symbol_targeted_for_steal
        )
        logging.info("Worm Animation initialized and linked to callbacks.")

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
                logging.info(f"Symbol targeted by help system was transported by a worm. Resetting help target.")
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

    def get_hex_with_alpha(self, hex_color, alpha):
        """Convert a hex color and alpha value to a hex color with the specified transparency"""
        try:
            # Extract RGB components
            r = int(hex_color[1:3], 16)
            g = int(hex_color[3:5], 16)
            b = int(hex_color[5:7], 16)
            
            # Apply alpha against black background
            r = int(r * alpha)
            g = int(g * alpha)
            b = int(b * alpha)
            
            # Convert back to hex
            return f"#{r:02x}{g:02x}{b:02x}"
        except Exception as e:
            logging.error(f"Error in color conversion: {e}")
            return hex_color  # Return original color on error

    def _ensure_fullscreen(self):
        """Ensure the window is displayed in fullscreen mode"""
        try:
            self.state('zoomed')  # Windows approach
        except:
            try:
                self.attributes('-fullscreen', True)  # Unix/Linux approach
            except Exception as e:
                logging.error(f"Failed to set fullscreen: {e}")
        
        # Ensure visibility and focus
        self.attributes('-alpha', 1.0)
        self.focus_force()
        
        logging.info("Fullscreen enforcement applied")
    
    def set_fullscreen(self):
        """Set the window to fullscreen mode"""
        self._ensure_fullscreen()  # Use the internal method
    
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
                # Use the centralized reset mechanism for retry
                logging.info("Retry selected: Using centralized reset")
                self.reset_for_new_level()
                
            elif choice == "next":
                # Use the same centralized reset mechanism for next level
                logging.info("Next level selected: Using centralized reset")
                self.reset_for_new_level()
                
            elif choice == "level_select":
                # When returning to level select, ensure all animations are properly disabled
                logging.info("Level select chosen: Cleaning up gameplay screen before destroying")
                self._disable_all_animations()
                
                # Show the parent window
                if self.parent and hasattr(self.parent, 'deiconify') and self.parent.winfo_exists():
                    self.parent.deiconify()  # Show the parent (level select) window
                
                # Destroy this window
                if self.winfo_exists():
                    self.destroy()  # Close the gameplay window
                
                logging.info("Successfully returned to level select screen")
            else:
                logging.error(f"Unknown popup choice: {choice}")
        except Exception as e:
            logging.error(f"Error handling popup choice '{choice}': {str(e)}")
            logging.error(traceback.format_exc())
            
            # Recovery mechanism if reset fails
            try:
                logging.info("Attempting recovery from popup handling error")
                # Fall back to basic reset operations
                self.in_level_transition = True
                self.clear_saved_game()
                self.clear_all_cracks()
                self.game_over = False
                self.visible_chars = set()
                self.incorrect_clicks = 0
                self.currently_targeted_by_worm = None
                
                # Stop any existing animations using our disable method
                self._disable_all_animations()
                
                # Basic problem loading
                self.load_new_problem()
                
                # Basic animation restart
                self.after(500, self._finish_transition)
                
                logging.info("Basic recovery completed")
            except Exception as recovery_error:
                logging.error(f"Failed to recover from error: {str(recovery_error)}")
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
        """Handle completion of level"""
        if self.game_over:
            return
            
        self.game_over = True
        
        # Get the current level (handle potential attribute naming differences)
        current_level = getattr(self, 'level', None)
        if current_level is None:
            current_level = getattr(self, 'current_level', 'unknown')
        
        # Log level completion
        elapsed_time = time.time() - self.level_start_time
        logging.info(f"Level {current_level} completed in {elapsed_time:.2f} seconds!")
        
        # Stop any active animations or timers that shouldn't continue
        if hasattr(self, 'falling_symbols') and self.falling_symbols:
            self.falling_symbols.reduce_generation_rate()  # Slow down but don't stop completely for visual effect
        
        # Make the worms celebrate if they exist
        if hasattr(self, 'worm_animation') and self.worm_animation:
            self.worm_animation.celebrate(3000)  # Celebrate for 3 seconds
            
        # Show a temporary success message on the solution canvas
        self.show_success_message()
        
        # Update the lock animation to celebrate
        if hasattr(self, 'lock_animation') and self.lock_animation:
            self.lock_animation.celebrate_problem_solved()
            
        # Play success sound if available
        if hasattr(self, 'sound_manager') and self.sound_manager:
            self.sound_manager.play_level_complete_sound()
            
        # Show the level complete popup instead of auto-advancing
        if self.winfo_exists():
            self.show_level_complete_popup()
        
        # Refresh auto-saving so we don't auto-save in a completed state
        if hasattr(self, 'auto_save_timer') and self.auto_save_timer:
            self.after_cancel(self.auto_save_timer)
            
        # Update and save statistics
        if hasattr(self, 'stats_manager') and self.stats_manager:
            level_stats = {
                'level': current_level,  # Use our safe current_level variable
                'time_taken': round(elapsed_time, 2),
                'incorrect_clicks': self.incorrect_clicks,
                'difficulty': getattr(self, 'difficulty', 'unknown'),
                'problem': getattr(self, 'current_problem', '')
            }
            self.stats_manager.record_level_completion(level_stats)
            self.stats_manager.save()
            
    def show_level_complete_popup(self):
        """Displays the Matrix-themed 'Level Complete' popup window"""
        print("DEBUG: show_level_complete_popup method called")
        if not self.winfo_exists(): return # Don't show if main window closed
        
        # Import the level complete popup class
        from level_complete_popup import LevelCompletePopup
        print("DEBUG: Imported LevelCompletePopup class")
        
        # Create success message based on current level
        if self.current_level == "Easy":
            subtitle = "Great job! You've mastered this algebra problem."
        elif self.current_level == "Medium":
            subtitle = "Well done! You're becoming a math master."
        elif self.current_level == "Division":
            subtitle = "Excellent! Division mastered."
        else:
            subtitle = "Congratulations on completing this level!"
        
        print(f"DEBUG: Created subtitle: '{subtitle}'")
        
        # Create and show the enhanced popup with matrix theme
        popup_manager = LevelCompletePopup(self)
        print("DEBUG: Created LevelCompletePopup instance")
        
        popup = popup_manager.show(
            title="Level Complete!",
            subtitle=subtitle,
            callback_next=lambda: self.handle_popup_choice(None, "next"),
            callback_level_select=lambda: self.handle_popup_choice(None, "level_select"),
            width=450,
            height=300
        )
        print("DEBUG: Called show() method on popup_manager")
        
        # Wait for the popup to be closed
        print("DEBUG: About to wait_window for popup")
        self.wait_window(popup)
        print("DEBUG: Returned from wait_window")

    def clear_saved_game(self):
        """Clear any saved game for the current level"""
        save_file = os.path.join(self.save_dir, f"level_{self.current_level}.json")
        if os.path.exists(save_file):
            try:
                os.remove(save_file)
                logging.info(f"Cleared saved game for level {self.current_level}")
            except Exception as e:
                logging.error(f"Error clearing saved game for level {self.current_level}: {e}")
                
    def load_game_state(self):
        """Load the game state from a save file"""
        save_file = os.path.join(self.save_dir, f"level_{self.current_level}.json")
        if not os.path.exists(save_file):
            logging.info(f"No saved game found for level {self.current_level}")
            return False
            
        try:
            with open(save_file, 'r') as f:
                data = json.load(f)
                
            # Load saved game state
            self.current_problem = data.get('problem', '')
            self.current_solution_steps = data.get('solution_steps', [])
            self.visible_chars = set((line, char) for line, char in data.get('visible_chars', []))
            self.incorrect_clicks = data.get('incorrect_clicks', 0)
            self.game_over = data.get('game_over', False)
            self.completed_line_indices_for_problem = set(data.get('completed_lines', []))
            
            # Redraw solution with visible characters
            self.draw_solution_lines()
            
            logging.info(f"Loaded saved game for level {self.current_level}")
            return True
        except Exception as e:
            logging.error(f"Error loading saved game for level {self.current_level}: {e}")
            return False
            
    def schedule_auto_save(self):
        """Schedule the auto-save function"""
        self.auto_save_timer = self.after(self.auto_save_interval, self.auto_save_game)

    def auto_save_game(self):
        """Save the current game state to a file"""
        save_file = os.path.join(self.save_dir, f"level_{self.current_level}.json")
        data = {
            'problem': self.current_problem,
            'solution_steps': self.current_solution_steps,
            'visible_chars': list(self.visible_chars),
            'incorrect_clicks': self.incorrect_clicks,
            'game_over': self.game_over,
            'completed_lines': list(self.completed_line_indices_for_problem)
        }
        try:
            with open(save_file, 'w') as f:
                json.dump(data, f)
            logging.info(f"Game state saved for level {self.current_level}")
        except Exception as e:
            logging.error(f"Error saving game state for level {self.current_level}: {e}")
        
        # Schedule the next auto-save
        self.schedule_auto_save()
        
    def auto_reveal_spaces(self):
        """Automatically reveal spaces in the current solution step"""
        if self.game_over:
            return
            
        try:
            # Find valid positions for the current step
            valid_positions = self.find_next_required_char()
            
            # Check each position to see if it's a space
            for line_idx, char_idx, char_val in valid_positions:
                if char_val.isspace():
                    # Reveal spaces automatically
                    self.reveal_char(line_idx, char_idx)
            
            # Check for level completion
            self.check_level_complete()
        except Exception as e:
            logging.error(f"Error in auto_reveal_spaces: {e}")
            
    def exit_game(self, event=None):
        """Exit the gameplay screen and return to level select"""
        logging.info("User exiting gameplay screen.")
        
        # Attempt to disable all animations and cancel timers before destroying
        try:
            if hasattr(self, 'in_level_transition') and not self.in_level_transition:
                # If not already in a transition (which would call _disable_all_animations),
                # call it now to clean up before explicit exit.
                self._disable_all_animations()
            elif not hasattr(self, 'in_level_transition'):
                # If the flag doesn't exist for some reason, try to disable anyway
                # This is a fallback, ideally the flag always exists.
                self._disable_all_animations() 
        except Exception as e:
            logging.error(f"Exception during pre-exit cleanup in exit_game: {e}")

        if hasattr(self.parent, 'deiconify') and self.parent.winfo_exists():
            self.parent.deiconify() # Show the WelcomeScreen/LevelSelectScreen

        if self.winfo_exists():
            self.destroy()  # Close the gameplay screen window
        logging.info("Gameplay screen destroyed.")

    def get_solution_char_coords(self, line_idx, char_idx):
        """Returns the canvas coordinates of a specific solution character.
        Delegates to SolutionSymbolDisplay for accurate coordinates.
        
        Args:
            line_idx: The line/step index
            char_idx: The character index within the line
            
        Returns:
            Tuple (x, y) of the character's center position or None if not found
        """
        try:
            if not hasattr(self, 'solution_symbol_display') or not self.solution_symbol_display:
                logging.warning("[get_solution_char_coords] SolutionSymbolDisplay not initialized.")
                return None

            # Use the SolutionSymbolDisplay to get coordinates
            coords = self.solution_symbol_display.get_symbol_coordinates(line_idx, char_idx)
            
            if coords and coords[0] is not None and coords[1] is not None:
                # SolutionSymbolDisplay.get_symbol_coordinates should already return center.
                logging.debug(f"[get_solution_char_coords] Coords from SSD for L{line_idx}C{char_idx}: {coords}")
                return coords
            else:
                logging.warning(f"[get_solution_char_coords] SSD returned invalid coords for L{line_idx}C{char_idx}: {coords}. Solution steps: {len(self.current_solution_steps)}")
                if self.debug_mode and line_idx < len(self.current_solution_steps):
                    logging.debug(f"Line content: '{self.current_solution_steps[line_idx]}'")
                return None
                
        except Exception as e:
            logging.error(f"Error in get_solution_char_coords for L{line_idx}C{char_idx}: {e}")
            import traceback
            logging.error(traceback.format_exc())
            return None

    def provide_help(self):
        """Provide contextual help based on the current problem state and reveal next character."""
        logging.info("HELP BUTTON CLICKED: Starting help processing")
        
        try:
            # Set the flag to true since help button was clicked
            self.help_button_clicked = True
            
            # Make the solution canvas visible on first help click
            if not self.solution_canvas_visible:
                self.solution_canvas_visible = True
                logging.info("Making solution canvas visible now that help button was clicked")
                
            # STEP 1: Find the next character to reveal
            valid_positions = self.find_next_required_char()
            if valid_positions:
                # Get the first unrevealed character position
                next_pos = valid_positions[0]  # (line_idx, char_idx, char)
                line_idx, char_idx = next_pos[0], next_pos[1]
                
                # Reveal this character
                logging.info(f"Help button revealing character at position ({line_idx}, {char_idx})")
                self.reveal_char(line_idx, char_idx)
            
            # STEP 2: Draw solution lines if this is the first help click
            # This will make the text box visible only after help is clicked
            if hasattr(self, 'solution_symbol_display') and self.solution_symbol_display:
                self.draw_solution_lines()
            
            # STEP 3: Show explanatory text (existing functionality)
            # Force creation of help display if it doesn't exist
            if not hasattr(self, 'help_display') or self.help_display is None:
                logging.info("Help display not found - creating it now")
                self.help_display = HelpDisplay(
                    self.solution_canvas,
                    x=20,
                    y=120
                )
            
            # Get current progress
            current_step = self._get_current_step_index()
            logging.info(f"Current step index: {current_step}")
            
            # Get text to display
            if current_step is not None and current_step < len(self.current_solution_steps):
                current_step_text = self.current_solution_steps[current_step]
                logging.info(f"Current step text: '{current_step_text}'")
                
                # Create a more immediate visual feedback that help is working
                self._flash_help_area()
                
                # Update help display with contextual information
                self.help_display.update_help_text(
                    current_step_index=current_step,
                    total_steps=len(self.current_solution_steps),
                    step_text=current_step_text
                )
                
                # Make sure it's visible
                self.help_display.show()
                
                logging.info(f"Help provided for step {current_step}")
            else:
                # Fallback to symbol-based help
                symbols = set()
                for line in self.current_solution_steps:
                    for char in line:
                        if char in "+-*/=×÷":
                            symbols.add(char)
                
                # Create a more immediate visual feedback
                self._flash_help_area()
                
                # Update help with symbol-based context
                self.help_display.update_help_text(symbols=list(symbols))
                
                # Make sure it's visible
                self.help_display.show()
                
                logging.info(f"Symbol-based help provided with symbols: {symbols}")
        except Exception as e:
            logging.error(f"Error providing help: {e}")
            import traceback
            logging.error(traceback.format_exc())

    def _flash_help_area(self):
        """Create a visual flash on the help area to show button press registered."""
        try:
            if not hasattr(self, 'solution_canvas') or not self.solution_canvas.winfo_exists():
                return
                
            # Calculate position for the flash effect
            canvas_width = self.solution_canvas.winfo_width()
            flash_x = 20  # Same as help_display x
            flash_y = 120  # Same as help_display y
            flash_width = min(300, canvas_width - 40)  # Limited by canvas width
            flash_height = 80
            
            # Create a temporary highlight rectangle
            flash_id = self.solution_canvas.create_rectangle(
                flash_x, flash_y,
                flash_x + flash_width, flash_y + flash_height,
                fill="#AAFFAA",  # Light green
                outline="#44AA44",
                stipple="gray50",
                tags="help_flash"
            )
            
            # Schedule removal of flash effect
            def remove_flash():
                try:
                    if self.solution_canvas.winfo_exists():
                        self.solution_canvas.delete("help_flash")
                except:
                    pass
                    
            self.after(500, remove_flash)
            
        except Exception as e:
            logging.error(f"Error creating help flash effect: {e}")

    def _get_current_step_index(self):
        """Determine which step the player is currently working on."""
        try:
            # If no solution steps or in transition, return a safe value
            if not self.current_solution_steps or hasattr(self, 'in_level_transition') and self.in_level_transition:
                return 0 # Return 0 instead of None for safer indexing
            
            # Find the first incomplete step
            for step_idx, step_text in enumerate(self.current_solution_steps):
                # Count visible characters in this step
                visible_count = sum(1 for char_idx in range(len(step_text)) 
                                   if (step_idx, char_idx) in self.visible_chars)
                
                # If not all characters are visible, this is the current step
                if visible_count < len(step_text):
                    return step_idx
            
            # If all steps are complete, return the last step
            return len(self.current_solution_steps) - 1 if self.current_solution_steps else 0
        
        except Exception as e:
            logging.error(f"Error determining current step: {e}")
            return 0 # Return 0 instead of None for safer indexing

    def show_success_message(self):
        """Show a temporary success message on the solution canvas when level is complete."""
        try:
            if hasattr(self, 'solution_canvas') and self.solution_canvas.winfo_exists():
                # Delete any existing success message
                if hasattr(self, 'success_message_id'):
                    self.solution_canvas.delete(self.success_message_id)
                    
                # Get canvas dimensions
                canvas_width = self.solution_canvas.winfo_width()
                canvas_height = self.solution_canvas.winfo_height()
                
                # Create the success message
                self.success_message_id = self.solution_canvas.create_text(
                    canvas_width / 2, 
                    canvas_height / 2,
                    text="Level Complete!",
                    font=("Arial", 24, "bold"),
                    fill="#00AA00",  # Green color
                    tags="success_message"
                )
                
                # Add a glow effect
                self.success_glow_id = self.solution_canvas.create_oval(
                    canvas_width / 2 - 120, 
                    canvas_height / 2 - 40,
                    canvas_width / 2 + 120, 
                    canvas_height / 2 + 40,
                    fill="#AAFFAA",
                    outline="#00AA00",
                    width=2,
                    stipple="gray50",
                    tags="success_message"
                )
                
                # Move glow behind text
                self.solution_canvas.tag_lower(self.success_glow_id, self.success_message_id)
                
                # Schedule cleanup after 4 seconds
                self.after(4000, self._clear_success_message)
                
                logging.info("Displayed level complete success message")
        except Exception as e:
            logging.error(f"Error displaying success message: {e}")
            
    def _clear_success_message(self):
        """Clear the success message from the solution canvas."""
        try:
            if hasattr(self, 'solution_canvas') and self.solution_canvas.winfo_exists():
                self.solution_canvas.delete("success_message")
                
            # Clear the IDs
            if hasattr(self, 'success_message_id'):
                del self.success_message_id
            if hasattr(self, 'success_glow_id'):
                del self.success_glow_id
        except Exception as e:
            logging.error(f"Error clearing success message: {e}")

    def _setup_help_display(self):
        """Set up the help display after a short delay to ensure solution_canvas exists."""
        try:
            if hasattr(self, 'solution_canvas') and self.solution_canvas.winfo_exists():
                # Initialize help display in Window B area
                self.help_display = HelpDisplay(
                    self.solution_canvas,  # Use the solution canvas
                    x=20,                  # Position near left edge
                    y=120                  # Position below the help button
                )
                self.help_display.show()   # Show with default text
                
                # Force initial visibility
                self.help_display.current_help_text = "Click HELP button for algebra assistance"
                self.help_display.update_display()
                
                logging.info("Help display initialized successfully")
            else:
                logging.warning("Could not initialize help display - solution_canvas not found or not ready")
                # Try again after a delay
                self.after(300, self._setup_help_display)
        except Exception as e:
            logging.error(f"Error setting up help display: {e}")
            import traceback
            logging.error(traceback.format_exc())

    def _ensure_help_display_visible(self):
        """Make sure the help display is visible after initialization."""
        try:
            if hasattr(self, 'help_display') and self.help_display:
                logging.info("Ensuring help display is visible")
                self.help_display.update_display()
                self.help_display.show()
        except Exception as e:
            logging.error(f"Error making help display visible: {e}")

    def _disable_all_animations(self):
        """Disable all animations during transitions to prevent lag"""
        logging.info("Disabling all animations for transition")
        
        self.in_level_transition = True
        cancelled_timers = 0
        
        # Cancel generic GameplayScreen after() timers if any were tracked by a non-standard `after_ids()`
        # It's safer to manage after_ids within each component or for specific known GameplayScreen timers.
        # For now, assuming self.after_ids() was a placeholder or for specific known timers.
        # If GameplayScreen schedules its own loops (like auto_save_timer), they need explicit cancellation.

        if hasattr(self, 'auto_save_timer') and self.auto_save_timer:
            try:
                self.after_cancel(self.auto_save_timer)
                self.auto_save_timer = None # Clear the ID
                cancelled_timers += 1
                logging.info("Auto-save timer cancelled")
            except Exception as e:
                logging.warning(f"Error cancelling auto_save_timer: {e}")

        # Stop FallingSymbols animation
        if hasattr(self, 'falling_symbols') and self.falling_symbols:
            self.falling_symbols.stop_animation()
            self.falling_symbols.clear_symbols()
            logging.info("Falling symbols animation stopped and symbols cleared")
            
        # Stop WormAnimation
        if hasattr(self, 'worm_animation') and self.worm_animation:
            self.worm_animation.stop_animation()
            self.worm_animation.clear_worms() # Also clears particles and internal states
            self.currently_targeted_by_worm = None # Reset gameplay screen's tracking
            logging.info("Worm animation stopped and worms cleared")
            
        # Stop SolutionSymbolDisplay pulsations
        if hasattr(self, 'solution_symbol_display') and self.solution_symbol_display:
            self.solution_symbol_display.stop_all_pulsations()
            self.solution_symbol_display.clear_all_visuals() # Clear drawn symbols
            logging.info("Solution symbol display pulsations stopped and visuals cleared")

        # Stop LockAnimation activities
        if hasattr(self, 'lock_animation') and self.lock_animation:
            self.lock_animation.stop_all_persistent_animations()
            self.lock_animation.clear_visuals() # Ensure its canvas items are gone
            logging.info("Lock animation persistent tasks stopped and visuals cleared")
            
        # Reset error animation state (clears cracks and any scheduled crack animations)
        if hasattr(self, 'error_animation') and self.error_animation:
            self.error_animation.clear_all_cracks()
            logging.info("Error animation cracks cleared")

        # Clear teleport manager pending operations if any
        if hasattr(self, 'teleport_manager') and self.teleport_manager and hasattr(self.teleport_manager, 'clear_pending_operations'):
            self.teleport_manager.clear_pending_operations()
            logging.info("Teleport manager operations cleared")
        
        # Cancel any tracked timers
        if hasattr(self, 'active_timers'):
            for timer_id in list(self.active_timers):
                try:
                    self.after_cancel(timer_id)
                    cancelled_timers += 1
                except Exception as e:
                    logging.warning(f"Error cancelling tracked timer {timer_id}: {e}")
            self.active_timers.clear()
        
        logging.info(f"Explicitly cancelled known timers. Total cancelled: {cancelled_timers}")
            
        # Force garbage collection to clean up memory
        try:
            import gc
            gc.collect()
            logging.info("Forced garbage collection during transition")
        except Exception:
            pass
            
        logging.info("All animations and key activities disabled for transition")
            
    def _enable_animations_after_transition(self):
        """Restart animations in sequence after transition completes"""
        if not self.winfo_exists():
            return
            
        logging.info("Restarting animations in sequence with conservative timing")
        
        # Step 1: Ensure UI is updated first
        self.update_idletasks()
        
        # Step 2: Reset help display to avoid index errors (do this first)
        self._reset_help_display()
        
        # Step 3: Re-create falling symbols but don't start yet (less resource intensive)
        if not hasattr(self, 'falling_symbols') or self.falling_symbols is None:
            self.falling_symbols = FallingSymbols(self.symbol_canvas, list("0123456789Xx +-=÷×*/()"))
        
        # Define sequence of delayed operations with progressively longer gaps
        # The ordering and timing is crucial for preventing overlap
        schedule = [
            # First update the solution display with current data
            (400, lambda: self.solution_symbol_display.update_data(self.current_solution_steps, self.visible_chars) if hasattr(self, 'solution_symbol_display') else None),
            
            # Then add the stoic quote watermark after solution display is updated
            (800, lambda: self.add_stoic_quote_watermark()),
            
            # Reset worm system but don't start animation yet
            (1200, lambda: self._reset_worm_system()),
            
            # Start falling symbols animation in window C
            (1800, lambda: self.falling_symbols.start_animation() if hasattr(self, 'falling_symbols') and self.falling_symbols else None),
            
            # Finally, complete the transition process
            (2400, lambda: self._finish_transition())
        ]
        
        # Schedule each operation with proper delay and error handling
        for delay, operation in schedule:
            def safe_wrapper(op=operation):
                try:
                    # Check if window still exists before executing operation
                    if self.winfo_exists() and not self.game_over:
                        op()
                except Exception as e:
                    logging.error(f"Error during animation restart sequence: {e}")
            
            self.after(delay, safe_wrapper)
        
        logging.info("Animation restart sequence scheduled with conservative timing")
        
        # Add a safety timer to ensure transition completes even if some operations fail
        self.after(4000, lambda: self._finish_transition() if hasattr(self, 'in_level_transition') and self.in_level_transition else None)

    def _reset_worm_system(self):
        # Properly stop and clear the worm animation system to avoid glitches during level transition
        if hasattr(self, 'worm_animation') and self.worm_animation:
            self.worm_animation.stop_animation()
            self.worm_animation.clear_worms()
            self.worm_animation = None

        # Reset worm update retries counter
        self._worm_update_retries = 0

    def _reset_help_display(self):
        """Reset help display to avoid index errors after transition"""
        try:
            if hasattr(self, 'help_display') and self.help_display:
                self.help_display.current_help_text = "Click HELP button for algebra assistance"
                self.help_display.update_display()
        except Exception as e:
            logging.error(f"Error resetting help display: {e}")
            
    def _reset_worm_update_retries(self):
        """Reset the worm update retry counter"""
        self._worm_update_retries = 0
    
    def _schedule_with_tracking(self, delay, callback):
        """Schedule a callback with timer tracking for better cleanup"""
        timer_id = self.after(delay, callback)
        if hasattr(self, 'active_timers'):
            self.active_timers.add(timer_id)
        return timer_id
    
    def _cancel_tracked_timer(self, timer_id):
        """Cancel a tracked timer and remove from tracking"""
        if timer_id:
            try:
                self.after_cancel(timer_id)
            except Exception as e:
                logging.warning(f"Error cancelling timer {timer_id}: {e}")
            finally:
                if hasattr(self, 'active_timers'):
                    self.active_timers.discard(timer_id)
            
    def _finish_transition(self):
        """Complete the transition process"""
        # Clear transition flag
        self.in_level_transition = False
        
        # Restart auto-save
        self.schedule_auto_save()
        
        # Reset help button flag to ensure window B is hidden until help button is clicked
        self.help_button_clicked = False
        
        # Reset any worm and symbol interaction data
        self.currently_targeted_by_worm = None
        self.solution_symbols_data_for_worms = []
        self.transported_by_worm_symbols = []
        
        # Ensure all animations are properly reset and initialized
        if hasattr(self, 'worm_animation') and self.worm_animation:
            self.worm_animation.reset_for_new_problem()
            
        # Force garbage collection to clean up memory
        try:
            import gc
            gc.collect()
        except Exception:
            pass
            
        logging.info("Level transition complete - normal operation resumed")

    def teleport_symbol(self, symbol_id, start_pos, end_pos, is_correct=False):
        """Teleport a symbol from Window C to its place in solution
        
        Args:
            symbol_id: Canvas ID of the symbol
            start_pos: (x, y) tuple of starting position
            end_pos: (x, y) tuple of target position
            is_correct: Whether symbol matches solution (affects visual effects)
        """
        # Safety check for null or invalid end_pos
        if not end_pos or None in end_pos:
            logging.error(f"Cannot handle teleport: end_pos is None for symbol_id {symbol_id}")
            return
            
        try:
            # Extract coordinates
            start_x, start_y = start_pos
            end_x, end_y = end_pos
            
            # Calculate parameters for arc
            # ...rest of the method continues as before
        except Exception as e:
            logging.error(f"Error handling teleport_symbol: {e}")

    def reset_for_new_level(self):
        """
        Comprehensive reset for transitioning to a new level without recreating UI.
        This centralizes the level transition logic to avoid animation overlap and lag.
        """
        logging.info("=== BEGINNING COMPREHENSIVE LEVEL RESET ===")
        
        # Flag that we're in transition to prevent new animations from starting
        self.in_level_transition = True
        
        # 1. Cancel all animations and timers
        logging.info("1. Canceling all animations and timers")
        self._disable_all_animations()  # This also calls component-specific cleanup
        
        # 2. Clear game state
        logging.info("2. Clearing game state")
        self.visible_chars = set()
        self.incorrect_clicks = 0
        self.game_over = False
        self.completed_line_indices_for_problem.clear()
        self.help_button_clicked = False  # Start with help text hidden
        
        # 3. Clear saved game data
        logging.info("3. Clearing saved game data")
        self.clear_saved_game()
        
        # 4. Update stoic quote
        self.stoic_quote = get_random_quote()
        if hasattr(self, 'stoic_quote_id') and self.stoic_quote_id:
            try:
                self.solution_canvas.delete(self.stoic_quote_id)
            except tk.TclError:
                pass
            self.stoic_quote_id = None
        
        # 5. Load new problem
        logging.info("5. Loading new problem")
        self.load_new_problem()  # This will update necessary labels and prepare solution steps
        
        # 6. Update level start time
        self.level_start_time = time.time()
        self.level_transition_timer = time.time()  # Track transition time for coordination
        
        # 7. Schedule restart of animations with conservative delays
        logging.info("6. Re-enabling animations with sequential delays")
        self.after(300, self._enable_animations_after_transition)
        
        logging.info("=== LEVEL RESET PROCEDURE INITIATED ===")
        return True  # Indicate success
