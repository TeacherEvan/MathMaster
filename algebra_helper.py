import logging
import re

class AlgebraHelper:
    """Provides contextual algebra help based on the current step and symbols."""
    
    def __init__(self):
        self.help_texts = {
            # Basic operations
            'addition': "Addition Rule: Add the same value to both sides of the equation to keep it balanced.",
            'subtraction': "Subtraction Rule: Subtract the same value from both sides of the equation to keep it balanced.",
            'multiplication': "Multiplication Rule: Multiply both sides of the equation by the same value to keep it balanced.",
            'division': "Division Rule: Divide both sides of the equation by the same value to keep it balanced.",
            
            # Moving terms
            'move_term': "Move Term: To move a term to the other side of the equation, change its sign (+ to -, or - to +).",
            'combine_like_terms': "Combine Like Terms: Add or subtract coefficients of terms with the same variable.",
            
            # Common problem types
            'isolate_x': "Isolate the Variable: Rearrange the equation to get the variable (x) by itself on one side.",
            'solve_for_x': "Solve for x: Move all non-x terms to the right side and combine like terms.",
            'verify_solution': "Verify Solution: Substitute your answer back into the original equation to check.",
            
            # Step transitions
            'step_progression': "Step Progression: Break down the solution process into smaller steps.",
            'final_step': "Final Step: The solution shows the value of the variable.",
            
            # Default
            'default': "Algebra Help: Find the value of x by following the solution steps."
        }
    
    def get_help_for_steps(self, current_step_index, total_steps, step_text, next_required_chars=None):
        """Return contextual help based on the current solution step.
        
        Args:
            current_step_index: The index of the current step (0-based)
            total_steps: Total number of steps in the solution
            step_text: The text of the current step
            next_required_chars: Optional list of the next required characters
            
        Returns:
            A help text string appropriate for the current context
        """
        try:
            # If we're at the beginning (first step)
            if current_step_index == 0:
                if 'x =' in step_text:
                    return self._format_help(self.help_texts['solve_for_x'])
                else:
                    # Analyze the first step to determine the type of equation
                    return self._analyze_equation(step_text)
            
            # If we're at the end (last step) 
            elif current_step_index == total_steps - 1:
                return self._format_help(self.help_texts['final_step'])
            
            # For middle steps, analyze the transition
            else:
                prev_step = current_step_index - 1
                return self._analyze_transition(step_text, prev_step)
                
        except Exception as e:
            logging.error(f"Error generating algebra help: {e}")
            return self._format_help(self.help_texts['default'])
    
    def _analyze_equation(self, equation_text):
        """Analyze the equation to provide specific help."""
        equation_text = equation_text.lower()
        
        if '+' in equation_text and '-' in equation_text:
            return self._format_help(self.help_texts['combine_like_terms'])
        elif '+' in equation_text:
            return self._format_help(self.help_texts['addition'])
        elif '-' in equation_text:
            return self._format_help(self.help_texts['subtraction'])
        elif '*' in equation_text or '×' in equation_text:
            return self._format_help(self.help_texts['multiplication'])
        elif '/' in equation_text or '÷' in equation_text:
            return self._format_help(self.help_texts['division'])
        else:
            # Look for common patterns
            if re.search(r'x\s*[=]\s*\d+', equation_text):
                return self._format_help(self.help_texts['final_step'])
            elif 'x' in equation_text:
                return self._format_help(self.help_texts['isolate_x'])
            
        return self._format_help(self.help_texts['default'])
    
    def _analyze_transition(self, current_text, prev_step_index):
        """Analyze the transition between steps to provide context-specific help."""
        current_text = current_text.lower()
        
        # Check for specific transitions
        if '=' in current_text:
            if current_text.count('=') == 1:
                sides = current_text.split('=')
                if 'x' in sides[0] and len(sides[0].strip()) <= 5:
                    # If x is almost isolated
                    return self._format_help(self.help_texts['isolate_x'])
        
        # Check for operations
        if '+' in current_text:
            return self._format_help(self.help_texts['addition'])
        elif '-' in current_text:
            if re.search(r'x\s*[-]', current_text) or re.search(r'[-]\s*x', current_text):
                return self._format_help(self.help_texts['move_term'])
            else:
                return self._format_help(self.help_texts['subtraction'])
        
        # Default for middle steps
        return self._format_help(self.help_texts['step_progression'])
    
    def _format_help(self, help_text):
        """Format the help text for display."""
        return help_text
        
    def get_help_for_symbols(self, symbols):
        """Generate help text based on specific symbols involved.
        
        Args:
            symbols: List of symbols or characters involved
            
        Returns:
            Help text relevant to the symbols
        """
        if not symbols:
            return self._format_help(self.help_texts['default'])
            
        # Check for specific symbols and provide targeted help
        if '+' in symbols:
            return self._format_help(self.help_texts['addition'])
        elif '-' in symbols:
            return self._format_help(self.help_texts['subtraction'])
        elif '*' in symbols or '×' in symbols:
            return self._format_help(self.help_texts['multiplication'])
        elif '/' in symbols or '÷' in symbols:
            return self._format_help(self.help_texts['division'])
        elif '=' in symbols:
            return self._format_help(self.help_texts['isolate_x'])
            
        return self._format_help(self.help_texts['default'])

# For testing
if __name__ == "__main__":
    helper = AlgebraHelper()
    print(helper.get_help_for_steps(0, 5, "x + 4 = 10"))
    print(helper.get_help_for_steps(1, 5, "x = 10 - 4"))
    print(helper.get_help_for_steps(4, 5, "x = 6"))
    print(helper.get_help_for_symbols(['+', '=', 'x'])) 