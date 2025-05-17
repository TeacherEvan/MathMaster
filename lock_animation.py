import tkinter as tk
import random
import math
import time
import logging

class LockAnimation:
    def __init__(self, canvas, x, y, size=100, level_name="Easy"):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.size = size
        self.level_name = level_name
        self.is_active = True
        self.after_ids = {}
        self.lock_body_item = None
        self.shackle_item = None
        self.lock_parts_items = []  # Stores canvas item IDs for the 4 segments
        self.diagonal_arms = []  # Stores diagonal connecting arms
        self.arm_pistons = []  # Stores piston elements
        self.unlocked_parts = 0
        self.total_parts = 4  # Number of visual parts in the lock
        self.animation_items = []  # To track created animation elements
        self.original_segment_positions = []  # To store original positions for segments
        self.orbit_particles = []  # To store orbiting particles
        self.last_particle_update = time.time()  # For controlling particle updates
        
        # For character-themed particles
        self.current_particle_state = "orbital"  # Can be "orbital", "transition", or "character"
        self.character_formation_char = None  # Current character being formed
        self.transition_progress = 0.0  # Progress (0.0 to 1.0) in transition animation
        self.particle_positions = {}  # For storing target positions during transitions
        self.transition_start_time = 0  # To track transition timing
        self.character_display_timer = None  # For scheduling character display duration
        
        # Define level color themes
        self.level_themes = {
            "Easy": {
                "locked": ['#E74C3C', '#E57E31', '#D35400', '#C0392B'],  # Red theme
                "unlocked": ['#27AE60', '#2ECC71', '#58D68D', '#82E0AA']  # Green theme
            },
            "Medium": {
                "locked": ['#3498DB', '#2980B9', '#1F618D', '#154360'],  # Blue theme
                "unlocked": ['#F1C40F', '#F39C12', '#F5B041', '#F8C471']  # Yellow theme
            },
            "Division": {
                "locked": ['#9B59B6', '#8E44AD', '#7D3C98', '#6C3483'],  # Purple theme
                "unlocked": ['#1ABC9C', '#16A085', '#48C9B0', '#76D7C4']  # Turquoise theme
            }
        }
        
        # Default to Easy if level_name is not recognized
        if level_name not in self.level_themes:
            self.level_name = "Easy"
        
        # Create initial lock parts
        self._create_lock_visuals()
        
        # Create initial orbiting particles
        self._create_orbiting_particles()
        
        # Start particle animation
        self._animate_particles()
        
    def _create_lock_visuals(self):
        """Create the visual elements of the lock"""
        # Add a subtle glow behind the lock
        glow_padding = self.size // 8
        self.glow_item = self.canvas.create_oval(
            self.x - self.size // 2 - glow_padding, 
            self.y - self.size // 2 - glow_padding * 1.5,  # Extended for taller lock
            self.x + self.size // 2 + glow_padding, 
            self.y + self.size // 2 + glow_padding,
            fill='#1a2533', outline='#1a2533', tags="lock_visual"
        )
        
        # Lock body - taller rectangle for a more elongated look
        body_height = int(self.size * 1.3)  # Make body 30% taller
        self.lock_body_item = self.canvas.create_rectangle(
            self.x - self.size // 2, self.y - self.size // 2,
            self.x + self.size // 2, self.y + self.size // 2 + self.size // 3,  # Extended bottom
            fill='#34495E', outline='#2C3E50', width=4, tags="lock_visual"
        )
        
        # Add metallic highlight to top of lock body
        highlight_height = self.size // 10
        self.highlight_item = self.canvas.create_rectangle(
            self.x - self.size // 2 + 5, self.y - self.size // 2 + 5,
            self.x + self.size // 2 - 5, self.y - self.size // 2 + highlight_height,
            fill='#4A6A8F', outline='', tags="lock_visual"
        )
        
        # Lock shackle (the U-shaped part) - make taller
        shackle_y_start = self.y - self.size // 2 
        shackle_width = self.size // 2.5
        shackle_height = self.size // 2  # Increased height
        
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
            self.y + self.size // 6,  # Moved down to center on taller body
            self.x + keyhole_radius, 
            self.y + self.size // 6 + keyhole_radius * 2,
            fill='#1C2833', outline='#17202A', width=2, tags="lock_visual"
        )
        
        self.keyhole_bottom = self.canvas.create_rectangle(
            self.x - keyhole_radius // 2,
            self.y + self.size // 6 + keyhole_radius * 2,
            self.x + keyhole_radius // 2,
            self.y + self.size // 6 + keyhole_radius * 3.5,
            fill='#1C2833', outline='#17202A', width=1, tags="lock_visual"
        )
        
        # Get color theme for this level
        color_theme = self.level_themes[self.level_name]
        segment_colors = color_theme["locked"]
        segment_outline_colors = [self._darken_color(color, 0.8) for color in segment_colors]
        
        # Lock mechanism parts (4 segments inside the body) - Spaced out for taller lock
        body_bottom = self.y + self.size // 2 + self.size // 3  # Bottom of taller body
        segment_height = (body_bottom - (self.y - self.size // 2)) // self.total_parts
        
        # Create segments and diagonal arms between them
        for i in range(self.total_parts):
            y_top = self.y - self.size // 2 + i * segment_height + 5
            y_bottom = self.y - self.size // 2 + (i + 1) * segment_height - 5
            x_left = self.x - self.size // 3
            x_right = self.x + self.size // 3
            
            base_color_hex = segment_colors[i]
            outline_color_hex = segment_outline_colors[i]

            # Main segment body
            segment = self.canvas.create_rectangle(
                x_left, y_top,
                x_right, y_bottom,
                fill=base_color_hex, outline=outline_color_hex, width=2, tags="lock_visual"
            )
            self.lock_parts_items.append(segment)

            # Add subtle 3D effect/shading to segments
            # Top highlight
            self.canvas.create_line(
                x_left + 2, y_top + 2,
                x_right - 2, y_top + 2,
                fill=self._brighten_color(base_color_hex, 1.2), width=2, tags="lock_visual"
            )
            # Left highlight
            self.canvas.create_line(
                x_left + 2, y_top + 2,
                x_left + 2, y_bottom -2,
                fill=self._brighten_color(base_color_hex, 1.1), width=2, tags="lock_visual"
            )
            # Bottom shadow
            self.canvas.create_line(
                x_left + 2, y_bottom -2,
                x_right -2, y_bottom -2,
                fill=self._darken_color(base_color_hex, 0.7), width=2, tags="lock_visual"
            )
            # Right shadow
            self.canvas.create_line(
                x_right -2, y_top + 2,
                x_right -2, y_bottom -2,
                fill=self._darken_color(base_color_hex, 0.8), width=2, tags="lock_visual"
            )
            
            # Store original positions for separation animation
            self.original_segment_positions.append((y_top, y_bottom))
            
            # Create hidden diagonal arms after the first segment
            # These will be revealed when a segment is unlocked
            if i > 0:
                # Start from bottom of previous segment to top of current
                prev_bottom = self.y - self.size // 2 + i * segment_height - 5
                
                # Calculate diagonal line coordinates
                arm_start_x = self.x - self.size // 6  # Left side
                arm_start_y = prev_bottom
                arm_end_x = self.x + self.size // 6  # Right side
                arm_end_y = y_top
                
                # Create diagonal arms (initially hidden)
                diag_arm = self.canvas.create_line(
                    arm_start_x, arm_start_y,
                    arm_end_x, arm_end_y,
                    fill='#7F8C8D', width=3, state='hidden', tags="lock_visual"
                )
                self.diagonal_arms.append(diag_arm)
                
                # Create piston circle at center of the diagonal arm
                piston_x = (arm_start_x + arm_end_x) / 2
                piston_y = (arm_start_y + arm_end_y) / 2
                piston_radius = self.size // 20
                
                piston = self.canvas.create_oval(
                    piston_x - piston_radius, piston_y - piston_radius,
                    piston_x + piston_radius, piston_y + piston_radius,
                    fill='#95A5A6', outline='#7F8C8D', width=1, state='hidden', tags="lock_visual"
                )
                self.arm_pistons.append(piston)
    
    def _create_orbiting_particles(self):
        """Create particles that orbit around the lock"""
        # Clear any existing particles
        for particle in self.orbit_particles:
            try:
                if 'id' in particle:
                    self.canvas.delete(particle['id'])
            except tk.TclError:
                pass
        self.orbit_particles = []
        
        # Get colors based on level theme
        color_theme = self.level_themes[self.level_name]
        locked_colors = color_theme["locked"]
        unlocked_colors = color_theme["unlocked"]
        
        # Create a mix of colors from both themes plus some neutrals
        all_colors = locked_colors + unlocked_colors + ['#ECF0F1', '#BDC3C7', '#95A5A6']
        
        # Create particles in different orbital rings
        num_rings = 1 
        particles_per_ring = [16]  # Doubled from 8 (originally 5 -> 8 -> 16)
        
        for ring_idx in range(num_rings):
            # Calculate radius for this ring
            ring_radius = (self.size * 0.6) + (ring_idx * self.size * 0.2)  
            
            # Create particles for this ring
            for i in range(particles_per_ring[ring_idx]):
                # Distribute particles evenly around the circle
                angle = i * (2 * math.pi / particles_per_ring[ring_idx])
                
                # Add some randomness to initial positions
                angle_jitter = random.uniform(-0.05, 0.05)
                radius_jitter = random.uniform(-5, 5)
                
                # Calculate position
                x = self.x + (ring_radius + radius_jitter) * math.cos(angle + angle_jitter)
                y = self.y + (ring_radius + radius_jitter) * math.sin(angle + angle_jitter)
                
                # Random size
                size = random.uniform(1.5, 3.5)
                
                # Random color from theme
                color = random.choice(all_colors)
                
                # Determine if this particle should have a glowing pulsating effect (1 in 5)
                is_glowing_pulsating = (i % 5 == 0)

                # Create particle
                particle_id = self.canvas.create_oval(
                    x - size, y - size,
                    x + size, y + size,
                    fill=color, outline='', tags="lock_particle"
                )
                
                # Store particle data
                self.orbit_particles.append({
                    'id': particle_id,
                    'ring_radius': ring_radius + radius_jitter,
                    'angle': angle + angle_jitter,
                    'size': size,
                    'original_size': size,
                    'color': color,
                    'original_color': color, # Store original color for glowing effect
                    'speed': 0.005 * (1 - 0.2 * ring_idx),
                    'direction': 1 if random.random() > 0.3 else -1,
                    'phase': random.random() * 2 * math.pi,
                    'pulse_speed': random.uniform(0.02, 0.05),
                    'is_glowing_pulsating': is_glowing_pulsating # New attribute
                })
    
    def _animate_particles(self):
        if not self.is_active or not self.canvas.winfo_exists():
            return
        
        try:
            # Update particles less frequently for better performance
            current_time = time.time()
            should_update = (current_time - self.last_particle_update) > 0.04  # Changed from 0.02 (50 FPS) to 0.04 (~25 FPS)
            
            if should_update:
                self.last_particle_update = current_time
                
                # Update each particle position
                for particle in self.orbit_particles:
                    if 'id' not in particle:
                        continue
                        
                    try:
                        # Update angle based on speed and direction
                        particle['angle'] += particle['speed'] * particle['direction']
                        
                        # Update phase for pulsating effect
                        particle['phase'] += particle['pulse_speed']
                        
                        # Calculate pulse factor (1.0 +/- 0.2 for normal, more for glowing)
                        pulse_amplitude = 0.2
                        current_color = particle['original_color']

                        if particle.get('is_glowing_pulsating'):
                            pulse_amplitude = 0.4 # More pronounced pulse for glowing particles
                            # Glowing effect: oscillate brightness
                            brightness_factor = 0.7 + 0.3 * math.sin(particle['phase'] * 2) # Multiplies phase for faster glow
                            current_color = self._brighten_color(particle['original_color'], brightness_factor, ensure_visible=True)

                        pulse = 1.0 + pulse_amplitude * math.sin(particle['phase'])
                        
                        # Calculate new position
                        x = self.x + particle['ring_radius'] * math.cos(particle['angle'])
                        y = self.y + particle['ring_radius'] * math.sin(particle['angle'])
                        
                        # Apply size based on pulse
                        size = particle['original_size'] * pulse
                        
                        # Update position, size, and color
                        self.canvas.coords(
                            particle['id'],
                            x - size, y - size,
                            x + size, y + size
                        )
                        if particle.get('is_glowing_pulsating'):
                            self.canvas.itemconfig(particle['id'], fill=current_color)
                        else: # Ensure non-glowing particles retain their original color if not already set
                            if self.canvas.itemcget(particle['id'], 'fill') != particle['original_color']:
                                 self.canvas.itemconfig(particle['id'], fill=particle['original_color'])
                                
                    except tk.TclError:
                        # Skip if particle was deleted
                        continue
                        
            # Schedule next animation frame
            if self.is_active:
                new_after_id = self.canvas.after(30, self._animate_particles)
                self.after_ids['animate_particles'] = new_after_id
                
        except tk.TclError:
            # Canvas might be gone
            pass
    
    def _update_orbital_particles(self):
        """Update particles in orbital motion"""
        for particle in self.orbit_particles:
            if 'id' not in particle:
                continue
                
            try:
                # Update angle based on speed and direction
                particle['angle'] += particle['speed'] * particle['direction']
                
                # Update phase for pulsating effect
                particle['phase'] += particle['pulse_speed']
                
                # Calculate pulse factor (1.0 +/- 0.2 for normal, more for glowing)
                pulse_amplitude = 0.2
                current_color = particle['original_color']

                if particle.get('is_glowing_pulsating'):
                    pulse_amplitude = 0.4 # More pronounced pulse for glowing particles
                    # Glowing effect: oscillate brightness
                    brightness_factor = 0.7 + 0.3 * math.sin(particle['phase'] * 2) # Multiplies phase for faster glow
                    current_color = self._brighten_color(particle['original_color'], brightness_factor, ensure_visible=True)

                pulse = 1.0 + pulse_amplitude * math.sin(particle['phase'])
                
                # Calculate new position
                x = self.x + particle['ring_radius'] * math.cos(particle['angle'])
                y = self.y + particle['ring_radius'] * math.sin(particle['angle'])
                
                # Apply size based on pulse
                size = particle['original_size'] * pulse
                
                # Update position, size, and color
                self.canvas.coords(
                    particle['id'],
                    x - size, y - size,
                    x + size, y + size
                )
                if particle.get('is_glowing_pulsating'):
                    self.canvas.itemconfig(particle['id'], fill=current_color)
                else: # Ensure non-glowing particles retain their original color if not already set
                    if self.canvas.itemcget(particle['id'], 'fill') != particle['original_color']:
                         self.canvas.itemconfig(particle['id'], fill=particle['original_color'])
                        
            except tk.TclError:
                # Skip if particle was deleted
                continue
    
    def _update_transitioning_particles(self, current_time):
        """Update particles that are transitioning between orbital and character states"""
        # Calculate transition progress
        elapsed = current_time - self.transition_start_time
        transition_duration = 1.0  # seconds
        
        # Update progress 
        self.transition_progress = min(1.0, elapsed / transition_duration)
        
        # For each particle, interpolate between its orbital position and target character position
        for particle in self.orbit_particles:
            if 'id' not in particle or particle['id'] not in self.particle_positions:
                continue
                
            try:
                # Get starting orbital position
                start_angle = particle['angle']
                radius = particle['ring_radius']
                start_x = self.x + radius * math.cos(start_angle)
                start_y = self.y + radius * math.sin(start_angle)
                
                # Get target character position
                target_pos = self.particle_positions[particle['id']]
                target_x, target_y = target_pos
                
                # Ease in/out function for smoother transition
                progress = self._ease_in_out(self.transition_progress)
                
                # Interpolate position with "magnetic" effect
                # Initially slow, then accelerating toward target
                if progress < 0.5:
                    # Slower start (particles "hesitate")
                    t = progress * 0.5  # half speed
                else:
                    # Faster finish (particles "snap" to position)
                    t = 0.25 + (progress - 0.5) * 1.5  # accelerating
                
                new_x = start_x + (target_x - start_x) * t
                new_y = start_y + (target_y - start_y) * t
                
                # Add slight "trail" effect during transition
                if progress > 0.3 and progress < 0.8:
                    # Make particles slightly larger during transition
                    size_factor = 1.0 + 0.5 * math.sin(progress * math.pi)
                    size = particle['original_size'] * size_factor
                else:
                    size = particle['original_size']
                
                # Update position and size
                self.canvas.coords(
                    particle['id'],
                    new_x - size, new_y - size,
                    new_x + size, new_y + size
                )
                
                # Update color for tracer effect
                if 0.2 < progress < 0.8:
                    # Get level theme colors
                    color_theme = self.level_themes[self.level_name]
                    all_colors = color_theme["locked"] + color_theme["unlocked"]
                    
                    # Pulse between normal color and highlight color
                    highlight_intensity = math.sin(progress * 10) ** 2  # Creates pulses
                    
                    if highlight_intensity > 0.7:  # Only change during peak of pulse
                        highlight_color = random.choice(all_colors)
                        self.canvas.itemconfig(particle['id'], fill=highlight_color)
                
            except tk.TclError:
                continue
        
        # When transition complete, update state
        if self.transition_progress >= 1.0:
            self.current_particle_state = "character"
            
            # Schedule return to orbital state after a delay
            display_duration = 2.0  # seconds
            self.character_display_timer = self.canvas.after(
                int(display_duration * 1000), 
                self._transition_to_orbital
            )
    
    def _update_character_particles(self, current_time):
        """Update particles that are in character formation"""
        # Make the character formation pulse subtly
        pulse_rate = 3.0  # Hz
        pulse_amount = 0.1  # Scale factor
        
        pulse_factor = 1.0 + pulse_amount * math.sin(current_time * pulse_rate * 2 * math.pi)
        
        # Apply small rotation to the entire formation for visual interest
        angle = math.sin(current_time * 0.8) * 0.05  # Small wobble
        cos_angle = math.cos(angle)
        sin_angle = math.sin(angle)
        
        for particle in self.orbit_particles:
            if 'id' not in particle or particle['id'] not in self.particle_positions:
                continue
                
            try:
                # Get character position and apply pulse
                base_x, base_y = self.particle_positions[particle['id']]
                
                # Center of rotation is the lock center
                rel_x = base_x - self.x
                rel_y = base_y - self.y
                
                # Apply rotation
                rot_x = rel_x * cos_angle - rel_y * sin_angle
                rot_y = rel_x * sin_angle + rel_y * cos_angle
                
                # Apply pulsing and return to absolute coordinates
                new_x = self.x + rot_x * pulse_factor
                new_y = self.y + rot_y * pulse_factor
                
                # Apply size pulse as well
                size = particle['original_size'] * pulse_factor
                
                # Update position and size
                self.canvas.coords(
                    particle['id'],
                    new_x - size, new_y - size,
                    new_x + size, new_y + size
                )
                
            except tk.TclError:
                continue
    
    def _transition_to_orbital(self):
        """Start transition from character back to orbital state"""
        self.current_particle_state = "transition"
        self.transition_progress = 0.0
        self.transition_start_time = time.time()
        
        # Switch direction - now transitioning from character to orbital
        # The transition animation will handle the movement, and when complete,
        # it will set the state back to "orbital"
        
        # Cancel any pending timer
        if self.character_display_timer:
            self.canvas.after_cancel(self.character_display_timer)
            self.character_display_timer = None
    
    def _ease_in_out(self, x):
        """Cubic ease-in/ease-out function for smoother transitions"""
        if x < 0.5:
            return 4 * x * x * x
        else:
            return 1 - pow(-2 * x + 2, 3) / 2
    
    def display_character_formation(self, character):
        """Transition particles to form a specific character"""
        if not self.canvas.winfo_exists() or not character:
            return
        
        # Only allow alphanumeric characters
        character = str(character)[0]  # Take only first character
        if not character.isalnum() and character not in ['+', '-', '=']:
            return
            
        self.character_formation_char = character
        
        # Cancel any existing transition
        if self.character_display_timer:
            self.canvas.after_cancel(self.character_display_timer)
            self.character_display_timer = None
        
        # Calculate character shape and assign particles
        self._form_character_shape(character)
        
        # Start transition
        self.current_particle_state = "transition"
        self.transition_progress = 0.0
        self.transition_start_time = time.time()
    
    def _form_character_shape(self, character):
        """Generate coordinates for particles to form a specific character"""
        # Clear previous positions
        self.particle_positions = {}
        
        # Character size - use a portion of the lock size
        char_size = self.size * 0.7
        
        # Get particle coordinates for this character
        positions = self._get_character_coordinates(character.upper(), char_size)
        
        # Determine how many particles to use based on character complexity
        # We'll use at most len(self.orbit_particles) positions
        num_particles = min(len(positions), len(self.orbit_particles))
        
        # Randomly select particles to participate in the formation
        particles_to_use = random.sample(self.orbit_particles, num_particles)
        
        # Assign positions to particles
        for i, particle in enumerate(particles_to_use):
            if i < len(positions) and 'id' in particle:
                # Apply a small random offset for more natural look
                offset_x = random.uniform(-2, 2)
                offset_y = random.uniform(-2, 2)
                
                pos_x, pos_y = positions[i]
                self.particle_positions[particle['id']] = (
                    self.x + pos_x + offset_x, 
                    self.y + pos_y + offset_y
                )
    
    def _get_character_coordinates(self, char, size):
        """Get the coordinates that form a specific character"""
        # Base size and center offsets
        half_width = size / 2
        half_height = size / 2
        
        # Dictionary of coordinate lists for characters
        # Each list contains relative x,y coordinates to form the character
        character_data = {
            # Numbers
            '0': self._generate_oval_points(-half_width*0.6, -half_height*0.8, half_width*0.6, half_height*0.8, 20),
            '1': self._generate_line_points(0, -half_height, 0, half_height, 10),
            '2': self._generate_custom_path([
                (-half_width*0.6, -half_height*0.5),
                (0, -half_height*0.8),
                (half_width*0.6, -half_height*0.5),
                (half_width*0.6, 0),
                (0, half_height*0.4),
                (-half_width*0.6, half_height*0.8),
                (half_width*0.6, half_height*0.8)
            ], 20),
            '3': self._generate_custom_path([
                (-half_width*0.6, -half_height*0.8),
                (half_width*0.6, -half_height*0.4),
                (0, 0),
                (half_width*0.6, half_height*0.4),
                (-half_width*0.6, half_height*0.8)
            ], 20),
            '4': self._generate_custom_path([
                (half_width*0.2, -half_height*0.8),
                (half_width*0.2, half_height*0.8),
                (half_width*0.2, 0),
                (-half_width*0.6, 0),
                (-half_width*0.6, -half_height*0.4)
            ], 20),
            '5': self._generate_custom_path([
                (half_width*0.6, -half_height*0.8),
                (-half_width*0.6, -half_height*0.8),
                (-half_width*0.6, 0),
                (half_width*0.6, 0),
                (half_width*0.6, half_height*0.8),
                (-half_width*0.6, half_height*0.8)
            ], 24),
            '6': self._generate_custom_path([
                (half_width*0.6, -half_height*0.8),
                (-half_width*0.6, 0),
                (-half_width*0.6, half_height*0.8),
                (half_width*0.6, half_height*0.8),
                (half_width*0.6, 0),
                (-half_width*0.6, 0)
            ], 24),
            '7': self._generate_custom_path([
                (-half_width*0.6, -half_height*0.8),
                (half_width*0.6, -half_height*0.8),
                (0, half_height*0.8)
            ], 15),
            '8': self._generate_custom_path([
                (0, -half_height*0.8),
                (half_width*0.6, -half_height*0.4),
                (half_width*0.6, 0),
                (0, half_height*0.4),
                (-half_width*0.6, half_height*0.8),
                (half_width*0.6, half_height*0.8),
                (0, half_height*0.4),
                (-half_width*0.6, 0),
                (-half_width*0.6, -half_height*0.4),
                (0, -half_height*0.8)
            ], 30),
            '9': self._generate_custom_path([
                (-half_width*0.6, -half_height*0.8),
                (half_width*0.6, -half_height*0.8),
                (half_width*0.6, 0),
                (-half_width*0.6, 0),
                (half_width*0.6, 0),
                (half_width*0.6, half_height*0.8)
            ], 24),
            
            # Letters - a subset of common ones
            'A': self._generate_custom_path([
                (-half_width*0.6, half_height*0.8),
                (0, -half_height*0.8),
                (half_width*0.6, half_height*0.8),
                (half_width*0.4, half_height*0.2),
                (-half_width*0.4, half_height*0.2)
            ], 20),
            'X': self._generate_custom_path([
                (-half_width*0.6, -half_height*0.8),
                (half_width*0.6, half_height*0.8),
                (0, 0),
                (-half_width*0.6, half_height*0.8),
                (half_width*0.6, -half_height*0.8)
            ], 20),
            '+': self._generate_custom_path([
                (0, -half_height*0.8),
                (0, half_height*0.8),
                (0, 0),
                (-half_width*0.8, 0),
                (half_width*0.8, 0)
            ], 20),
            '-': self._generate_line_points(-half_width*0.8, 0, half_width*0.8, 0, 10),
            '=': self._generate_custom_path([
                (-half_width*0.8, -half_height*0.2),
                (half_width*0.8, -half_height*0.2),
                (-half_width*0.8, half_height*0.2),
                (half_width*0.8, half_height*0.2)
            ], 16),
        }
        
        # Default to a simple circle if character not found
        if char not in character_data:
            return self._generate_oval_points(-half_width*0.6, -half_height*0.6, half_width*0.6, half_height*0.6, 20)
            
        return character_data[char]
    
    def _generate_line_points(self, x1, y1, x2, y2, num_points):
        """Generate evenly spaced points along a line"""
        points = []
        for i in range(num_points):
            t = i / (num_points - 1) if num_points > 1 else 0
            x = x1 + (x2 - x1) * t
            y = y1 + (y2 - y1) * t
            points.append((x, y))
        return points
    
    def _generate_oval_points(self, x1, y1, x2, y2, num_points):
        """Generate points around an oval"""
        center_x = (x1 + x2) / 2
        center_y = (y1 + y2) / 2
        radius_x = (x2 - x1) / 2
        radius_y = (y2 - y1) / 2
        
        points = []
        for i in range(num_points):
            angle = 2 * math.pi * i / num_points
            x = center_x + radius_x * math.cos(angle)
            y = center_y + radius_y * math.sin(angle)
            points.append((x, y))
        return points
    
    def _generate_custom_path(self, path_points, num_points):
        """Generate points along a custom path defined by line segments"""
        if len(path_points) < 2:
            return []
            
        # Calculate total path length for even distribution
        total_length = 0
        segments = []
        
        for i in range(len(path_points) - 1):
            x1, y1 = path_points[i]
            x2, y2 = path_points[i + 1]
            segment_length = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
            total_length += segment_length
            segments.append((x1, y1, x2, y2, segment_length))
        
        # Generate evenly spaced points along the path
        points = []
        remaining_length = 0
        current_segment = 0
        
        for i in range(num_points):
            # Target position along the path (0 to 1)
            target_pos = i / (num_points - 1) if num_points > 1 else 0
            target_length = target_pos * total_length
            
            # Find segment containing this point
            while current_segment < len(segments) and remaining_length + segments[current_segment][4] < target_length:
                remaining_length += segments[current_segment][4]
                current_segment += 1
                
            if current_segment >= len(segments):
                # Add the final point
                points.append(path_points[-1])
                continue
                
            # Calculate position within current segment
            x1, y1, x2, y2, seg_length = segments[current_segment]
            segment_pos = (target_length - remaining_length) / seg_length if seg_length > 0 else 0
            
            # Calculate point coordinates
            x = x1 + (x2 - x1) * segment_pos
            y = y1 + (y2 - y1) * segment_pos
            points.append((x, y))
            
        return points
    
    def _react_particles_to_completion(self, row_index):
        """Make particles react dramatically when a row is completed"""
        if not self.canvas.winfo_exists():
            return
            
        try:
            # Get color from the newly unlocked segment
            color_theme = self.level_themes[self.level_name]
            unlock_colors = color_theme["unlocked"]
            new_color = unlock_colors[row_index % len(unlock_colors)]
            
            # Shake effect - jiggle particles outward then inward
            self._shake_particles(intensity=0.2)  # Reduced intensity further from 0.5
            
            # Color burst - change nearby particles to the completion color
            self._color_burst(row_index, new_color)
            
            # Speed boost - temporarily increase particle speed
            for particle in self.orbit_particles:
                if 'id' in particle:
                    # Increase speed dramatically
                    particle['speed'] *= 3.0  # Increased from 2.5
                    
                    # Also reverse direction for some particles for chaotic effect
                    if random.random() < 0.3:  # 30% chance to reverse
                        particle['direction'] *= -1
                    
                    # Schedule return to normal speed
                    self.canvas.after(800, lambda p=particle: self._reset_particle_speed(p))
                    
            # Create explosion effect centered on the completed row
            segment_info = self.original_segment_positions[row_index]
            center_y = (segment_info[0] + segment_info[1]) / 2
            
            # Create a single, smaller explosion for a less dramatic effect
            self._create_completion_explosion(self.x, center_y, new_color, num_particles_explosion=3) # Reduced from 6
            # self.canvas.after(150, lambda: self._create_completion_explosion(self.x - self.size/4, center_y, new_color))
            # self.canvas.after(300, lambda: self._create_completion_explosion(self.x + self.size/4, center_y, new_color))
            
            # Create circular wave pattern of particles - reduced waves and particles
            self._create_circular_wave_pattern(self.x, center_y, new_color, num_waves_override=1, particles_per_wave_override=4) # Reduced particles from 8
            
            # Display row number as character formation
            # Convert to numeric character ('1' through '4')
            self.display_character_formation(str(row_index + 1))
            
        except (tk.TclError, Exception) as e:
            print(f"Error in particle reaction: {e}")
    
    def _create_circular_wave_pattern(self, center_x, center_y, color, num_waves_override=None, particles_per_wave_override=None):
        """Create expanding circular waves of particles when a row is completed"""
        try:
            # Generate complementary colors for the wave particles
            base_color = color.lstrip('#')
            r = int(base_color[0:2], 16)
            g = int(base_color[2:4], 16)
            b = int(base_color[4:6], 16)
            
            # Create complementary color
            comp_r = 255 - r
            comp_g = 255 - g
            comp_b = 255 - b
            complementary_color = f'#{comp_r:02x}{comp_g:02x}{comp_b:02x}'
            
            # Create a mix of colors for visual interest
            wave_colors = [color, complementary_color, '#FFFFFF']
            
            # Create multiple waves with different timing
            num_waves = num_waves_override if num_waves_override is not None else 2 # Doubled from 1 (originally 3 -> 1 -> 2)
            for wave_idx in range(num_waves):
                # Schedule each wave to start with a delay
                delay = wave_idx * 150  # Reduced delay from 200ms
                self.canvas.after(delay, lambda idx=wave_idx: self._start_wave(
                    center_x, center_y, idx, num_waves, wave_colors, particles_per_wave_override=particles_per_wave_override))
                
        except Exception as e:
            print(f"Error creating circular wave: {e}")
    
    def _start_wave(self, center_x, center_y, wave_idx, total_waves, colors, particles_per_wave_override=None):
        """Start a single circular wave of particles"""
        try:
            if not self.canvas.winfo_exists():
                return
                
            # Parameters for this wave
            # Doubled particle count
            num_particles = particles_per_wave_override if particles_per_wave_override is not None else (10 + wave_idx * 4)  # Doubled (from 5 + idx*2), (orig 16 + idx*4 -> 5+idx*2 -> 10+idx*4)
            radius = self.size * 0.15 * (wave_idx + 1)  # Adjusted starting radius from 0.2
            max_radius = self.size * (0.7 + 0.2 * wave_idx)  # Adjusted max radius from 1.0 + 0.3
            
            # Create particles distributed evenly around the circle
            wave_particles_data = []
            
            # Add main particles
            for i in range(num_particles):
                angle = i * (2 * math.pi / num_particles)
                
                # Particle color alternates between the provided colors
                particle_color = colors[i % len(colors)]
                
                # Particle size varies to create texture
                size = random.uniform(2.5, 4.5)
                is_pulsating = (i % 10 == 0) # 1 in 10 pulsate
                
                # Create particle
                particle_id = self.canvas.create_oval(
                    center_x - size, center_y - size,
                    center_x + size, center_y + size,
                    fill=particle_color, outline='', tags="lock_wave"
                )
                
                # Store particle information
                wave_particles_data.append({
                    'id': particle_id,
                    'angle': angle,
                    'original_size': size,
                    'current_size': size,
                    'radius': radius,
                    'max_radius': max_radius,
                    'original_color': particle_color,
                    'phase': random.random() * 2 * math.pi,  # Random phase for oscillation
                    'type': 'main',  # Main particle
                    'trail_ids': [],  # Will store IDs of trail particles
                    'is_pulsating': is_pulsating,
                    'pulse_phase': random.uniform(0, 2 * math.pi) # For pulsation
                })
            
            # Start animating the wave
            self._animate_wave(center_x, center_y, wave_particles_data, 0, 60)  # 60 frames total
            
        except tk.TclError:
            pass
    
    def _animate_wave(self, center_x, center_y, particles_data, frame, max_frames):
        """Animate a circular wave of particles expanding outward"""
        if frame >= max_frames or not self.canvas.winfo_exists():
            # Clean up particles when animation completes
            for particle_info in particles_data:
                try:
                    self.canvas.delete(particle_info['id'])
                    # Also delete any trail particles
                    for trail_id in particle_info.get('trail_ids', []):
                        self.canvas.delete(trail_id)
                except tk.TclError:
                    pass
            return
            
        try:
            # Animation progress (0.0 to 1.0)
            progress = frame / max_frames
            
            # Use easing function for smooth acceleration and deceleration
            ease_progress = self._ease_in_out(progress)
            
            for particle_info in particles_data:
                if 'id' not in particle_info:
                    continue
                    
                # Calculate current radius based on progress
                current_radius = particle_info['radius'] + (particle_info['max_radius'] - particle_info['radius']) * ease_progress
                
                # Add oscillation to radius for wave-like effect
                oscillation = math.sin(particle_info['phase'] + progress * 8 * math.pi) * (self.size * 0.05)
                current_radius += oscillation
                
                # Calculate position
                angle = particle_info['angle']
                
                # Add a slight rotation to the angle for swirling effect
                angle += progress * 0.5 * math.pi * (1 if frame % 2 == 0 else -1)  # Alternating direction
                
                x = center_x + current_radius * math.cos(angle)
                y = center_y + current_radius * math.sin(angle)
                
                # Calculate current size - particles grow then shrink
                size_factor = 1.0
                if progress < 0.3:
                    # Grow during first 30%
                    size_factor = 1.0 + progress * 2
                elif progress > 0.7:
                    # Shrink during last 30%
                    size_factor = 1.0 + 0.6 - (progress - 0.7) * 2
                
                particle_info['current_size'] = particle_info['original_size'] * size_factor
                current_color_to_set = particle_info['original_color']
                size_to_draw = particle_info['current_size']

                if particle_info['is_pulsating']:
                    particle_info['pulse_phase'] += 0.2 # Speed of wave pulse
                    size_pulse_amplitude = 0.25
                    brightness_pulse_amplitude = 0.4

                    pulsed_size_modifier = (1.0 + size_pulse_amplitude * math.sin(particle_info['pulse_phase']))
                    size_to_draw = particle_info['current_size'] * pulsed_size_modifier
                    
                    brightness_factor = 1.0 + brightness_pulse_amplitude * math.sin(particle_info['pulse_phase'] + math.pi/1.5)
                    current_color_to_set = self._brighten_color(particle_info['original_color'], brightness_factor, ensure_visible=True)

                size_to_draw = max(0, size_to_draw)
                
                # Create trail effect by adding smaller particles behind main particle
                if frame % 3 == 0 and frame > 5 and frame < max_frames - 10:  # Only add trails every 3 frames and during middle of animation
                    # Clean up old trails if too many
                    if len(particle_info.get('trail_ids', [])) > 5:
                        try:
                            old_trail = particle_info['trail_ids'].pop(0)
                            self.canvas.delete(old_trail)
                        except (tk.TclError, IndexError):
                            pass
                    
                    # Create new trail particle
                    trail_size = size_to_draw * 0.6  # Smaller than main particle
                    trail_color = self._apply_opacity(current_color_to_set, 0.5)  # Semi-transparent
                    
                    trail_id = self.canvas.create_oval(
                        x - trail_size, y - trail_size,
                        x + trail_size, y + trail_size,
                        fill=trail_color, outline='', tags="lock_wave"
                    )
                    
                    # Add to trail IDs
                    if 'trail_ids' not in particle_info:
                        particle_info['trail_ids'] = []
                    particle_info['trail_ids'].append(trail_id)
                
                # Update position and size of main particle
                self.canvas.coords(
                    particle_info['id'],
                    x - size_to_draw, y - size_to_draw,
                    x + size_to_draw, y + size_to_draw
                )
                self.canvas.itemconfig(particle_info['id'], fill=current_color_to_set)
                
                # Add glow effect at certain animation stages (removed, handled by pulsation)
                # Add trailing effect by changing opacity toward the end (if not pulsating)
                if not particle_info['is_pulsating'] and progress > 0.6:
                    opacity = 1.0 - (progress - 0.6) / 0.4  # Fade out in last 40%
                    self.canvas.itemconfig(particle_info['id'], fill=self._apply_opacity(particle_info['original_color'], opacity))
                elif particle_info['is_pulsating'] and progress > 0.85: # Pulsating ones fade faster at very end
                     opacity = 1.0 - (progress - 0.85) / 0.15
                     self.canvas.itemconfig(particle_info['id'], fill=self._apply_opacity(current_color_to_set, opacity))

            # Schedule next frame
            self.canvas.after(16, lambda: self._animate_wave(
                center_x, center_y, particles_data, frame + 1, max_frames))
                
        except tk.TclError:
            # Canvas or item might be gone
            pass
            
    def _brighten_color(self, hex_color, factor=1.3, ensure_visible=False):
        """Brighten a given hex color by a factor.
        If ensure_visible is True, it prevents the color from becoming too dark.
        """
        # Remove # if present
        hex_color = hex_color.lstrip('#')
        
        # Convert to RGB
        r_orig = int(hex_color[0:2], 16)
        g_orig = int(hex_color[2:4], 16)
        b_orig = int(hex_color[4:6], 16)

        r = min(255, int(r_orig * factor))
        g = min(255, int(g_orig * factor))
        b = min(255, int(b_orig * factor))

        if ensure_visible:
            # Ensure that the color doesn't become too dark, maintain some luminosity
            min_luminosity_component = 30 # Minimum value for any RGB component for "glow"
            if factor < 0.5: # If dimming significantly, ensure it's not black
                r = max(r, min(r_orig, min_luminosity_component))
                g = max(g, min(g_orig, min_luminosity_component))
                b = max(b, min(b_orig, min_luminosity_component))
        
        # Convert back to hex
        return f'#{r:02x}{g:02x}{b:02x}'
    
    def _shake_particles(self, intensity=1.0):
        """Shake all particles temporarily"""
        try:
            for particle in self.orbit_particles:
                if 'id' in particle:
                    # Apply a radial jolt outward
                    particle['ring_radius'] += random.uniform(5, 15) * intensity
                    
                    # Schedule return to normal radius
                    original_radius = particle['ring_radius']
                    self.canvas.after(300, lambda p=particle, r=original_radius: self._reset_particle_radius(p, r))
        except Exception as e:
            print(f"Error in shake_particles: {e}")
    
    def _reset_particle_radius(self, particle, original_radius):
        """Reset particle radius back to original after shake effect"""
        try:
            if 'id' in particle:
                particle['ring_radius'] = original_radius
        except Exception:
            pass
    
    def _reset_particle_speed(self, particle):
        """Reset particle speed back to normal after boost"""
        try:
            if 'id' in particle:
                # Reduce speed back to normal (divide by the same factor we multiplied by)
                particle['speed'] /= 2.5
        except Exception:
            pass
    
    def _color_burst(self, row_index, new_color):
        """Create a color burst effect, changing particles near the completed row"""
        try:
            # Get y-position of the completed row
            segment_info = self.original_segment_positions[row_index]
            row_y = (segment_info[0] + segment_info[1]) / 2
            
            # Change color of particles near this row
            for particle in self.orbit_particles:
                if 'id' in particle:
                    # Calculate particle position
                    angle = particle['angle']
                    radius = particle['ring_radius']
                    x = self.x + radius * math.cos(angle)
                    y = self.y + radius * math.sin(angle)
                    
                    # Check vertical proximity to the row
                    distance = abs(y - row_y)
                    if distance < self.size / 3:  # Closer particles are affected
                        # Change color with a chance based on distance
                        chance = 1.0 - (distance / (self.size / 3))
                        if random.random() < chance:
                            self.canvas.itemconfig(particle['id'], fill=new_color)
                            particle['color'] = new_color
        except Exception as e:
            print(f"Error in color burst: {e}")
    
    def _create_completion_explosion(self, x, y, color, num_particles_explosion=None):
        """Create an explosion effect when a row is completed"""
        try:
            # Create flying particles, allow override for number of particles
            num_to_create = num_particles_explosion if num_particles_explosion is not None else 6 # Doubled from 3 (originally 6 -> 3 -> 6)
            for i in range(num_to_create):
                # Random angle and speed
                angle = random.uniform(0, 2 * math.pi)
                speed = random.uniform(2, 6)
                
                # Initial position
                px = x
                py = y
                
                # Random size
                size = random.uniform(2, 5)
                is_pulsating = (i % 10 == 0) # 1 in 10 pulsates
                
                # Create the particle
                particle_item_id = self.canvas.create_oval(
                    px - size, py - size,
                    px + size, py + size,
                    fill=color, outline='', tags="explosion_particle"
                )
                
                # Animate the particle
                self._animate_explosion_particle(particle_item_id, px, py, angle, speed, size, 0, 25, color, is_pulsating)
                
        except Exception as e:
            print(f"Error creating explosion: {e}")
    
    def _animate_explosion_particle(self, particle_id, x, y, angle, speed, original_size, frame, max_frames, original_color, is_pulsating):
        """Animate a single explosion particle"""
        if frame >= max_frames or not self.canvas.winfo_exists():
            try:
                self.canvas.delete(particle_id)
            except tk.TclError:
                pass
            return
            
        try:
            # Update position
            new_x = x + speed * math.cos(angle) * frame
            new_y = y + speed * math.sin(angle) * frame
            
            # Apply gravity effect
            new_y += 0.1 * frame * frame
            
            # Update size (shrink as it moves)
            current_size = original_size * (1 - frame / max_frames)
            current_color_to_set = original_color

            if is_pulsating:
                # Pulsating effect for size and brightness
                pulse_phase = frame * 0.5 # Adjust speed of pulse
                size_pulse_amplitude = 0.3
                brightness_pulse_amplitude = 0.5
                
                current_size *= (1.0 + size_pulse_amplitude * math.sin(pulse_phase))
                
                brightness_factor = 1.0 + brightness_pulse_amplitude * math.sin(pulse_phase + math.pi/2) # phase shift for brightness
                current_color_to_set = self._brighten_color(original_color, brightness_factor, ensure_visible=True)

            # Ensure size is not negative
            current_size = max(0, current_size)
            
            # Update particle
            self.canvas.coords(
                particle_id,
                new_x - current_size, new_y - current_size,
                new_x + current_size, new_y + current_size
            )
            self.canvas.itemconfig(particle_id, fill=current_color_to_set)
            
            # Add opacity effect toward the end (only if not already pulsating color)
            if not is_pulsating and frame > max_frames * 0.7:
                # Calculate opacity factor
                opacity = 1.0 - (frame - max_frames * 0.7) / (max_frames * 0.3)
                # Get original color
                # Apply opacity
                self.canvas.itemconfig(particle_id, fill=self._apply_opacity(original_color, opacity))
            elif is_pulsating and frame >= max_frames -1: # Ensure pulsating ones also fade at very end
                 self.canvas.itemconfig(particle_id, fill=self._apply_opacity(current_color_to_set, 0.1))

            
            # Schedule next frame
            self.canvas.after(20, lambda: self._animate_explosion_particle(
                particle_id, x, y, angle, speed, original_size, frame + 1, max_frames, original_color, is_pulsating))
                
        except tk.TclError:
            pass
            
    def _apply_opacity(self, color, opacity):
        """Apply opacity to a color by blending with background (roughly approximated)"""
        try:
            # Remove # if present
            color = color.lstrip('#')
            
            # Convert to RGB
            r = int(color[0:2], 16)
            g = int(color[2:4], 16)
            b = int(color[4:6], 16)
            
            # Apply opacity (blend with black background)
            r = int(r * opacity)
            g = int(g * opacity)
            b = int(b * opacity)
            
            # Convert back to hex
            return f'#{r:02x}{g:02x}{b:02x}'
        except Exception:
            return color
    
    def _darken_color(self, hex_color, factor=0.7):
        """Darken a given hex color by a factor"""
        # Remove # if present
        hex_color = hex_color.lstrip('#')
        
        # Convert to RGB
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        
        # Darken each component
        r = int(max(0, r * factor))
        g = int(max(0, g * factor))
        b = int(max(0, b * factor))
        
        # Convert back to hex
        return f'#{r:02x}{g:02x}{b:02x}'
            
    def unlock_next_part(self):
        """Trigger animation for unlocking the next part"""
        if self.unlocked_parts < self.total_parts:
            current_part_idx = self.unlocked_parts
            current_part_item = self.lock_parts_items[current_part_idx]
            
            # Get color theme for unlocked state based on level
            color_theme = self.level_themes[self.level_name]
            unlock_colors = color_theme["unlocked"]
            unlock_outline_colors = [self._darken_color(color, 0.8) for color in unlock_colors]
            
            # Use different colors for different segments
            color_idx = current_part_idx % len(unlock_colors)
            new_color = unlock_colors[color_idx]
            
            # Briefly flash the segment with white before changing to the unlocked color
            self.canvas.itemconfig(current_part_item, fill='#FFFFFF')
            
            # Schedule the actual color change after a brief flash
            self.canvas.after(150, lambda: self.canvas.itemconfig(
                current_part_item, 
                fill=new_color, 
                outline=unlock_outline_colors[color_idx]
            ))
            
            # Show the connecting arms for segments above the first one
            if current_part_idx > 0:
                # Index for the diagonal arm is one less than the segment
                arm_idx = current_part_idx - 1
                
                # Show and animate the diagonal arm
                self._animate_diagonal_arm_release(arm_idx)
            
            # Make particles react to completion of this row with a slight delay
            # to sync with the color change
            segment_info = self.original_segment_positions[current_part_idx]
            center_y = (segment_info[0] + segment_info[1]) / 2
            
            # Initial quick reaction
            self._shake_particles(intensity=1.8)  # Increase intensity for more drama
            
            # Add sparkle effect immediately
            self._create_sparkle_effect(current_part_idx)
            
            # Schedule the main reaction with a slight delay to create a multi-stage effect
            self.canvas.after(200, lambda: self._react_particles_to_completion(current_part_idx))
            
            # Create additional delayed waves for sustained effect
            self.canvas.after(500, lambda: self._create_circular_wave_pattern(self.x, center_y, new_color))
            
            # Animate the cell separation (expanding in length)
            self._animate_cell_separation()
            
            # If all parts are unlocked, show a special animation
            if self.unlocked_parts == self.total_parts - 1:
                self.after_unlocked = self.canvas.after(500, self._show_unlock_complete_animation)
            
            self.unlocked_parts += 1
    
    def _animate_cell_separation(self):
        """Animate cells breaking apart and expanding in length"""
        # Calculate the total expansion distance
        expansion_distance = self.size // 5  # How much the lock will expand in total
        
        # Calculate the expansion per segment (more segments = more expansion)
        expansion_per_segment = expansion_distance / max(1, self.unlocked_parts)
        
        # Start the animation sequence
        self._expand_lock_cells(0, 10, expansion_per_segment)
        
    def _expand_lock_cells(self, step, max_steps, total_expansion):
        if not self.is_active or not self.canvas.winfo_exists():
            return

        if step >= max_steps:
            return

        progress = self._ease_in_out(step / max_steps)
        current_expansion = total_expansion * progress

        for i in range(self.total_parts):
            # Defensive check (ensured)
            if i >= len(self.lock_parts_items) or i >= len(self.original_segment_positions):
                logging.warning(f"_expand_lock_cells: Index {i} out of bounds for lock_parts_items ({len(self.lock_parts_items)}) or original_segment_positions ({len(self.original_segment_positions)}).")
                continue

            segment_item = self.lock_parts_items[i]
            original_top, original_bottom = self.original_segment_positions[i]
            
            # When expanding upwards, we need to move segments above the current one
            # So segments with index < unlocked_parts need to move up
            if i < self.unlocked_parts:
                # Higher segments move up more (reversed from expanding downward)
                # The first segment (i=0) should move the most, last segment the least
                # Use (self.unlocked_parts - i - 1) to get the right ordering
                additional_gap = current_expansion * (self.unlocked_parts - i)
                
                # Move upward (negative Y direction), ensure we don't go off canvas
                # Get current coords
                coords = self.canvas.coords(segment_item)
                left, _, right, _ = coords
                
                # Update with new top/bottom positions (move upward)
                new_top = max(5, original_top - additional_gap)  # Ensure stays on canvas
                new_bottom = original_bottom - additional_gap
                
                self.canvas.coords(segment_item,
                    left, new_top,
                    right, new_bottom
                )
            else:
                # For segments not moving up, just ensure they're properly positioned
                # considering the safe offset
                coords = self.canvas.coords(segment_item)
                left, _, right, _ = coords
                self.canvas.coords(segment_item,
                    left, original_top,
                    right, original_bottom
                )
        
        # Also update diagonal arms between segments
        for i in range(self.total_parts):
            # Only adjust arms for unlocked segments
            if i > 0 and i <= self.unlocked_parts:
                arm_idx = i - 1  # Arms are offset by 1 from segments
                if arm_idx < len(self.diagonal_arms):
                    arm_item = self.diagonal_arms[arm_idx]
                    piston_item = self.arm_pistons[arm_idx]
                    
                    # Calculate connecting points
                    # If current segment (i) and previous segment (i-1) are both unlocked,
                    # need to account for both moving
                    current_gap = current_expansion * (self.unlocked_parts - i) if i < self.unlocked_parts else 0
                    prev_gap = current_expansion * (self.unlocked_parts - i + 1) if i - 1 < self.unlocked_parts else 0
                    
                    # Get original positions with safe offset
                    prev_bottom = self.original_segment_positions[i-1][1] - prev_gap
                    curr_top = self.original_segment_positions[i][0] - current_gap
                    
                    # Update diagonal arm coordinates
                    arm_start_x = self.x - self.size // 6
                    arm_start_y = prev_bottom
                    arm_end_x = self.x + self.size // 6
                    arm_end_y = curr_top
                    
                    self.canvas.coords(arm_item,
                        arm_start_x, arm_start_y,
                        arm_end_x, arm_end_y
                    )
                    
                    # Update piston position to remain in the middle of the arm
                    piston_x = (arm_start_x + arm_end_x) / 2
                    piston_y = (arm_start_y + arm_end_y) / 2
                    piston_radius = self.size // 18  # Match the size in _animate_piston_release
                    
                    self.canvas.coords(piston_item,
                        piston_x - piston_radius, piston_y - piston_radius,
                        piston_x + piston_radius, piston_y + piston_radius
                    )
        
        # Update the lock body and shackle
        if self.unlocked_parts > 0:
            # Calculate how much to move the top of the lock up
            # The more segments unlocked, the more we move up
            top_expansion = current_expansion * self.unlocked_parts
            
            # Update the lock body - stretch upward, with safe offset
            body_coords = self.canvas.coords(self.lock_body_item)
            left, body_orig_top, right, body_orig_bottom = body_coords # Assuming these are the initial coords
            # The lock body itself does not have original_segment_positions, so we work from its current or initial state.
            # For simplicity, we adjust relative to the current top_expansion.
            # The goal is that as segments separate, the main lock body might appear to stretch or shift.
            # This part needs careful review of original intent vs. current structure.
            # For now, let's assume the body top moves up with top_expansion
            new_body_top = max(5, body_orig_top - top_expansion) 
            # The bottom of the body might not change, or it might stretch. 
            # Let's assume it doesn't change relative to its initial position for now to avoid overcomplicating.
            self.canvas.coords(self.lock_body_item, left, new_body_top, right, body_orig_bottom)

            glow_padding = self.size // 8
            # Glow should also move with the body top
            # Initial glow position is relative to self.x, self.y, self.size.
            # This needs to be re-evaluated based on how self.y is defined (center or top of lock body)
            # Assuming self.y is the center of the main lock structure (excluding shackle initially)
            initial_glow_top = self.y - self.size // 2 - glow_padding * 1.5
            new_glow_top = max(5, initial_glow_top - top_expansion)
            self.canvas.coords(self.glow_item,
                self.x - self.size // 2 - glow_padding, 
                new_glow_top,
                self.x + self.size // 2 + glow_padding, 
                self.y + self.size // 2 + glow_padding) # Assuming bottom of glow does not change relative to self.y+size/2

            # Move the shackle and its fill
            if self.shackle_item and self.shackle_fill:
                # Get current coordinates
                shackle_coords = self.canvas.coords(self.shackle_item)
                shackle_fill_coords = self.canvas.coords(self.shackle_fill)
                
                # Update shackle position - move upward with lock
                if len(shackle_coords) >= 4:  # Ensure we have valid coordinates
                    x1, y1, x2, y2 = shackle_coords[:4]
                    new_y1 = max(5, y1 - top_expansion)
                    new_y2 = y2 - top_expansion
                    self.canvas.coords(self.shackle_item, x1, new_y1, x2, new_y2)
                if len(shackle_fill_coords) >= 4:  # Ensure we have valid coordinates
                    x1, y1, x2, y2 = shackle_fill_coords[:4]
                    new_y1 = max(5, y1 - top_expansion)
                    new_y2 = y2 - top_expansion
                    self.canvas.coords(self.shackle_fill, x1, new_y1, x2, new_y2)
            
            # Move the highlight
            if self.highlight_item:
                highlight_coords = self.canvas.coords(self.highlight_item)
                if len(highlight_coords) >= 4:
                    x1, y1, x2, y2 = highlight_coords
                    new_y1 = max(5, y1 - top_expansion)
                    new_y2 = y2 - top_expansion
                    self.canvas.coords(self.highlight_item, x1, new_y1, x2, new_y2)
            
            # Move the keyhole
            if self.keyhole_top and self.keyhole_bottom:
                keyhole_top_coords = self.canvas.coords(self.keyhole_top)
                keyhole_bottom_coords = self.canvas.coords(self.keyhole_bottom)
                
                if len(keyhole_top_coords) >= 4:
                    x1, y1, x2, y2 = keyhole_top_coords
                    new_y1 = max(5, y1 - top_expansion)
                    new_y2 = y2 - top_expansion
                    self.canvas.coords(self.keyhole_top, x1, new_y1, x2, new_y2)
                
                if len(keyhole_bottom_coords) >= 4:
                    x1, y1, x2, y2 = keyhole_bottom_coords
                    new_y1 = max(5, y1 - top_expansion)
                    new_y2 = y2 - top_expansion
                    self.canvas.coords(self.keyhole_bottom, x1, new_y1, x2, new_y2)
        
        # Schedule next animation step
        if self.is_active:
            # Create a unique key for each scheduled call if parameters change
            key = f'_expand_lock_cells_step_{step}' 
            new_after_id = self.canvas.after(30, lambda s=step: self._expand_lock_cells(s + 1, max_steps, total_expansion))
            self.after_ids[key] = new_after_id
    
    def _animate_diagonal_arm_release(self, arm_idx):
        """Animate the diagonal arm with a piston release effect"""
        if arm_idx < 0 or arm_idx >= len(self.diagonal_arms):
            return
            
        diag_arm = self.diagonal_arms[arm_idx]
        piston = self.arm_pistons[arm_idx]
        
        # Make arm and piston visible
        self.canvas.itemconfig(diag_arm, state='normal')
        self.canvas.itemconfig(piston, state='normal')
        
        # Get current coordinates
        arm_coords = self.canvas.coords(diag_arm)
        piston_coords = self.canvas.coords(piston)
        
        # Save original positions for the animation
        self._animate_piston_release(piston, diag_arm, 0, 10)
        
    def _animate_piston_release(self, piston, arm, step, max_steps):
        if not self.is_active or not self.canvas.winfo_exists():
            return

        if step >= max_steps:
            try:
                if self.canvas.winfo_exists():
                    self.canvas.itemconfig(arm, state='normal', fill='#AAB7B8')
                    self.canvas.itemconfig(piston, fill='#BDC3C7')
            except tk.TclError: pass
            return

        arm_coords = self.canvas.coords(arm)
        # Defensive check (ensured)
        if not arm_coords or len(arm_coords) != 4:
            logging.warning(f"_animate_piston_release: Invalid arm_coords {arm_coords} for arm {arm}. Skipping animation frame.")
            try:
                if self.canvas.winfo_exists():
                    self.canvas.itemconfig(arm, state='normal', fill='#AAB7B8')
                    self.canvas.itemconfig(piston, fill='#BDC3C7')
            except tk.TclError: pass
            return
        
        arm_start_x, arm_start_y, arm_end_x, arm_end_y = arm_coords
        
        try:
            # Calculate percentage of animation (0 to 1 to 0)
            if step < max_steps / 2:
                # First half: extend
                percent = step / (max_steps / 2)
            else:
                # Second half: retract
                percent = (max_steps - step) / (max_steps / 2)
                
            # Calculate midpoint
            mid_x = (arm_start_x + arm_end_x) / 2
            mid_y = (arm_start_y + arm_end_y) / 2
            
            # Calculate perpendicular direction (normalized)
            dx = arm_end_x - arm_start_x
            dy = arm_end_y - arm_start_y
            length = math.sqrt(dx*dx + dy*dy)
            
            if length > 0:
                # Perpendicular vector
                perp_dx = -dy / length
                perp_dy = dx / length
                
                # Create bulge effect - increased for more dramatic extension
                bulge_amount = self.size / 8 * percent  # Increased from self.size / 15
                
                # Apply bulge to midpoint of line
                new_mid_x = mid_x + perp_dx * bulge_amount
                new_mid_y = mid_y + perp_dy * bulge_amount
                
                # Update piston position
                piston_radius = self.size // 18  # Slightly larger piston
                self.canvas.coords(piston,
                    new_mid_x - piston_radius, new_mid_y - piston_radius,
                    new_mid_x + piston_radius, new_mid_y + piston_radius
                )
                
                # Highlight during extension
                highlight_color = '#ECF0F1' if percent > 0.3 else '#95A5A6'  # Highlight sooner
                self.canvas.itemconfig(piston, fill=highlight_color)
                
                # Make arm thicker during extension for more visual impact
                arm_width = 3 + int(2 * percent)  # Width varies from 3 to 5
                self.canvas.itemconfig(arm, width=arm_width)
            
            # Schedule next step
            if self.is_active:
                key = f'_animate_piston_release_p{piston}_a{arm}_s{step}'
                new_after_id = self.canvas.after(50, lambda p=piston, a=arm, s=step: self._animate_piston_release(p, a, s + 1, max_steps))
                self.after_ids[key] = new_after_id
                
        except tk.TclError:
            pass
            
    def celebrate_problem_solved(self):
        """Grand celebration animation when the entire problem is solved"""
        try:
            # Clear previous animations
            for item in self.animation_items:
                try:
                    self.canvas.delete(item)
                except tk.TclError:
                    pass
            self.animation_items = []
            
            # Display a special character formation for celebration
            self.display_character_formation("=")
            
            # Animate the shackle opening
            self._animate_shackle_opening()
            
            # Create radiating circles
            self._create_radiating_circles()
            
            # Create floating stars
            self._create_floating_stars()
            
            # Create rotating sparkles
            self._create_rotating_sparkles()
            
        except Exception as e:
            print(f"Error in celebration animation: {e}")
            
    def _animate_shackle_opening(self):
        """Animate the shackle opening upward"""
        try:
            # Hide the original shackle
            self.canvas.itemconfig(self.shackle_item, state="hidden")
            self.canvas.itemconfig(self.shackle_fill, state="hidden")
            
            # Create a new shackle that will be animated
            shackle_y_start = self.y - self.size // 2
            shackle_width = self.size // 2.5
            shackle_height = self.size // 2
            
            # The animated shackle (filled part)
            animated_shackle_fill = self.canvas.create_arc(
                self.x - shackle_width, shackle_y_start - shackle_height,
                self.x + shackle_width, shackle_y_start + shackle_height // 3,
                start=0, extent=180, 
                fill='#3C526B', outline='', tags="celebration_anim"
            )
            
            # The animated shackle (outline)
            animated_shackle = self.canvas.create_arc(
                self.x - shackle_width, shackle_y_start - shackle_height,
                self.x + shackle_width, shackle_y_start + shackle_height // 3,
                start=0, extent=180, style=tk.ARC,
                outline='#2C3E50', width=7, tags="celebration_anim"
            )
            
            self.animation_items.extend([animated_shackle_fill, animated_shackle])
            
            # Animation parameters
            max_lift = self.size // 1.5  # How high the shackle will lift
            steps = 15
            lift_per_step = max_lift / steps
            
            # Schedule the lifting animation
            self._move_shackle_up(animated_shackle_fill, animated_shackle, lift_per_step, steps)
            
        except tk.TclError:
            pass
            
    def _move_shackle_up(self, fill_item, outline_item, distance, steps_left, delay=30):
        if not self.is_active or not self.canvas.winfo_exists():
            return
        
        if steps_left <= 0:
            return
            
        try:
            # Move both items up
            self.canvas.move(fill_item, 0, -distance)
            self.canvas.move(outline_item, 0, -distance)
            
            # Schedule next movement with a slight ease-out
            next_distance = distance * 0.9  # Slow down movement for natural effect
            self.canvas.after(delay, lambda: self._move_shackle_up(
                fill_item, outline_item, next_distance, steps_left - 1, delay))
                
        except tk.TclError:
            pass
            
        if self.is_active:
            key = f'_move_shackle_up_f{fill_item}_o{outline_item}_sl{steps_left}'
            new_after_id = self.canvas.after(delay, lambda fi=fill_item, oi=outline_item, sl=steps_left: self._move_shackle_up(fi, oi, distance, sl - 1, delay))
            self.after_ids[key] = new_after_id
    
    def _create_radiating_circles(self):
        """Create expanding circles animation from the center of the lock"""
        try:
            for i in range(2):  # Create 2 circles (halved from 5, rounded down from 2.5)
                delay = i * 200  # 200ms between each circle
                self.canvas.after(delay, lambda idx=i: self._start_radiating_circle(idx))
        except tk.TclError:
            pass
            
    def _start_radiating_circle(self, index):
        """Start a single radiating circle with staggered timing"""
        try:
            if not self.canvas.winfo_exists():
                return
                
            # Create circle with initial small radius
            colors = ['#F1C40F', '#2ECC71', '#3498DB', '#9B59B6', '#E74C3C']
            color = colors[index % len(colors)]
            
            circle = self.canvas.create_oval(
                self.x - 5, self.y - 5,
                self.x + 5, self.y + 5,
                outline=color, width=2, fill='', tags="celebration_anim"
            )
            
            self.animation_items.append(circle)
            
            # Start expansion animation
            self._expand_circle(circle, 5, 30, color)
        except tk.TclError:
            pass
            
    def _expand_circle(self, circle_id, radius, max_radius, color, alpha=1.0):
        if not self.is_active or not self.canvas.winfo_exists():
            return
        
        if radius >= max_radius:
            return
        
        try:
            # Update circle size
            self.canvas.coords(
                circle_id,
                self.x - radius, self.y - radius,
                self.x + radius, self.y + radius
            )
            
            # Fade the color
            new_alpha = alpha - 0.02
            # Create a hex color with alpha by manipulating the hex values
            r = int(color[1:3], 16)
            g = int(color[3:5], 16)
            b = int(color[5:7], 16)
            
            # Simple approximation of alpha - blend with background (black)
            r = int(r * new_alpha)
            g = int(g * new_alpha)
            b = int(b * new_alpha)
            new_color = f"#{r:02x}{g:02x}{b:02x}"
            
            self.canvas.itemconfig(circle_id, outline=new_color)
            
            # Schedule next expansion
            if self.is_active:
                key = f'_expand_circle_{circle_id}_r{radius:.2f}' # Radius can be float
                new_after_id = self.canvas.after(30, lambda c_id=circle_id, r=radius, mr=max_radius, col=color, al=new_alpha: self._expand_circle(c_id, r + 2, mr, col, al))
                self.after_ids[key] = new_after_id
                
        except tk.TclError:
            pass
            
    def _create_floating_stars(self):
        """Create floating star particles"""
        try:
            for _ in range(5): # Halved from 10
                # Random parameters for each star
                angle = random.uniform(0, 2 * math.pi)
                distance = random.uniform(self.size/6, self.size/3)
                size = random.uniform(self.size/30, self.size/15)
                
                # Star position
                x = self.x + math.cos(angle) * distance
                y = self.y + math.sin(angle) * distance
                
                # Create star
                star = self._create_star(x, y, size, 5, '#FFD700')
                self.animation_items.append(star)
                
                # Animate the star
                dx = math.cos(angle) * random.uniform(1, 2)
                dy = math.sin(angle) * random.uniform(1, 2) - 1  # Slightly upward bias
                self._animate_star(star, dx, dy, 0, 40)  # Float for 40 frames
        except tk.TclError:
            pass
                
    def _create_star(self, x, y, size, points, color):
        """Create a star shape"""
        coords = []
        for i in range(points * 2):
            # Alternating inner and outer points
            radius = size if i % 2 == 0 else size * 0.4
            angle = math.pi * i / points
            px = x + radius * math.cos(angle)
            py = y + radius * math.sin(angle)
            coords.extend([px, py])
            
        return self.canvas.create_polygon(coords, fill=color, outline='', tags="celebration_anim")
        
    def _animate_star(self, star_id, dx, dy, frame, max_frames):
        if not self.is_active or not self.canvas.winfo_exists():
            return

        if frame >= max_frames:
            try:
                self.canvas.delete(star_id)
                if star_id in self.animation_items:
                    self.animation_items.remove(star_id)
            except tk.TclError:
                pass
            return
            
        try:
            # Move the star
            self.canvas.move(star_id, dx, dy)
            
            # Slight rotation effect by modifying coordinates
            coords = list(self.canvas.coords(star_id))
            center_x = sum(coords[::2]) / (len(coords) // 2)
            center_y = sum(coords[1::2]) / (len(coords) // 2)
            
            # Rotate slightly around center
            rotation_angle = math.pi / 60  # Small angle for subtle rotation
            new_coords = []
            for i in range(0, len(coords), 2):
                x, y = coords[i], coords[i+1]
                # Translate to origin, rotate, translate back
                x_shifted = x - center_x
                y_shifted = y - center_y
                x_rotated = x_shifted * math.cos(rotation_angle) - y_shifted * math.sin(rotation_angle)
                y_rotated = x_shifted * math.sin(rotation_angle) + y_shifted * math.cos(rotation_angle)
                new_coords.extend([x_rotated + center_x, y_rotated + center_y])
                
            self.canvas.coords(star_id, *new_coords)
            
            # Fade effect as it rises
            if frame > max_frames * 0.7:  # Start fading after 70% of animation
                alpha = 1.0 - (frame - max_frames * 0.7) / (max_frames * 0.3)
                # Hacky way to simulate alpha by manipulating fill color toward black
                r = int(255 * alpha)
                g = int(215 * alpha)
                b = int(0 * alpha)
                fade_color = f"#{r:02x}{g:02x}{b:02x}"
                self.canvas.itemconfig(star_id, fill=fade_color)
            
            # Next frame
            if self.is_active:
                key = f'_animate_star_{star_id}_f{frame}'
                new_after_id = self.canvas.after(30, lambda s_id=star_id, x=dx, y=dy, f=frame: self._animate_star(s_id, x, y, f + 1, max_frames))
                self.after_ids[key] = new_after_id
                
        except tk.TclError:
            pass
            
    def _create_rotating_sparkles(self):
        """Create sparkles that rotate around the lock"""
        try:
            # Create orbit particles
            for i in range(10): # Halved from 20
                angle = i * (2 * math.pi / 10)  # Adjusted denominator to new count
                radius = self.size * 0.8
                x = self.x + radius * math.cos(angle)
                y = self.y + radius * math.sin(angle)
                size = random.uniform(2, 4)
                
                # Create sparkle
                colors = ['#F1C40F', '#F39C12', '#FFEB3B', '#FFC107', '#FFFFFF']
                sparkle = self.canvas.create_oval(
                    x - size, y - size,
                    x + size, y + size,
                    fill=random.choice(colors), outline='', tags="celebration_anim"
                )
                self.animation_items.append(sparkle)
                
                # Start orbit animation
                self._orbit_sparkle(sparkle, angle, radius, 0, 120)  # 120 frames
        except tk.TclError:
            pass
                
    def _orbit_sparkle(self, sparkle_id, angle, radius, frame, max_frames):
        if not self.is_active or not self.canvas.winfo_exists():
            return

        if frame >= max_frames:
            try:
                self.canvas.delete(sparkle_id)
                if sparkle_id in self.animation_items:
                    self.animation_items.remove(sparkle_id)
            except tk.TclError:
                pass
            return
            
        try:
            # Update orbit position
            orbit_speed = 2 * math.pi / 120  # Complete orbit in 120 frames
            new_angle = angle + orbit_speed
            x = self.x + radius * math.cos(new_angle)
            y = self.y + radius * math.sin(new_angle)
            
            # Get current size from coordinates
            coords = self.canvas.coords(sparkle_id)
            size = (coords[2] - coords[0]) / 2
            
            # Update position
            self.canvas.coords(
                sparkle_id,
                x - size, y - size,
                x + size, y + size
            )
            
            # Pulsate size
            pulse_factor = 0.8 + 0.4 * math.sin(frame * math.pi / 10)  # Gentle pulsating
            new_size = size * pulse_factor
            self.canvas.coords(
                sparkle_id,
                x - new_size, y - new_size,
                x + new_size, y + new_size
            )
            
            # Next frame
            if self.is_active:
                key = f'_orbit_sparkle_{sparkle_id}_f{frame}'
                new_after_id = self.canvas.after(50, lambda s_id=sparkle_id, ang=new_angle, rad=radius, f=frame: self._orbit_sparkle(s_id, ang, rad, f + 1, max_frames))
                self.after_ids[key] = new_after_id
                
        except tk.TclError:
            pass

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
        
        # Adjust for taller lock body
        body_bottom = self.y + self.size // 2 + self.size // 3
        segment_height = (body_bottom - (self.y - self.size // 2)) // self.total_parts
        
        center_x = self.x
        center_y = self.y - self.size // 2 + (part_index + 0.5) * segment_height
        
        sparkle_colors = ['#F1C40F', '#F39C12', '#FFEB3B', '#FFC107', '#FFFFFF']  # Yellow/gold colors + white
        
        # Doubled number of sparkles 
        for i in range(4):  # Doubled from 2 (originally 4 -> 2 -> 4)
            angle = random.uniform(0, 2 * math.pi)
            # Sparkles should emanate from the segment's center
            distance = random.uniform(2, 10)  # Initial distance from center
            particle_size = random.uniform(1.5, 4)  # Increased size for visibility
            
            x = center_x + math.cos(angle) * distance
            y = center_y + math.sin(angle) * distance
            is_pulsating = (i % 10 == 0) # 1 in 10 pulsates (though with only 4 particles, only the first would)
                                         # For more visual variety with small numbers, consider i % 2 or similar if desired
            
            original_color_for_sparkle = random.choice(sparkle_colors)
            sparkle = self.canvas.create_oval(
                x - particle_size, y - particle_size, 
                x + particle_size, y + particle_size,
                fill=original_color_for_sparkle, outline='', tags="lock_visual" # Changed tag to lock_visual from celebration_anim
            )
            sparkle_points.append({
                'id': sparkle,
                'dx': math.cos(angle) * random.uniform(1.5, 3),  # Faster movement
                'dy': math.sin(angle) * random.uniform(1.5, 3),
                'life': random.randint(20, 30),  # Longer lifespan
                'original_size': particle_size,
                'current_size': particle_size, # Added current_size for pulsation
                'shrink_rate': particle_size / random.randint(20, 30),
                'is_pulsating': is_pulsating,
                'original_color': original_color_for_sparkle,
                'pulse_phase': random.uniform(0, 2 * math.pi) # For pulsation offset
            })
            
        self._animate_sparkles(sparkle_points)
        
    def _animate_sparkles(self, sparkles):
        """Animate the sparkle particles with size reduction for fade effect"""
        active_sparkles = False
        for sparkle_data in sparkles[:]:  # Iterate over a copy for safe removal
            if sparkle_data['life'] <= 0 or sparkle_data['current_size'] <= 0:
                try:
                    self.canvas.delete(sparkle_data['id'])
                except tk.TclError:
                    pass  # Item might already be deleted if canvas is closing
                sparkles.remove(sparkle_data)
                continue
                
            try:
                # Move the sparkle
                self.canvas.move(sparkle_data['id'], sparkle_data['dx'], sparkle_data['dy'])
                
                # Shrink the sparkle for fade-out effect (base shrinkage)
                sparkle_data['current_size'] -= sparkle_data['shrink_rate']
                current_color_to_set = sparkle_data['original_color']
                size_to_draw = sparkle_data['current_size']

                if sparkle_data['is_pulsating'] and sparkle_data['current_size'] > 0:
                    sparkle_data['pulse_phase'] += 0.3 # Speed of pulse
                    size_pulse_amplitude = 0.5 
                    brightness_pulse_amplitude = 0.6

                    # Apply pulsation to size, ensuring it doesn't go below shrink rate
                    pulsed_size_modifier = (1.0 + size_pulse_amplitude * math.sin(sparkle_data['pulse_phase']))
                    size_to_draw = sparkle_data['current_size'] * pulsed_size_modifier
                    size_to_draw = max(0, size_to_draw) # Ensure not negative

                    brightness_factor = 1.0 + brightness_pulse_amplitude * math.sin(sparkle_data['pulse_phase'] + math.pi/2)
                    current_color_to_set = self._brighten_color(sparkle_data['original_color'], brightness_factor, ensure_visible=True)
                
                if size_to_draw > 0:
                    item_id = sparkle_data['id']
                    current_coords = self.canvas.coords(item_id)
                    if len(current_coords) == 4:  # Ensure we have valid coordinates
                        center_x = (current_coords[0] + current_coords[2]) / 2
                        center_y = (current_coords[1] + current_coords[3]) / 2
                        self.canvas.coords(
                            item_id,
                            center_x - size_to_draw, center_y - size_to_draw,
                            center_x + size_to_draw, center_y + size_to_draw
                        )
                        self.canvas.itemconfig(item_id, fill=current_color_to_set)
                    else: # Degenerate sparkle, remove
                        sparkle_data['life'] = 0 
                else: # Size is zero or less, mark for removal
                    sparkle_data['life'] = 0

            except tk.TclError:
                pass  # Item might already be deleted
                
            sparkle_data['life'] -= 1
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
                
        # Also make original shackle visible if it was hidden during celebration
        try:
            if self.shackle_item:
                self.canvas.itemconfig(self.shackle_item, state="normal")
            if hasattr(self, 'shackle_fill') and self.shackle_fill:
                self.canvas.itemconfig(self.shackle_fill, state="normal")
        except tk.TclError:
            pass
            
        # Clean up any celebration animations
        self._clear_celebration_animations()
    
    def _clear_celebration_animations(self):
        """Clear any celebration animations"""
        try:
            self.canvas.delete("celebration_anim")
            self.canvas.delete("lock_wave")  # Clear wave particles
            for item in self.animation_items:
                try:
                    self.canvas.delete(item)
                except tk.TclError:
                    pass
            self.animation_items = []
        except tk.TclError:
            pass
    
    def clear_visuals(self):
        """Clear all visual elements of the lock and its animations from the canvas."""
        self.is_active = False # SET TO FALSE FIRST
        
        # Cancel all scheduled .after() calls for this instance
        for after_id_key in list(self.after_ids.keys()): # Iterate over keys copy for safe modification
            after_id_val = self.after_ids.pop(after_id_key, None) # Use pop to remove and get value
            if after_id_val:
                try:
                    self.canvas.after_cancel(after_id_val)
                except Exception as e:
                    logging.warning(f"Error cancelling after_id {after_id_val} for key {after_id_key}: {e}")
        # self.after_ids should be empty now due to pop, but clear just in case.
        self.after_ids.clear()

        # Delete general animation items
        try:
            # More robust way using the common tag for all lock visuals
            self.canvas.delete("lock_visual")
            self.canvas.delete("celebration_anim")
            self.canvas.delete("lock_particle")
            self.canvas.delete("lock_wave")  # Clear wave particles
            
            # Reset instance variables
            self.lock_body_item = None
            self.shackle_item = None
            self.lock_parts_items = []
            self.animation_items = []
            
        except tk.TclError:
            # Handle cases where canvas/items might already be gone
            pass
    
    def react_to_character_reveal(self, character):
        """Show character formation when user reveals a character in the solution"""
        if not self.canvas.winfo_exists():
            return
            
        # Only react to significant characters
        if character and character in "0123456789+-=xX":
            # Display the character formation
            self.display_character_formation(character)