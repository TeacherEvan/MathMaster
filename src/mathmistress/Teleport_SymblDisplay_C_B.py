import tkinter as tk
from tkinter import Canvas
import math
import random
import time
import logging
from typing import Tuple, List, Dict

class GlowEffect:
    def __init__(self, canvas: Canvas):
        self.canvas = canvas
        self.glowing_symbols: Dict[int, dict] = {}  # Store glowing symbol info
        self.is_active = True
        
    def start_glow(self, symbol_id: int, is_left_side: bool) -> None:
        """Start a pulsating glow effect for a symbol"""
        # Base color based on symbol position
        base_color = "#FF4444" if is_left_side else "#4444FF"  # Red for left, Blue for right
        
        # Create glow circle behind symbol
        coords = self.canvas.bbox(symbol_id)
        if not coords:
            return
            
        center_x = (coords[0] + coords[2]) / 2
        center_y = (coords[1] + coords[3]) / 2
        size = max(coords[2] - coords[0], coords[3] - coords[1])
        
        glow = self.canvas.create_oval(
            center_x - size/1.5, center_y - size/1.5,
            center_x + size/1.5, center_y + size/1.5,
            fill=base_color,
            stipple='gray50',
            state='normal',
            tags=('glow',)
        )
        
        # Store info for animation
        self.glowing_symbols[symbol_id] = {
            'glow_id': glow,
            'base_color': base_color,
            'center': (center_x, center_y),
            'size': size,
            'phase': 0.0
        }
        
        # Ensure animation is running
        if len(self.glowing_symbols) == 1:  # First symbol added
            self._animate_glows()
    
    def stop_glow(self, symbol_id: int) -> None:
        """Stop the glow effect for a symbol"""
        if symbol_id in self.glowing_symbols:
            glow_info = self.glowing_symbols.pop(symbol_id)
            self.canvas.delete(glow_info['glow_id'])
    
    def _animate_glows(self) -> None:
        """Animate all active glow effects"""
        if not self.is_active or not self.glowing_symbols:
            return
            
        for symbol_id, info in self.glowing_symbols.items():
            # Update phase
            info['phase'] += 0.1
            
            # Calculate current size multiplier (1.0 to 1.3)
            size_mult = 1.0 + 0.3 * abs(math.sin(info['phase']))
            
            # Calculate current opacity (0.2 to 0.6)
            opacity = 0.2 + 0.4 * abs(math.sin(info['phase']))
            
            # Update glow position and size
            size = info['size'] * size_mult
            self.canvas.coords(
                info['glow_id'],
                info['center'][0] - size/1.5,
                info['center'][1] - size/1.5,
                info['center'][0] + size/1.5,
                info['center'][1] + size/1.5
            )
            
            # Update stipple pattern based on opacity
            stipple = f'gray{int(opacity * 100)}'
            self.canvas.itemconfig(info['glow_id'], stipple=stipple)
        
        # Continue animation
        self.canvas.after(50, self._animate_glows)

class PortalEffect:
    def __init__(self, canvas: Canvas):
        self.canvas = canvas
        self.portal_particles: List[Dict[str, any]] = [] # Store particle IDs and their properties
        self.portal_colors = [
            "#FF00FF",  # Magenta
            "#00FFFF",  # Cyan
            "#FF69B4",  # Hot Pink
            "#4B0082",  # Indigo
            "#7FFFD4",  # Aquamarine
            "#FF1493"   # Deep Pink
        ]
        
    def create_portal(self, x: float, y: float, duration: float = 1.0) -> None:
        """Creates an LSD-style portal effect at the given coordinates"""
        radius = 5
        max_radius = 40
        particles_spiraling = 12
        burst_particles_count = 15 # For initial burst
        burst_particle_life = 10 # Frames for burst particles to live

        # Initial Burst Effect
        for _ in range(burst_particles_count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(1, 3)
            burst_color = random.choice(self.portal_colors)
            size = random.uniform(1, 3)
            particle_id = self.canvas.create_oval(
                x - size, y - size, x + size, y + size,
                fill=burst_color, outline=''
            )
            self.portal_particles.append({
                'id': particle_id, 'x': x, 'y': y, 'vx': math.cos(angle) * speed, 'vy': math.sin(angle) * speed,
                'life': burst_particle_life, 'type': 'burst', 'original_size': size, 'color': burst_color
            })
        
        def animate_portal(start_time: float, current_radius: float, frame_count: int = 0) -> None:
            if not self.canvas.winfo_exists(): return

            # Animate existing burst particles
            particles_to_remove_from_main_list = []
            for p_data in self.portal_particles[:]: # Iterate copy for safe removal
                if p_data.get('type') == 'burst':
                    p_data['x'] += p_data['vx']
                    p_data['y'] += p_data['vy']
                    p_data['life'] -= 1
                    new_size = p_data['original_size'] * (p_data['life'] / burst_particle_life)
                    if p_data['life'] <= 0 or new_size <= 0:
                        self.canvas.delete(p_data['id'])
                        particles_to_remove_from_main_list.append(p_data)
                    else:
                        try:
                            self.canvas.coords(p_data['id'], 
                                           p_data['x'] - new_size, p_data['y'] - new_size, 
                                           p_data['x'] + new_size, p_data['y'] + new_size)
                            # Optional: fade color for burst particles
                            # current_opacity = max(0, p_data['life'] / burst_particle_life)
                            # faded_burst_color = self._apply_opacity(p_data['color'], current_opacity) 
                            # self.canvas.itemconfig(p_data['id'], fill=faded_burst_color)
                        except tk.TclError: # Item might be gone
                            particles_to_remove_from_main_list.append(p_data)
            
            for p_to_remove in particles_to_remove_from_main_list:
                 if p_to_remove in self.portal_particles: self.portal_particles.remove(p_to_remove)

            # Spiraling Portal Logic
            if time.time() - start_time > duration and all(p.get('type') != 'spiral' for p in self.portal_particles):
                self._cleanup_portal() # Cleans up any remaining burst particles if portal duration ends
                return
                
            # Clear previous spiraling particles (those tagged as 'spiral')
            current_spiral_particles = [p for p in self.portal_particles if p.get('type') == 'spiral']
            for p_data in current_spiral_particles:
                self.canvas.delete(p_data['id'])
                self.portal_particles.remove(p_data)
            
            # Create new spiraling particles if portal is still active
            if time.time() - start_time <= duration:
                for i in range(particles_spiraling):
                    angle = (i / particles_spiraling) * 2 * math.pi + (frame_count * 0.1) # Rotate spiral over time
                    color = random.choice(self.portal_colors)
                    
                    # Pulsating radius for the spiral itself
                    pulse_factor = 0.8 + 0.2 * math.sin(frame_count * 0.2)
                    effective_radius = current_radius * pulse_factor

                    spiral_x = x + effective_radius * math.cos(angle + time.time() * 5)
                    spiral_y = y + effective_radius * math.sin(angle + time.time() * 5)
                    
                    particle_size = random.uniform(2,4) # random size for spiral particles

                    particle = self.canvas.create_oval(
                        spiral_x - particle_size, spiral_y - particle_size,
                        spiral_x + particle_size, spiral_y + particle_size,
                        fill=color, outline=color
                    )
                    self.portal_particles.append({'id': particle, 'type': 'spiral'}) # Tag as spiral
            
            # Update portal size with pulsing effect
            new_radius = current_radius
            if current_radius < max_radius and time.time() - start_time <= duration:
                new_radius += 2
            
            self.canvas.after(30, lambda: animate_portal(start_time, new_radius, frame_count + 1))
            
        animate_portal(time.time(), radius)
    
    def _cleanup_portal(self) -> None:
        """Cleans up portal particles"""
        for particle_data in self.portal_particles[:]: # Iterate copy for safe removal
            try:
                self.canvas.delete(particle_data['id'])
            except tk.TclError:
                pass # Item might be gone
        self.portal_particles.clear()

    # Helper for fading, if used for burst particles. Requires canvas access.
    # def _apply_opacity(self, hex_color, alpha):
    #     r_orig, g_orig, b_orig = int(hex_color[1:3],16), int(hex_color[3:5],16), int(hex_color[5:7],16)
    #     # Assuming black background for simplicity of fading to transparent over black
    #     r = int(r_orig * alpha)
    #     g = int(g_orig * alpha)
    #     b = int(b_orig * alpha)
    #     return f"#{r:02x}{g:02x}{b:02x}"

class ErrorEffect:
    def __init__(self, canvas: Canvas):
        self.canvas = canvas
        self.overlay_id = None
        self.crack_ids = []
        self.shockwave_ids = []  # New: for shockwave effect
        
    def show_error(self) -> None:
        """Shows the error effect with red overlay and cracks"""
        # Create shockwave first
        self._create_shockwave()
        
        # Delay the overlay and cracks slightly
        self.canvas.after(200, self._show_overlay_and_cracks)
    
    def _create_shockwave(self) -> None:
        """Create and animate a shockwave effect for error feedback"""
        def get_stipple_pattern(opacity):
            """Convert opacity (0-1) to valid stipple pattern"""
            if opacity >= 0.75:
                return 'gray75'
            elif opacity >= 0.5:
                return 'gray50'
            elif opacity >= 0.25:
                return 'gray25'
            else:
                return 'gray12'

        def animate_shockwave(radius, opacity):
            try:
                # Get center coordinates
                center_x = self.canvas.winfo_width() / 2
                center_y = self.canvas.winfo_height() / 2
                
                # Create shockwave with valid stipple pattern
                shockwave = self.canvas.create_oval(
                    center_x - radius, center_y - radius,
                    center_x + radius, center_y + radius,
                    outline='#ff0000',  # Red color for error feedback
                    width=2,
                    stipple=get_stipple_pattern(opacity)
                )
                
                # Animate the shockwave
                if opacity > 0:
                    self.canvas.after(50, lambda: animate_shockwave(radius + 5, opacity - 0.1))
                else:
                    self.canvas.delete(shockwave)
                    
            except Exception as e:
                logging.error(f"Error in shockwave animation: {e}")
                
        # Start the animation
        animate_shockwave(10, 1.0)
    
    def _show_overlay_and_cracks(self) -> None:
        """Shows the overlay and cracks with original timing"""
        try:
            # Create semi-transparent red overlay using stipple instead of alpha
            self.overlay_id = self.canvas.create_rectangle(
                0, 0, self.canvas.winfo_width(), self.canvas.winfo_height(),
                fill='#FF0000', stipple='gray25', state='normal'  # gray25 for 25% opacity
            )
            
            # Create cracks
            self._create_cracks()
            
            # Start fade out after 1 second
            self.canvas.after(1000, self._start_fade_out)
            
        except Exception as e:
            logging.error(f"Error showing overlay and cracks: {e}")
    
    def _create_cracks(self) -> None:
        """Creates crack effects on the screen"""
        center_x = self.canvas.winfo_width() / 2
        center_y = self.canvas.winfo_height() / 2
        
        for _ in range(8):  # Create 8 cracks
            points = [(center_x, center_y)]
            current_x, current_y = center_x, center_y
            
            # Generate random crack path
            angle = random.uniform(0, 2 * math.pi)
            length = random.uniform(50, 200)
            
            for _ in range(5):  # 5 segments per crack
                angle += random.uniform(-0.5, 0.5)  # Slight angle variation
                segment_length = length / 5
                
                new_x = current_x + math.cos(angle) * segment_length
                new_y = current_y + math.sin(angle) * segment_length
                
                points.append((new_x, new_y))
                current_x, current_y = new_x, new_y
            
            # Create the crack line with red glow effect
            crack = self.canvas.create_line(
                *[coord for point in points for coord in point],
                fill='#FF0000',
                width=2,
                stipple='gray75'
            )
            self.crack_ids.append(crack)
    
    def _start_fade_out(self) -> None:
        """Starts the fade out animation"""
        self._fade_out(1.0, 5.0)  # 5 second fade
    
    def _get_valid_stipple(self, opacity):
        """Convert opacity (0-1) to valid stipple pattern"""
        if opacity <= 0.12:
            return 'gray12'
        elif opacity <= 0.25:
            return 'gray25'
        elif opacity <= 0.50:
            return 'gray50'
        else:
            return 'gray75'

    def _fade_out(self, current_alpha: float, duration: float, start_time: float = None) -> None:
        """Handles the fade out animation"""
        if start_time is None:
            start_time = time.time()
        
        elapsed = time.time() - start_time
        if elapsed >= duration:
            # Clean up
            if self.overlay_id:
                self.canvas.delete(self.overlay_id)
            for crack_id in self.crack_ids:
                self.canvas.delete(crack_id)
            return
        
        # Calculate new alpha
        new_alpha = 1.0 - (elapsed / duration)
        if new_alpha < 0:
            new_alpha = 0
            
        # Get valid stipple pattern
        stipple_pattern = self._get_valid_stipple(new_alpha)
            
        # Update overlay and crack transparency
        if self.overlay_id:
            self.canvas.itemconfig(self.overlay_id, stipple=stipple_pattern)
        for crack_id in self.crack_ids:
            self.canvas.itemconfig(crack_id, stipple=stipple_pattern)
            
        self.canvas.after(16, lambda: self._fade_out(new_alpha, duration, start_time))

class SymbolTeleportManager:
    def __init__(self, canvas_c: Canvas, canvas_b: Canvas):
        self.canvas_c = canvas_c
        self.canvas_b = canvas_b
        self.portal_effect_c = PortalEffect(canvas_c)
        self.portal_effect_b = PortalEffect(canvas_b)
        self.error_effect = ErrorEffect(canvas_c)
        self.glow_effect = GlowEffect(canvas_b)
        self.active_symbols: Dict[int, bool] = {}  # Track active symbols and their side
        self.teleport_timers = []
        self.active_particles = []
        self.currently_teleporting = False
        
    def teleport_symbol(self, symbol_id: int, start_pos: Tuple[float, float], 
                       end_pos: Tuple[float, float], is_correct: bool, 
                       is_left_side: bool = True) -> None:
        """Handles the symbol teleportation animation"""
        # Start portal effect at source with sparkles
        self.portal_effect_c.create_portal(start_pos[0], start_pos[1])
        
        if is_correct:
            # Create destination portal after a short delay
            self.canvas_c.after(500, lambda: self._handle_correct_teleport(
                symbol_id, end_pos, is_left_side))
        else:
            # Red error effects have been disabled as per user request
            # Only the crack effects from error_animation.py will be shown
            pass
            
        logging.info(f"Symbol teleport animation triggered - Correct: {is_correct}")
    
    def _handle_correct_teleport(self, symbol_id: int, end_pos: Tuple[float, float], 
                               is_left_side: bool) -> None:
        """Handle the correct symbol teleportation"""
        # Check if end_pos is None
        if end_pos is None:
            logging.error(f"Cannot handle teleport: end_pos is None for symbol_id {symbol_id}")
            return
        
        # Create destination portal
        self.portal_effect_b.create_portal(end_pos[0], end_pos[1])
        
        # Start glow effect after a short delay
        self.canvas_b.after(1000, lambda: self._start_symbol_glow(
            symbol_id, is_left_side))
    
    def _start_symbol_glow(self, symbol_id: int, is_left_side: bool) -> None:
        """Start the glow effect for a correctly placed symbol"""
        self.active_symbols[symbol_id] = is_left_side
        self.glow_effect.start_glow(symbol_id, is_left_side)
    
    def remove_symbol(self, symbol_id: int) -> None:
        """Remove a symbol's effects"""
        if symbol_id in self.active_symbols:
            self.glow_effect.stop_glow(symbol_id)
            del self.active_symbols[symbol_id] 

    def clear_pending_operations(self):
        """Clear any pending teleport operations to prevent errors during transitions"""
        try:
            # Cancel any ongoing animations
            if hasattr(self, 'teleport_timers') and self.teleport_timers:
                for timer_id in self.teleport_timers:
                    try:
                        if self.canvas_c.winfo_exists():
                            self.canvas_c.after_cancel(timer_id)
                    except Exception:
                        pass
                self.teleport_timers = []
                
            # Cancel any active particles
            if hasattr(self, 'active_particles') and self.active_particles:
                for particle_id in self.active_particles:
                    try:
                        if self.canvas_c.winfo_exists():
                            self.canvas_c.delete(particle_id)
                    except Exception:
                        pass
                self.active_particles = []
                
            # Reset any other state
            self.currently_teleporting = False
            
            logging.info("Teleport manager pending operations cleared")
            return True
        except Exception as e:
            logging.error(f"Error clearing teleport operations: {e}")
            return False 