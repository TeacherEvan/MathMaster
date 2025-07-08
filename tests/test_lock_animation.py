#!/usr/bin/env python3
"""
Test script for the improved lock animation
This script creates a simple window to test the lock animation functionality
"""

import tkinter as tk
import logging
import time

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

try:
    from lock_animation_improved import LockAnimation
    print("✓ Successfully imported improved lock animation")
except ImportError as e:
    print(f"✗ Failed to import improved lock animation: {e}")
    try:
        from lock_animation import LockAnimation
        print("✓ Fallback to original lock animation")
    except ImportError as e2:
        print(f"✗ Failed to import original lock animation: {e2}")
        exit(1)

class LockAnimationTest:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Lock Animation Test")
        self.root.geometry("800x600")
        self.root.configure(bg="#1e1e1e")
        
        # Create main frame
        self.main_frame = tk.Frame(self.root, bg="#1e1e1e")
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Create canvas for lock animation
        self.canvas = tk.Canvas(
            self.main_frame, 
            bg="#111111", 
            highlightthickness=0,
            width=400,
            height=400
        )
        self.canvas.pack(side=tk.LEFT, padx=(0, 20))
        
        # Create control panel
        self.control_frame = tk.Frame(self.main_frame, bg="#1e1e1e")
        self.control_frame.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Title
        title_label = tk.Label(
            self.control_frame,
            text="Lock Animation Test",
            font=("Arial", 16, "bold"),
            fg="#00FF00",
            bg="#1e1e1e"
        )
        title_label.pack(pady=(0, 20))
        
        # Level selection
        level_frame = tk.Frame(self.control_frame, bg="#1e1e1e")
        level_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(level_frame, text="Level:", fg="#FFFFFF", bg="#1e1e1e").pack(anchor=tk.W)
        
        self.level_var = tk.StringVar(value="Easy")
        for level in ["Easy", "Medium", "Division"]:
            rb = tk.Radiobutton(
                level_frame,
                text=level,
                variable=self.level_var,
                value=level,
                fg="#FFFFFF",
                bg="#1e1e1e",
                selectcolor="#333333",
                command=self.change_level
            )
            rb.pack(anchor=tk.W)
        
        # Control buttons
        button_frame = tk.Frame(self.control_frame, bg="#1e1e1e")
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        # Unlock buttons
        for i in range(4):
            btn = tk.Button(
                button_frame,
                text=f"Unlock Part {i+1}",
                command=lambda idx=i: self.unlock_part(idx),
                bg="#333333",
                fg="#FFFFFF",
                font=("Arial", 10),
                relief=tk.FLAT,
                padx=10,
                pady=5
            )
            btn.pack(fill=tk.X, pady=2)
        
        # Special action buttons
        tk.Button(
            button_frame,
            text="Celebrate Problem Solved",
            command=self.celebrate_solved,
            bg="#006600",
            fg="#FFFFFF",
            font=("Arial", 10, "bold"),
            relief=tk.FLAT,
            padx=10,
            pady=5
        ).pack(fill=tk.X, pady=(10, 2))
        
        tk.Button(
            button_frame,
            text="React to Character (X)",
            command=lambda: self.react_character("X"),
            bg="#666600",
            fg="#FFFFFF",
            font=("Arial", 10),
            relief=tk.FLAT,
            padx=10,
            pady=5
        ).pack(fill=tk.X, pady=2)
        
        tk.Button(
            button_frame,
            text="Shake Particles",
            command=self.shake_particles,
            bg="#660066",
            fg="#FFFFFF",
            font=("Arial", 10),
            relief=tk.FLAT,
            padx=10,
            pady=5
        ).pack(fill=tk.X, pady=2)
        
        tk.Button(
            button_frame,
            text="Reset Lock",
            command=self.reset_lock,
            bg="#660000",
            fg="#FFFFFF",
            font=("Arial", 10),
            relief=tk.FLAT,
            padx=10,
            pady=5
        ).pack(fill=tk.X, pady=(10, 2))
        
        # Performance info
        self.perf_frame = tk.Frame(self.control_frame, bg="#1e1e1e")
        self.perf_frame.pack(fill=tk.X, pady=(20, 0))
        
        tk.Label(
            self.perf_frame,
            text="Performance Stats:",
            fg="#FFFFFF",
            bg="#1e1e1e",
            font=("Arial", 10, "bold")
        ).pack(anchor=tk.W)
        
        self.perf_label = tk.Label(
            self.perf_frame,
            text="Initializing...",
            fg="#CCCCCC",
            bg="#1e1e1e",
            font=("Arial", 8),
            justify=tk.LEFT
        )
        self.perf_label.pack(anchor=tk.W)
        
        # Initialize lock animation
        self.lock_animation = None
        self.init_lock_animation()
        
        # Start performance monitoring
        self.update_performance_stats()
        
        # Bind close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def init_lock_animation(self):
        """Initialize the lock animation"""
        try:
            # Calculate center position
            canvas_width = 400
            canvas_height = 400
            center_x = canvas_width // 2
            center_y = canvas_height // 2
            
            # Create lock animation
            self.lock_animation = LockAnimation(
                self.canvas,
                x=center_x,
                y=center_y,
                size=120,
                level_name=self.level_var.get()
            )
            
            print(f"✓ Lock animation initialized for level: {self.level_var.get()}")
            
        except Exception as e:
            print(f"✗ Error initializing lock animation: {e}")
            logging.error(f"Lock animation initialization error: {e}")
    
    def change_level(self):
        """Change the level theme"""
        if self.lock_animation:
            try:
                self.lock_animation.set_level_theme(self.level_var.get())
                print(f"✓ Changed level to: {self.level_var.get()}")
            except Exception as e:
                print(f"✗ Error changing level: {e}")
    
    def unlock_part(self, part_index):
        """Unlock a specific part"""
        if self.lock_animation:
            try:
                # Only unlock if this part hasn't been unlocked yet
                if part_index < self.lock_animation.unlocked_parts:
                    print(f"Part {part_index + 1} is already unlocked")
                    return
                
                # Unlock parts in sequence up to the requested part
                max_attempts = 10  # Prevent infinite loops
                attempts = 0
                while (self.lock_animation.unlocked_parts <= part_index and 
                       self.lock_animation.unlocked_parts < self.lock_animation.total_parts and 
                       attempts < max_attempts):
                    self.lock_animation.unlock_next_part()
                    print(f"✓ Unlocked part {self.lock_animation.unlocked_parts}")
                    attempts += 1
                    
                if attempts >= max_attempts:
                    print(f"⚠ Warning: Maximum unlock attempts reached for part {part_index + 1}")
                    
            except Exception as e:
                print(f"✗ Error unlocking part {part_index + 1}: {e}")
    
    def celebrate_solved(self):
        """Trigger problem solved celebration"""
        if self.lock_animation:
            try:
                self.lock_animation.celebrate_problem_solved()
                print("✓ Triggered problem solved celebration")
            except Exception as e:
                print(f"✗ Error triggering celebration: {e}")
    
    def react_character(self, character):
        """React to character reveal"""
        if self.lock_animation:
            try:
                self.lock_animation.react_to_character_reveal(character)
                print(f"✓ Reacted to character: {character}")
            except Exception as e:
                print(f"✗ Error reacting to character: {e}")
    
    def shake_particles(self):
        """Shake particles"""
        if self.lock_animation:
            try:
                self.lock_animation.shake_particles(intensity=2.0)
                print("✓ Shook particles")
            except Exception as e:
                print(f"✗ Error shaking particles: {e}")
    
    def reset_lock(self):
        """Reset the lock animation"""
        if self.lock_animation:
            try:
                self.lock_animation.reset()
                print("✓ Reset lock animation")
            except Exception as e:
                print(f"✗ Error resetting lock: {e}")
    
    def update_performance_stats(self):
        """Update performance statistics display"""
        if self.lock_animation:
            try:
                stats = self.lock_animation.get_performance_stats()
                
                perf_text = f"""Frame Count: {stats['frame_count']}
Avg Frame Time: {stats['avg_frame_time']:.3f}s
Particle Count: {stats['particle_count']}
Unlocked Parts: {self.lock_animation.unlocked_parts}/4
Fully Unlocked: {self.lock_animation.is_fully_unlocked}"""
                
                self.perf_label.config(text=perf_text)
                
            except Exception as e:
                self.perf_label.config(text=f"Error: {e}")
        
        # Schedule next update
        self.root.after(1000, self.update_performance_stats)
    
    def on_closing(self):
        """Handle window closing"""
        print("Closing test application...")
        if self.lock_animation:
            try:
                self.lock_animation.stop_all_persistent_animations()
                print("✓ Stopped all animations")
            except Exception as e:
                print(f"✗ Error stopping animations: {e}")
        
        self.root.destroy()
    
    def run(self):
        """Run the test application"""
        print("Starting lock animation test...")
        print("Use the controls on the right to test different features")
        self.root.mainloop()

def main():
    """Main function"""
    print("=" * 50)
    print("Lock Animation Test Application")
    print("=" * 50)
    
    try:
        test_app = LockAnimationTest()
        test_app.run()
    except Exception as e:
        print(f"✗ Fatal error: {e}")
        logging.error(f"Fatal error in test application: {e}")
    
    print("Test application finished.")

if __name__ == "__main__":
    main() 