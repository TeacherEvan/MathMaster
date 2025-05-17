import re
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def fix_window_b_solution_symbols():
    """Improve the get_symbol_coordinates method in window_b_solution_symbols.py to prioritize actual positions."""
    file_path = 'window_b_solution_symbols.py'
    
    try:
        # Read file
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Look for get_symbol_coordinates method
        pattern = r'def get_symbol_coordinates\(self, line_idx, char_idx\):(.*?)def'
        match = re.search(pattern, content, re.DOTALL)
        
        if not match:
            logging.error(f"Could not find get_symbol_coordinates method in {file_path}")
            return False
        
        # Get the current method code
        current_method = match.group(1)
        
        # Check if the method already has the improved implementation
        if "Using actual position for symbol" in current_method:
            logging.info(f"Method get_symbol_coordinates in {file_path} already has improved implementation")
            return True
        
        # Create improved method implementation
        improved_method = '''
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
        '''
        
        # Replace the method while preserving the remaining code
        new_content = re.sub(pattern, f'def get_symbol_coordinates(self, line_idx, char_idx):{improved_method}def', content, flags=re.DOTALL)
        
        # Write changes back to the file
        with open(file_path, 'w') as f:
            f.write(new_content)
        
        logging.info(f"Successfully updated get_symbol_coordinates method in {file_path}")
        return True
    
    except Exception as e:
        logging.error(f"Error updating {file_path}: {e}")
        return False

def fix_gameplay_screen():
    """Fix level transition issues in gameplay_screen.py."""
    file_path = 'gameplay_screen.py'
    
    try:
        # Read file
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Fix 1: Ensure worm targets are cleared in handle_popup_choice
        # Look for the section where game state is reset
        pattern = r'(self\.visible_chars = set\(\))\s+(self\.incorrect_clicks = 0)'
        
        # Check if the fix is already applied
        if "self.currently_targeted_by_worm = None" in content and "self.transported_by_worm_symbols = []" in content:
            logging.info("gameplay_screen.py already has worm target cleanup fix")
        else:
            # Add worm target cleanup
            replacement = r'\1\n                self.currently_targeted_by_worm = None\n                self.transported_by_worm_symbols = []  # Clear tracked worm symbols\n                \2'
            content = re.sub(pattern, replacement, content)
            logging.info("Applied worm target cleanup fix to gameplay_screen.py")
        
        # Fix 2: Ensure worm animation is stopped and restarted properly
        pattern = r'if hasattr\(self, [\'"]falling_symbols[\'"]\) and self\.falling_symbols:(.*?)self\.falling_symbols\.stop_animation\(\)(.*?)self\.falling_symbols = None'
        
        # Check if the fix is already applied
        if "if hasattr(self, 'worm_animation') and self.worm_animation:" in content and "self.worm_animation.stop_animation()" in content:
            logging.info("gameplay_screen.py already has worm animation stop/restart fix")
        else:
            # Add worm animation stop and restart
            replacement = r'if hasattr(self, \'falling_symbols\') and self.falling_symbols:\1self.falling_symbols.stop_animation()\2self.falling_symbols = None\n\n                # Reset worm animation if it exists\n                if hasattr(self, \'worm_animation\') and self.worm_animation:\n                    self.worm_animation.stop_animation()'
            content = re.sub(pattern, replacement, content, flags=re.DOTALL)
            logging.info("Applied worm animation stop/restart fix to gameplay_screen.py")
        
        # Write changes back to the file
        with open(file_path, 'w') as f:
            f.write(content)
        
        logging.info(f"Successfully updated {file_path}")
        return True
    
    except Exception as e:
        logging.error(f"Error updating {file_path}: {e}")
        return False

def main():
    """Apply all fixes and print summary."""
    logging.info("Starting game fixes...")
    
    fix1 = fix_window_b_solution_symbols()
    fix2 = fix_gameplay_screen()
    
    if fix1 and fix2:
        logging.info("All fixes applied successfully! Please restart the game.")
    else:
        logging.warning("Some fixes could not be applied. Check the log for details.")

if __name__ == "__main__":
    main() 