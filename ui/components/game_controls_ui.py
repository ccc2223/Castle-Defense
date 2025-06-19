# ui/components/game_controls_ui.py
"""
Game controls UI component for Castle Defense
Displays play/pause button and game speed slider
"""
import pygame
from .ui_component import UIComponent
from ui.elements import Button, Slider
from registry import STATE_MANAGER

class GameControlsUI(UIComponent):
    """UI component for game control buttons and sliders"""
    
    def __init__(self, screen, registry=None):
        """
        Initialize game controls UI
        
        Args:
            screen: Pygame surface to draw on
            registry: Optional ComponentRegistry for accessing game components
        """
        super().__init__(screen, registry)
        
        # Initialize play/pause button
        self.play_pause_button = Button(
            (20, 20),
            (50, 50),
            "||",  # Pause symbol
            self.toggle_pause,
            color=(60, 60, 100),
            hover_color=(80, 80, 140)
        )
        
        # Initialize game speed slider
        # Default max speed is 2.5, but can be increased by research
        self.base_max_speed = 2.5
        self.game_speed_slider = Slider(
            (20, 80),
            (150, 20),
            "Game Speed:",
            1.0,  # Default value
            0.5,  # Min value
            self.base_max_speed,  # Max value (will be updated based on research)
            0.5,  # Step
            self.set_game_speed,
            lambda x: f"{x:.1f}x"  # Format function
        )
        
        # State tracking
        self.is_paused = False
        
        # Check initial state - important for correct button state on init
        self.update_pause_state()
    
    def update(self, dt):
        """
        Update UI element states
        
        Args:
            dt: Time delta in seconds
        """
        if not self.active:
            return
            
        # Update button hover state
        mouse_pos = pygame.mouse.get_pos()
        self.play_pause_button.update(mouse_pos)
        
        # Update game speed slider max value based on research
        self.update_max_speed()
        
        # Update pause state from current game state
        self.update_pause_state()
    
    def draw(self):
        """Draw game control UI elements"""
        if not self.visible:
            return
            
        # Draw play/pause button
        self.play_pause_button.draw(self.screen)
        
        # Draw game speed slider
        self.draw_game_speed_slider()
    
    def handle_event(self, event):
        """
        Handle pygame events
        
        Args:
            event: Pygame event
            
        Returns:
            True if event was handled, False otherwise
        """
        if not self.active:
            return False
            
        # Handle play/pause button
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            
            # Check play/pause button
            if self.play_pause_button.rect.collidepoint(mouse_pos):
                self.play_pause_button.click()
                return True
                
            # Handle game speed slider
            if hasattr(self.game_speed_slider, 'slider_rect') and hasattr(self.game_speed_slider, 'handle_rect'):
                if self.game_speed_slider.slider_rect.collidepoint(mouse_pos) or \
                   self.game_speed_slider.handle_rect.collidepoint(mouse_pos):
                    # Set slider value based on click position
                    slider_width = self.game_speed_slider.slider_rect.width
                    slider_left = self.game_speed_slider.slider_rect.left
                    slider_pos = (mouse_pos[0] - slider_left) / slider_width
                    value = self.game_speed_slider.min_value + slider_pos * (self.game_speed_slider.max_value - self.game_speed_slider.min_value)
                    # Round to nearest step
                    value = round(value / self.game_speed_slider.step) * self.game_speed_slider.step
                    # Clamp to min/max
                    value = max(self.game_speed_slider.min_value, min(self.game_speed_slider.max_value, value))
                    self.game_speed_slider.value = value
                    self.set_game_speed(value)
                    return True
                
        return False
    
    def update_pause_state(self):
        """Update pause state based on current game state"""
        if not self.registry:
            return
            
        try:
            # Get the state manager from registry
            state_manager = self.registry.get(STATE_MANAGER)
            
            # Check current state
            current_state_name = state_manager.current_state.__class__.__name__
            
            # Update is_paused flag based on current state
            new_paused_state = (current_state_name == "PausedState")
            
            # Only update if changed to avoid unnecessary updates
            if new_paused_state != self.is_paused:
                self.is_paused = new_paused_state
                self.play_pause_button.text = "▶" if self.is_paused else "||"  # Play or Pause icon
        except (KeyError, AttributeError) as e:
            # Registry error - print for debugging
            print(f"Error updating pause state: {e}")
    
    def update_max_speed(self):
        """
        Update the maximum speed of the slider based on research
        """
        if not self.registry:
            return
            
        try:
            # Access the game through registry
            game = self.registry.get("game")
            if hasattr(game, "base_time_scale"):
                # Calculate new max speed based on research
                # The base max speed is 2.5x, and research can increase this
                new_max_speed = self.base_max_speed
                
                # If base_time_scale > 1.0, it means research has increased it
                if game.base_time_scale > 1.0:
                    # Each 0.2 increase in base_time_scale from research adds 0.5 to max speed
                    research_boost = (game.base_time_scale - 1.0) * 2.5  # Convert 0.2 to 0.5 increase ratio
                    new_max_speed += research_boost
                
                # Update slider max value if it changed
                if new_max_speed != self.game_speed_slider.max_value:
                    # Store the current position ratio
                    current_ratio = (self.game_speed_slider.value - self.game_speed_slider.min_value) / \
                                  (self.game_speed_slider.max_value - self.game_speed_slider.min_value)
                    
                    # Update max value
                    self.game_speed_slider.max_value = new_max_speed
                    
                    # Adjust current value to maintain same position on slider
                    new_value = self.game_speed_slider.min_value + \
                              current_ratio * (new_max_speed - self.game_speed_slider.min_value)
                    
                    # Round to nearest step
                    new_value = round(new_value / self.game_speed_slider.step) * self.game_speed_slider.step
                    
                    # Update slider value
                    self.game_speed_slider.value = new_value
        except (KeyError, AttributeError) as e:
            # Registry error - print for debugging
            print(f"Error updating max speed: {e}")
    
    def toggle_pause(self):
        """Toggle the game between paused and playing states"""
        if not self.registry:
            return
            
        try:
            # Get the state manager from registry
            state_manager = self.registry.get(STATE_MANAGER)
            
            # Toggle pause state
            if self.is_paused:
                # Resume game
                self.is_paused = False
                self.play_pause_button.text = "||"  # Pause icon
                state_manager.change_state("playing")
            else:
                # Pause game
                self.is_paused = True
                self.play_pause_button.text = "▶"  # Play icon
                state_manager.change_state("paused")
        except (KeyError, AttributeError) as e:
            # Registry error - print for debugging
            print(f"Error toggling pause: {e}")
    
    def set_game_speed(self, value):
        """
        Set the game speed
        
        Args:
            value: New game speed value
        """
        if not self.registry:
            return
            
        try:
            # Access the game through registry and set time scale
            game = self.registry.get("game")
            if hasattr(game, "time_scale") and hasattr(game, "base_time_scale"):
                # This value from the slider is the effective speed
                # We need to convert it to a value relative to the base_time_scale
                game.time_scale = value
                
                # Display an indicator if the speed is at max due to research
                if abs(value - self.game_speed_slider.max_value) < 0.01:
                    print(f"Max speed reached due to Clockwork Speed research: {value:.1f}x")
                    
                    # Could add a notification here if needed
                    if hasattr(game, 'notification_manager'):
                        boost_amount = (game.base_time_scale - 1.0) * 100.0  # percentage
                        game.notification_manager.add_notification(
                            f"Max speed boosted by {boost_amount:.0f}% due to Clockwork research!", 
                            2.0, 
                            (180, 180, 220)
                        )
            
        except KeyError:
            # Try legacy method - access global game instance
            try:
                from game import Game
                game_instance = Game.get_instance()
                if game_instance:
                    game_instance.time_scale = value
            except (ImportError, AttributeError):
                pass
    
    def draw_game_speed_slider(self):
        """Draw the game speed slider"""
        # Draw label
        font = pygame.font.Font(None, 24)
        label_surface = font.render("Game Speed:", True, (255, 255, 255))
        self.screen.blit(label_surface, (20, 80))
        
        # Draw slider background
        slider_rect = pygame.Rect(20, 105, 150, 10)
        pygame.draw.rect(self.screen, (60, 60, 60), slider_rect)
        pygame.draw.rect(self.screen, (120, 120, 120), slider_rect, 1)
        
        # Calculate handle position
        value_range = self.game_speed_slider.max_value - self.game_speed_slider.min_value
        value_ratio = (self.game_speed_slider.value - self.game_speed_slider.min_value) / value_range
        handle_x = slider_rect.left + int(value_ratio * slider_rect.width)
        
        # Draw handle
        handle_rect = pygame.Rect(handle_x - 5, slider_rect.top - 5, 10, 20)
        pygame.draw.rect(self.screen, (150, 150, 200), handle_rect)
        
        # Draw value
        value_text = f"{self.game_speed_slider.value:.1f}x"
        value_surface = font.render(value_text, True, (255, 255, 255))
        self.screen.blit(value_surface, (175, 100))
        
        # Store handle rect for interactions
        self.game_speed_slider.slider_rect = slider_rect
        self.game_speed_slider.handle_rect = handle_rect