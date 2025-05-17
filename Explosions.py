import tkinter as tk
import random
import math
import logging

class ExplosionManager:
    def __init__(self, canvas):
        self.canvas = canvas
        self.explosions = [] # List to hold active explosion animations

    def create_explosion(self, x, y, base_size=36, num_particles_range=(20, 30), duration_ms=600):
        """
        Creates a vibrant explosion effect at the given coordinates.
        Args:
            x (int): Center x-coordinate of the explosion.
            y (int): Center y-coordinate of the explosion.
            base_size (int): Approximate radius of the explosion, roughly 3x worm size (worm is ~12).
            num_particles_range (tuple): Min and max number of particles.
            duration_ms (int): Total duration of the explosion effect in milliseconds.
        """
        num_particles = random.randint(*num_particles_range)
        particles = []
        
        # Vibrant colors - can be expanded
        colors = ["#FF0000", "#FF4500", "#FFA500", "#FFD700", "#FFFF00", "#FF69B4", "#FF1493"]

        for _ in range(num_particles):
            angle = random.uniform(0, 2 * math.pi)
            # Particles spread outwards, with some initial speed variation
            speed = random.uniform(base_size * 0.05, base_size * 0.15) 
            start_radius_factor = random.uniform(0.1, 0.3) # Start slightly offset from center for a better "boom"

            particle = {
                'id': None,
                'cx': x, # Center of explosion
                'cy': y, # Center of explosion
                'angle': angle,
                'speed': speed,
                'current_radius': base_size * start_radius_factor, # Initial distance from center
                'x': x + math.cos(angle) * (base_size * start_radius_factor),
                'y': y + math.sin(angle) * (base_size * start_radius_factor),
                'size': random.uniform(base_size * 0.05, base_size * 0.15), # Particle size
                'color': random.choice(colors),
                'life_total': duration_ms,
                'life_remaining': duration_ms,
                'deceleration': 0.95 + random.uniform(-0.02, 0.02) # Slight variation in how quickly particles slow
            }
            particles.append(particle)
        
        explosion_data = {
            'center_x': x,
            'center_y': y,
            'particles': particles,
            'start_time': self.canvas.after(0, lambda: None), # Using time.time() might be better
            'duration_ms': duration_ms
        }
        self.explosions.append(explosion_data)
        
        # Start animation for this explosion if it's the first one, 
        # or rely on an existing global animation loop for explosions.
        # For simplicity, let's assume a manager-level animate call.
        if len(self.explosions) == 1: # If this is the first active explosion, start the animation loop
             self._animate_explosions()
        
        logging.info(f"Created explosion at ({x},{y}) with {num_particles} particles.")

    def _animate_explosions(self):
        if not self.canvas.winfo_exists():
            self.explosions.clear()
            return

        active_explosions_exist = False
        for explosion in list(self.explosions): # Iterate over a copy for safe removal
            particles_to_remove_from_explosion = []
            
            current_time_ms = self.canvas.after(0, lambda: None) 
            # elapsed_ms = current_time_ms - explosion['start_time'] # This doesn't work as expected with after(0)
            # A simple frame-based life decay is easier here

            if not explosion['particles']:
                self.explosions.remove(explosion)
                continue

            active_explosions_exist = True # Found at least one explosion with particles

            for p in explosion['particles']:
                p['life_remaining'] -= 30 # Approximate ms per frame (adjust as needed for FRAME_DELAY)

                if p['life_remaining'] <= 0:
                    if p['id']:
                        self.canvas.delete(p['id'])
                    particles_to_remove_from_explosion.append(p)
                    continue

                # Move particle outwards
                p['current_radius'] += p['speed']
                p['x'] = explosion['center_x'] + math.cos(p['angle']) * p['current_radius']
                p['y'] = explosion['center_y'] + math.sin(p['angle']) * p['current_radius']
                p['speed'] *= p['deceleration'] # Slow down
                p['speed'] = max(0, p['speed'] ) # Don't go negative

                # Update size (shrink over life)
                life_ratio = max(0, p['life_remaining'] / p['life_total'])
                current_size = p['size'] * life_ratio
                current_size = max(1, current_size) # Min particle size 1px

                # Create or update particle on canvas
                if p['id'] is None:
                    p['id'] = self.canvas.create_oval(
                        p['x'] - current_size, p['y'] - current_size,
                        p['x'] + current_size, p['y'] + current_size,
                        fill=p['color'], outline=""
                    )
                else:
                    try:
                        self.canvas.coords(
                            p['id'],
                            p['x'] - current_size, p['y'] - current_size,
                            p['x'] + current_size, p['y'] + current_size
                        )
                        # Optional: Could fade color too, but let's keep it simple for now
                    except tk.TclError: # Item might have been deleted
                        p['id'] = None # Mark as needing recreation if we had logic for that
                        particles_to_remove_from_explosion.append(p)


            # Remove dead particles from this specific explosion
            for dead_p in particles_to_remove_from_explosion:
                if dead_p in explosion['particles']:
                    explosion['particles'].remove(dead_p)
            
            # If an explosion has no more particles, remove it from the main list
            if not explosion['particles']:
                if explosion in self.explosions: # Check again, might have been removed if all died in one go
                    self.explosions.remove(explosion)

        if self.explosions: # If there are still active explosions
            self.canvas.after(30, self._animate_explosions) # Adjust frame rate (e.g., ~33 FPS)
        else:
            logging.info("All explosions finished.")

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    root = tk.Tk()
    root.title("Explosion Test")
    canvas_width = 600
    canvas_height = 400
    canvas = tk.Canvas(root, width=canvas_width, height=canvas_height, bg="black")
    canvas.pack()

    explosion_manager = ExplosionManager(canvas)

    def test_explosion(event):
        explosion_manager.create_explosion(event.x, event.y)

    canvas.bind("<Button-1>", test_explosion)
    
    # Example of multiple explosions
    explosion_manager.create_explosion(100, 100, base_size=40)
    root.after(500, lambda: explosion_manager.create_explosion(300, 200, base_size=25))
    root.after(1000, lambda: explosion_manager.create_explosion(500, 300, base_size=50))

    root.mainloop() 