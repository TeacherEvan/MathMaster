import re
import os
import logging
import time

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def fix_teleport_symbol_display():
    """Fix the issue with end_pos being None in _handle_correct_teleport"""
    file_path = 'Teleport_SymblDisplay_C_B.py'
    
    try:
        with open(file_path, 'r') as f:
            content = f.read()
            
        # Add check for end_pos being None
        if 'if end_pos is None:' not in content:
            pattern = r'(def _handle_correct_teleport.*?is_left_side: bool\) -> None:\s+""".*?"""\s+)(# Create destination portal)'
            replacement = r'\1# Check if end_pos is None\n        if end_pos is None:\n            logging.error(f"Cannot handle teleport: end_pos is None for symbol_id {symbol_id}")\n            return\n        \n        \2'
            
            content = re.sub(pattern, replacement, content, flags=re.DOTALL)
            logging.info("Added NULL check for end_pos in _handle_correct_teleport")
        else:
            logging.info("NULL check for end_pos already present")
            
        # Write changes back to the file
        with open(file_path, 'w') as f:
            f.write(content)
            
        logging.info(f"Successfully updated {file_path}")
        return True
        
    except Exception as e:
        logging.error(f"Error updating {file_path}: {e}")
        return False

def fix_solution_steps_attribute():
    """Fix the 'solution_steps' attribute error in get_solution_char_coords"""
    file_path = 'gameplay_screen.py'
    
    try:
        with open(file_path, 'r') as f:
            content = f.read()
            
        # Update the get_solution_char_coords method
        if 'solution_steps = getattr(self, \'solution_steps\', None)' not in content:
            pattern = r'(def get_solution_char_coords.*?try:\s+)(# Check if the indices are valid)'
            replacement = r'\1# Check for the correct attribute name (the attribute might be named differently)\n            solution_steps = getattr(self, \'solution_steps\', None)\n            if solution_steps is None:\n                solution_steps = getattr(self, \'current_solution_steps\', [])\n                \n            \2'
            
            content = re.sub(pattern, replacement, content, flags=re.DOTALL)
            
            # Update the references to self.solution_steps
            content = re.sub(
                r'if line_idx < 0 or line_idx >= len\(self\.solution_steps\):',
                r'if line_idx < 0 or line_idx >= len(solution_steps):',
                content
            )
            
            content = re.sub(
                r'line = self\.solution_steps\[line_idx\]',
                r'line = solution_steps[line_idx]',
                content
            )
            
            # Update line text access to handle different structures
            content = re.sub(
                r'if char_idx < 0 or char_idx >= len\(line\[\'text\'\]\):',
                r'# Handle different data structures (might be a string or a dict with \'text\')\n            line_text = line if isinstance(line, str) else line.get(\'text\', \'\')\n            \n            if char_idx < 0 or char_idx >= len(line_text):',
                content
            )
            
            logging.info("Updated get_solution_char_coords to handle solution_steps attribute")
        else:
            logging.info("get_solution_char_coords already updated")
            
        # Write changes back to the file
        with open(file_path, 'w') as f:
            f.write(content)
            
        logging.info(f"Successfully updated {file_path}")
        return True
        
    except Exception as e:
        logging.error(f"Error updating {file_path}: {e}")
        return False

def fix_level_attribute():
    """Fix the 'level' attribute error in level_complete"""
    file_path = 'gameplay_screen.py'
    
    try:
        with open(file_path, 'r') as f:
            content = f.read()
            
        # Update the level_complete method
        if 'current_level = getattr(self, \'level\', None)' not in content:
            # Add safe level access
            pattern = r'(def level_complete.*?self\.game_over = True\s+)(# Log level completion)'
            replacement = r'\1# Get the current level (handle potential attribute naming differences)\n        current_level = getattr(self, \'level\', None)\n        if current_level is None:\n            current_level = getattr(self, \'current_level\', \'unknown\')\n        \n        \2'
            
            content = re.sub(pattern, replacement, content, flags=re.DOTALL)
            
            # Update the level reference
            content = re.sub(
                r'logging\.info\(f"Level \{self\.level\} completed in \{elapsed_time:.2f\} seconds!"\)',
                r'logging.info(f"Level {current_level} completed in {elapsed_time:.2f} seconds!")',
                content
            )
            
            # Update stats_manager handling
            content = re.sub(
                r'if self\.stats_manager:',
                r'if hasattr(self, \'stats_manager\') and self.stats_manager:',
                content
            )
            
            content = re.sub(
                r'\'level\': self\.level,',
                r'\'level\': current_level,  # Use our safe current_level variable',
                content
            )
            
            content = re.sub(
                r'\'difficulty\': self\.difficulty,',
                r'\'difficulty\': getattr(self, \'difficulty\', \'unknown\'),',
                content
            )
            
            content = re.sub(
                r'\'problem\': self\.current_problem',
                r'\'problem\': getattr(self, \'current_problem\', \'\')',
                content
            )
            
            logging.info("Updated level_complete to handle level attribute safely")
        else:
            logging.info("level_complete already updated")
            
        # Write changes back to the file
        with open(file_path, 'w') as f:
            f.write(content)
            
        logging.info(f"Successfully updated {file_path}")
        return True
        
    except Exception as e:
        logging.error(f"Error updating {file_path}: {e}")
        return False

def add_log_entry_to_history():
    """Add a log entry to history.mdc about the fixes made"""
    try:
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"\n\n## {timestamp} - Teleport and Level Transition Fixes\n\n"
        log_entry += "Applied fixes to resolve several issues with level transitions and teleportation:\n\n"
        log_entry += "1. Fixed NoneType error in `_handle_correct_teleport` by adding null check for end_pos\n"
        log_entry += "2. Fixed missing `solution_steps` attribute in `get_solution_char_coords` by using getattr with fallback\n"
        log_entry += "3. Fixed missing `level` attribute in `level_complete` by safely accessing level information\n"
        log_entry += "4. Enhanced error resilience when accessing object attributes throughout the game\n\n"
        log_entry += "These changes should prevent crashes during level transitions and symbol teleportation."
        
        with open('history.mdc', 'a') as f:
            f.write(log_entry)
            
        logging.info("Added log entry to history.mdc")
        return True
    except Exception as e:
        logging.error(f"Error adding log entry to history.mdc: {e}")
        return False

if __name__ == "__main__":
    print("Applying fixes for teleport and level transition issues...")
    
    successes = []
    successes.append(fix_teleport_symbol_display())
    successes.append(fix_solution_steps_attribute())
    successes.append(fix_level_attribute())
    successes.append(add_log_entry_to_history())
    
    if all(successes):
        print("All fixes applied successfully! Please restart the game.")
    else:
        print("Some fixes could not be applied. Check the logs for details.") 