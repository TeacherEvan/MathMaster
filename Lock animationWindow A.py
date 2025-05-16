class LockAnimation:
    def __init__(self, canvas, x, y, size=100):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.size = size
        self.lock_parts = []
        self.unlocked_parts = 0
        self.total_parts = 4  # Number of steps in the math problem
        self.animation_speed = 2
        self.animation_running = False
        
        # Create initial lock parts
        self.create_lock_parts()
        
    def create_lock_parts(self):
        """Create the visual elements of the lock"""
        # Lock body
        body = self.canvas.create_rectangle(
            self.x - self.size//2, self.y - self.size//2,
            self.x + self.size//2, self.y + self.size//2,
            fill='#2C3E50', outline='#34495E', width=3
        )
        
        # Lock shackle (the U-shaped part)
        shackle = self.canvas.create_arc(
            self.x - self.size//3, self.y - self.size//2,
            self.x + self.size//3, self.y,
            start=0, extent=180,
            fill='#2C3E50', outline='#34495E', width=3
        )
        
        # Lock mechanism parts (4 segments)
        segment_height = self.size // 4
        for i in range(4):
            segment = self.canvas.create_rectangle(
                self.x - self.size//4, self.y - self.size//2 + i * segment_height,
                self.x + self.size//4, self.y - self.size//2 + (i + 1) * segment_height,
                fill='#E74C3C', outline='#C0392B', width=2
            )
            self.lock_parts.append(segment)
            
    def unlock_next_part(self):
        """Trigger animation for unlocking the next part"""
        if self.unlocked_parts < self.total_parts:
            self.animation_running = True
            self.animate_unlock(self.unlocked_parts)
            self.unlocked_parts += 1
            
    def animate_unlock(self, part_index):
        """Animate the unlocking of a specific part"""
        if not self.animation_running:
            return
            
        current_part = self.lock_parts[part_index]
        current_opacity = float(self.canvas.itemcget(current_part, 'fill'))
        
        # Fade out the locked part
        if current_opacity > 0:
            new_opacity = max(0, current_opacity - 0.1)
            self.canvas.itemconfig(current_part, fill=f'#{int(new_opacity * 255):02x}0000')
            self.canvas.after(20, lambda: self.animate_unlock(part_index))
        else:
            # Replace with unlocked part (green)
            self.canvas.itemconfig(current_part, fill='#27AE60', outline='#219A52')
            
            # Add sparkle effect
            self.create_sparkle_effect(part_index)
            
    def create_sparkle_effect(self, part_index):
        """Create sparkle animation effect when part is unlocked"""
        sparkle_points = []
        center_x = self.x
        center_y = self.y - self.size//2 + (part_index + 0.5) * (self.size//4)
        
        # Create sparkle particles
        for _ in range(8):
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(5, 15)
            x = center_x + math.cos(angle) * distance
            y = center_y + math.sin(angle) * distance
            
            sparkle = self.canvas.create_oval(
                x-2, y-2, x+2, y+2,
                fill='#F1C40F', outline=''
            )
            sparkle_points.append({
                'id': sparkle,
                'dx': math.cos(angle) * 2,
                'dy': math.sin(angle) * 2,
                'life': 20
            })
            
        self.animate_sparkles(sparkle_points)
        
    def animate_sparkles(self, sparkles):
        """Animate the sparkle particles"""
        for sparkle in sparkles[:]:
            if sparkle['life'] <= 0:
                self.canvas.delete(sparkle['id'])
                sparkles.remove(sparkle)
                continue
                
            self.canvas.move(
                sparkle['id'],
                sparkle['dx'],
                sparkle['dy']
            )
            sparkle['life'] -= 1
            
        if sparkles:
            self.canvas.after(20, lambda: self.animate_sparkles(sparkles))
            
    def reset(self):
        """Reset the lock to its initial state"""
        self.unlocked_parts = 0
        for part in self.lock_parts:
            self.canvas.itemconfig(part, fill='#E74C3C', outline='#C0392B')
