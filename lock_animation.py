import tkinter as tk
import random
import math
import time
import logging
from typing import Dict, List, Tuple, Optional, Any

class LockAnimationConfig:
    """Configuration class for lock animation settings"""
    
    # Performance settings
    MAX_PARTICLES = 50
    MAX_SPARKLES = 30
    ANIMATION_FPS = 30
    FRAME_DELAY = 33  # ~30 FPS
    
    # Visual settings
    DEFAULT_SIZE = 100
    PARTICLE_LIFETIME = 60  # frames
    SPARKLE_LIFETIME = 45   # frames
    
    # Animation timing
    UNLOCK_FLASH_DURATION = 150  # ms
    CELEBRATION_DURATION = 3000  # ms
    TRANSITION_DURATION = 500    # ms
    
    # Level themes with improved color palettes
    LEVEL_THEMES = {
        "Easy": {
            "locked": ['#E74C3C', '#E57E31', '#D35400', '#C0392B'],
            "unlocked": ['#27AE60', '#2ECC71', '#58D68D', '#82E0AA'],
            "particles": ['#FF6B6B', '#FF8E53', '#FF6B35'],
            "effects": ['#FFD93D', '#6BCF7F', '#4ECDC4']
        },
        "Medium": {
            "locked": ['#3498DB', '#2980B9', '#1F618D', '#154360'],
            "unlocked": ['#F1C40F', '#F39C12', '#F5B041', '#F8C471'],
            "particles": ['#74B9FF', '#0984E3', '#6C5CE7'],
            "effects": ['#FDCB6E', '#E17055', '#00B894']
        },
        "Division": {
            "locked": ['#9B59B6', '#8E44AD', '#7D3C98', '#6C3483'],
            "unlocked": ['#1ABC9C', '#16A085', '#48C9B0', '#76D7C4'],
            "particles": ['#A29BFE', '#6C5CE7', '#FD79A8'],
            "effects": ['#00CEC9', '#55A3FF', '#FF7675']
        }
    }

class ParticleSystem:
    """Manages particle effects for the lock animation"""
    
    def __init__(self, canvas: tk.Canvas, config: LockAnimationConfig):
        self.canvas = canvas
        self.config = config
        self.particles: List[Dict[str, Any]] = []
        self.active = False
        self.last_update = time.time()
        
    def add_particle(self, x: float, y: float, particle_type: str = "orbital", **kwargs) -> None:
        """Add a new particle to the system"""
        if len(self.particles) >= self.config.MAX_PARTICLES:
            # Remove oldest particle
            self._remove_oldest_particle()
            
        particle = {
            'x': x,
            'y': y,
            'type': particle_type,
            'life': kwargs.get('life', self.config.PARTICLE_LIFETIME),
            'max_life': kwargs.get('life', self.config.PARTICLE_LIFETIME),
            'size': kwargs.get('size', 3),
            'color': kwargs.get('color', '#FFFFFF'),
            'velocity_x': kwargs.get('velocity_x', 0),
            'velocity_y': kwargs.get('velocity_y', 0),
            'angle': kwargs.get('angle', 0),
            'angular_velocity': kwargs.get('angular_velocity', 0),
            'radius': kwargs.get('radius', 0),
            'id': None,
            'created_time': time.time()
        }
        
        # Create canvas item
        try:
            particle['id'] = self.canvas.create_oval(
                x - particle['size'], y - particle['size'],
                x + particle['size'], y + particle['size'],
                fill=particle['color'], outline='', tags="lock_particle"
            )
            self.particles.append(particle)
        except tk.TclError:
            # Canvas might be destroyed
            pass
    
    def update(self) -> None:
        """Update all particles"""
        if not self.active or not self.canvas.winfo_exists():
            return
            
        current_time = time.time()
        dt = current_time - self.last_update
        self.last_update = current_time
        
        # Update particles in reverse order for safe removal
        for i in range(len(self.particles) - 1, -1, -1):
            particle = self.particles[i]
            
            # Update particle based on type
            if particle['type'] == 'orbital':
                self._update_orbital_particle(particle, dt)
            elif particle['type'] == 'explosion':
                self._update_explosion_particle(particle, dt)
            elif particle['type'] == 'wave':
                self._update_wave_particle(particle, dt)
            
            # Update life and remove if dead
            particle['life'] -= 1
            if particle['life'] <= 0 or not self._is_particle_valid(particle):
                self._remove_particle(i)
    
    def _update_orbital_particle(self, particle: Dict[str, Any], dt: float) -> None:
        """Update orbital particle movement"""
        particle['angle'] += particle['angular_velocity'] * dt
        
        # Calculate new position
        new_x = particle['x'] + math.cos(particle['angle']) * particle['radius']
        new_y = particle['y'] + math.sin(particle['angle']) * particle['radius']
        
        # Update canvas item
        try:
            if particle['id']:
                self.canvas.coords(
                    particle['id'],
                    new_x - particle['size'], new_y - particle['size'],
                    new_x + particle['size'], new_y + particle['size']
                )
                
                # Fade out over time
                alpha = particle['life'] / particle['max_life']
                faded_color = self._apply_alpha(particle['color'], alpha)
                self.canvas.itemconfig(particle['id'], fill=faded_color)
        except tk.TclError:
            particle['life'] = 0  # Mark for removal
    
    def _update_explosion_particle(self, particle: Dict[str, Any], dt: float) -> None:
        """Update explosion particle movement"""
        # Move particle
        particle['x'] += particle['velocity_x'] * dt * 60  # Scale for frame rate
        particle['y'] += particle['velocity_y'] * dt * 60
        
        # Apply gravity
        particle['velocity_y'] += 0.5 * dt * 60
        
        # Update canvas item
        try:
            if particle['id']:
                self.canvas.coords(
                    particle['id'],
                    particle['x'] - particle['size'], particle['y'] - particle['size'],
                    particle['x'] + particle['size'], particle['y'] + particle['size']
                )
                
                # Fade and shrink over time
                progress = 1 - (particle['life'] / particle['max_life'])
                alpha = 1 - progress
                size_factor = 1 - progress * 0.5
                
                faded_color = self._apply_alpha(particle['color'], alpha)
                self.canvas.itemconfig(particle['id'], fill=faded_color)
                
                # Update size
                new_size = particle['size'] * size_factor
                self.canvas.coords(
                    particle['id'],
                    particle['x'] - new_size, particle['y'] - new_size,
                    particle['x'] + new_size, particle['y'] + new_size
                )
        except tk.TclError:
            particle['life'] = 0
    
    def _update_wave_particle(self, particle: Dict[str, Any], dt: float) -> None:
        """Update wave particle movement"""
        # Expand radius
        particle['radius'] += particle['velocity_x'] * dt * 60
        
        # Update position in wave
        wave_x = particle['x'] + math.cos(particle['angle']) * particle['radius']
        wave_y = particle['y'] + math.sin(particle['angle']) * particle['radius']
        
        try:
            if particle['id']:
                self.canvas.coords(
                    particle['id'],
                    wave_x - particle['size'], wave_y - particle['size'],
                    wave_x + particle['size'], wave_y + particle['size']
                )
                
                # Fade out as wave expands
                alpha = particle['life'] / particle['max_life']
                faded_color = self._apply_alpha(particle['color'], alpha)
                self.canvas.itemconfig(particle['id'], fill=faded_color)
        except tk.TclError:
            particle['life'] = 0
    
    def _remove_particle(self, index: int) -> None:
        """Remove particle at given index"""
        if 0 <= index < len(self.particles):
            particle = self.particles[index]
            try:
                if particle['id']:
                    self.canvas.delete(particle['id'])
            except tk.TclError:
                pass
            del self.particles[index]
    
    def _remove_oldest_particle(self) -> None:
        """Remove the oldest particle to make room for new ones"""
        if self.particles:
            oldest_index = 0
            oldest_time = self.particles[0]['created_time']
            
            for i, particle in enumerate(self.particles):
                if particle['created_time'] < oldest_time:
                    oldest_time = particle['created_time']
                    oldest_index = i
            
            self._remove_particle(oldest_index)
    
    def _is_particle_valid(self, particle: Dict[str, Any]) -> bool:
        """Check if particle is still valid"""
        try:
            if particle['id']:
                coords = self.canvas.coords(particle['id'])
                return len(coords) == 4
        except tk.TclError:
            pass
        return False
    
    def _apply_alpha(self, color: str, alpha: float) -> str:
        """Apply alpha transparency to a color"""
        try:
            # Extract RGB components
            r = int(color[1:3], 16)
            g = int(color[3:5], 16)
            b = int(color[5:7], 16)
            
            # Apply alpha
            r = int(r * alpha)
            g = int(g * alpha)
            b = int(b * alpha)
            
            return f"#{r:02x}{g:02x}{b:02x}"
        except (ValueError, IndexError):
            return color
    
    def clear_all(self) -> None:
        """Clear all particles"""
        for particle in self.particles:
            try:
                if particle['id']:
                    self.canvas.delete(particle['id'])
            except tk.TclError:
                pass
        self.particles.clear()
    
    def start(self) -> None:
        """Start particle system"""
        self.active = True
        self.last_update = time.time()
    
    def stop(self) -> None:
        """Stop particle system"""
        self.active = False

class LockVisuals:
    """Manages the visual components of the lock"""
    
    def __init__(self, canvas: tk.Canvas, x: float, y: float, size: float, config: LockAnimationConfig):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.size = size
        self.config = config
        
        # Visual components
        self.lock_body_item = None
        self.shackle_item = None
        self.shackle_fill = None
        self.glow_item = None
        self.highlight_item = None
        self.keyhole_top = None
        self.keyhole_bottom = None
        self.lock_parts_items: List[int] = []
        self.diagonal_arms: List[int] = []
        
        # State
        self.original_segment_positions: List[Tuple[float, float]] = []
        
    def create_lock_components(self, level_name: str) -> None:
        """Create all visual components of the lock"""
        try:
            self._create_glow_effect()
            self._create_lock_body()
            self._create_shackle()
            self._create_keyhole()
            self._create_lock_segments(level_name)
        except tk.TclError as e:
            logging.error(f"Error creating lock components: {e}")
    
    def _create_glow_effect(self) -> None:
        """Create subtle glow behind the lock"""
        glow_padding = max(self.size // 8, 5)
        try:
            self.glow_item = self.canvas.create_oval(
                self.x - self.size // 2 - glow_padding,
                self.y - self.size // 2 - glow_padding * 1.5,
                self.x + self.size // 2 + glow_padding,
                self.y + self.size // 2 + glow_padding,
                fill='#1a2533', outline='#1a2533', tags="lock_visual"
            )
        except tk.TclError:
            pass
    
    def _create_lock_body(self) -> None:
        """Create the main lock body"""
        try:
            # Main body rectangle
            self.lock_body_item = self.canvas.create_rectangle(
                self.x - self.size // 2, self.y - self.size // 2,
                self.x + self.size // 2, self.y + self.size // 2 + self.size // 3,
                fill='#34495E', outline='#2C3E50', width=max(2, self.size // 25), 
                tags="lock_visual"
            )
            
            # Metallic highlight
            highlight_height = max(self.size // 10, 3)
            self.highlight_item = self.canvas.create_rectangle(
                self.x - self.size // 2 + 5, self.y - self.size // 2 + 5,
                self.x + self.size // 2 - 5, self.y - self.size // 2 + highlight_height,
                fill='#4A6A8F', outline='', tags="lock_visual"
            )
        except tk.TclError:
            pass
    
    def _create_shackle(self) -> None:
        """Create the U-shaped shackle"""
        try:
            shackle_y_start = self.y - self.size // 2
            shackle_width = self.size // 2.5
            shackle_height = self.size // 2
            
            # Filled portion for better appearance
            self.shackle_fill = self.canvas.create_arc(
                self.x - shackle_width, shackle_y_start - shackle_height,
                self.x + shackle_width, shackle_y_start + shackle_height // 3,
                start=0, extent=180,
                fill='#3C526B', outline='', tags="lock_visual"
            )
            
            # Main shackle outline
            self.shackle_item = self.canvas.create_arc(
                self.x - shackle_width, shackle_y_start - shackle_height,
                self.x + shackle_width, shackle_y_start + shackle_height // 3,
                start=0, extent=180, style=tk.ARC,
                outline='#2C3E50', width=max(3, self.size // 15), tags="lock_visual"
            )
        except tk.TclError:
            pass
    
    def _create_keyhole(self) -> None:
        """Create the keyhole for realism"""
        try:
            keyhole_radius = max(self.size // 12, 2)
            
            # Circular top part
            self.keyhole_top = self.canvas.create_oval(
                self.x - keyhole_radius,
                self.y + self.size // 6,
                self.x + keyhole_radius,
                self.y + self.size // 6 + keyhole_radius * 2,
                fill='#1C2833', outline='#17202A', width=1, tags="lock_visual"
            )
            
            # Rectangular bottom part
            self.keyhole_bottom = self.canvas.create_rectangle(
                self.x - keyhole_radius // 2,
                self.y + self.size // 6 + keyhole_radius * 2,
                self.x + keyhole_radius // 2,
                self.y + self.size // 6 + keyhole_radius * 3.5,
                fill='#1C2833', outline='#17202A', width=1, tags="lock_visual"
            )
        except tk.TclError:
            pass
    
    def _create_lock_segments(self, level_name: str) -> None:
        """Create the internal lock segments"""
        try:
            # Get color theme
            theme = self.config.LEVEL_THEMES.get(level_name, self.config.LEVEL_THEMES["Easy"])
            segment_colors = theme["locked"]
            
            # Calculate segment positions
            body_top_y = self.y - self.size // 2
            body_bottom_y = self.y + self.size // 2 + self.size // 3
            total_height = body_bottom_y - body_top_y
            segment_height = total_height / 4  # 4 segments
            segment_padding = max(segment_height * 0.05, 2)
            
            x_left = self.x - self.size // 3
            x_right = self.x + self.size // 3
            
            for i in range(4):  # 4 segments
                y_top = body_top_y + (i * segment_height) + segment_padding
                y_bottom = body_top_y + ((i + 1) * segment_height) - segment_padding
                
                color_idx = i % len(segment_colors)
                base_color = segment_colors[color_idx]
                outline_color = self._darken_color(base_color, 0.8)
                
                # Create main segment
                segment = self.canvas.create_rectangle(
                    x_left, y_top, x_right, y_bottom,
                    fill=base_color, outline=outline_color, 
                    width=max(1, self.size // 50), tags="lock_visual"
                )
                self.lock_parts_items.append(segment)
                
                # Store original position
                self.original_segment_positions.append((y_top, y_bottom))
                
                # Add 3D shading effects
                self._add_segment_shading(x_left, x_right, y_top, y_bottom, base_color, i)
                
        except tk.TclError:
            pass
    
    def _add_segment_shading(self, x_left: float, x_right: float, y_top: float, 
                           y_bottom: float, base_color: str, segment_index: int) -> None:
        """Add 3D shading effects to a segment"""
        try:
            # Top highlight
            self.canvas.create_line(
                x_left + 2, y_top + 2, x_right - 2, y_top + 2,
                fill=self._brighten_color(base_color, 1.2), 
                width=max(1, self.size // 50), tags="lock_visual"
            )
            
            # Left highlight
            self.canvas.create_line(
                x_left + 2, y_top + 2, x_left + 2, y_bottom - 2,
                fill=self._brighten_color(base_color, 1.1), 
                width=max(1, self.size // 60), tags="lock_visual"
            )
            
            # Bottom shadow
            self.canvas.create_line(
                x_left + 2, y_bottom - 2, x_right - 2, y_bottom - 2,
                fill=self._darken_color(base_color, 0.7), 
                width=max(1, self.size // 50), tags="lock_visual"
            )
            
            # Right shadow
            self.canvas.create_line(
                x_right - 2, y_top + 2, x_right - 2, y_bottom - 2,
                fill=self._darken_color(base_color, 0.8), 
                width=max(1, self.size // 60), tags="lock_visual"
            )
        except tk.TclError:
            pass
    
    def _brighten_color(self, hex_color: str, factor: float = 1.3) -> str:
        """Brighten a hex color by a factor"""
        try:
            r = int(hex_color[1:3], 16)
            g = int(hex_color[3:5], 16)
            b = int(hex_color[5:7], 16)
            
            r = min(255, int(r * factor))
            g = min(255, int(g * factor))
            b = min(255, int(b * factor))
            
            return f"#{r:02x}{g:02x}{b:02x}"
        except (ValueError, IndexError):
            return hex_color
    
    def _darken_color(self, hex_color: str, factor: float = 0.7) -> str:
        """Darken a hex color by a factor"""
        try:
            r = int(hex_color[1:3], 16)
            g = int(hex_color[3:5], 16)
            b = int(hex_color[5:7], 16)
            
            r = max(0, int(r * factor))
            g = max(0, int(g * factor))
            b = max(0, int(b * factor))
            
            return f"#{r:02x}{g:02x}{b:02x}"
        except (ValueError, IndexError):
            return hex_color
    
    def update_segment_color(self, segment_index: int, color: str, outline_color: str) -> None:
        """Update the color of a specific segment"""
        if 0 <= segment_index < len(self.lock_parts_items):
            try:
                self.canvas.itemconfig(
                    self.lock_parts_items[segment_index],
                    fill=color, outline=outline_color
                )
            except tk.TclError:
                pass
    
    def clear_all(self) -> None:
        """Clear all visual components"""
        try:
            self.canvas.delete("lock_visual")
        except tk.TclError:
            pass
        
        # Reset component references
        self.lock_body_item = None
        self.shackle_item = None
        self.shackle_fill = None
        self.glow_item = None
        self.highlight_item = None
        self.keyhole_top = None
        self.keyhole_bottom = None
        self.lock_parts_items.clear()
        self.diagonal_arms.clear()
        self.original_segment_positions.clear()

class LockAnimation:
    """Enhanced lock animation with improved performance and organization"""
    
    def __init__(self, canvas: tk.Canvas, x: float, y: float, size: float = 100, level_name: str = "Easy"):
        # Core properties
        self.canvas = canvas
        self.x = x
        self.y = y
        self.size = max(size, 50)  # Minimum size for visibility
        self.level_name = level_name if level_name in LockAnimationConfig.LEVEL_THEMES else "Easy"
        
        # Configuration
        self.config = LockAnimationConfig()
        
        # State management
        self.is_active = True
        self.unlocked_parts = 0
        self.total_parts = 4
        self.is_fully_unlocked = False
        
        # Component systems
        self.visuals = LockVisuals(canvas, x, y, self.size, self.config)
        self.particle_system = ParticleSystem(canvas, self.config)
        
        # Animation management
        self.after_ids: Dict[str, Any] = {}
        self.animation_frame = 0
        self.last_frame_time = time.time()
        
        # Performance monitoring
        self.performance_stats = {
            'frame_count': 0,
            'avg_frame_time': 0,
            'particle_count': 0
        }
        
        # Initialize components
        self._initialize()
    
    def _initialize(self) -> None:
        """Initialize the lock animation"""
        try:
            # Create visual components
            self.visuals.create_lock_components(self.level_name)
            
            # Start particle system
            self.particle_system.start()
            
            # Create initial orbital particles
            self._create_initial_particles()
            
            # Start main animation loop
            self._start_animation_loop()
            
            logging.info(f"Lock animation initialized for level {self.level_name} at size {self.size}")
            
        except Exception as e:
            logging.error(f"Error initializing lock animation: {e}")
            self.is_active = False
    
    def _create_initial_particles(self) -> None:
        """Create initial orbital particles around the lock"""
        if not self.is_active:
            return
            
        theme = self.config.LEVEL_THEMES[self.level_name]
        particle_colors = theme["particles"]
        
        # Create orbital particles
        num_particles = min(8, self.config.MAX_PARTICLES // 2)
        for i in range(num_particles):
            angle = (2 * math.pi * i) / num_particles
            radius = self.size * 0.8
            color = random.choice(particle_colors)
            
            self.particle_system.add_particle(
                self.x, self.y,
                particle_type="orbital",
                angle=angle,
                angular_velocity=0.02 + random.uniform(-0.01, 0.01),
                radius=radius,
                size=random.uniform(2, 4),
                color=color,
                life=self.config.PARTICLE_LIFETIME * 2  # Longer life for orbital particles
            )
    
    def _start_animation_loop(self) -> None:
        """Start the main animation loop with frame rate limiting"""
        if not self.is_active or not self.canvas.winfo_exists():
            return
            
        current_time = time.time()
        frame_time = current_time - self.last_frame_time
        
        # Frame rate limiting
        if frame_time >= (1.0 / self.config.ANIMATION_FPS):
            self._update_animation()
            self.last_frame_time = current_time
            self.animation_frame += 1
            
            # Update performance stats
            self._update_performance_stats(frame_time)
        
        # Schedule next frame
        self.after_ids['main_loop'] = self.canvas.after(
            self.config.FRAME_DELAY, 
            self._start_animation_loop
        )
    
    def _update_animation(self) -> None:
        """Update all animation components"""
        try:
            # Update particle system
            self.particle_system.update()
            
            # Add new particles occasionally for orbital effect
            if self.animation_frame % 60 == 0:  # Every 2 seconds at 30 FPS
                self._add_ambient_particle()
                
        except Exception as e:
            logging.error(f"Error updating animation: {e}")
    
    def _add_ambient_particle(self) -> None:
        """Add ambient particles for visual interest"""
        if len(self.particle_system.particles) < self.config.MAX_PARTICLES // 2:
            theme = self.config.LEVEL_THEMES[self.level_name]
            color = random.choice(theme["particles"])
            
            angle = random.uniform(0, 2 * math.pi)
            radius = self.size * random.uniform(0.6, 1.2)
            
            self.particle_system.add_particle(
                self.x, self.y,
                particle_type="orbital",
                angle=angle,
                angular_velocity=random.uniform(0.01, 0.03),
                radius=radius,
                size=random.uniform(1, 3),
                color=color,
                life=self.config.PARTICLE_LIFETIME
            )
    
    def _update_performance_stats(self, frame_time: float) -> None:
        """Update performance monitoring statistics"""
        self.performance_stats['frame_count'] += 1
        
        # Update average frame time (rolling average)
        alpha = 0.1  # Smoothing factor
        self.performance_stats['avg_frame_time'] = (
            alpha * frame_time + 
            (1 - alpha) * self.performance_stats['avg_frame_time']
        )
        
        self.performance_stats['particle_count'] = len(self.particle_system.particles)
        
        # Log performance issues
        if frame_time > 0.05:  # More than 50ms per frame
            logging.warning(f"Lock animation frame time high: {frame_time:.3f}s")
    
    def unlock_next_part(self) -> None:
        """Unlock the next part of the lock with enhanced effects"""
        if not self.is_active or self.unlocked_parts >= self.total_parts:
            return
            
        try:
            current_part_idx = self.unlocked_parts
            
            # Get theme colors
            theme = self.config.LEVEL_THEMES[self.level_name]
            unlock_colors = theme["unlocked"]
            effect_colors = theme["effects"]
            
            # Flash effect
            self._create_unlock_flash(current_part_idx)
            
            # Update segment color after flash
            self.canvas.after(
                self.config.UNLOCK_FLASH_DURATION,
                lambda: self._apply_unlock_color(current_part_idx, unlock_colors)
            )
            
            # Create particle effects
            self._create_unlock_effects(current_part_idx, effect_colors)
            
            # Update unlock count
            self.unlocked_parts += 1
            
            # Check if fully unlocked
            if self.unlocked_parts >= self.total_parts:
                self.canvas.after(500, self._trigger_full_unlock_celebration)
                
            logging.info(f"Lock part {current_part_idx + 1} unlocked ({self.unlocked_parts}/{self.total_parts})")
            
        except Exception as e:
            logging.error(f"Error unlocking part: {e}")
    
    def _create_unlock_flash(self, part_index: int) -> None:
        """Create a flash effect when unlocking a part"""
        if 0 <= part_index < len(self.visuals.lock_parts_items):
            try:
                # Flash white briefly
                self.visuals.update_segment_color(part_index, '#FFFFFF', '#FFFFFF')
            except Exception as e:
                logging.error(f"Error creating unlock flash: {e}")
    
    def _apply_unlock_color(self, part_index: int, unlock_colors: List[str]) -> None:
        """Apply the unlock color to a segment"""
        if 0 <= part_index < len(unlock_colors):
            try:
                color = unlock_colors[part_index % len(unlock_colors)]
                outline_color = self.visuals._darken_color(color, 0.8)
                self.visuals.update_segment_color(part_index, color, outline_color)
            except Exception as e:
                logging.error(f"Error applying unlock color: {e}")
    
    def _create_unlock_effects(self, part_index: int, effect_colors: List[str]) -> None:
        """Create particle effects for unlocking"""
        if not (0 <= part_index < len(self.visuals.original_segment_positions)):
            return
            
        try:
            # Get segment center
            y_top, y_bottom = self.visuals.original_segment_positions[part_index]
            center_y = (y_top + y_bottom) / 2
            
            # Create explosion particles
            num_particles = 12
            for i in range(num_particles):
                angle = (2 * math.pi * i) / num_particles
                speed = random.uniform(2, 5)
                color = random.choice(effect_colors)
                
                self.particle_system.add_particle(
                    self.x, center_y,
                    particle_type="explosion",
                    velocity_x=math.cos(angle) * speed,
                    velocity_y=math.sin(angle) * speed,
                    size=random.uniform(3, 6),
                    color=color,
                    life=self.config.PARTICLE_LIFETIME // 2
                )
            
            # Create wave effect
            self._create_wave_effect(center_y, effect_colors[0])
            
        except Exception as e:
            logging.error(f"Error creating unlock effects: {e}")
    
    def _create_wave_effect(self, center_y: float, color: str) -> None:
        """Create a circular wave effect"""
        try:
            num_wave_particles = 16
            for i in range(num_wave_particles):
                angle = (2 * math.pi * i) / num_wave_particles
                
                self.particle_system.add_particle(
                    self.x, center_y,
                    particle_type="wave",
                    angle=angle,
                    velocity_x=3,  # Expansion speed
                    radius=10,     # Starting radius
                    size=2,
                    color=color,
                    life=self.config.PARTICLE_LIFETIME // 3
                )
        except Exception as e:
            logging.error(f"Error creating wave effect: {e}")
    
    def _trigger_full_unlock_celebration(self) -> None:
        """Trigger celebration when lock is fully unlocked"""
        if not self.is_active:
            return
            
        try:
            self.is_fully_unlocked = True
            
            # Create massive particle explosion
            theme = self.config.LEVEL_THEMES[self.level_name]
            all_colors = theme["unlocked"] + theme["effects"] + theme["particles"]
            
            # Central explosion
            num_particles = 30
            for i in range(num_particles):
                angle = random.uniform(0, 2 * math.pi)
                speed = random.uniform(3, 8)
                color = random.choice(all_colors)
                
                self.particle_system.add_particle(
                    self.x, self.y,
                    particle_type="explosion",
                    velocity_x=math.cos(angle) * speed,
                    velocity_y=math.sin(angle) * speed,
                    size=random.uniform(4, 8),
                    color=color,
                    life=self.config.PARTICLE_LIFETIME
                )
            
            # Multiple wave effects
            for wave in range(3):
                self.canvas.after(
                    wave * 200,
                    lambda w=wave: self._create_celebration_wave(w, all_colors)
                )
            
            logging.info("Lock fully unlocked - celebration triggered")
            
        except Exception as e:
            logging.error(f"Error triggering celebration: {e}")
    
    def _create_celebration_wave(self, wave_index: int, colors: List[str]) -> None:
        """Create celebration wave effects"""
        try:
            wave_radius = 20 + (wave_index * 15)
            num_particles = 20
            color = colors[wave_index % len(colors)]
            
            for i in range(num_particles):
                angle = (2 * math.pi * i) / num_particles
                
                self.particle_system.add_particle(
                    self.x, self.y,
                    particle_type="wave",
                    angle=angle,
                    velocity_x=2 + wave_index,
                    radius=wave_radius,
                    size=3,
                    color=color,
                    life=self.config.PARTICLE_LIFETIME // 2
                )
        except Exception as e:
            logging.error(f"Error creating celebration wave: {e}")
    
    def celebrate_problem_solved(self) -> None:
        """Celebrate when the entire problem is solved"""
        if not self.is_active:
            return
            
        try:
            # Trigger full unlock if not already done
            if not self.is_fully_unlocked:
                self.unlocked_parts = self.total_parts
                self._trigger_full_unlock_celebration()
            
            # Additional celebration effects
            self._create_victory_effects()
            
            logging.info("Problem solved celebration triggered")
            
        except Exception as e:
            logging.error(f"Error in problem solved celebration: {e}")
    
    def _create_victory_effects(self) -> None:
        """Create special victory effects"""
        try:
            theme = self.config.LEVEL_THEMES[self.level_name]
            colors = theme["effects"]
            
            # Create spiraling particles
            for spiral in range(2):
                for i in range(20):
                    angle = (2 * math.pi * i) / 20 + (spiral * math.pi)
                    radius = 30 + (i * 2)
                    
                    self.canvas.after(
                        i * 50,
                        lambda a=angle, r=radius, c=colors[spiral % len(colors)]: 
                        self._create_spiral_particle(a, r, c)
                    )
        except Exception as e:
            logging.error(f"Error creating victory effects: {e}")
    
    def _create_spiral_particle(self, angle: float, radius: float, color: str) -> None:
        """Create a single spiral particle"""
        try:
            x = self.x + math.cos(angle) * radius
            y = self.y + math.sin(angle) * radius
            
            self.particle_system.add_particle(
                x, y,
                particle_type="explosion",
                velocity_x=math.cos(angle + math.pi/2) * 2,
                velocity_y=math.sin(angle + math.pi/2) * 2,
                size=4,
                color=color,
                life=self.config.PARTICLE_LIFETIME // 2
            )
        except Exception as e:
            logging.error(f"Error creating spiral particle: {e}")
    
    def react_to_character_reveal(self, character: str) -> None:
        """React to character reveals with subtle effects"""
        if not self.is_active or character not in "0123456789+-=xX":
            return
            
        try:
            theme = self.config.LEVEL_THEMES[self.level_name]
            color = random.choice(theme["particles"])
            
            # Create small particle burst
            for i in range(3):
                angle = random.uniform(0, 2 * math.pi)
                speed = random.uniform(1, 3)
                
                self.particle_system.add_particle(
                    self.x + random.uniform(-20, 20),
                    self.y + random.uniform(-20, 20),
                    particle_type="explosion",
                    velocity_x=math.cos(angle) * speed,
                    velocity_y=math.sin(angle) * speed,
                    size=random.uniform(2, 4),
                    color=color,
                    life=self.config.PARTICLE_LIFETIME // 3
                )
                
        except Exception as e:
            logging.error(f"Error reacting to character reveal: {e}")
    
    def shake_particles(self, intensity: float = 1.0) -> None:
        """Shake particles for feedback effects"""
        if not self.is_active:
            return
            
        try:
            for particle in self.particle_system.particles:
                if particle['type'] == 'orbital':
                    # Add random velocity for shake effect
                    shake_x = random.uniform(-intensity, intensity)
                    shake_y = random.uniform(-intensity, intensity)
                    
                    particle['velocity_x'] = particle.get('velocity_x', 0) + shake_x
                    particle['velocity_y'] = particle.get('velocity_y', 0) + shake_y
                    
        except Exception as e:
            logging.error(f"Error shaking particles: {e}")
    
    def reset(self) -> None:
        """Reset the lock to initial state"""
        try:
            logging.info("Resetting lock animation")
            
            # Stop all animations
            self.stop_all_persistent_animations()
            
            # Reset state
            self.unlocked_parts = 0
            self.is_fully_unlocked = False
            self.animation_frame = 0
            
            # Clear and recreate components
            self.particle_system.clear_all()
            self.visuals.clear_all()
            
            # Reinitialize if still active
            if self.is_active and self.canvas.winfo_exists():
                self.visuals.create_lock_components(self.level_name)
                self.particle_system.start()
                self._create_initial_particles()
                self._start_animation_loop()
                
            logging.info("Lock animation reset complete")
            
        except Exception as e:
            logging.error(f"Error resetting lock animation: {e}")
    
    def clear_visuals(self) -> None:
        """Clear all visual elements"""
        try:
            self.stop_all_persistent_animations()
            self.particle_system.clear_all()
            self.visuals.clear_all()
        except Exception as e:
            logging.error(f"Error clearing visuals: {e}")
    
    def stop_all_persistent_animations(self) -> None:
        """Stop all ongoing animations and timers"""
        try:
            logging.debug("Stopping all lock animation timers")
            
            # Set inactive to prevent new animations
            self.is_active = False
            
            # Stop particle system
            self.particle_system.stop()
            
            # Cancel all scheduled callbacks
            for key, after_id in list(self.after_ids.items()):
                try:
                    if after_id:
                        self.canvas.after_cancel(after_id)
                        logging.debug(f"Cancelled timer: {key}")
                except tk.TclError:
                    pass  # Canvas might be destroyed
                except Exception as e:
                    logging.warning(f"Error cancelling timer {key}: {e}")
            
            self.after_ids.clear()
            logging.debug("All lock animation timers stopped")
            
        except Exception as e:
            logging.error(f"Error stopping animations: {e}")
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get current performance statistics"""
        return self.performance_stats.copy()
    
    def set_level_theme(self, level_name: str) -> None:
        """Change the level theme"""
        if level_name in self.config.LEVEL_THEMES:
            self.level_name = level_name
            # Recreate visuals with new theme
            if self.is_active:
                self.visuals.clear_all()
                self.visuals.create_lock_components(level_name)
                logging.info(f"Lock theme changed to {level_name}")
    
    def resize(self, new_size: float) -> None:
        """Resize the lock animation"""
        if new_size != self.size and new_size >= 50:
            old_size = self.size
            self.size = new_size
            
            # Update visuals
            self.visuals.size = new_size
            self.visuals.clear_all()
            self.visuals.create_lock_components(self.level_name)
            
            logging.info(f"Lock resized from {old_size} to {new_size}")
    
    def reposition(self, new_x: float, new_y: float) -> None:
        """Reposition the lock animation"""
        if new_x != self.x or new_y != self.y:
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
    
    def stop_all_persistent_animations(self):
        """Stop all ongoing after() loops managed by this instance."""
        logging.debug(f"[LockAnimation] Stopping all persistent animations. Current after_ids: {list(self.after_ids.keys())}")
        
        # First set inactive to prevent new animations from starting
        self.is_active = False
        
        # Cancel character display timer specifically
        if hasattr(self, 'character_display_timer') and self.character_display_timer:
            try:
                self.canvas.after_cancel(self.character_display_timer)
                self.character_display_timer = None
                logging.debug("[LockAnimation] Cancelled character_display_timer")
            except Exception as e:
                logging.warning(f"[LockAnimation] Error cancelling character_display_timer: {e}")
        
        # Cancel all tracked after_ids
        for key in list(self.after_ids.keys()): # Iterate over a copy of keys
            after_id = self.after_ids.pop(key, None)
            if after_id:
                try:
                    self.canvas.after_cancel(after_id)
                    logging.debug(f"[LockAnimation] Cancelled after_id for '{key}': {after_id}")
                except tk.TclError as e:
                    # This can happen if the canvas is already destroyed
                    logging.warning(f"[LockAnimation] TclError cancelling after_id for '{key}' ({after_id}): {e}")
                except Exception as e:
                    logging.error(f"[LockAnimation] Exception cancelling after_id for '{key}' ({after_id}): {e}")
        
        # Clear the dictionary
        self.after_ids.clear()
        logging.debug("[LockAnimation] All persistent animations stopped")