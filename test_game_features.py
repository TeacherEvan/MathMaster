#!/usr/bin/env python3
"""
Test script to verify that game features (worms and quotes) work properly
after level transitions in MathMaster.

This script will run the game and automatically test level transitions
to ensure worms and quotes continue working.
"""

import sys
import os
import time
import logging

# Set up logging to see what's happening
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('test_game_features.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

def test_game_features():
    """Test the game features automatically"""
    try:
        # Import the game modules
        from welcome_screen import WelcomeScreen
        import tkinter as tk
        
        logging.info("Starting MathMaster feature test...")
        
        # Create and run the welcome screen
        root = WelcomeScreen()
        
        # Set up automatic testing
        def auto_test():
            try:
                logging.info("Auto-test starting in 3 seconds...")
                root.after(3000, lambda: check_features(root))
            except Exception as e:
                logging.error(f"Error in auto test setup: {e}")
        
        def check_features(welcome_window):
            """Check if features are working"""
            try:
                logging.info("Checking game features...")
                
                # Check if stoic quotes are working
                if hasattr(welcome_window, 'stoic_quote'):
                    logging.info(f"✓ Stoic quotes working: {welcome_window.stoic_quote[:50]}...")
                else:
                    logging.warning("✗ Stoic quotes not found")
                
                # Simulate clicking to go to level select
                logging.info("Simulating click to continue...")
                welcome_window.on_click(None)
                
                # Schedule level test after transition
                root.after(2000, lambda: test_level_features(welcome_window))
                
            except Exception as e:
                logging.error(f"Error checking features: {e}")
        
        def test_level_features(welcome_window):
            """Test features in the actual gameplay"""
            try:
                # Look for level select or gameplay windows
                for widget in welcome_window.winfo_children():
                    if hasattr(widget, 'current_level'):
                        logging.info("Found gameplay window - testing features...")
                        
                        # Check worm animation
                        if hasattr(widget, 'worm_animation'):
                            if widget.worm_animation:
                                logging.info("✓ Worm animation system exists")
                            else:
                                logging.warning("✗ Worm animation is None")
                        
                        # Check quotes
                        if hasattr(widget, 'stoic_quote'):
                            logging.info("✓ Stoic quotes available in gameplay")
                        
                        break
                        
                # Schedule shutdown
                root.after(5000, lambda: shutdown_test(welcome_window))
                
            except Exception as e:
                logging.error(f"Error testing level features: {e}")
        
        def shutdown_test(welcome_window):
            """Clean shutdown of test"""
            logging.info("Test completed. Shutting down...")
            try:
                welcome_window.destroy()
            except:
                pass
        
        # Start the auto test
        auto_test()
        
        # Run the main loop
        root.mainloop()
        
        logging.info("Feature test completed successfully")
        return True
        
    except Exception as e:
        logging.error(f"Error in feature test: {e}")
        import traceback
        logging.error(traceback.format_exc())
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("MathMaster Feature Test")
    print("=" * 50)
    print("This will test that worms and quotes work after level transitions")
    print("Check the log output for results...")
    print("=" * 50)
    
    success = test_game_features()
    
    if success:
        print("\n✓ Test completed - check 'test_game_features.log' for details")
    else:
        print("\n✗ Test failed - check 'test_game_features.log' for errors")