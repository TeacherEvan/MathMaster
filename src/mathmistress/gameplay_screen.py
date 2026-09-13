# gameplay_screen.py
import tkinter as tk
import random
import time
import logging
import json
import os
import traceback # Added import
from ui_components.feedback_manager import FeedbackManager # Added import
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
from constants import DEFAULT_HELP_TEXT, EQUATION_PATTERN_A, EQUATION_PATTERN_B, EQUATION_PATTERN_B_PREFIX  # Hoisted repeated literals (2026-09-10)
import help_system as _help_system  # Extracted help subsystem (2026-09-13)
import canvas_interaction as _canvas  # Extracted canvas subsystem (2026-09-13)
import worm_system as _worm  # Extracted worm subsystem (2026-09-13)
import transition_system as _transition  # Extracted transition subsystem (2026-09-13)
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
        logging.info("[generate_solution_steps] Found literal '\\n' in problem. Splitting by '\\n'.")
        return [step.strip() for step in problem.split("\\n") if step.strip()]
    if "\n" in problem: # Check for actual newline characters
        logging.info("[generate_solution_steps] Found actual newline character in problem. Splitting by newline.")
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
        if EQUATION_PATTERN_A in equation_part: 
            logging.info(f"[generate_solution_steps] Attempting to parse as '{EQUATION_PATTERN_A}' for '{equation_part}'")
            try:
                # Split around "+ x -" to get 'a' and 'c'
                parts = equation_part.split(EQUATION_PATTERN_A)
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
                    logging.warning(f"[generate_solution_steps] '{EQUATION_PATTERN_A}' pattern for '{problem}' split yielded {len(parts)} parts, expected 2. Parts: {parts}")
            except (ValueError, IndexError) as e:
                logging.warning(f"[generate_solution_steps] Error parsing '{problem}' with '{EQUATION_PATTERN_A}' specific pattern: {e}. Falling through.")

        # Try to parse "x + a - c = b"
        # Example: x + 12 - 2 = 20
        elif equation_part.startswith("x +") and "-" in equation_part: 
            logging.info(f"[generate_solution_steps] Attempting to parse as '{EQUATION_PATTERN_B}' for '{equation_part}'")
            try:
                # Remove "x + " from the beginning, then split by "-"
                temp_eq = equation_part.replace(EQUATION_PATTERN_B_PREFIX, "", 1).strip()
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
                    logging.warning(f"[generate_solution_steps] '{EQUATION_PATTERN_B}' pattern for '{problem}' split yielded {len(parts)} parts, expected 2. Parts: {parts}")
            except (ValueError, IndexError) as e:
                logging.warning(f"[generate_solution_steps] Error parsing '{problem}' with '{EQUATION_PATTERN_B}' specific pattern: {e}. Falling through.")
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
                    # Also check if b_div_val is 0, which would create invalid math (x/a = 0)
                    if b_div_val == 0:
                        logging.warning(f"[generate_solution_steps] Invalid equation x/a=0 for '{problem}' - solution would be x=0.")
                        return [original_problem_for_steps, "x = 0"]
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
            self.help_display.current_help_text = DEFAULT_HELP_TEXT  # from constants 
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
        """Add a stoic quote as a subtle watermark to the solution canvas"""
        try:
            # Ensure canvas exists and is ready
            if not hasattr(self, 'solution_canvas') or not self.solution_canvas or not self.solution_canvas.winfo_exists():
                logging.warning("Solution canvas not ready for stoic quote watermark. Retrying later.")
                # Retry after a short delay
                if self.winfo_exists() and not getattr(self, 'in_level_transition', False):
                    self.after(500, self.add_stoic_quote_watermark)
                return
                
            # Get canvas dimensions with validation
            try:
                canvas_width = self.solution_canvas.winfo_width()
                canvas_height = self.solution_canvas.winfo_height()
            except tk.TclError:
                logging.warning("Canvas dimensions not available for stoic quote. Retrying later.")
                if self.winfo_exists() and not getattr(self, 'in_level_transition', False):
                    self.after(500, self.add_stoic_quote_watermark)
                return
                
            # Skip if canvas dimensions aren't valid yet
            if canvas_width <= 1 or canvas_height <= 1:
                logging.info(f"Canvas dimensions not ready ({canvas_width}x{canvas_height}). Retrying stoic quote.")
                if self.winfo_exists() and not getattr(self, 'in_level_transition', False):
                    self.after(500, self.add_stoic_quote_watermark)
                return
                
            # Clear any existing quote
            if hasattr(self, 'stoic_quote_id') and self.stoic_quote_id:
                try:
                    self.solution_canvas.delete(self.stoic_quote_id)
                except tk.TclError:
                    pass  # Quote item may have been already deleted
                self.stoic_quote_id = None
                
            # Ensure we have a quote
            if not hasattr(self, 'stoic_quote') or not self.stoic_quote:
                from stoic_quotes import get_random_quote
                self.stoic_quote = get_random_quote()
                logging.info("Generated new stoic quote for watermark")
                
            # Calculate font size and position
            font_size = max(10, min(canvas_width // 60, 16))
            
            # Position near bottom center, with safety margins
            quote_x = canvas_width // 2
            quote_y = max(canvas_height - 80, canvas_height * 0.85)  # Ensure it's not too close to bottom
            
            # Create the watermark with subtle styling
            self.stoic_quote_id = self.solution_canvas.create_text(
                quote_x, quote_y,
                text=self.stoic_quote,
                font=("Helvetica", font_size, "italic"),
                fill="#E0E0E0",  # Light gray for subtle appearance
                width=canvas_width * 0.8,  # Wrap text to 80% of canvas width
                justify=tk.CENTER,
                tags="stoic_quote_watermark"
            )
            
            # Verify the quote was created and adjust position if needed
            if self.stoic_quote_id:
                try:
                    # Get the actual bounds of the text
                    bbox = self.solution_canvas.bbox(self.stoic_quote_id)
                    if bbox:
                        actual_bottom = bbox[3]
                        # If text extends beyond canvas, move it up
                        if actual_bottom > canvas_height - 10:
                            new_y = canvas_height - (actual_bottom - quote_y) - 20
                            self.solution_canvas.coords(self.stoic_quote_id, quote_x, new_y)
                            logging.info(f"Repositioned stoic quote to prevent overflow: {new_y}px from top")
                except tk.TclError:
                    # If there's an error getting bbox, just log it but don't fail
                    logging.warning("Could not verify stoic quote positioning")
                    
                logging.info("Stoic quote watermark added successfully")
            else:
                logging.warning("Failed to create stoic quote watermark")
                
        except Exception as e:
            logging.error(f"Error adding stoic quote watermark: {e}")
            # Don't retry on unexpected errors to avoid infinite loops
            import traceback
            logging.error(traceback.format_exc())

    def _init_worm_animation(self, *args, **kwargs):
        return _worm._init_worm_animation(self, *args, **kwargs)

    def handle_symbol_transport(self, *args, **kwargs):
        return _worm.handle_symbol_transport(self, *args, **kwargs)

    def handle_symbol_targeted_for_steal(self, *args, **kwargs):
        return _worm.handle_symbol_targeted_for_steal(self, *args, **kwargs)

    def _update_worm_solution_symbols(self, *args, **kwargs):
        return _worm._update_worm_solution_symbols(self, *args, **kwargs)

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
            if hasattr(self, 'worm_animation') and self.worm_animation:
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
            else:
                # Worm animation not ready - try to initialize it
                logging.warning("Worm animation not available on step completion. Attempting to initialize.")
                try:
                    self._init_worm_animation()
                    # After initialization, try to start it
                    if hasattr(self, 'worm_animation') and self.worm_animation:
                        logging.info("Worm animation initialized, starting with first row completion.")
                        self.worm_animation.start_animation(1)
                        self._start_transport_timer()
                    else:
                        logging.error("Failed to initialize worm animation after step completion")
                except Exception as e:
                    logging.error(f"Error initializing worm animation on step completion: {e}")

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
    
    def _is_symbol_match(self, *args, **kwargs):
        return _canvas._is_symbol_match(self, *args, **kwargs)

    def redraw_game_elements(self, *args, **kwargs):
        return _canvas.redraw_game_elements(self, *args, **kwargs)

    def create_layout(self, *args, **kwargs):
        return _canvas.create_layout(self, *args, **kwargs)

    def _update_lock_dimensions(self, *args, **kwargs):
        return _canvas._update_lock_dimensions(self, *args, **kwargs)

    def load_new_problem(self, *args, **kwargs):
        return _canvas.load_new_problem(self, *args, **kwargs)

    def draw_solution_lines(self, *args, **kwargs):
        return _canvas.draw_solution_lines(self, *args, **kwargs)

    def print_solution_details(self, *args, **kwargs):
        return _canvas.print_solution_details(self, *args, **kwargs)

    def find_next_required_char(self, *args, **kwargs):
        return _canvas.find_next_required_char(self, *args, **kwargs)

    def handle_canvas_c_click(self, *args, **kwargs):
        return _canvas.handle_canvas_c_click(self, *args, **kwargs)

    def reveal_char(self, *args, **kwargs):
        return _canvas.reveal_char(self, *args, **kwargs)

    def _check_for_lock_visual_update(self, *args, **kwargs):
        return _canvas._check_for_lock_visual_update(self, *args, **kwargs)

    def flash_char_green(self, *args, **kwargs):
        return _canvas.flash_char_green(self, *args, **kwargs)

    def reset_char_color(self, *args, **kwargs):
        return _canvas.reset_char_color(self, *args, **kwargs)

    def clear_all_cracks(self, *args, **kwargs):
        return _canvas.clear_all_cracks(self, *args, **kwargs)

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

    def provide_help(self, *args, **kwargs):
        return _help_system.provide_help(self, *args, **kwargs)

    def _flash_help_area(self, *args, **kwargs):
        return _help_system._flash_help_area(self, *args, **kwargs)

    def _get_current_step_index(self, *args, **kwargs):
        return _help_system._get_current_step_index(self, *args, **kwargs)

    def show_success_message(self, *args, **kwargs):
        return _help_system.show_success_message(self, *args, **kwargs)

    def _clear_success_message(self, *args, **kwargs):
        return _help_system._clear_success_message(self, *args, **kwargs)

    def _setup_help_display(self, *args, **kwargs):
        return _help_system._setup_help_display(self, *args, **kwargs)

    def _ensure_help_display_visible(self, *args, **kwargs):
        return _help_system._ensure_help_display_visible(self, *args, **kwargs)

    def _disable_all_animations(self, *args, **kwargs):
        return _transition._disable_all_animations(self, *args, **kwargs)

    def _enable_animations_after_transition(self, *args, **kwargs):
        return _transition._enable_animations_after_transition(self, *args, **kwargs)

    def _reset_worm_system(self, *args, **kwargs):
        return _transition._reset_worm_system(self, *args, **kwargs)

    def _reset_help_display(self, *args, **kwargs):
        return _transition._reset_help_display(self, *args, **kwargs)

    def _reset_worm_update_retries(self, *args, **kwargs):
        return _transition._reset_worm_update_retries(self, *args, **kwargs)

    def _schedule_with_tracking(self, *args, **kwargs):
        return _transition._schedule_with_tracking(self, *args, **kwargs)

    def _cancel_tracked_timer(self, *args, **kwargs):
        return _transition._cancel_tracked_timer(self, *args, **kwargs)

    def _finish_transition(self, *args, **kwargs):
        return _transition._finish_transition(self, *args, **kwargs)

    def teleport_symbol(self, *args, **kwargs):
        return _transition.teleport_symbol(self, *args, **kwargs)

    def reset_for_new_level(self):
        """
        Comprehensive reset for transitioning to a new level without recreating UI.
        This centralizes the level transition logic to avoid animation overlap and lag.
        """
        logging.info("=== BEGINNING COMPREHENSIVE LEVEL RESET ===")
        
        # Flag that we're in transition to prevent new animations from starting
        self.in_level_transition = True
        
        # 1. Cancel all animations and timers (but preserve worm system)
        logging.info("1. Disabling animations and canceling timers")
        self._disable_all_animations()  # This calls _reset_worm_system() which now preserves the worm object
        
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
        
        # 4. Update stoic quote for new level
        logging.info("4. Updating stoic quote")
        from stoic_quotes import get_random_quote
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
