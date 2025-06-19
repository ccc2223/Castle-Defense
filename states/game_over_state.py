# states/game_over_state.py
"""
Game over state for Castle Defense
"""
import pygame
import math
from .game_state import GameState

class GameOverState(GameState):
    """
    Game over state - displayed when the player loses, but allows continuing
    """
    def __init__(self, game):
        """
        Initialize game over state
        
        Args:
            game: Game instance
        """
        super().__init__(game)
        self.time_in_state = 0
        self.auto_continue_time = 15.0  # Auto-continue after 15 seconds
        self.setback_wave = 1  # Default setback
        self.current_wave = 0  # Will be set when entering the state
        
        # Colors for styling (matched with UI system)
        self.HEADER_COLOR = (255, 200, 100)
        self.TEXT_COLOR = (220, 220, 220)
        self.SUBTEXT_COLOR = (180, 180, 180)
        self.CARD_BG_COLOR = (60, 60, 60)
        self.BUTTON_COLOR = (80, 80, 80)
        self.POSITIVE_COLOR = (100, 255, 100)
        self.NEGATIVE_COLOR = (255, 100, 100)
        
        # Font objects
        self.title_font = pygame.font.Font(None, 36)
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 18)
        
        # Button states
        self.continue_button_hover = False
        self.quit_button_hover = False
    
    def enter(self):
        """Called when entering game over state"""
        self.time_in_state = 0
        self.current_wave = self.game.wave_manager.current_wave
        self.continue_button_hover = False
        self.quit_button_hover = False
        
        # Calculate setback wave based on current progress
        if self.current_wave >= 11:
            # If player has reached wave 11+, setback 10 waves
            self.setback_wave = max(1, self.current_wave - 10)
        else:
            # Otherwise, reset to wave 1
            self.setback_wave = 1
    
    def handle_events(self, events):
        """
        Handle events during game over state
        
        Args:
            events: List of pygame events
            
        Returns:
            Boolean indicating if events were handled
        """
        # Reset button hover states
        self.continue_button_hover = False
        self.quit_button_hover = False
        
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    # Exit game on Escape
                    self.game.running = False
                    return True
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    # Continue immediately on Enter/Space
                    self.continue_game()
                    return True
            
            # Handle mouse movement for button hover effects
            elif event.type == pygame.MOUSEMOTION:
                mouse_pos = pygame.mouse.get_pos()
                
                # Get button rectangles
                continue_button_rect, quit_button_rect = self.get_button_rects()
                
                # Update hover states
                self.continue_button_hover = continue_button_rect.collidepoint(mouse_pos)
                self.quit_button_hover = quit_button_rect.collidepoint(mouse_pos)
            
            # Handle mouse clicks on buttons
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                
                # Get button rectangles
                continue_button_rect, quit_button_rect = self.get_button_rects()
                
                # Check for button clicks
                if continue_button_rect.collidepoint(mouse_pos):
                    self.continue_game()
                    return True
                elif quit_button_rect.collidepoint(mouse_pos):
                    self.game.running = False
                    return True
        
        return False
    
    def get_button_rects(self):
        """
        Get the rectangles for the continue and quit buttons
        
        Returns:
            Tuple of (continue_button_rect, quit_button_rect)
        """
        # Calculate card position and size
        card_width = self.game.scale_value(500)
        card_height = self.game.scale_value(400)
        card_rect = pygame.Rect(
            (self.game.WINDOW_WIDTH - card_width) // 2,
            (self.game.WINDOW_HEIGHT - card_height) // 2,
            card_width,
            card_height
        )
        
        # Calculate button dimensions
        button_width = self.game.scale_value(180)
        button_height = self.game.scale_value(40)
        
        # Create continue button rect
        continue_button_rect = pygame.Rect(
            card_rect.left + self.game.scale_value(50),
            card_rect.bottom - self.game.scale_value(120),
            button_width,
            button_height
        )
        
        # Create quit button rect
        quit_button_rect = pygame.Rect(
            card_rect.right - self.game.scale_value(50) - button_width,
            card_rect.bottom - self.game.scale_value(120),
            button_width,
            button_height
        )
        
        return continue_button_rect, quit_button_rect
    
    def update(self, dt):
        """
        Update game over logic
        
        Args:
            dt: Time delta in seconds
        """
        self.time_in_state += dt
        
        # Auto-continue after the timer expires
        if self.time_in_state >= self.auto_continue_time:
            self.continue_game()
    
    def continue_game(self):
        """Reset castle health and continue the game from setback wave"""
        # Reset castle health to full
        self.game.castle.health = self.game.castle.max_health
        
        # Set the wave number to the setback wave
        self.game.wave_manager.current_wave = self.setback_wave - 1  # -1 because starting next wave increments
        
        # Clear any active monsters and reset wave state
        self.game.wave_manager.active_monsters = []
        self.game.wave_manager.wave_active = False
        self.game.wave_manager.wave_completed = True
        self.game.wave_manager.monsters_to_spawn = 0
        
        # Change back to playing state
        self.game.state_manager.change_state("playing")
    
    def draw_card(self, screen, rect, title=None, content=None, border_color=(100, 100, 100)):
        """
        Draw a card with optional title and content
        
        Args:
            screen: Pygame surface to draw on
            rect: Rectangle for the card
            title: Optional title text
            content: Optional content text
            border_color: Color for card border
        """
        # Draw card background
        pygame.draw.rect(screen, self.CARD_BG_COLOR, rect)
        pygame.draw.rect(screen, border_color, rect, 1)
        
        y_pos = rect.top + 10
        
        # Draw title if provided
        if title:
            title_surface = self.font.render(title, True, self.TEXT_COLOR)
            title_rect = title_surface.get_rect(midtop=(rect.centerx, y_pos))
            screen.blit(title_surface, title_rect)
            y_pos += 25
        
        # Draw content if provided
        if content:
            if isinstance(content, list):
                # Draw multiple lines
                for line in content:
                    line_surface = self.small_font.render(line, True, self.SUBTEXT_COLOR)
                    line_rect = line_surface.get_rect(midtop=(rect.centerx, y_pos))
                    screen.blit(line_surface, line_rect)
                    y_pos += 20
            else:
                # Draw single line
                content_surface = self.small_font.render(content, True, self.SUBTEXT_COLOR)
                content_rect = content_surface.get_rect(midtop=(rect.centerx, y_pos))
                screen.blit(content_surface, content_rect)
    
    def draw_castle_icon(self, screen, rect):
        """
        Draw a damaged castle icon
        
        Args:
            screen: Pygame surface to draw on
            rect: Rectangle for the castle icon
        """
        # Castle base
        castle_color = (150, 150, 180)
        pygame.draw.rect(screen, castle_color, rect)
        
        # Castle walls (inner rectangle)
        wall_rect = rect.inflate(-rect.width * 0.2, -rect.height * 0.2)
        pygame.draw.rect(screen, (100, 100, 130), wall_rect)
        
        # Draw castle turrets
        turret_size = max(10, int(rect.width * 0.15))
        turret_height = max(15, int(rect.height * 0.2))
        
        # Top left turret
        pygame.draw.rect(screen, castle_color,
                        (rect.left, rect.top - turret_height // 2,
                         turret_size, turret_height))
        
        # Top right turret
        pygame.draw.rect(screen, castle_color,
                        (rect.right - turret_size, rect.top - turret_height // 2,
                         turret_size, turret_height))
        
        # Middle turret
        pygame.draw.rect(screen, castle_color,
                        (rect.centerx - turret_size // 2, rect.top - turret_height // 2,
                         turret_size, turret_height))
        
        # Draw damage cracks
        crack_color = (180, 50, 50)
        crack_width = max(2, int(rect.width * 0.03))
        
        # Random-looking cracks
        cracks = [
            [(rect.left + rect.width * 0.2, rect.top + rect.height * 0.3),
             (rect.left + rect.width * 0.4, rect.top + rect.height * 0.6)],
            
            [(rect.right - rect.width * 0.2, rect.top + rect.height * 0.4),
             (rect.right - rect.width * 0.5, rect.top + rect.height * 0.7)],
             
            [(rect.centerx - rect.width * 0.1, rect.top),
             (rect.centerx + rect.width * 0.1, rect.top + rect.height * 0.4)],
             
            [(rect.left + rect.width * 0.3, rect.bottom - rect.height * 0.2),
             (rect.left + rect.width * 0.6, rect.bottom)]
        ]
        
        # Draw each crack
        for start, end in cracks:
            pygame.draw.line(screen, crack_color, start, end, crack_width)
            
            # Add small branching cracks
            mid_x = (start[0] + end[0]) / 2
            mid_y = (start[1] + end[1]) / 2
            
            # Branch point
            branch_end = (mid_x + rect.width * 0.1, mid_y + rect.height * 0.1)
            pygame.draw.line(screen, crack_color, (mid_x, mid_y), branch_end, max(1, crack_width - 1))
    
    def draw(self, screen):
        """
        Draw game over screen
        
        Args:
            screen: Pygame surface to draw on
        """
        # First draw the base game (frozen)
        self.game.states["playing"].draw(screen)
        
        # Create semi-transparent overlay
        overlay = pygame.Surface((self.game.WINDOW_WIDTH, self.game.WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))  # Black with 70% opacity
        screen.blit(overlay, (0, 0))
        
        # Calculate card position and size
        card_width = self.game.scale_value(500)
        card_height = self.game.scale_value(400)
        card_rect = pygame.Rect(
            (self.game.WINDOW_WIDTH - card_width) // 2,
            (self.game.WINDOW_HEIGHT - card_height) // 2,
            card_width,
            card_height
        )
        
        # Draw main card background
        pygame.draw.rect(screen, (50, 50, 50), card_rect)
        pygame.draw.rect(screen, (180, 100, 100), card_rect, 2)
        
        # Draw title
        title_text = "Castle Destroyed"
        title_surface = self.title_font.render(title_text, True, (255, 100, 100))
        title_rect = title_surface.get_rect(centerx=card_rect.centerx, top=card_rect.top + 20)
        screen.blit(title_surface, title_rect)
        
        # Draw subtitle with pulsing effect
        pulse = (math.sin(pygame.time.get_ticks() * 0.003) + 1) * 0.1 + 0.9
        subtitle_alpha = int(255 * pulse)
        subtitle_text = "Rebuilding in progress..."
        subtitle_surface = self.font.render(subtitle_text, True, (200, 200, 255))
        subtitle_surface.set_alpha(subtitle_alpha)
        subtitle_rect = subtitle_surface.get_rect(centerx=card_rect.centerx, top=title_rect.bottom + 10)
        screen.blit(subtitle_surface, subtitle_rect)
        
        # Draw damaged castle icon
        castle_icon_size = self.game.scale_value(80)
        castle_icon_rect = pygame.Rect(
            card_rect.centerx - castle_icon_size // 2,
            subtitle_rect.bottom + 20,
            castle_icon_size,
            castle_icon_size
        )
        self.draw_castle_icon(screen, castle_icon_rect)
        
        # Draw setback info card
        setback_card_rect = pygame.Rect(
            card_rect.left + self.game.scale_value(30),
            castle_icon_rect.bottom + 20,
            card_rect.width - self.game.scale_value(60),
            self.game.scale_value(70)
        )
        
        # Format setback message
        if self.current_wave >= 11:
            setback_title = "Setting back 10 waves"
            setback_content = [f"Wave {self.current_wave} → {self.setback_wave}"]
        else:
            setback_title = "Restarting"
            setback_content = [f"Back to Wave {self.setback_wave}"]
        
        # Draw the card
        self.draw_card(screen, setback_card_rect, setback_title, setback_content, border_color=(180, 100, 100))
        
        # Draw countdown progress bar
        remaining_time = max(0, self.auto_continue_time - self.time_in_state)
        progress_pct = 1 - (remaining_time / self.auto_continue_time)
        
        bar_rect = pygame.Rect(
            card_rect.left + self.game.scale_value(50),
            setback_card_rect.bottom + 20,
            card_rect.width - self.game.scale_value(100),
            self.game.scale_value(20)
        )
        
        # Draw progress bar background
        pygame.draw.rect(screen, (80, 80, 80), bar_rect)
        
        # Draw progress fill
        fill_width = int(bar_rect.width * progress_pct)
        if fill_width > 0:
            fill_rect = pygame.Rect(
                bar_rect.left,
                bar_rect.top,
                fill_width,
                bar_rect.height
            )
            pygame.draw.rect(screen, (100, 150, 255), fill_rect)
        
        # Draw border
        pygame.draw.rect(screen, (150, 150, 150), bar_rect, 1)
        
        # Draw time text
        time_text = f"Auto-continue: {int(remaining_time)} seconds"
        time_surface = self.small_font.render(time_text, True, self.TEXT_COLOR)
        time_rect = time_surface.get_rect(midtop=(bar_rect.centerx, bar_rect.bottom + 5))
        screen.blit(time_surface, time_rect)
        
        # Get button rectangles
        continue_button_rect, quit_button_rect = self.get_button_rects()
        
        # Draw continue button
        continue_color = (90, 140, 90) if self.continue_button_hover else (80, 120, 80)
        continue_border = (150, 255, 150) if self.continue_button_hover else (100, 200, 100)
        pygame.draw.rect(screen, continue_color, continue_button_rect)
        pygame.draw.rect(screen, continue_border, continue_button_rect, 2)
        
        continue_text = self.font.render("Continue", True, (220, 220, 220))
        continue_text_rect = continue_text.get_rect(center=continue_button_rect.center)
        screen.blit(continue_text, continue_text_rect)
        
        # Draw quit button
        quit_color = (140, 90, 90) if self.quit_button_hover else (120, 80, 80)
        quit_border = (255, 150, 150) if self.quit_button_hover else (200, 100, 100)
        pygame.draw.rect(screen, quit_color, quit_button_rect)
        pygame.draw.rect(screen, quit_border, quit_button_rect, 2)
        
        quit_text = self.font.render("Quit Game", True, (220, 220, 220))
        quit_text_rect = quit_text.get_rect(center=quit_button_rect.center)
        screen.blit(quit_text, quit_text_rect)
        
        # Draw key command hints
        hint_text = "Press SPACE to continue, ESC to quit"
        hint_surface = self.small_font.render(hint_text, True, (180, 180, 180))
        hint_rect = hint_surface.get_rect(midbottom=(card_rect.centerx, card_rect.bottom - 10))
        screen.blit(hint_surface, hint_rect)
