import tkinter as tk
import random
import math
import time
import logging

class WormAnimation:
    def __init__(self, canvas, canvas_width=None, canvas_height=None):
        """Initialize the worm animation on the specified canvas.
        
        Args:
            canvas: The tkinter canvas where the worm will be drawn
            canvas_width: Optional initial width of the canvas
            canvas_height: Optional initial height of the canvas
        """
        self.canvas = canvas
        self.width = canvas_width or canvas.winfo_width()
        self.height = canvas_height or canvas.winfo_height()
        self.worms = []
        self.animation_running = False
        self.animation_speed = 1.0  # Base speed multiplier
        self.after_id = None
        self.worm_segments = 8  # Number of segments in the worm
        self.worm_size = 12  # Base size of each segment
        self.blink_timer = 0  # Timer for blinking
        self.mouth_state = 0  # 0 = closed, 1 = opening, 2 = open, 3 = closing
        self.mouth_timer = 0  # Timer for mouth animation
        
        # Added for solution symbol interactions
        self.solution_symbols = []  # List to store visible solution symbol coordinates and info
        self.interaction_enabled = False  # Flag to control when interaction is enabled
        self.interaction_cooldown = {}  # Cooldown for interactions per worm
        self.symbol_shake_ids = {}  # Track active symbol shake animations
        self.interaction_particles = []  # Particle effects for interactions
        
        # Bind to canvas resize events
        self.canvas.bind("<Configure>", self.on_canvas_resize)
        
        logging.info("WormAnimation initialized")

    def on_canvas_resize(self, event=None):
        """Handle canvas resize events"""
        self.width = self.canvas.winfo_width()
        self.height = self.canvas.winfo_height()
        logging.info(f"Canvas resized to {self.width}x{self.height}")
        
    def create_worm(self, num_worms=1):
        """Create the specified number of worms on the canvas"""
        if not self.width or self.width <= 1 or not self.height or self.height <= 1:
            # Canvas not properly sized yet, try to get dimensions
            self.width = self.canvas.winfo_width()
            self.height = self.canvas.winfo_height()
            if not self.width or self.width <= 1 or not self.height or self.height <= 1:
                # Still not proper dimensions, schedule to try again shortly
                self.canvas.after(100, lambda: self.create_worm(num_worms))
                return

        # Create the specified number of worms
        for _ in range(num_worms):
            # Create a new worm with random starting position and direction
            worm = {
                'x': random.randint(50, self.width - 50),
                'y': random.randint(50, self.height - 50),
                'angle': random.uniform(0, 2 * math.pi),
                'segments': [],
                'eyes': [],
                'mouth': None,
                'blink_state': False,
                'blink_timer': random.randint(50, 200),  # Random initial blink time
                'mouth_state': 0,  # 0 = closed, 1 = open
                'mouth_timer': random.randint(20, 100),  # Random initial mouth time
                'history': [(0, 0)] * self.worm_segments,  # Position history for segments
                'segment_size': self.worm_size + random.randint(-2, 2),  # Slight size variation
                'color': f"#{random.randint(60, 120):02x}{random.randint(140, 180):02x}{random.randint(60, 100):02x}",  # Earthy colors
                'last_interaction_time': 0,  # Track when last interacted with a symbol
                'target_symbol': None,  # Target symbol when in hunting mode
                'id': random.randint(1000, 9999)  # Unique ID for this worm
            }
            
            # Draw the initial worm
            self._draw_worm(worm)
            
            # Add to the list of worms
            self.worms.append(worm)
            
        logging.info(f"Created {num_worms} worms")
        
    def _draw_worm(self, worm):
        """Draw a single worm with all its components"""
        if not self.canvas.winfo_exists():
            return
            
        # Clear previous segments
        for segment in worm['segments']:
            self.canvas.delete(segment)
        worm['segments'] = []
        
        # Clear previous eyes
        for eye in worm['eyes']:
            self.canvas.delete(eye)
        worm['eyes'] = []
        
        # Clear previous mouth
        if worm['mouth']:
            self.canvas.delete(worm['mouth'])
            worm['mouth'] = None
            
        # Create segments in reverse order (tail to head)
        for i in range(self.worm_segments - 1, -1, -1):
            if i >= len(worm['history']):
                continue
                
            x, y = worm['history'][i]
            if x == 0 and y == 0:  # Skip initial empty positions
                continue
                
            # Calculate segment size - gradually smaller toward the tail
            segment_size = int(worm['segment_size'] * (0.7 + 0.3 * (i / self.worm_segments)))
            
            # Create segment
            segment = self.canvas.create_oval(
                x - segment_size, y - segment_size,
                x + segment_size, y + segment_size,
                fill=worm['color'],
                outline="",
                tags=("worm_segment", f"worm_{worm['id']}")
            )
            worm['segments'].append(segment)
            
        # Add eyes only if we have segments
        if worm['segments']:
            # Head position is the first entry in the history
            head_x, head_y = worm['history'][0]
            angle = worm['angle']
            
            # Eye size
            eye_size = int(worm['segment_size'] * 0.4)
            
            # Eye positions (on either side of the head)
            eye_offset = worm['segment_size'] * 0.5
            left_eye_x = head_x + math.cos(angle + math.pi/4) * eye_offset
            left_eye_y = head_y + math.sin(angle + math.pi/4) * eye_offset
            right_eye_x = head_x + math.cos(angle - math.pi/4) * eye_offset
            right_eye_y = head_y + math.sin(angle - math.pi/4) * eye_offset
            
            # Draw eyes - white background
            left_eye_bg = self.canvas.create_oval(
                left_eye_x - eye_size, left_eye_y - eye_size,
                left_eye_x + eye_size, left_eye_y + eye_size,
                fill="white",
                outline="",
                tags=("worm_eye", f"worm_{worm['id']}")
            )
            right_eye_bg = self.canvas.create_oval(
                right_eye_x - eye_size, right_eye_y - eye_size,
                right_eye_x + eye_size, right_eye_y + eye_size,
                fill="white",
                outline="",
                tags=("worm_eye", f"worm_{worm['id']}")
            )
            worm['eyes'].extend([left_eye_bg, right_eye_bg])
            
            # Pupil size
            pupil_size = int(eye_size * 0.6)
            
            # Draw pupils - if not blinking
            if not worm['blink_state']:
                left_pupil = self.canvas.create_oval(
                    left_eye_x - pupil_size, left_eye_y - pupil_size,
                    left_eye_x + pupil_size, left_eye_y + pupil_size,
                    fill="black",
                    outline="",
                    tags=("worm_eye", f"worm_{worm['id']}")
                )
                right_pupil = self.canvas.create_oval(
                    right_eye_x - pupil_size, right_eye_y - pupil_size,
                    right_eye_x + pupil_size, right_eye_y + pupil_size,
                    fill="black",
                    outline="",
                    tags=("worm_eye", f"worm_{worm['id']}")
                )
                worm['eyes'].extend([left_pupil, right_pupil])
            
            # Draw mouth
            mouth_offset = worm['segment_size'] * 0.7
            mouth_x = head_x + math.cos(angle) * mouth_offset
            mouth_y = head_y + math.sin(angle) * mouth_offset
            
            mouth_width = int(worm['segment_size'] * 0.6)
            mouth_height = int(worm['segment_size'] * (0.1 if worm['mouth_state'] == 0 else 0.4))
            
            worm['mouth'] = self.canvas.create_oval(
                mouth_x - mouth_width, mouth_y - mouth_height,
                mouth_x + mouth_width, mouth_y + mouth_height,
                fill="#AA3333",  # Reddish mouth
                outline="",
                tags=("worm_mouth", f"worm_{worm['id']}")
            )
            
    def animate(self):
        """Main animation loop for all worms"""
        if not self.animation_running or not self.canvas.winfo_exists():
            return
            
        try:
            # Get current canvas dimensions (in case of resize)
            current_width = self.canvas.winfo_width()
            current_height = self.canvas.winfo_height()
            if current_width > 1 and current_height > 1:
                self.width, self.height = current_width, current_height
                
            # Update each worm
            for worm in self.worms:
                self._update_worm(worm)
                
            # Update any interaction particles
            self._update_particles()
                
            # Schedule next animation frame
            self.after_id = self.canvas.after(50, self.animate)
        except Exception as e:
            logging.error(f"Error in worm animation: {e}")
            
    def _update_worm(self, worm):
        """Update a single worm's position and appearance"""
        # Check for interaction with solution symbols if enabled
        if self.interaction_enabled and self.animation_speed > 1.0:
            self._check_symbol_interaction(worm)
        
        # If worm has a target symbol, move toward it
        if worm.get('target_symbol') and random.random() < 0.7:  # 70% chance to follow target
            target_x, target_y = worm['target_symbol']['position']
            head_x, head_y = worm['history'][0] if worm['history'][0] != (0, 0) else (worm['x'], worm['y'])
            
            # Calculate angle to target
            dx = target_x - head_x
            dy = target_y - head_y
            target_angle = math.atan2(dy, dx)
            
            # Gradually turn toward target
            angle_diff = (target_angle - worm['angle'] + math.pi) % (2 * math.pi) - math.pi
            worm['angle'] += angle_diff * 0.2  # Smooth turning
        else:
            # Randomly change direction occasionally
            if random.random() < 0.05:
                worm['angle'] += random.uniform(-math.pi/4, math.pi/4)
            
        # Apply speed based on animation_speed
        speed = 3 * self.animation_speed
        
        # Calculate new position
        new_x = worm['x'] + math.cos(worm['angle']) * speed
        new_y = worm['y'] + math.sin(worm['angle']) * speed
        
        # Bounce off walls
        bounced = False
        if new_x < worm['segment_size'] or new_x > self.width - worm['segment_size']:
            worm['angle'] = math.pi - worm['angle']
            bounced = True
        if new_y < worm['segment_size'] or new_y > self.height - worm['segment_size']:
            worm['angle'] = -worm['angle']
            bounced = True
            
        # Add some wiggle to the movement
        if not bounced and random.random() < 0.1:
            worm['angle'] += random.uniform(-math.pi/8, math.pi/8)
            
        # Update position
        worm['x'] = worm['x'] + math.cos(worm['angle']) * speed
        worm['y'] = worm['y'] + math.sin(worm['angle']) * speed
        
        # Ensure we stay within bounds
        worm['x'] = max(worm['segment_size'], min(self.width - worm['segment_size'], worm['x']))
        worm['y'] = max(worm['segment_size'], min(self.height - worm['segment_size'], worm['y']))
        
        # Update position history
        worm['history'].insert(0, (worm['x'], worm['y']))
        worm['history'] = worm['history'][:self.worm_segments]
        
        # Handle blinking
        worm['blink_timer'] -= 1
        if worm['blink_timer'] <= 0:
            worm['blink_state'] = not worm['blink_state']
            # Shorter blink, longer open eyes
            worm['blink_timer'] = random.randint(5, 10) if worm['blink_state'] else random.randint(50, 200)
            
        # Handle mouth animation
        worm['mouth_timer'] -= 1
        if worm['mouth_timer'] <= 0:
            worm['mouth_state'] = 1 - worm['mouth_state']  # Toggle between 0 and 1
            worm['mouth_timer'] = random.randint(20, 100)
            
        # Clear target if worm hasn't reached it in a while
        if worm.get('target_symbol') and random.random() < 0.01:  # Small chance to forget target
            worm['target_symbol'] = None
            
        # Redraw the worm
        self._draw_worm(worm)
        
    def _check_symbol_interaction(self, worm):
        """Check if worm head is interacting with any solution symbols"""
        # Skip if cooldown is active for this worm
        current_time = time.time()
        cooldown_time = self.interaction_cooldown.get(worm['id'], 0)
        if current_time < cooldown_time:
            return
            
        # Get head position
        head_pos = worm['history'][0] if worm['history'][0] != (0, 0) else (worm['x'], worm['y'])
        head_x, head_y = head_pos
        
        # Interaction range
        interaction_range = worm['segment_size'] * 2
        
        # Check for collision with any solution symbol
        for symbol in self.solution_symbols:
            sym_x, sym_y = symbol['position']
            # Simple distance check
            distance = math.sqrt((head_x - sym_x)**2 + (head_y - sym_y)**2)
            
            if distance < interaction_range:
                # Interaction detected!
                self._handle_symbol_interaction(worm, symbol)
                
                # Set cooldown
                self.interaction_cooldown[worm['id']] = current_time + 2.0  # 2 second cooldown
                
                # Remove this target
                if worm.get('target_symbol') == symbol:
                    worm['target_symbol'] = None
                    
                # Maybe find a new target
                if random.random() < 0.7 and self.solution_symbols:
                    potential_targets = [s for s in self.solution_symbols if s != symbol]
                    if potential_targets:
                        worm['target_symbol'] = random.choice(potential_targets)
                
                # Break after one interaction
                break
                
        # Occasionally set a random target if no collision and no current target
        if random.random() < 0.02 and not worm.get('target_symbol') and self.solution_symbols:
            worm['target_symbol'] = random.choice(self.solution_symbols)
    
    def _handle_symbol_interaction(self, worm, symbol):
        """Handle interaction between a worm and a solution symbol"""
        try:
            # Get symbol info
            symbol_id = symbol.get('id')
            symbol_char = symbol.get('char', '')
            
            if not symbol_id:
                return
                
            # Make the symbol shake
            self._shake_symbol(symbol_id)
            
            # Create particles around the symbol
            self._create_interaction_particles(symbol['position'], worm['color'])
            
            # Make the worm open its mouth
            worm['mouth_state'] = 1
            worm['mouth_timer'] = random.randint(20, 40)
            
            # Log the interaction
            logging.info(f"Worm {worm['id']} interacted with symbol '{symbol_char}' (ID: {symbol_id})")
        except Exception as e:
            logging.error(f"Error handling symbol interaction: {e}")
    
    def _shake_symbol(self, symbol_id):
        """Make a solution symbol shake briefly"""
        try:
            # Don't shake if already shaking
            if symbol_id in self.symbol_shake_ids:
                return
                
            # Original position
            original_pos = self.canvas.coords(symbol_id)
            if not original_pos or len(original_pos) < 2:
                return
                
            shake_count = 0
            max_shakes = 5
            shake_amount = 2
            
            def shake_step():
                nonlocal shake_count
                if shake_count >= max_shakes or not self.canvas.winfo_exists():
                    # Stop shaking and reset position
                    if self.canvas.winfo_exists() and symbol_id in self.symbol_shake_ids:
                        try:
                            self.canvas.coords(symbol_id, original_pos)
                            del self.symbol_shake_ids[symbol_id]
                        except tk.TclError:
                            pass
                    return
                
                # Random offset
                dx = random.uniform(-shake_amount, shake_amount)
                dy = random.uniform(-shake_amount, shake_amount)
                
                try:
                    # Move the symbol
                    self.canvas.move(symbol_id, dx, dy)
                    
                    # Schedule next shake
                    shake_count += 1
                    self.symbol_shake_ids[symbol_id] = self.canvas.after(50, shake_step)
                except tk.TclError:
                    # Symbol might have been deleted
                    if symbol_id in self.symbol_shake_ids:
                        del self.symbol_shake_ids[symbol_id]
            
            # Start shaking
            self.symbol_shake_ids[symbol_id] = self.canvas.after(0, shake_step)
            
        except Exception as e:
            logging.error(f"Error shaking symbol: {e}")
    
    def _create_interaction_particles(self, position, color, num_particles=8):
        """Create particles around interaction point"""
        x, y = position
        
        for _ in range(num_particles):
            # Create a particle with random properties
            particle = {
                'x': x,
                'y': y,
                'vx': random.uniform(-2, 2),
                'vy': random.uniform(-2, 2),
                'size': random.uniform(2, 6),
                'color': color,
                'life': random.uniform(10, 20),  # Frames
                'id': None
            }
            
            # Create the particle on canvas
            particle['id'] = self.canvas.create_oval(
                x - particle['size'], y - particle['size'],
                x + particle['size'], y + particle['size'],
                fill=particle['color'],
                outline="",
                tags="worm_particle"
            )
            
            # Add to particle list
            self.interaction_particles.append(particle)
    
    def _update_particles(self):
        """Update particle effects"""
        # Process each particle
        particles_to_remove = []
        for particle in self.interaction_particles:
            # Update position
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            
            # Apply gravity and friction
            particle['vy'] += 0.1
            particle['vx'] *= 0.95
            particle['vy'] *= 0.95
            
            # Decrease life
            particle['life'] -= 1
            
            # Update size based on life
            new_size = particle['size'] * (particle['life'] / 20)
            
            # Update on canvas if it still exists
            try:
                self.canvas.coords(
                    particle['id'],
                    particle['x'] - new_size, particle['y'] - new_size,
                    particle['x'] + new_size, particle['y'] + new_size
                )
                
                # Fade out
                alpha = particle['life'] / 20
                faded_color = self._adjust_color_alpha(particle['color'], alpha)
                self.canvas.itemconfig(particle['id'], fill=faded_color)
                
            except (tk.TclError, KeyError):
                # Particle's visual element might be gone
                particles_to_remove.append(particle)
                continue
                
            # Remove dead particles
            if particle['life'] <= 0:
                try:
                    self.canvas.delete(particle['id'])
                except tk.TclError:
                    pass
                particles_to_remove.append(particle)
        
        # Remove dead particles from list
        for particle in particles_to_remove:
            if particle in self.interaction_particles:
                self.interaction_particles.remove(particle)
    
    def _adjust_color_alpha(self, hex_color, alpha):
        """Adjust a hex color's opacity by blending with background"""
        # Extract RGB
        r = int(hex_color[1:3], 16)
        g = int(hex_color[3:5], 16)
        b = int(hex_color[5:7], 16)
        
        # Blend with white (or whatever the canvas background is)
        bg_color = "#FFFFFF"  # Assume white background
        bg_r = int(bg_color[1:3], 16)
        bg_g = int(bg_color[3:5], 16)
        bg_b = int(bg_color[5:7], 16)
        
        r = int(r * alpha + bg_r * (1 - alpha))
        g = int(g * alpha + bg_g * (1 - alpha))
        b = int(b * alpha + bg_b * (1 - alpha))
        
        # Return new color
        return f"#{r:02x}{g:02x}{b:02x}"
        
    def start_animation(self, num_worms=1):
        """Start the worm animation with the specified number of worms"""
        if self.animation_running:
            return
            
        self.animation_running = True
        self.create_worm(num_worms)
        self.animate()
        logging.info(f"Started worm animation with {num_worms} worms")
        
    def stop_animation(self):
        """Stop the worm animation"""
        self.animation_running = False
        if self.after_id:
            self.canvas.after_cancel(self.after_id)
            self.after_id = None
            
        # Cancel any shake animations
        for shake_id in self.symbol_shake_ids.values():
            if shake_id:
                try:
                    self.canvas.after_cancel(shake_id)
                except:
                    pass
        self.symbol_shake_ids = {}
            
        logging.info("Stopped worm animation")
        
    def clear_worms(self):
        """Clear all worms from the canvas"""
        if not self.canvas.winfo_exists():
            return
            
        # Delete all worm-related canvas items
        for worm in self.worms:
            for segment in worm['segments']:
                self.canvas.delete(segment)
            for eye in worm['eyes']:
                self.canvas.delete(eye)
            if worm['mouth']:
                self.canvas.delete(worm['mouth'])
                
        # Clear any particles
        for particle in self.interaction_particles:
            self.canvas.delete(particle.get('id'))
        self.interaction_particles = []
                
        self.worms = []
        logging.info("Cleared all worms")
        
    def increase_speed(self, percent=35):
        """Increase the animation speed by the specified percentage"""
        prev_speed = self.animation_speed
        self.animation_speed *= (1 + percent/100)
        
        # Enable interactions if speed is increased above threshold
        if prev_speed <= 1.0 and self.animation_speed > 1.0:
            self.interaction_enabled = True
            self._add_borders_to_solution_symbols()
            
        logging.info(f"Increased worm speed by {percent}%. New speed: {self.animation_speed}")
        
    def reset_speed(self):
        """Reset animation speed to the default"""
        self.animation_speed = 1.0
        self.interaction_enabled = False
        self._remove_borders_from_solution_symbols()
        logging.info("Reset worm speed to default")
        
    def celebrate(self, duration=3000):
        """Make worms celebrate by moving faster and more erratically for a duration
        
        Args:
            duration: Time in milliseconds for celebration
        """
        original_speed = self.animation_speed
        self.animation_speed = 2.0  # Double speed during celebration
        
        # Enable interactions temporarily
        prev_interaction = self.interaction_enabled
        self.interaction_enabled = True
        self._add_borders_to_solution_symbols()
        
        # Make worms more erratic during celebration
        for worm in self.worms:
            worm['angle'] += random.uniform(-math.pi/2, math.pi/2)
            
        logging.info(f"Worms celebrating for {duration}ms")
        
        # Reset after duration
        def reset_after_celebration():
            if self.canvas.winfo_exists():
                self.animation_speed = original_speed
                self.interaction_enabled = prev_interaction
                if not self.interaction_enabled:
                    self._remove_borders_from_solution_symbols()
                logging.info("Worm celebration ended")
                
        self.canvas.after(duration, reset_after_celebration)
        
    def on_step_complete(self):
        """Called when user completes a step in the solution"""
        # Increase speed by 35%
        self.increase_speed(35)
        
        # Reset speed after 10 seconds
        def reset_speed_after_delay():
            if self.canvas.winfo_exists():
                self.reset_speed()
                
        self.canvas.after(10000, reset_speed_after_delay)
        
    def update_solution_symbols(self, symbol_list):
        """Update the list of solution symbols
        
        Args:
            symbol_list: List of dictionaries with keys:
                         - id: Canvas ID of the symbol
                         - position: (x, y) tuple of coordinates
                         - char: The character this symbol represents
        """
        self.solution_symbols = symbol_list
        
        # If interaction is enabled, add borders
        if self.interaction_enabled:
            self._add_borders_to_solution_symbols()
            
        logging.info(f"Updated solution symbols: {len(symbol_list)} symbols")
        
    def _add_borders_to_solution_symbols(self):
        """Add visible borders to all solution symbols to show they're interactive"""
        if not self.canvas.winfo_exists():
            return
            
        for symbol in self.solution_symbols:
            symbol_id = symbol.get('id')
            if not symbol_id:
                continue
                
            try:
                # Check if symbol exists and get its bounding box
                bbox = self.canvas.bbox(symbol_id)
                if not bbox:
                    continue
                    
                # Add a light glow effect around the symbol
                # For performance, we'll use a simple colored rectangle with padding
                padding = 3
                glow_id = f"glow_{symbol_id}"
                
                # Delete existing glow if any
                self.canvas.delete(glow_id)
                
                # Create new glow
                self.canvas.create_rectangle(
                    bbox[0] - padding, bbox[1] - padding,
                    bbox[2] + padding, bbox[3] + padding,
                    outline="#88CCFF",  # Light blue glow
                    width=2,
                    fill="",  # Transparent fill
                    tags=(glow_id, "symbol_glow")
                )
                
                # Move glow behind the text
                self.canvas.tag_lower(glow_id)
                
                # Store glow ID with the symbol
                symbol['glow_id'] = glow_id
                
            except tk.TclError:
                # Symbol might not exist anymore
                continue
                
    def _remove_borders_from_solution_symbols(self):
        """Remove borders from all solution symbols"""
        if not self.canvas.winfo_exists():
            return
            
        # Remove all symbol glows
        self.canvas.delete("symbol_glow")
        
        # Clear glow_id references in symbols
        for symbol in self.solution_symbols:
            if 'glow_id' in symbol:
                del symbol['glow_id']
                
# For testing the animation standalone
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Worm Animation Test with Symbol Interaction")
    root.geometry("600x400")
    
    canvas = tk.Canvas(root, bg="white")
    canvas.pack(fill=tk.BOTH, expand=True)
    
    worm_animation = WormAnimation(canvas, 600, 400)
    
    # Create some test symbols
    def create_test_symbols():
        symbols = []
        for i in range(5):
            x = random.randint(100, 500)
            y = random.randint(100, 300)
            char = random.choice("0123456789+-=xX")
            
            # Create text on canvas
            symbol_id = canvas.create_text(
                x, y, text=char, font=("Arial", 24, "bold"),
                fill="black", tags="test_symbol"
            )
            
            # Add to symbols list
            symbols.append({
                'id': symbol_id,
                'position': (x, y),
                'char': char
            })
            
        # Update worm animation with symbols
        worm_animation.update_solution_symbols(symbols)
    
    def start_animation():
        worm_animation.start_animation(2)  # Start with 2 worms
        
    def stop_animation():
        worm_animation.stop_animation()
        
    def clear_worms():
        worm_animation.clear_worms()
        
    def increase_speed():
        worm_animation.increase_speed(35)
        
    def reset_speed():
        worm_animation.reset_speed()
        
    def celebrate():
        worm_animation.celebrate()
        
    def add_test_symbols():
        create_test_symbols()
        
    # Add control buttons
    control_frame = tk.Frame(root)
    control_frame.pack(fill=tk.X)
    
    tk.Button(control_frame, text="Start", command=start_animation).pack(side=tk.LEFT, padx=5, pady=5)
    tk.Button(control_frame, text="Stop", command=stop_animation).pack(side=tk.LEFT, padx=5, pady=5)
    tk.Button(control_frame, text="Clear", command=clear_worms).pack(side=tk.LEFT, padx=5, pady=5)
    tk.Button(control_frame, text="Speed Up", command=increase_speed).pack(side=tk.LEFT, padx=5, pady=5)
    tk.Button(control_frame, text="Reset Speed", command=reset_speed).pack(side=tk.LEFT, padx=5, pady=5)
    tk.Button(control_frame, text="Celebrate", command=celebrate).pack(side=tk.LEFT, padx=5, pady=5)
    tk.Button(control_frame, text="Add Symbols", command=add_test_symbols).pack(side=tk.LEFT, padx=5, pady=5)
    
    root.mainloop() 