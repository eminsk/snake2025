"""
Professional Snake Game with Modern GUI
Optimized for performance and minimal memory usage
Author: letsley Games
Date: 2025
"""

import pygame
import random
from collections import deque
from enum import Enum
from typing import Tuple, List, Optional
import math
import json
from pathlib import Path


class Direction(Enum):
    """Enumeration for snake movement directions"""
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)


class GameState(Enum):
    """Game state enumeration"""
    MENU = "menu"
    PLAYING = "playing"
    PAUSED = "paused"
    GAME_OVER = "game_over"


class SnakeGame:
    """
    Professional Snake Game implementation with modern GUI
    Optimized for performance using deque and minimal conditionals
    """
    
    # Color palette - Modern dark theme with neon accents
    COLORS = {
        'background': (15, 15, 25),
        'grid': (25, 25, 35),
        'snake_head': (50, 255, 150),
        'snake_body': (40, 200, 120),
        'snake_gradient': [(40, 200, 120), (30, 150, 90), (20, 100, 60)],
        'food': (255, 100, 120),
        'special_food': (255, 215, 0),
        'text': (255, 255, 255),
        'text_shadow': (100, 100, 100),
        'game_over': (255, 50, 50),
        'pause': (255, 200, 50),
        'particle': (100, 255, 200),
        'button': (60, 60, 80),
        'button_hover': (80, 80, 100),
        'glow': (100, 255, 200, 50)
    }
    
    def __init__(self, width: int = 800, height: int = 600, cell_size: int = 20):
        """
        Initialize the Snake game
        
        Args:
            width: Window width in pixels
            height: Window height in pixels
            cell_size: Size of each grid cell
        """
        pygame.init()
        pygame.mixer.init()
        
        # Display settings
        self.width = width
        self.height = height
        self.cell_size = cell_size
        self.grid_width = width // cell_size
        self.grid_height = height // cell_size
        
        # Initialize display with modern settings
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Modern Snake Game - Professional Edition")
        
        # Clock for FPS control
        self.clock = pygame.time.Clock()
        self.fps = 10
        
        # Fonts for modern UI
        self.font_large = pygame.font.Font(None, 72)
        self.font_medium = pygame.font.Font(None, 48)
        self.font_small = pygame.font.Font(None, 32)
        
        # Game state
        self.state = GameState.MENU
        self.score = 0
        self.high_score = self._load_high_score()
        
        # Snake data structure - optimized with deque
        self.snake = deque()
        self.direction = Direction.RIGHT
        self.next_direction = Direction.RIGHT
        self.growing = False
        
        # Food
        self.food_pos = None
        self.special_food_pos = None
        self.special_food_timer = 0
        
        # Visual effects
        self.particles = []
        self.animations = []
        self.transition_alpha = 0
        
        # Performance optimization - pre-calculate common values
        self.direction_opposites = {
            Direction.UP: Direction.DOWN,
            Direction.DOWN: Direction.UP,
            Direction.LEFT: Direction.RIGHT,
            Direction.RIGHT: Direction.LEFT
        }
        
        # Input mapping for cleaner code
        self.key_mapping = {
            pygame.K_UP: Direction.UP,
            pygame.K_DOWN: Direction.DOWN,
            pygame.K_LEFT: Direction.LEFT,
            pygame.K_RIGHT: Direction.RIGHT,
            pygame.K_w: Direction.UP,
            pygame.K_s: Direction.DOWN,
            pygame.K_a: Direction.LEFT,
            pygame.K_d: Direction.RIGHT
        }
        
        # Initialize game
        self._reset_game()
    
    def _load_high_score(self) -> int:
        """Load high score from file"""
        try:
            save_file = Path("high_score.json")
            return json.loads(save_file.read_text()).get("high_score", 0) if save_file.exists() else 0
        except:
            return 0
    
    def _save_high_score(self):
        """Save high score to file"""
        try:
            Path("high_score.json").write_text(json.dumps({"high_score": self.high_score}))
        except:
            pass
    
    def _reset_game(self):
        """Reset game state for new game"""
        # Initialize snake at center
        center_x = self.grid_width // 2
        center_y = self.grid_height // 2
        
        self.snake.clear()
        self.snake.extend([
            (center_x - 2, center_y),
            (center_x - 1, center_y),
            (center_x, center_y)
        ])
        
        self.direction = Direction.RIGHT
        self.next_direction = Direction.RIGHT
        self.score = 0
        self.growing = False
        self.special_food_timer = 0
        
        self._spawn_food()
        self.particles.clear()
        self.animations.clear()
    
    def _spawn_food(self):
        """Spawn food at random location not occupied by snake"""
        # Use set for O(1) lookup performance
        snake_positions = set(self.snake)
        
        # Find valid positions
        valid_positions = [
            (x, y) 
            for x in range(self.grid_width) 
            for y in range(self.grid_height)
            if (x, y) not in snake_positions
        ]
        
        self.food_pos = random.choice(valid_positions) if valid_positions else None
        
        # Spawn special food occasionally
        self.special_food_pos = (
            random.choice(valid_positions) 
            if valid_positions and random.random() < 0.1 
            else None
        )
        self.special_food_timer = 150 if self.special_food_pos else 0
    
    def _handle_input(self, event: pygame.event.Event):
        """Handle keyboard input events"""
        # Use dictionary lookup instead of if-else chains
        new_direction = self.key_mapping.get(event.key)
        
        if new_direction and new_direction != self.direction_opposites.get(self.direction):
            self.next_direction = new_direction
    
    def _move_snake(self):
        """Move snake in current direction"""
        self.direction = self.next_direction
        head = self.snake[-1]
        dx, dy = self.direction.value
        new_head = (head[0] + dx, head[1] + dy)
        
        # Check collisions using mathematical operations
        wall_collision = not (0 <= new_head[0] < self.grid_width and 
                             0 <= new_head[1] < self.grid_height)
        self_collision = new_head in self.snake
        
        if wall_collision or self_collision:
            self._game_over()
            return
        
        # Move snake
        self.snake.append(new_head)
        
        # Check food collision
        food_eaten = new_head == self.food_pos
        special_eaten = new_head == self.special_food_pos
        
        if food_eaten or special_eaten:
            points = 10 if food_eaten else 50
            self.score += points
            self.growing = True
            self._create_eat_effect(new_head, special_eaten)
            
            if special_eaten:
                self.special_food_pos = None
                self.special_food_timer = 0
            
            if food_eaten:
                self._spawn_food()
        
        # Remove tail if not growing
        if not self.growing:
            self.snake.popleft()
        else:
            self.growing = False
    
    def _create_eat_effect(self, pos: Tuple[int, int], special: bool = False):
        """Create particle effect when food is eaten"""
        screen_x = pos[0] * self.cell_size + self.cell_size // 2
        screen_y = pos[1] * self.cell_size + self.cell_size // 2
        
        # Create multiple particles
        particle_count = 20 if special else 10
        color = self.COLORS['special_food'] if special else self.COLORS['food']
        
        for _ in range(particle_count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2, 6)
            self.particles.append({
                'x': screen_x,
                'y': screen_y,
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed,
                'life': 30,
                'color': color,
                'size': random.randint(2, 5)
            })
    
    def _update_particles(self):
        """Update particle positions and remove dead particles"""
        self.particles = [
            {
                **p,
                'x': p['x'] + p['vx'],
                'y': p['y'] + p['vy'],
                'vy': p['vy'] + 0.3,  # Gravity
                'life': p['life'] - 1,
                'size': max(1, p['size'] - 0.1)
            }
            for p in self.particles
            if p['life'] > 0
        ]
    
    def _game_over(self):
        """Handle game over state"""
        self.state = GameState.GAME_OVER
        if self.score > self.high_score:
            self.high_score = self.score
            self._save_high_score()
    
    def _draw_grid(self):
        """Draw subtle grid pattern"""
        for x in range(0, self.width, self.cell_size):
            pygame.draw.line(self.screen, self.COLORS['grid'], 
                           (x, 0), (x, self.height), 1)
        for y in range(0, self.height, self.cell_size):
            pygame.draw.line(self.screen, self.COLORS['grid'], 
                           (0, y), (self.width, y), 1)
    
    def _draw_snake(self):
        """Draw snake with gradient effect"""
        segment_count = len(self.snake)
        
        for i, segment in enumerate(self.snake):
            # Calculate color gradient
            gradient_ratio = i / max(segment_count - 1, 1)
            color = self._interpolate_color(
                self.COLORS['snake_gradient'][0],
                self.COLORS['snake_gradient'][-1],
                gradient_ratio
            )
            
            # Draw segment with rounded corners
            rect = pygame.Rect(
                segment[0] * self.cell_size,
                segment[1] * self.cell_size,
                self.cell_size,
                self.cell_size
            )
            
            # Draw main body
            pygame.draw.rect(self.screen, color, rect, border_radius=4)
            
            # Draw head with special effect
            if i == segment_count - 1:
                pygame.draw.rect(self.screen, self.COLORS['snake_head'], rect, border_radius=6)
                # Add glow effect
                self._draw_glow(rect.center, self.COLORS['snake_head'], 20)
    
    def _interpolate_color(self, color1: Tuple, color2: Tuple, ratio: float) -> Tuple:
        """Interpolate between two colors"""
        return tuple(int(c1 + (c2 - c1) * ratio) for c1, c2 in zip(color1, color2))
    
    def _draw_glow(self, pos: Tuple[int, int], color: Tuple, radius: int):
        """Draw glow effect"""
        surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        steps = 10
        for i in range(steps):
            alpha = int(50 * (1 - i / steps))
            r = int(radius * (1 - i / steps))
            glow_color = (*color, alpha)
            pygame.draw.circle(surf, glow_color, (radius, radius), r)
        self.screen.blit(surf, (pos[0] - radius, pos[1] - radius))
    
    def _draw_food(self):
        """Draw food with pulsing effect"""
        if self.food_pos:
            # Calculate pulse effect
            pulse = abs(math.sin(pygame.time.get_ticks() * 0.005)) * 0.2 + 0.8
            size = int(self.cell_size * pulse)
            offset = (self.cell_size - size) // 2
            
            rect = pygame.Rect(
                self.food_pos[0] * self.cell_size + offset,
                self.food_pos[1] * self.cell_size + offset,
                size,
                size
            )
            pygame.draw.rect(self.screen, self.COLORS['food'], rect, border_radius=size//2)
            
        # Draw special food with rotation
        if self.special_food_pos and self.special_food_timer > 0:
            self.special_food_timer -= 1
            
            center = (
                self.special_food_pos[0] * self.cell_size + self.cell_size // 2,
                self.special_food_pos[1] * self.cell_size + self.cell_size // 2
            )
            
            # Draw rotating star
            angle = pygame.time.get_ticks() * 0.002
            points = []
            for i in range(8):
                a = angle + i * math.pi / 4
                r = self.cell_size // 2 if i % 2 == 0 else self.cell_size // 4
                x = center[0] + math.cos(a) * r
                y = center[1] + math.sin(a) * r
                points.append((x, y))
            
            pygame.draw.polygon(self.screen, self.COLORS['special_food'], points)
            self._draw_glow(center, self.COLORS['special_food'], 25)
            
            if self.special_food_timer == 0:
                self.special_food_pos = None
    
    def _draw_particles(self):
        """Draw particle effects"""
        for particle in self.particles:
            alpha = int(255 * (particle['life'] / 30))
            color = (*particle['color'], alpha)
            
            surf = pygame.Surface((particle['size'] * 2, particle['size'] * 2), pygame.SRCALPHA)
            pygame.draw.circle(surf, color, 
                             (particle['size'], particle['size']), 
                             particle['size'])
            self.screen.blit(surf, 
                           (particle['x'] - particle['size'], 
                            particle['y'] - particle['size']))
    
    def _draw_ui(self):
        """Draw user interface elements"""
        # Score display with shadow
        score_text = f"Score: {self.score}"
        self._draw_text_with_shadow(score_text, (20, 20), self.font_medium)
        
        # High score
        high_score_text = f"Best: {self.high_score}"
        self._draw_text_with_shadow(high_score_text, (20, 60), self.font_small)
        
        # FPS display
        fps_text = f"Speed: {self.fps}"
        self._draw_text_with_shadow(fps_text, (self.width - 150, 20), self.font_small)
    
    def _draw_text_with_shadow(self, text: str, pos: Tuple[int, int], font):
        """Draw text with shadow effect"""
        # Shadow
        shadow_surf = font.render(text, True, self.COLORS['text_shadow'])
        self.screen.blit(shadow_surf, (pos[0] + 2, pos[1] + 2))
        
        # Main text
        text_surf = font.render(text, True, self.COLORS['text'])
        self.screen.blit(text_surf, pos)
    
    def _draw_menu(self):
        """Draw main menu"""
        # Title with animation
        title_y = 100 + math.sin(pygame.time.get_ticks() * 0.002) * 10
        title_text = "SNAKE"
        title_surf = self.font_large.render(title_text, True, self.COLORS['snake_head'])
        title_rect = title_surf.get_rect(center=(self.width // 2, title_y))
        self.screen.blit(title_surf, title_rect)
        
        # Subtitle
        subtitle_text = "Professional Edition"
        subtitle_surf = self.font_medium.render(subtitle_text, True, self.COLORS['text'])
        subtitle_rect = subtitle_surf.get_rect(center=(self.width // 2, title_y + 60))
        self.screen.blit(subtitle_surf, subtitle_rect)
        
        # Instructions
        instructions = [
            "Press SPACE to Start",
            "Use Arrow Keys or WASD to Move",
            "Press P to Pause",
            "Press ESC to Quit"
        ]
        
        y_offset = 250
        for instruction in instructions:
            inst_surf = self.font_small.render(instruction, True, self.COLORS['text'])
            inst_rect = inst_surf.get_rect(center=(self.width // 2, y_offset))
            self.screen.blit(inst_surf, inst_rect)
            y_offset += 40
        
        # High score display
        if self.high_score > 0:
            hs_text = f"High Score: {self.high_score}"
            hs_surf = self.font_medium.render(hs_text, True, self.COLORS['special_food'])
            hs_rect = hs_surf.get_rect(center=(self.width // 2, self.height - 100))
            self.screen.blit(hs_surf, hs_rect)
    
    def _draw_game_over(self):
        """Draw game over screen"""
        # Darken background
        overlay = pygame.Surface((self.width, self.height))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        # Game over text
        go_text = "GAME OVER"
        go_surf = self.font_large.render(go_text, True, self.COLORS['game_over'])
        go_rect = go_surf.get_rect(center=(self.width // 2, self.height // 2 - 100))
        self.screen.blit(go_surf, go_rect)
        
        # Score
        score_text = f"Final Score: {self.score}"
        score_surf = self.font_medium.render(score_text, True, self.COLORS['text'])
        score_rect = score_surf.get_rect(center=(self.width // 2, self.height // 2))
        self.screen.blit(score_surf, score_rect)
        
        # New high score notification
        if self.score == self.high_score and self.score > 0:
            nh_text = "NEW HIGH SCORE!"
            nh_surf = self.font_medium.render(nh_text, True, self.COLORS['special_food'])
            nh_rect = nh_surf.get_rect(center=(self.width // 2, self.height // 2 + 50))
            self.screen.blit(nh_surf, nh_rect)
        
        # Restart instruction
        restart_text = "Press SPACE to Play Again or ESC to Quit"
        restart_surf = self.font_small.render(restart_text, True, self.COLORS['text'])
        restart_rect = restart_surf.get_rect(center=(self.width // 2, self.height - 100))
        self.screen.blit(restart_surf, restart_rect)
    
    def _draw_pause(self):
        """Draw pause overlay"""
        # Darken background
        overlay = pygame.Surface((self.width, self.height))
        overlay.set_alpha(64)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        # Pause text
        pause_text = "PAUSED"
        pause_surf = self.font_large.render(pause_text, True, self.COLORS['pause'])
        pause_rect = pause_surf.get_rect(center=(self.width // 2, self.height // 2))
        self.screen.blit(pause_surf, pause_rect)
        
        # Resume instruction
        resume_text = "Press P to Resume"
        resume_surf = self.font_small.render(resume_text, True, self.COLORS['text'])
        resume_rect = resume_surf.get_rect(center=(self.width // 2, self.height // 2 + 60))
        self.screen.blit(resume_surf, resume_rect)
    
    def run(self):
        """Main game loop"""
        running = True
        
        while running:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    
                elif event.type == pygame.KEYDOWN:
                    # Global keys
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    
                    # State-specific keys
                    elif self.state == GameState.MENU:
                        if event.key == pygame.K_SPACE:
                            self._reset_game()
                            self.state = GameState.PLAYING
                    
                    elif self.state == GameState.PLAYING:
                        if event.key == pygame.K_p:
                            self.state = GameState.PAUSED
                        else:
                            self._handle_input(event)
                    
                    elif self.state == GameState.PAUSED:
                        if event.key == pygame.K_p:
                            self.state = GameState.PLAYING
                    
                    elif self.state == GameState.GAME_OVER:
                        if event.key == pygame.K_SPACE:
                            self._reset_game()
                            self.state = GameState.PLAYING
            
            # Update game logic
            if self.state == GameState.PLAYING:
                self._move_snake()
                self._update_particles()
                
                # Increase speed based on score
                self.fps = min(10 + self.score // 50, 20)
            
            # Clear screen
            self.screen.fill(self.COLORS['background'])
            
            # Draw based on state
            if self.state == GameState.PLAYING:
                self._draw_grid()
                self._draw_food()
                self._draw_snake()
                self._draw_particles()
                self._draw_ui()
            elif self.state == GameState.MENU:
                self._draw_menu()
            elif self.state == GameState.PAUSED:
                self._draw_grid()
                self._draw_food()
                self._draw_snake()
                self._draw_ui()
                self._draw_pause()
            elif self.state == GameState.GAME_OVER:
                self._draw_grid()
                self._draw_snake()
                self._draw_game_over()
            
            # Update display
            pygame.display.flip()
            self.clock.tick(self.fps)
        
        # Cleanup
        pygame.quit()


def main():
    """Entry point for the game"""
    game = SnakeGame(800, 600, 20)
    game.run()


if __name__ == "__main__":
    main()