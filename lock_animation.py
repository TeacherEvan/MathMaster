import tkinter as tk
import random
import math

class LockAnimation:
    def __init__(self, canvas, x, y, size=100):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.size = size
        self.lock_body_item = None
        self.shackle_item = None
        self.lock_parts_items = [] # Stores canvas item IDs for the 4 segments
        self.unlocked_parts = 0
        self.total_parts = 4  # Number of visual parts in the lock
        
        # Create initial lock parts
        self._create_lock_visuals()
        
    def _create_lock_visuals(self):
        """Create the visual elements of the lock"""
        # Add a subtle glow behind the lock
        glow_padding = self.size // 8
        self.glow_item = self.canvas.create_oval(
            self.x - self.size // 2 - glow_padding, 
            self.y - self.size // 2 - glow_padding,
            self.x + self.size // 2 + glow_padding, 
            self.y + self.size // 2 + glow_padding,
            fill='#1a2533', outline='#1a2533', tags="lock_visual"
        )
        
        # Lock body - with gradient effect
        self.lock_body_item = self.canvas.create_rectangle(
            self.x - self.size // 2, self.y - self.size // 2,
            self.x + self.size // 2, self.y + self.size // 2,
            fill='#34495E', outline='#2C3E50', width=4, tags="lock_visual"
        )
        
        # Add metallic highlight to top of lock body
        highlight_height = self.size // 10
        self.highlight_item = self.canvas.create_rectangle(
            self.x - self.size // 2 + 5, self.y - self.size // 2 + 5,
            self.x + self.size // 2 - 5, self.y - self.size // 2 + highlight_height,
            fill='#4A6A8F', outline='', tags="lock_visual"
        )
        
        # Lock shackle (the U-shaped part)
        # Adjust shackle position to sit on top of the body
        shackle_y_start = self.y - self.size // 2 
        shackle_width = self.size // 2.5
        shackle_height = self.size // 2.5
        
        # Create a filled portion for the shackle for better look
        self.shackle_fill = self.canvas.create_arc(
            self.x - shackle_width, shackle_y_start - shackle_height,
            self.x + shackle_width, shackle_y_start + shackle_height // 3,
            start=0, extent=180, 
            fill='#3C526B', outline='', tags="lock_visual"
        )
        
        # Create the actual shackle with thick outline for 3D effect
        self.shackle_item = self.canvas.create_arc(
            self.x - shackle_width, shackle_y_start - shackle_height,
            self.x + shackle_width, shackle_y_start + shackle_height // 3,
            start=0, extent=180, style=tk.ARC,
            outline='#2C3E50', width=7, tags="lock_visual"
        )
        
        # Add keyhole for realism
        keyhole_radius = self.size // 12
        self.keyhole_top = self.canvas.create_oval(
            self.x - keyhole_radius, 
            self.y, 
            self.x + keyhole_radius, 
            self.y + keyhole_radius * 2,
            fill='#1C2833', outline='#17202A', width=2, tags="lock_visual"
        )
        
        self.keyhole_bottom = self.canvas.create_rectangle(
            self.x - keyhole_radius // 2,
            self.y + keyhole_radius * 2,
            self.x + keyhole_radius // 2,
            self.y + keyhole_radius * 3.5,
            fill='#1C2833', outline='#17202A', width=1, tags="lock_visual"
        )
        
        # Lock mechanism parts (4 segments inside the body)
        segment_height = self.size // self.total_parts
        segment_colors = ['#E74C3C', '#E57E31', '#D35400', '#C0392B']  # Different red/orange hues for visual interest
        segment_outline_colors = ['#C0392B', '#CD6133', '#BA4A00', '#922B21']  # Darker version of each color
        
        for i in range(self.total_parts):
            segment = self.canvas.create_rectangle(
                self.x - self.size // 3, self.y - self.size // 2 + i * segment_height + 5,
                self.x + self.size // 3, self.y - self.size // 2 + (i + 1) * segment_height - 5,
                fill=segment_colors[i], outline=segment_outline_colors[i], width=2, tags="lock_visual"
            )
            self.lock_parts_items.append(segment)
            
    def unlock_next_part(self):
        """Trigger animation for unlocking the next part"""
        if self.unlocked_parts < self.total_parts:
            current_part_item = self.lock_parts_items[self.unlocked_parts]
            
            # Change color to green with an attractive metallic shade
            unlock_colors = ['#27AE60', '#2ECC71', '#58D68D', '#82E0AA']  # Different green hues
            unlock_outline_colors = ['#219A52', '#1D8348', '#186A3B', '#145A32']  # Darker versions
            
            # Use different greens for different segments
            color_idx = self.unlocked_parts % len(unlock_colors)
            self.canvas.itemconfig(current_part_item, 
                                   fill=unlock_colors[color_idx], 
                                   outline=unlock_outline_colors[color_idx])
            
            # Add sparkle effect
            self._create_sparkle_effect(self.unlocked_parts)
            
            # If all parts are unlocked, show a special animation
            if self.unlocked_parts == self.total_parts - 1:
                self.after_unlocked = self.canvas.after(500, self._show_unlock_complete_animation)
            
            self.unlocked_parts += 1
            
    def _show_unlock_complete_animation(self):
        """Special animation when all parts are unlocked"""
        try:
            # Create a burst of sparkles from the whole lock
            for _ in range(20):
                angle = random.uniform(0, 2 * math.pi)
                distance = random.uniform(self.size/4, self.size/2)
                particle_size = random.uniform(2, 4)
                
                x = self.x + math.cos(angle) * distance
                y = self.y + math.sin(angle) * distance
                
                colors = ['#F1C40F', '#F39C12', '#FFEB3B', '#FFC107']  # Yellow/gold colors
                sparkle = self.canvas.create_oval(
                    x - particle_size, y - particle_size, 
                    x + particle_size, y + particle_size,
                    fill=random.choice(colors), outline='', tags="lock_visual"
                )
                
                # Fade out and delete after a delay
                self.canvas.after(random.randint(300, 800), lambda s=sparkle: self._delete_if_exists(s))
        except tk.TclError:
            pass  # Handle case where canvas might be gone
                
    def _delete_if_exists(self, item_id):
        """Safely delete an item if it still exists"""
        try:
            if self.canvas.winfo_exists():
                self.canvas.delete(item_id)
        except tk.TclError:
            pass
            
    def _create_sparkle_effect(self, part_index):
        """Create sparkle animation effect when part is unlocked"""
        sparkle_points = []
        # Calculate center of the specific unlocked segment
        segment_height = self.size // self.total_parts
        center_x = self.x
        center_y = self.y - self.size // 2 + (part_index + 0.5) * segment_height
        
        sparkle_colors = ['#F1C40F', '#F39C12', '#FFEB3B', '#FFC107', '#FFFFFF']  # Yellow/gold colors + white
        
        for _ in range(12):  # Increased number of sparkles
            angle = random.uniform(0, 2 * math.pi)
            # Sparkles should emanate from the segment's center
            distance = random.uniform(2, 10)  # Initial distance from center
            particle_size = random.uniform(1.5, 4)  # Increased size for visibility
            
            x = center_x + math.cos(angle) * distance
            y = center_y + math.sin(angle) * distance
            
            sparkle = self.canvas.create_oval(
                x - particle_size, y - particle_size, 
                x + particle_size, y + particle_size,
                fill=random.choice(sparkle_colors), outline='', tags="lock_visual"
            )
            sparkle_points.append({
                'id': sparkle,
                'dx': math.cos(angle) * random.uniform(1.5, 3),  # Faster movement
                'dy': math.sin(angle) * random.uniform(1.5, 3),
                'life': random.randint(20, 30),  # Longer lifespan
                'size': particle_size,
                'shrink_rate': particle_size / random.randint(20, 30)  # For smoother fade out
            })
            
        self._animate_sparkles(sparkle_points)
        
    def _animate_sparkles(self, sparkles):
        """Animate the sparkle particles with size reduction for fade effect"""
        active_sparkles = False
        for sparkle in sparkles[:]:  # Iterate over a copy for safe removal
            if sparkle['life'] <= 0 or sparkle['size'] <= 0:
                try:
                    self.canvas.delete(sparkle['id'])
                except tk.TclError:
                    pass  # Item might already be deleted if canvas is closing
                sparkles.remove(sparkle)
                continue
                
            try:
                # Move the sparkle
                self.canvas.move(sparkle['id'], sparkle['dx'], sparkle['dy'])
                
                # Shrink the sparkle for fade-out effect
                sparkle['size'] -= sparkle['shrink_rate']
                if sparkle['size'] > 0:
                    item_id = sparkle['id']
                    current_coords = self.canvas.coords(item_id)
                    if len(current_coords) == 4:  # Ensure we have valid coordinates
                        center_x = (current_coords[0] + current_coords[2]) / 2
                        center_y = (current_coords[1] + current_coords[3]) / 2
                        self.canvas.coords(
                            item_id,
                            center_x - sparkle['size'], center_y - sparkle['size'],
                            center_x + sparkle['size'], center_y + sparkle['size']
                        )
            except tk.TclError:
                pass  # Item might already be deleted
                
            sparkle['life'] -= 1
            active_sparkles = True
            
        if active_sparkles and self.canvas.winfo_exists():
            self.canvas.after(30, lambda: self._animate_sparkles(sparkles))
            
    def reset(self):
        """Reset the lock to its initial state (all parts red)"""
        self.unlocked_parts = 0
        
        # Reset all segments to locked state with varying colors
        segment_colors = ['#E74C3C', '#E57E31', '#D35400', '#C0392B']
        segment_outline_colors = ['#C0392B', '#CD6133', '#BA4A00', '#922B21']
        
        for i, part_item in enumerate(self.lock_parts_items):
            color_idx = i % len(segment_colors)
            try:
                self.canvas.itemconfig(
                    part_item, 
                    fill=segment_colors[color_idx], 
                    outline=segment_outline_colors[color_idx]
                )
            except tk.TclError:
                # Canvas or item might not exist if reset is called during cleanup
                pass
    
    def clear_visuals(self):
        """Deletes all visual elements of the lock from the canvas."""
        try:
            # More robust way using the common tag for all lock visuals
            self.canvas.delete("lock_visual")
            
            # Reset instance variables
            self.lock_body_item = None
            self.shackle_item = None
            self.lock_parts_items = []
            
        except tk.TclError:
            # Handle cases where canvas/items might already be gone
            pass 