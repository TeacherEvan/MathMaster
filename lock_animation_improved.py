import tkinter as tk
import random
import math
import time
import logging
from typing import Dict, List, Tuple, Optional, Any

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class LockAnimationConfig:
    """Enhanced configuration class for lock animation settings"""
    
    # Performance settings
    MAX_PARTICLES = 50
    MAX_SPARKLES = 30
    ANIMATION_FPS = 30
    FRAME_DELAY = 33  # ~30 FPS
    PERFORMANCE_MONITORING = True
    
    # Visual settings
    DEFAULT_SIZE = 100
    PARTICLE_LIFETIME = 60  # frames
    SPARKLE_LIFETIME = 45   # frames
    GLOW_INTENSITY = 0.8
    
    # Animation timing
    UNLOCK_FLASH_DURATION = 150  # ms
    CELEBRATION_DURATION = 3000  # ms
    TRANSITION_DURATION = 500    # ms
    PARTICLE_SPAWN_RATE = 0.3    # particles per frame
    
    # Enhanced level themes with improved color palettes
    LEVEL_THEMES = {
        "Easy": {
            "locked": ['#E74C3C', '#E57E31', '#D35400', '#C0392B'],
            "unlocked": ['#27AE60', '#2ECC71', '#58D68D', '#82E0AA'],
            "particles": ['#FF6B6B', '#FF8E53', '#FF6B35', '#FFD93D'],
            "effects": ['#FFD93D', '#6BCF7F', '#4ECDC4', '#FF9FF3'],
            "glow": '#FFD700'
        },
        "Medium": {
            "locked": ['#3498DB', '#2980B9', '#1F618D', '#154360'],
            "unlocked": ['#F1C40F', '#F39C12', '#F5B041', '#F8C471'],
            "particles": ['#74B9FF', '#0984E3', '#6C5CE7', '#A29BFE'],
            "effects": ['#FDCB6E', '#E17055', '#00B894', '#55A3FF'],
            "glow": '#00BFFF'
        },
        "Division": {
            "locked": ['#9B59B6', '#8E44AD', '#7D3C98', '#6C3483'],
            "unlocked": ['#1ABC9C', '#16A085', '#48C9B0', '#76D7C4'],
            "particles": ['#A29BFE', '#6C5CE7', '#FD79A8', '#FDCB6E'],
            "effects": ['#00CEC9', '#55A3FF', '#FF7675', '#74B9FF'],
            "glow": '#FF69B4'
        }
    }

class ParticleSystem:
    """Enhanced particle system with better performance and visual effects"""
    
    def __init__(self, canvas: tk.Canvas, config: LockAnimationConfig):
        self.canvas = canvas
        self.config = config
        self.particles: List[Dict[str, Any]] = []
        self.active = False
        self.last_update = time.time()
        self.frame_count = 0
        self.performance_stats = {
            'avg_frame_time': 0,
            'particle_count': 0,
            'frames_processed': 0
        }
        
    def add_particle(self, x: float, y: float, particle_type: str = "orbital", **kwargs) -> None:
        """Add a new particle with enhanced properties"""
        if len(self.particles) >= self.config.MAX_PARTICLES:
            self._remove_oldest_particle()
            
        particle = {
            'x': x,
            'y': y,
            'original_x': x,
            'original_y': y,
            'type': particle_type,
            'life': kwargs.get('life', self.config.PARTICLE_LIFETIME),
            'max_life': kwargs.get('life', self.config.PARTICLE_LIFETIME),
            'size': kwargs.get('size', random.uniform(2, 4)),
            'color': kwargs.get('color', '#FFFFFF'),
            'velocity_x': kwargs.get('velocity_x', random.uniform(-2, 2)),
            'velocity_y': kwargs.get('velocity_y', random.uniform(-2, 2)),
            'angle': kwargs.get('angle', random.uniform(0, 2 * math.pi)),
            'angular_velocity': kwargs.get('angular_velocity', random.uniform(-0.1, 0.1)),
            'radius': kwargs.get('radius', random.uniform(20, 60)),
            'pulse_phase': random.uniform(0, 2 * math.pi),
            'id': None,
            'created_time': time.time(),
            'trail_positions': []
        }
        
        # Create canvas item with enhanced visuals
        try:
            if particle_type == "glow":
                # Create glowing particle with multiple layers
                particle['id'] = self._create_glow_particle(particle)
            else:
                particle['id'] = self.canvas.create_oval(
                    x - particle['size'], y - particle['size'],
                    x + particle['size'], y + particle['size'],
                    fill=particle['color'], outline='', tags="lock_particle"
                )
            
            if particle['id']:
                self.particles.append(particle)
                
        except tk.TclError as e:
            logger.warning(f"Failed to create particle: {e}")
    
    def _create_glow_particle(self, particle: Dict[str, Any]) -> Optional[int]:
        """Create a particle with glow effect"""
        try:
            # Create outer glow
            glow_size = particle['size'] * 2
            glow_color = self._lighten_color(particle['color'], 0.3)
            
            glow_id = self.canvas.create_oval(
                particle['x'] - glow_size, particle['y'] - glow_size,
                particle['x'] + glow_size, particle['y'] + glow_size,
                fill=glow_color, outline='', tags="lock_particle_glow"
            )
            
            # Create main particle
            main_id = self.canvas.create_oval(
                particle['x'] - particle['size'], particle['y'] - particle['size'],
                particle['x'] + particle['size'], particle['y'] + particle['size'],
                fill=particle['color'], outline='', tags="lock_particle"
            )
            
            # Store both IDs
            particle['glow_id'] = glow_id
            return main_id
            
        except tk.TclError:
            return None
    
    def update(self) -> None:
        """Enhanced particle update with performance monitoring"""
        if not self.active or not self._canvas_exists():
            return
            
        start_time = time.time()
        
        # Update particles in reverse order for safe removal
        for i in range(len(self.particles) - 1, -1, -1):
            particle = self.particles[i]
            
            # Update particle based on type
            if particle['type'] == 'orbital':
                self._update_orbital_particle(particle)
            elif particle['type'] == 'explosion':
                self._update_explosion_particle(particle)
            elif particle['type'] == 'wave':
                self._update_wave_particle(particle)
            elif particle['type'] == 'glow':
                self._update_glow_particle(particle)
            elif particle['type'] == 'spiral':
                self._update_spiral_particle(particle)
            
            # Update life and remove if dead
            particle['life'] -= 1
            if particle['life'] <= 0 or not self._is_particle_valid(particle):
                self._remove_particle(i)
        
        # Update performance stats
        if self.config.PERFORMANCE_MONITORING:
            frame_time = time.time() - start_time
            self._update_performance_stats(frame_time)
    
    def _update_orbital_particle(self, particle: Dict[str, Any]) -> None:
        """Enhanced orbital particle movement with pulsing"""
        particle['angle'] += particle['angular_velocity']
        particle['pulse_phase'] += 0.1
        
        # Calculate pulsing radius
        pulse_factor = 1 + 0.2 * math.sin(particle['pulse_phase'])
        current_radius = particle['radius'] * pulse_factor
        
        # Calculate new position
        new_x = particle['original_x'] + math.cos(particle['angle']) * current_radius
        new_y = particle['original_y'] + math.sin(particle['angle']) * current_radius
        
        # Update trail
        particle['trail_positions'].append((new_x, new_y))
        if len(particle['trail_positions']) > 5:
            particle['trail_positions'].pop(0)
        
        self._update_particle_position(particle, new_x, new_y)
    
    def _update_explosion_particle(self, particle: Dict[str, Any]) -> None:
        """Enhanced explosion particle with gravity and air resistance"""
        # Apply air resistance
        particle['velocity_x'] *= 0.98
        particle['velocity_y'] *= 0.98
        
        # Apply gravity
        particle['velocity_y'] += 0.3
        
        # Update position
        particle['x'] += particle['velocity_x']
        particle['y'] += particle['velocity_y']
        
        self._update_particle_position(particle, particle['x'], particle['y'])
    
    def _update_wave_particle(self, particle: Dict[str, Any]) -> None:
        """Enhanced wave particle with smooth expansion"""
        particle['radius'] += particle['velocity_x']
        particle['angle'] += particle['angular_velocity']
        
        # Calculate wave position
        wave_x = particle['original_x'] + math.cos(particle['angle']) * particle['radius']
        wave_y = particle['original_y'] + math.sin(particle['angle']) * particle['radius']
        
        self._update_particle_position(particle, wave_x, wave_y)
    
    def _update_glow_particle(self, particle: Dict[str, Any]) -> None:
        """Update glowing particle with pulsing effect"""
        particle['pulse_phase'] += 0.15
        
        # Pulsing size effect
        pulse_factor = 1 + 0.3 * math.sin(particle['pulse_phase'])
        current_size = particle['size'] * pulse_factor
        
        # Update both main and glow particles
        try:
            if particle['id']:
                self.canvas.coords(
                    particle['id'],
                    particle['x'] - current_size, particle['y'] - current_size,
                    particle['x'] + current_size, particle['y'] + current_size
                )
            
            if 'glow_id' in particle and particle['glow_id']:
                glow_size = current_size * 1.5
                self.canvas.coords(
                    particle['glow_id'],
                    particle['x'] - glow_size, particle['y'] - glow_size,
                    particle['x'] + glow_size, particle['y'] + glow_size
                )
                
        except tk.TclError:
            particle['life'] = 0
    
    def _update_spiral_particle(self, particle: Dict[str, Any]) -> None:
        """Update spiral particle movement"""
        particle['angle'] += particle['angular_velocity']
        particle['radius'] += particle['velocity_x']
        
        # Calculate spiral position
        spiral_x = particle['original_x'] + math.cos(particle['angle']) * particle['radius']
        spiral_y = particle['original_y'] + math.sin(particle['angle']) * particle['radius']
        
        self._update_particle_position(particle, spiral_x, spiral_y)
    
    def _update_particle_position(self, particle: Dict[str, Any], new_x: float, new_y: float) -> None:
        """Update particle position with fade effect"""
        try:
            if particle['id']:
                self.canvas.coords(
                    particle['id'],
                    new_x - particle['size'], new_y - particle['size'],
                    new_x + particle['size'], new_y + particle['size']
                )
                
                # Apply fade effect
                alpha = particle['life'] / particle['max_life']
                faded_color = self._apply_alpha(particle['color'], alpha)
                self.canvas.itemconfig(particle['id'], fill=faded_color)
                
        except tk.TclError:
            particle['life'] = 0
    
    def _remove_particle(self, index: int) -> None:
        """Enhanced particle removal with proper cleanup"""
        if 0 <= index < len(self.particles):
            particle = self.particles[index]
            try:
                if particle['id']:
                    self.canvas.delete(particle['id'])
                if 'glow_id' in particle and particle['glow_id']:
                    self.canvas.delete(particle['glow_id'])
            except tk.TclError:
                pass
            self.particles.pop(index)
    
    def _remove_oldest_particle(self) -> None:
        """Remove the oldest particle to maintain performance"""
        if self.particles:
            oldest_index = 0
            oldest_time = self.particles[0]['created_time']
            
            for i, particle in enumerate(self.particles):
                if particle['created_time'] < oldest_time:
                    oldest_time = particle['created_time']
                    oldest_index = i
            
            self._remove_particle(oldest_index)
    
    def _is_particle_valid(self, particle: Dict[str, Any]) -> bool:
        """Enhanced particle validation"""
        try:
            if not particle['id']:
                return False
            
            # Check if canvas item still exists
            self.canvas.coords(particle['id'])
            return True
            
        except tk.TclError:
            return False
    
    def _apply_alpha(self, color: str, alpha: float) -> str:
        """Apply alpha transparency to color"""
        try:
            if color.startswith('#'):
                r = int(color[1:3], 16)
                g = int(color[3:5], 16)
                b = int(color[5:7], 16)
            else:
                return color
            
            # Apply alpha
            r = int(r * alpha)
            g = int(g * alpha)
            b = int(b * alpha)
            
            return f"#{r:02x}{g:02x}{b:02x}"
            
        except (ValueError, IndexError):
            return color
    
    def _lighten_color(self, color: str, factor: float) -> str:
        """Lighten a color by a given factor"""
        try:
            if color.startswith('#'):
                r = int(color[1:3], 16)
                g = int(color[3:5], 16)
                b = int(color[5:7], 16)
            else:
                return color
            
            # Lighten
            r = min(255, int(r + (255 - r) * factor))
            g = min(255, int(g + (255 - g) * factor))
            b = min(255, int(b + (255 - b) * factor))
            
            return f"#{r:02x}{g:02x}{b:02x}"
            
        except (ValueError, IndexError):
            return color
    
    def _canvas_exists(self) -> bool:
        """Check if canvas still exists"""
        try:
            return self.canvas.winfo_exists()
        except tk.TclError:
            return False
    
    def _update_performance_stats(self, frame_time: float) -> None:
        """Update performance statistics"""
        self.performance_stats['frames_processed'] += 1
        self.performance_stats['particle_count'] = len(self.particles)
        
        # Calculate rolling average frame time
        if self.performance_stats['avg_frame_time'] == 0:
            self.performance_stats['avg_frame_time'] = frame_time
        else:
            self.performance_stats['avg_frame_time'] = (
                self.performance_stats['avg_frame_time'] * 0.9 + frame_time * 0.1
            )
    
    def clear_all(self) -> None:
        """Clear all particles with proper cleanup"""
        try:
            for particle in self.particles:
                if particle['id']:
                    self.canvas.delete(particle['id'])
                if 'glow_id' in particle and particle['glow_id']:
                    self.canvas.delete(particle['glow_id'])
        except tk.TclError:
            pass
        
        self.particles.clear()
        self.performance_stats = {
            'avg_frame_time': 0,
            'particle_count': 0,
            'frames_processed': 0
        }
    
    def start(self) -> None:
        """Start the particle system"""
        self.active = True
        self.last_update = time.time()
    
    def stop(self) -> None:
        """Stop the particle system"""
        self.active = False

class LockVisuals:
    """Enhanced lock visual components with better scaling and effects"""
    
    def __init__(self, canvas: tk.Canvas, x: float, y: float, size: float, config: LockAnimationConfig):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.size = size
        self.config = config
        
        # Visual component IDs
        self.lock_components = {
            'glow': [],
            'body': [],
            'shackle': [],
            'keyhole': [],
            'segments': [],
            'highlights': [],
            'shadows': []
        }
        
        # Scaling factors
        self.scale_factor = size / config.DEFAULT_SIZE
        
    def create_lock_components(self, level_name: str) -> None:
        """Create enhanced lock visual components"""
        try:
            self._create_glow_effect(level_name)
            self._create_lock_body(level_name)
            self._create_shackle(level_name)
            self._create_keyhole()
            self._create_lock_segments(level_name)
            self._create_highlights_and_shadows()
            
        except Exception as e:
            logger.error(f"Failed to create lock components: {e}")
    
    def _create_glow_effect(self, level_name: str) -> None:
        """Create enhanced glow effect around the lock"""
        theme = self.config.LEVEL_THEMES.get(level_name, self.config.LEVEL_THEMES["Easy"])
        glow_color = theme.get('glow', '#FFD700')
        
        # Create multiple glow layers for depth
        for i in range(3):
            glow_size = self.size * (1.3 + i * 0.1)
            alpha = 0.1 - i * 0.02
            
            try:
                glow_id = self.canvas.create_oval(
                    self.x - glow_size/2, self.y - glow_size/2,
                    self.x + glow_size/2, self.y + glow_size/2,
                    fill=self._apply_alpha(glow_color, alpha),
                    outline='',
                    tags="lock_glow"
                )
                self.lock_components['glow'].append(glow_id)
                
            except tk.TclError:
                pass
    
    def _create_lock_body(self, level_name: str) -> None:
        """Create enhanced lock body with gradient effect"""
        theme = self.config.LEVEL_THEMES.get(level_name, self.config.LEVEL_THEMES["Easy"])
        locked_colors = theme['locked']
        
        # Main body
        body_size = self.size * 0.6
        
        try:
            # Create gradient effect with multiple rectangles
            for i, color in enumerate(locked_colors):
                offset = i * 2
                body_id = self.canvas.create_rectangle(
                    self.x - body_size/2 + offset, self.y - body_size/4 + offset,
                    self.x + body_size/2 - offset, self.y + body_size/2 - offset,
                    fill=color,
                    outline=self._darken_color(color, 0.8),
                    width=2,
                    tags="lock_body"
                )
                self.lock_components['body'].append(body_id)
                
        except tk.TclError:
            pass
    
    def _create_shackle(self, level_name: str) -> None:
        """Create enhanced shackle with 3D effect"""
        theme = self.config.LEVEL_THEMES.get(level_name, self.config.LEVEL_THEMES["Easy"])
        locked_colors = theme['locked']
        
        shackle_width = self.size * 0.4
        shackle_height = self.size * 0.3
        
        try:
            # Left side of shackle
            left_id = self.canvas.create_arc(
                self.x - shackle_width/2, self.y - shackle_height,
                self.x + shackle_width/2, self.y,
                start=90, extent=90,
                outline=locked_colors[0],
                width=int(8 * self.scale_factor),
                style=tk.ARC,
                tags="lock_shackle"
            )
            
            # Right side of shackle
            right_id = self.canvas.create_arc(
                self.x - shackle_width/2, self.y - shackle_height,
                self.x + shackle_width/2, self.y,
                start=0, extent=90,
                outline=locked_colors[0],
                width=int(8 * self.scale_factor),
                style=tk.ARC,
                tags="lock_shackle"
            )
            
            self.lock_components['shackle'].extend([left_id, right_id])
            
        except tk.TclError:
            pass
    
    def _create_keyhole(self) -> None:
        """Create enhanced keyhole with depth effect"""
        keyhole_size = self.size * 0.15
        
        try:
            # Outer shadow
            shadow_id = self.canvas.create_oval(
                self.x - keyhole_size/2 + 2, self.y - keyhole_size/4 + 2,
                self.x + keyhole_size/2 + 2, self.y + keyhole_size/4 + 2,
                fill='#000000',
                outline='',
                tags="lock_keyhole"
            )
            
            # Main keyhole
            keyhole_id = self.canvas.create_oval(
                self.x - keyhole_size/2, self.y - keyhole_size/4,
                self.x + keyhole_size/2, self.y + keyhole_size/4,
                fill='#1a1a1a',
                outline='#333333',
                width=1,
                tags="lock_keyhole"
            )
            
            # Keyhole slot
            slot_id = self.canvas.create_rectangle(
                self.x - keyhole_size/6, self.y,
                self.x + keyhole_size/6, self.y + keyhole_size/3,
                fill='#1a1a1a',
                outline='',
                tags="lock_keyhole"
            )
            
            self.lock_components['keyhole'].extend([shadow_id, keyhole_id, slot_id])
            
        except tk.TclError:
            pass
    
    def _create_lock_segments(self, level_name: str) -> None:
        """Create enhanced lock segments with better visual separation"""
        theme = self.config.LEVEL_THEMES.get(level_name, self.config.LEVEL_THEMES["Easy"])
        locked_colors = theme['locked']
        
        segment_width = self.size * 0.6 / 4
        segment_height = self.size * 0.5
        
        for i in range(4):
            x_left = self.x - self.size * 0.3 + i * segment_width
            x_right = x_left + segment_width
            y_top = self.y - segment_height/4
            y_bottom = self.y + segment_height/2
            
            try:
                # Main segment
                segment_id = self.canvas.create_rectangle(
                    x_left, y_top,
                    x_right, y_bottom,
                    fill=locked_colors[i % len(locked_colors)],
                    outline=self._darken_color(locked_colors[i % len(locked_colors)], 0.7),
                    width=2,
                    tags=f"lock_segment_{i}"
                )
                
                self.lock_components['segments'].append(segment_id)
                self._add_segment_shading(x_left, x_right, y_top, y_bottom, locked_colors[i % len(locked_colors)], i)
                
            except tk.TclError:
                pass
    
    def _create_highlights_and_shadows(self) -> None:
        """Create highlights and shadows for 3D effect"""
        try:
            # Top highlight
            highlight_id = self.canvas.create_line(
                self.x - self.size * 0.3, self.y - self.size * 0.25,
                self.x + self.size * 0.3, self.y - self.size * 0.25,
                fill='#FFFFFF',
                width=2,
                tags="lock_highlight"
            )
            
            # Bottom shadow
            shadow_id = self.canvas.create_line(
                self.x - self.size * 0.3, self.y + self.size * 0.25,
                self.x + self.size * 0.3, self.y + self.size * 0.25,
                fill='#000000',
                width=2,
                tags="lock_shadow"
            )
            
            self.lock_components['highlights'].append(highlight_id)
            self.lock_components['shadows'].append(shadow_id)
            
        except tk.TclError:
            pass
    
    def _add_segment_shading(self, x_left: float, x_right: float, y_top: float, 
                           y_bottom: float, base_color: str, segment_index: int) -> None:
        """Add enhanced shading to lock segments"""
        try:
            # Top highlight
            highlight_color = self._brighten_color(base_color, 1.4)
            highlight_id = self.canvas.create_line(
                x_left + 2, y_top + 2,
                x_right - 2, y_top + 2,
                fill=highlight_color,
                width=2,
                tags=f"lock_segment_{segment_index}_highlight"
            )
            
            # Bottom shadow
            shadow_color = self._darken_color(base_color, 0.6)
            shadow_id = self.canvas.create_line(
                x_left + 2, y_bottom - 2,
                x_right - 2, y_bottom - 2,
                fill=shadow_color,
                width=2,
                tags=f"lock_segment_{segment_index}_shadow"
            )
            
            self.lock_components['highlights'].extend([highlight_id])
            self.lock_components['shadows'].extend([shadow_id])
            
        except tk.TclError:
            pass
    
    def _brighten_color(self, hex_color: str, factor: float = 1.3) -> str:
        """Brighten a hex color by a given factor"""
        try:
            if hex_color.startswith('#'):
                r = int(hex_color[1:3], 16)
                g = int(hex_color[3:5], 16)
                b = int(hex_color[5:7], 16)
            else:
                return hex_color
            
            r = min(255, int(r * factor))
            g = min(255, int(g * factor))
            b = min(255, int(b * factor))
            
            return f"#{r:02x}{g:02x}{b:02x}"
            
        except (ValueError, IndexError):
            return hex_color
    
    def _darken_color(self, hex_color: str, factor: float = 0.7) -> str:
        """Darken a hex color by a given factor"""
        try:
            if hex_color.startswith('#'):
                r = int(hex_color[1:3], 16)
                g = int(hex_color[3:5], 16)
                b = int(hex_color[5:7], 16)
            else:
                return hex_color
            
            r = int(r * factor)
            g = int(g * factor)
            b = int(b * factor)
            
            return f"#{r:02x}{g:02x}{b:02x}"
            
        except (ValueError, IndexError):
            return hex_color
    
    def _apply_alpha(self, color: str, alpha: float) -> str:
        """Apply alpha transparency to color"""
        try:
            if color.startswith('#'):
                r = int(color[1:3], 16)
                g = int(color[3:5], 16)
                b = int(color[5:7], 16)
            else:
                return color
            
            # Apply alpha
            r = int(r * alpha)
            g = int(g * alpha)
            b = int(b * alpha)
            
            return f"#{r:02x}{g:02x}{b:02x}"
            
        except (ValueError, IndexError):
            return color
    
    def update_segment_color(self, segment_index: int, color: str, outline_color: str) -> None:
        """Update the color of a specific segment with enhanced effects"""
        if 0 <= segment_index < len(self.lock_components['segments']):
            try:
                segment_id = self.lock_components['segments'][segment_index]
                self.canvas.itemconfig(segment_id, fill=color, outline=outline_color)
                
                # Update associated highlights and shadows
                highlight_color = self._brighten_color(color, 1.4)
                shadow_color = self._darken_color(color, 0.6)
                
                # Find and update highlights/shadows for this segment
                for item_id in self.canvas.find_withtag(f"lock_segment_{segment_index}_highlight"):
                    self.canvas.itemconfig(item_id, fill=highlight_color)
                
                for item_id in self.canvas.find_withtag(f"lock_segment_{segment_index}_shadow"):
                    self.canvas.itemconfig(item_id, fill=shadow_color)
                    
            except tk.TclError as e:
                logger.warning(f"Failed to update segment {segment_index}: {e}")
    
    def clear_all(self) -> None:
        """Clear all visual components with proper cleanup"""
        try:
            # Clear all component groups
            for component_group in self.lock_components.values():
                for item_id in component_group:
                    try:
                        self.canvas.delete(item_id)
                    except tk.TclError:
                        pass
                component_group.clear()
            
            # Clear by tags as backup
            for tag in ["lock_glow", "lock_body", "lock_shackle", "lock_keyhole", 
                       "lock_highlight", "lock_shadow"]:
                try:
                    self.canvas.delete(tag)
                except tk.TclError:
                    pass
            
            # Clear segment tags
            for i in range(4):
                for suffix in ["", "_highlight", "_shadow"]:
                    try:
                        self.canvas.delete(f"lock_segment_{i}{suffix}")
                    except tk.TclError:
                        pass
                        
        except Exception as e:
            logger.error(f"Error clearing lock visuals: {e}")

class LockAnimation:
    """Enhanced lock animation with improved performance and visual effects"""
    
    def __init__(self, canvas: tk.Canvas, x: float, y: float, size: float = 100, level_name: str = "Easy"):
        # Core properties
        self.canvas = canvas
        self.x = x
        self.y = y
        self.size = size
        self.level_name = level_name
        
        # Configuration and components
        self.config = LockAnimationConfig()
        self.particle_system = ParticleSystem(canvas, self.config)
        self.visuals = LockVisuals(canvas, x, y, size, self.config)
        
        # Animation state
        self.unlocked_parts = 0
        self.total_parts = 4
        self.is_fully_unlocked = False
        self.is_celebrating = False
        
        # Performance tracking
        self.performance_stats = {
            'frame_count': 0,
            'avg_frame_time': 0,
            'last_update': time.time()
        }
        
        # Timer management
        self.after_ids = {}
        self.animation_active = False
        
        # Initialize
        self._initialize()
    
    def _initialize(self) -> None:
        """Initialize the lock animation with enhanced setup"""
        try:
            logger.info(f"Initializing lock animation for level: {self.level_name}")
            
            # Create visual components
            self.visuals.create_lock_components(self.level_name)
            
            # Start particle system
            self.particle_system.start()
            
            # Create initial ambient particles
            self._create_initial_particles()
            
            # Start animation loop
            self._start_animation_loop()
            
            logger.info("Lock animation initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize lock animation: {e}")
    
    def _create_initial_particles(self) -> None:
        """Create initial ambient particles around the lock"""
        theme = self.config.LEVEL_THEMES.get(self.level_name, self.config.LEVEL_THEMES["Easy"])
        particle_colors = theme['particles']
        
        # Create orbital particles
        for i in range(8):
            angle = (i / 8) * 2 * math.pi
            radius = self.size * 0.8
            
            self.particle_system.add_particle(
                self.x, self.y,
                particle_type="orbital",
                angle=angle,
                angular_velocity=0.02,
                radius=radius,
                color=random.choice(particle_colors),
                size=random.uniform(2, 4),
                life=self.config.PARTICLE_LIFETIME * 2
            )
        
        # Create some glow particles
        for i in range(4):
            offset_x = random.uniform(-self.size * 0.3, self.size * 0.3)
            offset_y = random.uniform(-self.size * 0.3, self.size * 0.3)
            
            self.particle_system.add_particle(
                self.x + offset_x, self.y + offset_y,
                particle_type="glow",
                color=random.choice(particle_colors),
                size=random.uniform(3, 6),
                life=self.config.PARTICLE_LIFETIME * 3
            )
    
    def _start_animation_loop(self) -> None:
        """Start the enhanced animation loop with frame rate limiting"""
        if not self.animation_active:
            self.animation_active = True
            self._update_animation()
    
    def _update_animation(self) -> None:
        """Enhanced animation update with performance monitoring"""
        if not self.animation_active:
            return
        
        try:
            start_time = time.time()
            
            # Update particle system
            self.particle_system.update()
            
            # Add ambient particles occasionally
            if random.random() < self.config.PARTICLE_SPAWN_RATE:
                self._add_ambient_particle()
            
            # Update performance stats
            frame_time = time.time() - start_time
            self._update_performance_stats(frame_time)
            
            # Schedule next update with frame rate limiting
            self.after_ids['animation'] = self.canvas.after(
                self.config.FRAME_DELAY, 
                self._update_animation
            )
            
        except Exception as e:
            logger.error(f"Animation update error: {e}")
            self.animation_active = False
    
    def _add_ambient_particle(self) -> None:
        """Add ambient particles around the lock"""
        if len(self.particle_system.particles) >= self.config.MAX_PARTICLES:
            return
        
        theme = self.config.LEVEL_THEMES.get(self.level_name, self.config.LEVEL_THEMES["Easy"])
        particle_colors = theme['particles']
        
        # Random position around lock
        angle = random.uniform(0, 2 * math.pi)
        radius = random.uniform(self.size * 0.6, self.size * 1.2)
        
        particle_x = self.x + math.cos(angle) * radius
        particle_y = self.y + math.sin(angle) * radius
        
        self.particle_system.add_particle(
            particle_x, particle_y,
            particle_type=random.choice(["orbital", "glow"]),
            angle=angle,
            angular_velocity=random.uniform(-0.05, 0.05),
            radius=random.uniform(20, 60),
            color=random.choice(particle_colors),
            size=random.uniform(2, 5)
        )
    
    def _update_performance_stats(self, frame_time: float) -> None:
        """Update performance statistics"""
        self.performance_stats['frame_count'] += 1
        
        # Calculate rolling average
        if self.performance_stats['avg_frame_time'] == 0:
            self.performance_stats['avg_frame_time'] = frame_time
        else:
            self.performance_stats['avg_frame_time'] = (
                self.performance_stats['avg_frame_time'] * 0.95 + frame_time * 0.05
            )
        
        self.performance_stats['last_update'] = time.time()
    
    def unlock_next_part(self) -> None:
        """Enhanced unlock animation with better visual effects"""
        if self.unlocked_parts >= self.total_parts:
            logger.info("All parts already unlocked")
            return
        
        try:
            logger.info(f"Unlocking part {self.unlocked_parts + 1}")
            
            # Get theme colors
            theme = self.config.LEVEL_THEMES.get(self.level_name, self.config.LEVEL_THEMES["Easy"])
            unlock_colors = theme['unlocked']
            effect_colors = theme['effects']
            
            # Create unlock flash effect
            self._create_unlock_flash(self.unlocked_parts)
            
            # Update segment color
            self._apply_unlock_color(self.unlocked_parts, unlock_colors)
            
            # Create unlock effects
            self._create_unlock_effects(self.unlocked_parts, effect_colors)
            
            # Update state
            self.unlocked_parts += 1
            
            # Check if fully unlocked
            if self.unlocked_parts >= self.total_parts:
                self.is_fully_unlocked = True
                self._trigger_full_unlock_celebration()
            
            logger.info(f"Part {self.unlocked_parts} unlocked successfully")
            
        except Exception as e:
            logger.error(f"Failed to unlock part: {e}")
    
    def _create_unlock_flash(self, part_index: int) -> None:
        """Create enhanced flash effect for unlock"""
        try:
            # Calculate segment position
            segment_width = self.size * 0.6 / 4
            segment_x = self.x - self.size * 0.3 + part_index * segment_width + segment_width/2
            
            # Create flash effect
            flash_id = self.canvas.create_oval(
                segment_x - 20, self.y - 20,
                segment_x + 20, self.y + 20,
                fill='#FFFFFF',
                outline='',
                tags="unlock_flash"
            )
            
            # Animate flash
            def fade_flash(alpha=1.0):
                if alpha > 0:
                    try:
                        color = f"#{int(255*alpha):02x}{int(255*alpha):02x}{int(255*alpha):02x}"
                        self.canvas.itemconfig(flash_id, fill=color)
                        self.after_ids[f'flash_{part_index}'] = self.canvas.after(
                            20, lambda: fade_flash(alpha - 0.1)
                        )
                    except tk.TclError:
                        pass
                else:
                    try:
                        self.canvas.delete(flash_id)
                    except tk.TclError:
                        pass
            
            fade_flash()
            
        except Exception as e:
            logger.error(f"Failed to create unlock flash: {e}")
    
    def _apply_unlock_color(self, part_index: int, unlock_colors: List[str]) -> None:
        """Apply unlock color to segment with enhanced effects"""
        try:
            color = unlock_colors[part_index % len(unlock_colors)]
            outline_color = self.visuals._darken_color(color, 0.8)
            
            self.visuals.update_segment_color(part_index, color, outline_color)
            
        except Exception as e:
            logger.error(f"Failed to apply unlock color: {e}")
    
    def _create_unlock_effects(self, part_index: int, effect_colors: List[str]) -> None:
        """Create enhanced unlock particle effects"""
        try:
            # Calculate segment center
            segment_width = self.size * 0.6 / 4
            segment_x = self.x - self.size * 0.3 + part_index * segment_width + segment_width/2
            segment_y = self.y
            
            # Create explosion particles
            for i in range(12):
                angle = (i / 12) * 2 * math.pi
                velocity_x = math.cos(angle) * random.uniform(3, 8)
                velocity_y = math.sin(angle) * random.uniform(3, 8)
                
                self.particle_system.add_particle(
                    segment_x, segment_y,
                    particle_type="explosion",
                    velocity_x=velocity_x,
                    velocity_y=velocity_y,
                    color=random.choice(effect_colors),
                    size=random.uniform(3, 6),
                    life=self.config.PARTICLE_LIFETIME
                )
            
            # Create wave effect
            self._create_wave_effect(segment_y, random.choice(effect_colors))
            
            # Create spiral particles
            for i in range(6):
                angle = (i / 6) * 2 * math.pi
                
                self.particle_system.add_particle(
                    segment_x, segment_y,
                    particle_type="spiral",
                    angle=angle,
                    angular_velocity=0.1,
                    velocity_x=2,
                    color=random.choice(effect_colors),
                    size=random.uniform(2, 4),
                    life=self.config.PARTICLE_LIFETIME * 1.5
                )
                
        except Exception as e:
            logger.error(f"Failed to create unlock effects: {e}")
    
    def _create_wave_effect(self, center_y: float, color: str) -> None:
        """Create enhanced wave effect"""
        try:
            # Create expanding wave particles
            for i in range(16):
                angle = (i / 16) * 2 * math.pi
                
                self.particle_system.add_particle(
                    self.x, center_y,
                    particle_type="wave",
                    angle=angle,
                    angular_velocity=0,
                    velocity_x=3,
                    radius=10,
                    color=color,
                    size=random.uniform(2, 4),
                    life=self.config.PARTICLE_LIFETIME // 2
                )
                
        except Exception as e:
            logger.error(f"Failed to create wave effect: {e}")
    
    def _trigger_full_unlock_celebration(self) -> None:
        """Enhanced celebration when fully unlocked"""
        if self.is_celebrating:
            return
        
        try:
            logger.info("Triggering full unlock celebration")
            self.is_celebrating = True
            
            theme = self.config.LEVEL_THEMES.get(self.level_name, self.config.LEVEL_THEMES["Easy"])
            effect_colors = theme['effects']
            
            # Create multiple celebration waves
            for wave_index in range(5):
                delay = wave_index * 200
                self.after_ids[f'celebration_wave_{wave_index}'] = self.canvas.after(
                    delay, 
                    lambda idx=wave_index: self._create_celebration_wave(idx, effect_colors)
                )
            
            # Reset celebration state
            self.after_ids['celebration_reset'] = self.canvas.after(
                self.config.CELEBRATION_DURATION,
                lambda: setattr(self, 'is_celebrating', False)
            )
            
        except Exception as e:
            logger.error(f"Failed to trigger celebration: {e}")
    
    def _create_celebration_wave(self, wave_index: int, colors: List[str]) -> None:
        """Create enhanced celebration wave"""
        try:
            particle_count = 20 + wave_index * 5
            base_radius = 30 + wave_index * 20
            
            for i in range(particle_count):
                angle = (i / particle_count) * 2 * math.pi
                
                self.particle_system.add_particle(
                    self.x, self.y,
                    particle_type="wave",
                    angle=angle,
                    angular_velocity=random.uniform(-0.02, 0.02),
                    velocity_x=random.uniform(2, 5),
                    radius=base_radius,
                    color=random.choice(colors),
                    size=random.uniform(3, 7),
                    life=self.config.PARTICLE_LIFETIME * 2
                )
                
        except Exception as e:
            logger.error(f"Failed to create celebration wave: {e}")
    
    def celebrate_problem_solved(self) -> None:
        """Enhanced celebration for problem solved"""
        try:
            logger.info("Celebrating problem solved")
            
            theme = self.config.LEVEL_THEMES.get(self.level_name, self.config.LEVEL_THEMES["Easy"])
            effect_colors = theme['effects']
            
            # Create victory effects
            self._create_victory_effects()
            
            # Create burst of particles
            for i in range(30):
                angle = random.uniform(0, 2 * math.pi)
                radius = random.uniform(0, self.size)
                velocity_x = math.cos(angle) * random.uniform(5, 12)
                velocity_y = math.sin(angle) * random.uniform(5, 12)
                
                self.particle_system.add_particle(
                    self.x, self.y,
                    particle_type="explosion",
                    velocity_x=velocity_x,
                    velocity_y=velocity_y,
                    color=random.choice(effect_colors),
                    size=random.uniform(4, 8),
                    life=self.config.PARTICLE_LIFETIME * 2
                )
                
        except Exception as e:
            logger.error(f"Failed to celebrate problem solved: {e}")
    
    def _create_victory_effects(self) -> None:
        """Create enhanced victory effects"""
        try:
            theme = self.config.LEVEL_THEMES.get(self.level_name, self.config.LEVEL_THEMES["Easy"])
            effect_colors = theme['effects']
            
            # Create spiral burst
            for i in range(24):
                angle = (i / 24) * 4 * math.pi  # Double spiral
                radius = i * 3
                
                self._create_spiral_particle(angle, radius, random.choice(effect_colors))
            
            # Create pulsing glow particles
            for i in range(8):
                offset_x = random.uniform(-self.size * 0.5, self.size * 0.5)
                offset_y = random.uniform(-self.size * 0.5, self.size * 0.5)
                
                self.particle_system.add_particle(
                    self.x + offset_x, self.y + offset_y,
                    particle_type="glow",
                    color=random.choice(effect_colors),
                    size=random.uniform(6, 12),
                    life=self.config.PARTICLE_LIFETIME * 3
                )
                
        except Exception as e:
            logger.error(f"Failed to create victory effects: {e}")
    
    def _create_spiral_particle(self, angle: float, radius: float, color: str) -> None:
        """Create enhanced spiral particle"""
        try:
            spiral_x = self.x + math.cos(angle) * radius
            spiral_y = self.y + math.sin(angle) * radius
            
            self.particle_system.add_particle(
                spiral_x, spiral_y,
                particle_type="spiral",
                angle=angle,
                angular_velocity=0.05,
                velocity_x=1,
                color=color,
                size=random.uniform(3, 6),
                life=self.config.PARTICLE_LIFETIME
            )
            
        except Exception as e:
            logger.error(f"Failed to create spiral particle: {e}")
    
    def react_to_character_reveal(self, character: str) -> None:
        """Enhanced reaction to character reveals"""
        try:
            logger.info(f"Reacting to character: {character}")
            
            theme = self.config.LEVEL_THEMES.get(self.level_name, self.config.LEVEL_THEMES["Easy"])
            particle_colors = theme['particles']
            
            # Create reaction based on character type
            if character in "0123456789":
                # Number - create gentle pulse
                for i in range(6):
                    angle = (i / 6) * 2 * math.pi
                    
                    self.particle_system.add_particle(
                        self.x, self.y,
                        particle_type="orbital",
                        angle=angle,
                        angular_velocity=0.03,
                        radius=self.size * 0.7,
                        color=random.choice(particle_colors),
                        size=random.uniform(2, 4),
                        life=self.config.PARTICLE_LIFETIME
                    )
            
            elif character in "+-=":
                # Operator - create burst effect
                for i in range(12):
                    angle = (i / 12) * 2 * math.pi
                    velocity_x = math.cos(angle) * random.uniform(2, 5)
                    velocity_y = math.sin(angle) * random.uniform(2, 5)
                    
                    self.particle_system.add_particle(
                        self.x, self.y,
                        particle_type="explosion",
                        velocity_x=velocity_x,
                        velocity_y=velocity_y,
                        color=random.choice(particle_colors),
                        size=random.uniform(3, 5),
                        life=self.config.PARTICLE_LIFETIME // 2
                    )
                    
        except Exception as e:
            logger.error(f"Failed to react to character: {e}")
    
    def shake_particles(self, intensity: float = 1.0) -> None:
        """Enhanced particle shaking effect"""
        try:
            logger.info(f"Shaking particles with intensity: {intensity}")
            
            # Add shake to existing particles
            for particle in self.particle_system.particles:
                shake_x = random.uniform(-intensity * 5, intensity * 5)
                shake_y = random.uniform(-intensity * 5, intensity * 5)
                
                particle['velocity_x'] += shake_x
                particle['velocity_y'] += shake_y
            
            # Create additional shake particles
            theme = self.config.LEVEL_THEMES.get(self.level_name, self.config.LEVEL_THEMES["Easy"])
            particle_colors = theme['particles']
            
            for i in range(int(10 * intensity)):
                offset_x = random.uniform(-self.size * 0.5, self.size * 0.5)
                offset_y = random.uniform(-self.size * 0.5, self.size * 0.5)
                
                self.particle_system.add_particle(
                    self.x + offset_x, self.y + offset_y,
                    particle_type="explosion",
                    velocity_x=random.uniform(-intensity * 3, intensity * 3),
                    velocity_y=random.uniform(-intensity * 3, intensity * 3),
                    color=random.choice(particle_colors),
                    size=random.uniform(2, 4),
                    life=self.config.PARTICLE_LIFETIME // 2
                )
                
        except Exception as e:
            logger.error(f"Failed to shake particles: {e}")
    
    def reset(self) -> None:
        """Enhanced reset with proper cleanup"""
        try:
            logger.info("Resetting lock animation")
            
            # Stop all animations
            self.stop_all_persistent_animations()
            
            # Reset state
            self.unlocked_parts = 0
            self.is_fully_unlocked = False
            self.is_celebrating = False
            
            # Clear visuals
            self.clear_visuals()
            
            # Reinitialize
            self._initialize()
            
            logger.info("Lock animation reset successfully")
            
        except Exception as e:
            logger.error(f"Failed to reset lock animation: {e}")
    
    def clear_visuals(self) -> None:
        """Enhanced visual cleanup"""
        try:
            # Clear particle system
            self.particle_system.clear_all()
            
            # Clear lock visuals
            self.visuals.clear_all()
            
            # Clear any remaining canvas items with lock tags
            for tag in ["lock_particle", "lock_particle_glow", "unlock_flash"]:
                try:
                    self.canvas.delete(tag)
                except tk.TclError:
                    pass
                    
        except Exception as e:
            logger.error(f"Error clearing visuals: {e}")
    
    def stop_all_persistent_animations(self) -> None:
        """Enhanced animation stopping with comprehensive cleanup"""
        try:
            # Stop animation loop
            self.animation_active = False
            
            # Cancel all scheduled after calls
            for after_id in self.after_ids.values():
                try:
                    self.canvas.after_cancel(after_id)
                except (tk.TclError, ValueError):
                    pass
            
            self.after_ids.clear()
            
            # Stop particle system
            self.particle_system.stop()
            
            logger.info("All persistent animations stopped")
            
        except Exception as e:
            logger.error(f"Error stopping animations: {e}")
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get enhanced performance statistics"""
        particle_stats = self.particle_system.performance_stats
        
        return {
            'frame_count': self.performance_stats['frame_count'],
            'avg_frame_time': self.performance_stats['avg_frame_time'],
            'fps': 1.0 / max(self.performance_stats['avg_frame_time'], 0.001),
            'particle_count': len(self.particle_system.particles),
            'particle_avg_frame_time': particle_stats['avg_frame_time'],
            'particle_frames_processed': particle_stats['frames_processed'],
            'unlocked_parts': self.unlocked_parts,
            'is_fully_unlocked': self.is_fully_unlocked,
            'is_celebrating': self.is_celebrating,
            'animation_active': self.animation_active
        }
    
    def set_level_theme(self, level_name: str) -> None:
        """Enhanced level theme setting with smooth transition"""
        if level_name != self.level_name:
            try:
                logger.info(f"Changing level theme from {self.level_name} to {level_name}")
                
                old_level = self.level_name
                self.level_name = level_name
                
                # Clear current visuals
                self.clear_visuals()
                
                # Recreate with new theme
                self.visuals = LockVisuals(self.canvas, self.x, self.y, self.size, self.config)
                self.visuals.create_lock_components(level_name)
                
                # Update unlocked segments with new colors
                if self.unlocked_parts > 0:
                    theme = self.config.LEVEL_THEMES.get(level_name, self.config.LEVEL_THEMES["Easy"])
                    unlock_colors = theme['unlocked']
                    
                    for i in range(self.unlocked_parts):
                        color = unlock_colors[i % len(unlock_colors)]
                        outline_color = self.visuals._darken_color(color, 0.8)
                        self.visuals.update_segment_color(i, color, outline_color)
                
                # Recreate initial particles
                self._create_initial_particles()
                
                logger.info(f"Level theme changed successfully to {level_name}")
                
            except Exception as e:
                logger.error(f"Failed to change level theme: {e}")
                self.level_name = old_level
    
    def resize(self, new_size: float) -> None:
        """Enhanced resize with proper scaling"""
        if new_size != self.size:
            try:
                logger.info(f"Resizing lock animation from {self.size} to {new_size}")
                
                old_size = self.size
                self.size = new_size
                
                # Update visuals
                self.visuals.size = new_size
                self.visuals.scale_factor = new_size / self.config.DEFAULT_SIZE
                
                # Recreate visuals with new size
                self.clear_visuals()
                self.visuals = LockVisuals(self.canvas, self.x, self.y, new_size, self.config)
                self.visuals.create_lock_components(self.level_name)
                
                # Update state
                if self.unlocked_parts > 0:
                    theme = self.config.LEVEL_THEMES.get(self.level_name, self.config.LEVEL_THEMES["Easy"])
                    unlock_colors = theme['unlocked']
                    
                    for i in range(self.unlocked_parts):
                        color = unlock_colors[i % len(unlock_colors)]
                        outline_color = self.visuals._darken_color(color, 0.8)
                        self.visuals.update_segment_color(i, color, outline_color)
                
                # Recreate particles
                self._create_initial_particles()
                
                logger.info(f"Lock animation resized successfully")
                
            except Exception as e:
                logger.error(f"Failed to resize lock animation: {e}")
                self.size = old_size
    
    def reposition(self, new_x: float, new_y: float) -> None:
        """Enhanced repositioning with smooth transition"""
        if new_x != self.x or new_y != self.y:
            try:
                logger.info(f"Repositioning lock animation from ({self.x}, {self.y}) to ({new_x}, {new_y})")
                
                # Calculate offset
                offset_x = new_x - self.x
                offset_y = new_y - self.y
                
                # Update position
                self.x = new_x
                self.y = new_y
                
                # Update visuals position
                self.visuals.x = new_x
                self.visuals.y = new_y
                
                # Move all canvas items
                try:
                    for component_group in self.visuals.lock_components.values():
                        for item_id in component_group:
                            try:
                                self.canvas.move(item_id, offset_x, offset_y)
                            except tk.TclError:
                                pass
                    
                    # Move particles
                    for particle in self.particle_system.particles:
                        particle['x'] += offset_x
                        particle['y'] += offset_y
                        particle['original_x'] += offset_x
                        particle['original_y'] += offset_y
                        
                        if particle['id']:
                            try:
                                self.canvas.move(particle['id'], offset_x, offset_y)
                            except tk.TclError:
                                pass
                                
                except Exception as e:
                    logger.warning(f"Error moving canvas items: {e}")
                    # Fallback: recreate everything
                    self.clear_visuals()
                    self.visuals = LockVisuals(self.canvas, new_x, new_y, self.size, self.config)
                    self.visuals.create_lock_components(self.level_name)
                    self._create_initial_particles()
                
                logger.info(f"Lock animation repositioned successfully")
                
            except Exception as e:
                logger.error(f"Failed to reposition lock animation: {e}") 