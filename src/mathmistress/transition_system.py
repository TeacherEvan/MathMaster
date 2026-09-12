"""Extracted transition/reset subsystem from GameplayScreen.

Cluster of 9 methods (~257 lines) covering animation disable/enable,
worm reset, timer tracking, teleport, and level transition completion.
Extracted 2026-09-13 surgical-implementation pass (plan OBJ-004).
All functions take ``self`` as first argument.
"""

import logging
import traceback


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
        
        # Then recreate the worm animation system (CRITICAL FIX)
        (800, lambda: self._init_worm_animation()),
        
        # Add the stoic quote watermark after solution display is ready (improved timing)
        (1200, lambda: self.add_stoic_quote_watermark()),
        
        # Start falling symbols animation in window C
        (1600, lambda: self.falling_symbols.start_animation() if hasattr(self, 'falling_symbols') and self.falling_symbols else None),
        
        # Update worm symbols after everything is ready (CRITICAL FIX)
        (2000, lambda: self._update_worm_solution_symbols(initial_call=True) if hasattr(self, 'worm_animation') and self.worm_animation else None),
        
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
    """Reset worm system for level transition without completely destroying it"""
    logging.info("Resetting worm system for level transition")
    
    if hasattr(self, 'worm_animation') and self.worm_animation:
        try:
            # Stop animation and clear worms, but keep the system intact
            self.worm_animation.stop_animation()
            self.worm_animation.clear_worms()
            
            # Reset interaction states but keep the animation object
            self.worm_animation.interaction_enabled = False
            self.worm_animation.solution_symbols = []
            
            # Clear any transport timers
            if hasattr(self.worm_animation, 'transport_timer') and self.worm_animation.transport_timer:
                try:
                    self.worm_animation.canvas.after_cancel(self.worm_animation.transport_timer)
                except Exception as e:
                    logging.warning(f"Error cancelling worm transport timer: {e}")
                self.worm_animation.transport_timer = None
                
            logging.info("Worm animation system reset successfully")
            
        except Exception as e:
            logging.error(f"Error resetting worm animation: {e}")
            # If there's an error, mark for recreation
            self.worm_animation = None
    else:
        logging.info("No worm animation to reset")

    # Reset worm-related game state
    self.currently_targeted_by_worm = None
    self.solution_symbols_data_for_worms = []
    self.transported_by_worm_symbols = []
    
    # Reset worm update retries counter
    self._worm_update_retries = 0

def _reset_help_display(self):
    """Reset help display to avoid index errors after transition"""
    try:
        if hasattr(self, 'help_display') and self.help_display:
            self.help_display.current_help_text = DEFAULT_HELP_TEXT  # from constants
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
