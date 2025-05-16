# gameplay_screen.py
import tkinter as tk
import random
import time
import logging
import math  # For math functions in gameplay animations
import json
import os
from src.ui_components.feedback_manager import FeedbackManager # Added import
from lock_animation import LockAnimation # Import the new lock animation class

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

# Falling symbols list, now properly formatted for the different problem types
FALLING_SYMBOLS = list("0123456789Xx +-=÷×*/()")  # Use proper symbols including space, X, x, and parentheses

class GameplayScreen(tk.Toplevel):
    def __init__(self, parent, level):
        super().__init__(parent)
        self.parent = parent
        self.current_level = level
        self.title(f"MathMaster - Level: {self.current_level}")
        self.geometry("1000x700") # Default size
        self.configure(bg="#1e1e1e")
        
        # Add tracking for last problem to avoid repetition
        self.last_problems = []
        self.max_history = 3  # Remember last 3 problems to avoid repetition
        
        # Clear any existing cracks from previous sessions
        self.saved_cracks = []
        
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
        self.visible_chars = [] # List of (line_idx, char_idx) tuples
        self.falling_symbols_on_screen = [] # List of symbol objects/dictionaries
        self.incorrect_clicks = 0
        self.max_incorrect_clicks = 20
        self.game_over = False
        self.flash_ids = {} # To manage flashing effects
        self.animation_after_id = None # For managing animation loop
        self.auto_save_after_id = None # For managing auto-save loop
        self.completed_line_indices_for_problem = set() # For lock animation logic
        self.lock_animation = None # Placeholder for LockAnimation instance
        
        # Debug mode to print character details
        self.debug_mode = True

        # Auto-save directory
        self.save_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "saves")
        os.makedirs(self.save_dir, exist_ok=True)
        
        # --- Layout ---
        self.create_layout()

        # Initialize problem variables to empty state (can be useful, though problem load follows)
        self.current_problem = ""
        self.current_solution_steps = []
        self.visible_chars = [] 

        # Try to load saved state first, or load new problem for the session
        if not self.load_game_state():
            self.load_new_problem()
        else:
            # If a game state was loaded, and it's not game over, prepare the board
            if not self.game_over:
                # Cracks are usually cleared when a new problem loads or on game over.
                # For a loaded game, existing saved cracks might be relevant if we were to save/load them.
                # However, current save_game_state explicitly does not save cracks.
                # So, clearing them here or relying on load_new_problem/trigger_game_over to handle is fine.
                self.clear_all_cracks() # Ensure a clean start if loading a non-game-over state
                self.saved_cracks = []
        
        # --- Print Debug Info ---
        if self.debug_mode:
            self.print_solution_details()

        # --- Start Animation ---
        # Delay starting animation slightly to allow canvas to initialize
        self.after(100, self.animate_falling_symbols)

        # Force fullscreen after initialization
        self.after(200, self._ensure_fullscreen)

        # --- Bindings ---
        self.bind("<Escape>", self.exit_game)
        self.bind("<Configure>", self.on_resize) # Handle resize
        self.bind("<Map>", lambda event: self.refresh_cracks())
        
        # Set up auto-save timer
        self.auto_save_interval = 10000  # 10 seconds
        self.schedule_auto_save()

        # Log gameplay screen start
        logging.info(f"Gameplay screen opened for level: {level}")

        # Ensure fullscreen once widgets are ready
        self.after(50, self.set_fullscreen)

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

    def on_resize(self, event):
        """Handle window resize"""
        if event.widget == self: # Ensure the event is for the main Toplevel window
            # Use after_idle to ensure all resize operations are complete
            self.after_idle(self._process_resize)

    def _process_resize(self):
        """Actual resize processing logic"""
        self.redraw_game_elements()
        if hasattr(self, 'feedback_manager') and self.feedback_manager:
            if self.symbol_canvas.winfo_exists(): # Check if canvas exists
                self.feedback_manager.update_dimensions(self.symbol_canvas.winfo_width(), self.symbol_canvas.winfo_height())
                # self.feedback_manager.clear_feedback() # Clearing on resize might be too aggressive, let messages stay

    def redraw_game_elements(self):
        """Redraw elements that depend on window size"""
        # Redraw solution lines as their position depends on canvas size
        self.draw_solution_lines()
        # Redraw saved cracks
        self.redraw_saved_cracks()
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
        # Configure rows for problem prefix, equation, spacer, and lock animation at the bottom
        self.frame_a.grid_rowconfigure(0, weight=0)  # Problem Prefix Label
        self.frame_a.grid_rowconfigure(1, weight=0)  # Problem Equation Label
        self.frame_a.grid_rowconfigure(2, weight=1)  # Expanding Spacer
        self.frame_a.grid_rowconfigure(3, weight=0)  # Lock Animation Canvas

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

        # Expanding Spacer (New, at row 2)
        spacer_frame = tk.Frame(self.frame_a, bg="#111111") # Same bg as frame_a
        spacer_frame.grid(row=2, column=0, sticky="nsew")

        # Lock Animation Canvas - Make it larger for better visual appeal
        lock_canvas_width = 180  # Increased from 120 to 180
        lock_canvas_height = 180  # Increased from 120 to 180
        self.lock_canvas = tk.Canvas(self.frame_a, width=lock_canvas_width, height=lock_canvas_height, bg="#111111", highlightthickness=0)
        self.lock_canvas.grid(row=3, column=0, pady=(10,15), sticky="s") # Increased padding for prominence
        
        lock_size = 150  # Increased from 100 to 150
        self.lock_animation = LockAnimation(self.lock_canvas, x=lock_canvas_width/2, y=lock_canvas_height/2 + 10, size=lock_size) # Centered, y slightly adjusted for shackle

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

    def load_new_problem(self):
        """Loads a random problem for the selected level"""
        if self.current_level not in PROBLEMS or not PROBLEMS[self.current_level]:
            self.problem_prefix_label.config(text="Error")
            self.problem_equation_label.config(text="No equations available for this level.")
            logging.error(f"No problems found for level: {self.current_level}")
            self.current_problem = "" # Ensure problem state is cleared
            self.current_solution_steps = []
            return

        self.clear_all_cracks()
        self.falling_symbols_on_screen = []
        self.completed_line_indices_for_problem.clear() # Reset for new problem
        if self.lock_animation:
            self.lock_animation.reset()
        
        available_problems = PROBLEMS[self.current_level]
        
        # Filter out recently used problems AND any empty/whitespace-only problem strings
        fresh_problems = [p.strip() for p in available_problems if p.strip() and p not in self.last_problems]
        
        if not fresh_problems:
            # If all fresh problems were used or were empty, try from all available non-empty problems (excluding last one if possible)
            fresh_problems = [p.strip() for p in available_problems if p.strip() and (not self.last_problems or p != self.last_problems[-1])]
            if not fresh_problems:
                 # This means ALL problems for the level are empty/whitespace or only one bad one repeats
                 self.problem_prefix_label.config(text="Error")
                 self.problem_equation_label.config(text=f"No valid problems for {self.current_level}.")
                 logging.error(f"All problems for level {self.current_level} are empty or have been used. Cannot load new problem.")
                 self.current_problem = "" # Ensure problem state is cleared
                 self.current_solution_steps = []
                 return
        
        self.current_problem = random.choice(fresh_problems)
        # self.current_problem should already be stripped from list comprehension, but strip again to be safe.
        self.current_problem = self.current_problem.strip()

        # Update last_problems history to prevent immediate repetition in the same session
        if self.current_problem: # Only add if a valid problem was chosen
            self.last_problems.append(self.current_problem)
            if len(self.last_problems) > self.max_history:
                self.last_problems.pop(0)
        
        logging.info(f"Selected new problem: '{self.current_problem}' from {len(fresh_problems)} available problems. Last problems cache: {self.last_problems}")

        # Final check if problem is somehow still empty (should be caught by list comprehensions)
        if not self.current_problem:
            logging.error(f"Load New Problem: Selected an empty problem string for level '{self.current_level}' despite filtering. This indicates an issue with problem data or logic.")
            self.problem_prefix_label.config(text="Error")
            self.problem_equation_label.config(text="Problem loading failed.")
            self.current_solution_steps = [] # Clear steps
            return
        
        logging.info(f"Selected new problem: '{self.current_problem}' from {len(fresh_problems)} available problems")

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

        logging.info(f"Loaded equation: {display_text}")

        # Reset game state for new problem
        self.visible_chars = []
        self.incorrect_clicks = 0
        self.game_over = False
        self.flash_ids = {}
        # Clear previous solution lines from canvas
        self.solution_canvas.delete("solution_text")
        self.solution_canvas.delete("feedback_flash")

        # Get and prepare solution steps
        self.current_solution_steps = generate_solution_steps(self.current_problem)
        
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
            
        # Ensure redraw happens after canvas is sized
        self.after(50, self.draw_solution_lines)
        self.after(100, self.auto_reveal_spaces) # Auto-reveal initial spaces

    def draw_solution_lines(self):
        """Draw the solution lines on the solution canvas as 8 horizontal lines for solution steps.
        The lower 2/3 of the canvas is used, with a horizontal marker drawn for each line."""
        try:
            # Clear previous texts and markers
            self.solution_canvas.delete("solution_text")
            self.solution_canvas.delete("line_marker")
            
            canvas_width = self.solution_canvas.winfo_width()
            canvas_height = self.solution_canvas.winfo_height()
            if canvas_width <= 1 or canvas_height <= 1:
                self.after(50, self.draw_solution_lines)
                return
            
            num_lines = 8
            # Use bottom 2/3 of the canvas for solution lines
            offset = canvas_height / 3
            available_height = canvas_height * 2 / 3
            line_height = available_height / (num_lines + 1)
            char_width = 30  # Reduced character width for better fitting
            font_size = 22 # Reduced font size
            
            # Draw all solution steps
            if self.debug_mode:
                logging.info(f"Drawing {len(self.current_solution_steps)} solution steps, {num_lines} lines available")
            
            for i in range(num_lines):
                # Draw a horizontal line for each possible step
                y_pos = offset + line_height * (i + 1)
                
                # Draw horizontal marker (underline)
                self.solution_canvas.create_line(
                    10, y_pos + 10, 
                    canvas_width - 10, y_pos + 10, 
                    fill="#666666",  # Gray for better visibility
                    width=2,  # Thicker line
                    dash=(4, 2),  # Dash pattern
                    tags=("line_marker",)
                )
                
                # Draw the solution text for this line if it exists
                if i < len(self.current_solution_steps):
                    line_text = self.current_solution_steps[i]
                    if line_text:  # Skip empty lines
                        total_text_width = len(line_text) * char_width
                        x_start = (canvas_width - total_text_width) / 2
                        
                        # Determine if this is the active line (for debugging only)
                        is_active_line = False
                        if i > 0:
                            prev_line_complete = all((i-1, j) in self.visible_chars for j in range(len(self.current_solution_steps[i-1])))
                            this_line_incomplete = any((i, j) not in self.visible_chars for j in range(len(line_text)))
                            if prev_line_complete and this_line_incomplete:
                                is_active_line = True
                        elif i == 0:
                            this_line_incomplete = any((i, j) not in self.visible_chars for j in range(len(line_text)))
                            if this_line_incomplete:
                                is_active_line = True
                        
                        # Draw each character of the text
                        for j, char in enumerate(line_text):
                            is_visible = (i, j) in self.visible_chars
                            
                            # Set color: black for visible, white for invisible
                            color = "#000000" if is_visible else "#FFFFFF"
                            
                            char_tag = f"sol_{i}_{j}"
                            
                            # Create the character text
                            self.solution_canvas.create_text(
                                x_start + j * char_width, y_pos,
                                text=char,
                                font=("Courier New", font_size, "bold"), # Use new font_size
                                fill=color,
                                anchor="w",
                                tags=("solution_text", char_tag)
                            )
                            
                            # Log active line info for debugging purposes only
                            if self.debug_mode and is_active_line and not is_visible:
                                logging.info(f"Character at position ({i}, {j}) is in the active line and not yet revealed")
            
            if self.debug_mode:
                logging.info(f"Drew solution lines: {len(self.current_solution_steps)} steps")
                
        except Exception as e:
            logging.error(f"Error drawing solution lines: {e}")
            import traceback
            logging.error(traceback.format_exc())

    def animate_falling_symbols(self):
        """Manages the animation loop for falling symbols"""
        if self.game_over or not self.winfo_exists(): 
            if hasattr(self, 'animation_after_id') and self.animation_after_id:
                self.after_cancel(self.animation_after_id)
                self.animation_after_id = None
            return

        try:
            self.update_falling_symbols()
            self.draw_falling_symbols()
            if hasattr(self, 'animation_after_id') and self.animation_after_id: # Clear previous before setting new
                self.after_cancel(self.animation_after_id)
            self.animation_after_id = self.after(50, self.animate_falling_symbols) # Adjust speed (milliseconds)
        except Exception as e:
            if hasattr(self, 'animation_after_id') and self.animation_after_id:
                self.after_cancel(self.animation_after_id)
                self.animation_after_id = None
            if self.winfo_exists():
                logging.error(f"Falling symbol animation error: {e}")
                print(f"Falling symbol animation error: {e}")

    def update_falling_symbols(self):
        """Updates positions and generates new symbols"""
        if not self.winfo_exists(): return # Check if window exists

        canvas_height = self.symbol_canvas.winfo_height()
        canvas_width = self.symbol_canvas.winfo_width()

        if canvas_height <= 1 or canvas_width <= 1: return # Canvas not ready

        # Exactly 7 seconds to fall from top to bottom as per blueprint
        fall_speed = canvas_height / (7 * 20) # Pixels per 50ms interval for 7 sec fall

        # Move existing symbols
        next_symbols = []
        for symbol_info in self.falling_symbols_on_screen:
            symbol_info['y'] += fall_speed
            if symbol_info['y'] < canvas_height + symbol_info['size']: # Keep if still visible
                next_symbols.append(symbol_info)
            else:
                # Symbol reached bottom, delete its canvas item if it exists
                try:
                    if symbol_info.get('id'):
                        self.symbol_canvas.delete(symbol_info['id'])
                except tk.TclError: # Handle case where item might already be deleted
                    pass
        self.falling_symbols_on_screen = next_symbols

        # Add new symbols with 60% chance (increased from 15%)
        if random.random() < 0.60:
            char = random.choice(FALLING_SYMBOLS)
            x_pos = random.randint(20, canvas_width - 20)
            
            # Check if new symbol overlaps with existing ones spawned near the top (to avoid excessive overlap)
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
        if not self.winfo_exists(): return # Check if window exists
        
        try:
            # Clear all existing symbols
            self.symbol_canvas.delete("falling_symbol")
            
            # Draw each symbol
            for symbol_info in self.falling_symbols_on_screen:
                # Create text with larger font size
                symbol_id = self.symbol_canvas.create_text(
                    symbol_info['x'],
                    symbol_info['y'],
                    text=symbol_info['char'],
                    font=("Courier New", 44, "bold"),  # Doubled from 22 to 44
                    fill="#00FF00",
                    tags="falling_symbol"
                )
                symbol_info['id'] = symbol_id
        except tk.TclError:
            # Handle case where canvas is destroyed
            pass

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
        if self.game_over or not self.winfo_exists(): 
            return

        # Log raw click coordinates for debugging
        if self.debug_mode:
            logging.info(f"Raw click at ({event.x}, {event.y}) on symbol canvas")

        # Get canvas coordinates
        canvas = self.symbol_canvas  # Always use symbol_canvas for this handler
        click_x = canvas.canvasx(event.x)
        click_y = canvas.canvasy(event.y)
        click_pos = (click_x, click_y)

        # Use a larger hit area for better detection
        hit_radius = 10  # Increased from 5
        clicked_items = canvas.find_overlapping(
            click_x-hit_radius, click_y-hit_radius,
            click_x+hit_radius, click_y+hit_radius
        )
        
        if not clicked_items:
            if self.debug_mode:
                logging.info(f"No items found at click position {click_pos}")
            return

        # Get the closest item to the click point
        closest_item = None
        closest_distance = float('inf')
        
        for item_id in clicked_items:
            # Get item bounds
            try:
                bbox = canvas.bbox(item_id)
                if not bbox:
                    continue
                    
                # Calculate center of the item
                item_center_x = (bbox[0] + bbox[2]) / 2
                item_center_y = (bbox[1] + bbox[3]) / 2
                
                # Calculate distance to click
                distance = math.sqrt((click_x - item_center_x)**2 + (click_y - item_center_y)**2)
                
                if distance < closest_distance:
                    closest_distance = distance
                    closest_item = item_id
            except Exception as e:
                logging.error(f"Error during item bounds calculation: {e}")
                continue
        
        if not closest_item:
            if self.debug_mode:
                logging.info("Could not determine closest item to click")
            return

        # Find the symbol info for this item
        clicked_symbol_info = None
        symbol_index = -1
        
        for i, symbol_info in enumerate(self.falling_symbols_on_screen):
            if symbol_info.get('id') == closest_item:
                clicked_symbol_info = symbol_info
                symbol_index = i
                break

        if not clicked_symbol_info:
            if self.debug_mode:
                logging.info(f"Item {closest_item} is not in falling_symbols_on_screen")
            return

        clicked_char = clicked_symbol_info['char']
        if self.debug_mode:
            logging.info(f"User clicked symbol: '{clicked_char}' at position {click_pos}")
            logging.info(f"Symbol has ID: {closest_item}")

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
                
                # Calculate target position in solution canvas
                try:
                    target_coords = self.get_solution_char_coords(line_idx, char_idx)
                    
                    logging.info(f"Correct symbol '{clicked_char}' selected, revealing at ({line_idx}, {char_idx})")
                    self.reveal_char(line_idx, char_idx)
                    
                    # Use precise coordinates for teleportation
                    self.teleport_manager.teleport_symbol(
                        closest_item,
                        start_pos=click_pos,
                        end_pos=target_coords,
                        is_correct=True
                    )
                    
                    # Remove the symbol from tracking
                    if symbol_index != -1:
                        del self.falling_symbols_on_screen[symbol_index]
    
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
                    closest_item,
                    start_pos=click_pos,
                    end_pos=click_pos,  # Stay in place for incorrect
                    is_correct=False
                )
    
                self.incorrect_clicks += 1
                crack_info = self.draw_crack_effect()
                if crack_info:
                    self.saved_cracks.append(crack_info)
    
                if self.incorrect_clicks >= self.max_incorrect_clicks:
                    self.trigger_game_over()
        except Exception as e:
            logging.error(f"Critical error in handle_canvas_c_click: {e}")
            import traceback
            logging.error(traceback.format_exc())

    def reveal_char(self, line_idx, char_idx):
        """Reveals a character in the solution"""
        if self.game_over:
            logging.info(f"[reveal_char] Ignoring reveal_char call for ({line_idx}, {char_idx}) because game is over.")
            return
        
        char_to_reveal_for_log = '' # Initialize for logging in case of early error
        try:
            # Verify the indices are valid
            if line_idx < 0 or line_idx >= len(self.current_solution_steps):
                logging.error(f"[reveal_char] Invalid line_idx {line_idx}, max is {len(self.current_solution_steps)-1}. current_solution_steps: {self.current_solution_steps}")
                return
                
            current_line = self.current_solution_steps[line_idx]
            if char_idx < 0 or char_idx >= len(current_line):
                logging.error(f"[reveal_char] Invalid char_idx {char_idx} for line {line_idx} ('{current_line}'), max is {len(current_line)-1}.")
                return
            
            char_to_reveal_for_log = current_line[char_idx]
            logging.info(f"[reveal_char] Attempting to reveal char '{char_to_reveal_for_log}' (ord: {ord(char_to_reveal_for_log) if len(char_to_reveal_for_log)==1 else 'N/A'}) at ({line_idx}, {char_idx}).")

            # Check if already revealed
            if (line_idx, char_idx) in self.visible_chars:
                logging.info(f"[reveal_char] Character '{char_to_reveal_for_log}' at ({line_idx}, {char_idx}) is ALREADY in self.visible_chars. Skipping reveal.")
                return
                
            # Add to visible chars
            self.visible_chars.append((line_idx, char_idx))
            
            # Update display
            char_tag = f"sol_{line_idx}_{char_idx}"
            target_color = "#000000" # Black
            logging.info(f"[reveal_char] Preparing to update canvas item with tag '{char_tag}' to color '{target_color}' for char '{char_to_reveal_for_log}'.")
            try:
                self.solution_canvas.itemconfig(char_tag, fill=target_color)
                logging.info(f"[reveal_char] Successfully itemconfig-ed tag '{char_tag}' to '{target_color}'. Now flashing green.")
                self.flash_char_green(char_tag)
                
                # Check for step completion to trigger lock animation
                step_is_now_complete = all((line_idx, c_idx) in self.visible_chars for c_idx in range(len(current_line)))
                
                if step_is_now_complete and line_idx not in self.completed_line_indices_for_problem:
                    self.completed_line_indices_for_problem.add(line_idx)
                    num_distinct_completed_steps = len(self.completed_line_indices_for_problem)
                    
                    if self.lock_animation and self.lock_animation.unlocked_parts < self.lock_animation.total_parts:
                        # We check num_distinct_completed_steps against unlocked_parts + 1 
                        # because unlock_next_part will increment unlocked_parts. Or simply check
                        # if the current count of distinct completed steps is high enough to warrant a new unlock.
                        # Effectively, each new distinct completed step should try to unlock one part.
                        self.lock_animation.unlock_next_part()
                        logging.info(f"[LockAnimation] Unlocked part. Total distinct steps completed: {num_distinct_completed_steps}. Lock parts now visually unlocked: {self.lock_animation.unlocked_parts}")

                # Debug output
                if self.debug_mode:
                    logging.info(f"[reveal_char] Successfully revealed character '{char_to_reveal_for_log}' (tag: {char_tag}) at position ({line_idx}, {char_idx}).")
                    
                    # Show current completion state after revealing
                    total_chars_in_line = len(self.current_solution_steps[line_idx])
                    visible_chars_in_line = sum(1 for i in range(total_chars_in_line) if (line_idx, i) in self.visible_chars)
                    logging.info(f"[reveal_char] Step {line_idx} is now {visible_chars_in_line}/{total_chars_in_line} complete ({visible_chars_in_line/total_chars_in_line*100:.1f}%). Visible chars overall: {len(self.visible_chars)}")
                    
                    # Check if the step is complete
                    if visible_chars_in_line == total_chars_in_line:
                        logging.info(f"[reveal_char] Step {line_idx} ('{self.current_solution_steps[line_idx]}') is now COMPLETE!")
                        # Check if there are more steps
                        if line_idx < len(self.current_solution_steps) - 1:
                            logging.info(f"[reveal_char] Next step will be {line_idx + 1}: '{self.current_solution_steps[line_idx+1] if (line_idx+1) < len(self.current_solution_steps) else 'N/A'}'")
                
            except tk.TclError as e:
                logging.warning(f"[reveal_char] TclError during itemconfig/flash for char '{char_to_reveal_for_log}' tag '{char_tag}' ({line_idx}, {char_idx}): {e}")
                # Attempt to remove from visible_chars if update failed critically, to allow retry?
                # For now, just log. If it fails to update, it will appear not revealed but be in visible_chars.
                
        except Exception as e:
            logging.error(f"[reveal_char] Critical error in reveal_char for ({line_idx}, {char_idx}): {e}")
            import traceback
            logging.error(traceback.format_exc())

    def flash_char_green(self, tag):
        """Makes a character flash bright green when correctly revealed"""
        if not self.winfo_exists(): return
        try:
            original_color = "#000000"  # Black (normal visible color)
            flash_color = "#00FF00"     # Bright green as per blueprint
            logging.info(f"[flash_char_green] Flashing tag '{tag}'. Current color will be set to '{flash_color}'. Will revert to '{original_color}'.")

            # Cancel previous flash for this tag if any
            if tag in self.flash_ids:
                self.after_cancel(self.flash_ids[tag])
                logging.info(f"[flash_char_green] Cancelled existing flash timer for tag '{tag}'.")

            # Change to bright green
            self.solution_canvas.itemconfig(tag, fill=flash_color)
            logging.info(f"[flash_char_green] Set tag '{tag}' to '{flash_color}'.")

            # Schedule return to original color
            flash_duration = 150 # milliseconds
            self.flash_ids[tag] = self.after(flash_duration, lambda: self.reset_char_color(tag, original_color))
        except tk.TclError as e:
            logging.warning(f"[flash_char_green] TclError for tag '{tag}': {e}. Window likely closed.")

    def reset_char_color(self, tag, color):
        """Resets character color after flashing"""
        if not self.winfo_exists(): return
        try:
            logging.info(f"[reset_char_color] Resetting tag '{tag}' to color '{color}'.")
            self.solution_canvas.itemconfig(tag, fill=color)
            logging.info(f"[reset_char_color] Successfully set tag '{tag}' to '{color}'.")
            if tag in self.flash_ids:
                del self.flash_ids[tag] # Clean up flash ID
        except tk.TclError as e:
             logging.warning(f"[reset_char_color] TclError for tag '{tag}' (color: {color}): {e}. Item might have been deleted or window closed.")
             if tag in self.flash_ids: del self.flash_ids[tag]
             pass

    def draw_crack_effect(self):
        """Draws a root-like crack with fractal branching patterns"""
        if not self.winfo_exists(): return None

        # Only allow cracks on the symbol_canvas (Window C)
        target_canvas = self.symbol_canvas

        canvas_width = target_canvas.winfo_width()
        canvas_height = target_canvas.winfo_height()

        if canvas_width <= 1 or canvas_height <= 1: return None

        # Generate random crack length with increased variability
        minus_count = random.randint(11, 61)
        crack_length = minus_count * 8

        def create_fractal_branch(start_x, start_y, length, angle, depth, width):
            """Recursively creates root-like branching patterns"""
            if length < 10 or depth > 4: return []  # Stop if too small or too deep
            
            # Calculate end point
            end_x = start_x + length * math.cos(angle)
            end_y = start_y + length * math.sin(angle)
            
            try:
                # Create main branch with randomly chosen color (blue or black)
                crack_color = "#000000" if random.random() < 0.5 else "#B0C4DE"
                branch_id = target_canvas.create_line(
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
                    'canvas': 'solution' if target_canvas == self.solution_canvas else 'symbol'
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
            
            return all_branches
            
        except Exception as e:
            logging.error(f"Error drawing crack effect: {e}")
            return None

    def redraw_saved_cracks(self):
        """Redraws all saved cracks after resize or other canvas changes"""
        if not self.game_over:
            return
        if not hasattr(self, 'saved_cracks') or not self.saved_cracks or not self.winfo_exists():
            return
            
        try:
            # Delete all existing cracks from symbol_canvas only
            self.symbol_canvas.delete("crack")
            
            # Redraw each saved crack
            for crack_group in self.saved_cracks:
                if isinstance(crack_group, list):
                    for crack in crack_group:
                        try:
                            # Always redraw cracks only on symbol_canvas
                            crack['id'] = self.symbol_canvas.create_line(
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

    def draw_shatter_effect(self):
        """Creates multiple cracks for game over effect"""
        if not self.winfo_exists(): return
        # Create multiple cracks with lengths measured by minus count
        for _ in range(15):
            crack_info = self.draw_crack_effect()
            if crack_info and hasattr(self, 'saved_cracks'):
                self.saved_cracks.append(crack_info)
        logging.info("Shatter effect displayed with proper crack visuals.")

    def trigger_game_over(self):
        """Handle game over state"""
        if self.game_over:
            return
            
        self.game_over = True
        logging.info("Game Over! Too many incorrect clicks.")
        
        # Clear save when game over happens
        self.clear_saved_game()
        
        # Stop falling symbols
        if hasattr(self, 'animation_after_id'):
            self.after_cancel(self.animation_after_id)
        
        # Draw shatter effect
        self.draw_shatter_effect()
        
        # Show all remaining characters in red
        self.after(1000, self.reveal_all_remaining_red)
        
        # Show game over popup
        self.after(2000, self.show_level_failed_popup)

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
        self.visible_chars = [] # Clear visible list as game is over

    def show_level_failed_popup(self):
        """Displays the 'Level Failed' pop-up window"""
        if not self.winfo_exists(): return # Don't show if main window closed

        popup = tk.Toplevel(self)
        popup.title("Level Failed")
        popup.geometry("300x150")
        popup.configure(bg="#220000") # Dark red background
        popup.resizable(False, False)

        # Center the popup
        x = self.winfo_x() + (self.winfo_width() // 2) - 150
        y = self.winfo_y() + (self.winfo_height() // 2) - 75
        popup.geometry(f"+{x}+{y}")

        # Make popup modal (grab focus)
        popup.grab_set()
        popup.focus_set()
        popup.transient(self) # Associate with main game window

        label = tk.Label(popup, text="Try Again?", font=("Courier New", 18, "bold"), fg="#FF4444", bg="#220000")
        label.pack(pady=20)

        button_frame = tk.Frame(popup, bg="#220000")
        button_frame.pack(pady=10)

        retry_button = tk.Button(
            button_frame, text="Retry", width=10,
            command=lambda: self.handle_popup_choice(popup, "retry"),
            bg="#550000", fg="#FFAAAA", font=("Courier New", 12)
        )
        retry_button.grid(row=0, column=0, padx=10)

        level_select_button = tk.Button(
            button_frame, text="Level Select", width=12,
            command=lambda: self.handle_popup_choice(popup, "level_select"),
             bg="#550000", fg="#FFAAAA", font=("Courier New", 12)
        )
        level_select_button.grid(row=0, column=1, padx=10)

        # Wait for the popup to be closed
        self.wait_window(popup)

    def handle_popup_choice(self, popup, choice):
        """Handles the button clicks in the level failed popup"""
        popup.destroy() # Close the popup
        logging.info(f"Popup choice selected: {choice}")
        
        if choice == "retry":
            # Clear game state and load new problem
            self.clear_saved_game()
            self.clear_all_cracks()
            self.load_new_problem()
            self.game_over = False
            # Reset game state
            self.visible_chars = []
            self.incorrect_clicks = 0
            self.falling_symbols_on_screen = []
            # Restart animation
            self.animate_falling_symbols()
        elif choice == "level_select":
            # Return to level select screen
            self.parent.deiconify()  # Show the parent (level select) window
            self.destroy()  # Close the gameplay window
        elif choice == "next":
            # Clear current game state
            self.clear_saved_game()
            self.clear_all_cracks()
            # Load new problem
            self.load_new_problem()
            self.game_over = False
            # Reset game state
            self.visible_chars = []
            self.incorrect_clicks = 0
            self.falling_symbols_on_screen = []
            # Restart animation
            self.animate_falling_symbols()
            logging.info("Starting next problem")

    def check_level_complete(self):
        """Check if all characters in all solution steps are complete."""
        if self.game_over:
            return False # Already decided

        if not self.current_solution_steps or not any(self.current_solution_steps):
            logging.info("check_level_complete: No solution steps available.")
            return False # Cannot be complete if there are no steps

        for i, line in enumerate(self.current_solution_steps):
            if not line: # Skip if a step/line is empty for some reason
                if self.debug_mode:
                    logging.info(f"check_level_complete: Step {i} is empty, skipping.")
                continue
            for j, char_in_step in enumerate(line):
                # Every character, including spaces, must be in visible_chars
                if (i, j) not in self.visible_chars:
                    if self.debug_mode:
                        logging.info(f"check_level_complete: Level not complete. Char ({i},{j}) '''{char_in_step}''' is not visible.")
                    return False # Found an unrevealed character
        
        # If we went through all characters in all steps and all are visible
        logging.info("check_level_complete: All solution steps completed! Level complete.")
        self.game_over = True # Set game_over here to prevent repeated popups
        self.clear_saved_game()
        
        # Stop animation before showing popup
        if hasattr(self, 'animation_after_id') and self.animation_after_id:
            self.after_cancel(self.animation_after_id)
            self.animation_after_id = None
            logging.info("check_level_complete: Cancelled animation for level complete.")

        self.after(500, self.show_level_complete_popup)
        return True

    def level_complete(self):
        """Handle level completion"""
        if self.game_over:
            return
            
        self.game_over = True
        logging.info("Level completed successfully!")
        
        # Clear save when level is complete
        self.clear_saved_game()
        
        # Show level complete popup after a brief delay
        self.after(500, self.show_level_complete_popup)

    def show_level_complete_popup(self):
         """Displays the 'Level Complete' pop-up window"""
         if not self.winfo_exists(): return

         popup = tk.Toplevel(self)
         popup.title("Success!")
         popup.geometry("300x150")
         popup.configure(bg="#002200") # Dark green background
         popup.resizable(False, False)

         # Center the popup
         x = self.winfo_x() + (self.winfo_width() // 2) - 150
         y = self.winfo_y() + (self.winfo_height() // 2) - 75
         popup.geometry(f"+{x}+{y}")

         # Make popup modal
         popup.grab_set()
         popup.focus_set()
         popup.transient(self)

         label = tk.Label(popup, text="Level Complete!", font=("Courier New", 18, "bold"), fg="#44FF44", bg="#002200")
         label.pack(pady=20)

         button_frame = tk.Frame(popup, bg="#002200")
         button_frame.pack(pady=10)

         next_button = tk.Button(
             button_frame, text="Next Problem", width=15,
             command=lambda: self.handle_popup_choice(popup, "next"),
             bg="#005500", fg="#AAFFAA", font=("Courier New", 12)
         )
         next_button.grid(row=0, column=0, padx=10)

         level_select_button = tk.Button(
             button_frame, text="Level Select", width=12,
             command=lambda: self.handle_popup_choice(popup, "level_select"),
              bg="#005500", fg="#AAFFAA", font=("Courier New", 12)
         )
         level_select_button.grid(row=0, column=1, padx=10)

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
        self.clear_all_cracks()
        self.draw_shatter_effect()

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
            self.visible_chars = [(int(x), int(y)) for x, y in state['visible_chars']]
            self.incorrect_clicks = int(state['incorrect_clicks'])
            self.saved_cracks = []  # Reset cracks as they'll be regenerated if needed
            
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
        if hasattr(self, 'solution_canvas'):
            self.solution_canvas.delete("crack")
        if hasattr(self, 'symbol_canvas'):
            self.symbol_canvas.delete("crack")
        self.saved_cracks = []

    def destroy(self):
        """Override destroy to ensure cracks are cleared and timers are cancelled on close"""
        logging.info("GameplayScreen destroy called. Cleaning up...")
        # Cancel falling symbols animation timer
        if hasattr(self, 'animation_after_id') and self.animation_after_id:
            self.after_cancel(self.animation_after_id)
            self.animation_after_id = None
            logging.info("Cancelled animation_after_id.")

        # Cancel auto-save timer
        if hasattr(self, 'auto_save_after_id') and self.auto_save_after_id:
            self.after_cancel(self.auto_save_after_id)
            self.auto_save_after_id = None
            logging.info("Cancelled auto_save_after_id.")

        # Cancel any pending character flash timers
        if hasattr(self, 'flash_ids') and self.flash_ids:
            for tag_id in list(self.flash_ids.keys()): # Iterate over a copy of keys
                if self.flash_ids[tag_id]:
                    self.after_cancel(self.flash_ids[tag_id])
                    logging.info(f"Cancelled flash_id for tag: {tag_id}")
            self.flash_ids = {}

        # Clear cracks from canvases
        self.clear_all_cracks()
        logging.info("Cleared all cracks.")
        
        # Clear lock animation visuals if they exist
        if self.lock_animation:
            self.lock_animation.clear_visuals()
            self.lock_animation = None # Dereference

        super().destroy() # Call parent's destroy method
        logging.info("GameplayScreen super().destroy() completed.")

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
        """Calculate the exact coordinates for a character in the solution canvas"""
        canvas_width = self.solution_canvas.winfo_width()
        canvas_height = self.solution_canvas.winfo_height()
        
        # Use same calculations as in draw_solution_lines
        offset = canvas_height / 3
        available_height = canvas_height * 2 / 3
        num_lines = 8 # Matches draw_solution_lines
        line_height = available_height / (num_lines + 1) # Matches draw_solution_lines
        char_width = 30 # Reduced character width, matches draw_solution_lines
        
        # Calculate position
        y_pos = offset + line_height * (line_idx + 1)
        
        # Ensure line_idx is within bounds before accessing current_solution_steps
        if line_idx < 0 or line_idx >= len(self.current_solution_steps):
            logging.error(f"get_solution_char_coords: line_idx {line_idx} out of bounds for current_solution_steps (len {len(self.current_solution_steps)})")
            # Return a default coordinate or handle error appropriately
            return (canvas_width / 2, canvas_height / 2) # Fallback to canvas center

        line_text = self.current_solution_steps[line_idx]
        
        # Ensure char_idx is within bounds for the line_text
        if char_idx < 0 or char_idx >= len(line_text):
            logging.error(f"get_solution_char_coords: char_idx {char_idx} out of bounds for line_text (len {len(line_text)}) at line_idx {line_idx}")
            return (canvas_width / 2, canvas_height / 2) # Fallback

        total_text_width = len(line_text) * char_width
        x_start = (canvas_width - total_text_width) / 2
        
        # Calculate the left edge of the character
        char_left_x = x_start + char_idx * char_width
        
        # Target coordinates should be the center of the character cell
        x_target_center = char_left_x + (char_width / 2)
        y_target_center = y_pos # y_pos is already the vertical center for anchor='w' used in drawing

        return (x_target_center, y_target_center)

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
