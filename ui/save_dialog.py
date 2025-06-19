# ui/save_dialog.py
"""
Save dialog implementation for Castle Defense
"""
import pygame
import os
import datetime
from .base_menu import Menu
from .elements import Button

class SaveDialog(Menu):
    """Dialog for saving games with custom names"""
    def __init__(self, screen, game):
        """
        Initialize save dialog
        
        Args:
            screen: Pygame surface to draw on
            game: Game instance for access to save functionality
        """
        super().__init__(screen)
        self.game = game
        self.title = "Save Game"
        
        # Position at center of screen
        self.size = (450, 250)
        self.position = (
            (game.WINDOW_WIDTH - self.size[0]) // 2,
            (game.WINDOW_HEIGHT - self.size[1]) // 2
        )
        self.rect = pygame.Rect(self.position, self.size)
        
        # Text field properties
        self.text_field_rect = pygame.Rect(
            self.rect.left + 30,
            self.rect.top + 80,
            self.rect.width - 60,
            40
        )
        self.text_field_active = False
        self.text_value = self.generate_default_filename()
        self.cursor_visible = True
        self.cursor_timer = 0
        self.cursor_blink_rate = 0.5  # seconds
        
        # Error message
        self.error_message = ""
        self.error_timer = 0
        
        # Create buttons
        self.create_buttons()
        
        # Set up font for text input
        self.input_font = pygame.font.Font(None, 24)
    
    def create_buttons(self):
        """Create dialog buttons"""
        button_width = 150
        button_height = 40
        button_y = self.rect.bottom - 70
        
        # Save button
        self.save_button = Button(
            (self.rect.left + (self.rect.width // 4) - (button_width // 2), button_y),
            (button_width, button_height),
            "Save",
            self.save_game
        )
        
        # Cancel button
        self.cancel_button = Button(
            (self.rect.left + (self.rect.width * 3 // 4) - (button_width // 2), button_y),
            (button_width, button_height),
            "Cancel",
            self.close
        )
        
        self.buttons = [self.save_button, self.cancel_button]
    
    def generate_default_filename(self):
        """
        Generate default save filename based on date and wave
        
        Returns:
            Default filename string
        """
        now = datetime.datetime.now()
        date_str = now.strftime("%Y-%m-%d")
        wave_str = str(self.game.wave_manager.current_wave).zfill(3)
        return f"Save_{date_str}_Wave{wave_str}"
    
    def handle_event(self, event):
        """
        Handle pygame events
        
        Args:
            event: Pygame event
            
        Returns:
            True if event was handled, False otherwise
        """
        # First check if the dialog is even active
        if not self.active:
            return False
        
        # Text field activation
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Check if the text field was clicked
            if self.text_field_rect.collidepoint(event.pos):
                self.text_field_active = True
                # Reset cursor blink for better UX
                self.cursor_visible = True
                self.cursor_timer = 0
                return True
            else:
                self.text_field_active = False
                
                # Check if buttons were clicked
                for button in self.buttons:
                    if button.rect.collidepoint(event.pos):
                        button.click()
                        return True
        
        # Text input handling when field is active
        if self.text_field_active:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    # Save game on Enter
                    self.save_game()
                    return True
                    
                elif event.key == pygame.K_ESCAPE:
                    # Deactivate text field on Escape
                    self.text_field_active = False
                    return True
                    
                elif event.key == pygame.K_BACKSPACE:
                    # Remove last character
                    self.text_value = self.text_value[:-1]
                    return True
                    
                else:
                    # Add typed character if valid
                    if event.unicode.isprintable() and len(self.text_value) < 30:
                        # Ensure filename is valid
                        if self.is_char_valid_for_filename(event.unicode):
                            self.text_value += event.unicode
                        return True
        
        # Let parent class handle clicking outside the dialog
        return super().handle_event(event)
    
    def is_char_valid_for_filename(self, char):
        """
        Check if character is valid for a filename
        
        Args:
            char: Character to check
            
        Returns:
            True if valid, False otherwise
        """
        # Common invalid filename characters
        invalid_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
        return char not in invalid_chars
    
    def update(self, dt):
        """
        Update dialog animation
        
        Args:
            dt: Time delta in seconds
        """
        # Update cursor blink timer
        if self.text_field_active:
            self.cursor_timer += dt
            if self.cursor_timer >= self.cursor_blink_rate:
                self.cursor_timer = 0
                self.cursor_visible = not self.cursor_visible
        
        # Update error message timer
        if self.error_timer > 0:
            self.error_timer -= dt
            if self.error_timer <= 0:
                self.error_message = ""
    
    def save_game(self):
        """Save the game with the current filename"""
        # Make sure we have a valid filename
        if not self.text_value:
            self.show_error("Filename cannot be empty")
            return
        
        try:
            # Ensure extension is .save
            if not self.text_value.endswith(".save"):
                filename = f"{self.text_value}.save"
            else:
                filename = self.text_value
            
            # Try to get save manager from registry first
            if hasattr(self.game, 'registry') and self.game.registry:
                try:
                    save_manager = self.game.registry.get("save_manager")
                    save_manager.save_game(filename)
                    self.close()
                    return
                except KeyError:
                    pass  # Fall back to legacy method
            
            # Legacy method
            if hasattr(self.game, 'save_manager'):
                self.game.save_manager.save_game(filename)
                self.close()
        except Exception as e:
            self.show_error(f"Error saving game: {str(e)}")
    
    def show_error(self, message):
        """
        Show error message
        
        Args:
            message: Error message to display
        """
        self.error_message = message
        self.error_timer = 5.0  # Show for 5 seconds
    
    def close(self):
        """Close the dialog"""
        self.active = False
    
    def draw(self):
        """Draw save dialog"""
        if not self.active:
            return
        
        # Draw dialog background
        pygame.draw.rect(self.screen, (50, 50, 60), self.rect)
        pygame.draw.rect(self.screen, (150, 150, 180), self.rect, 2)
        
        # Draw title
        title_surface = self.font.render(self.title, True, (255, 255, 255))
        title_rect = title_surface.get_rect(center=(self.rect.centerx, self.rect.top + 30))
        self.screen.blit(title_surface, title_rect)
        
        # Draw text field label
        label = self.font.render("Save Name:", True, (220, 220, 220))
        label_rect = label.get_rect(bottomleft=(self.text_field_rect.left, self.text_field_rect.top - 10))
        self.screen.blit(label, label_rect)
        
        # Draw text field
        text_field_color = (70, 70, 90) if self.text_field_active else (60, 60, 70)
        pygame.draw.rect(self.screen, text_field_color, self.text_field_rect)
        pygame.draw.rect(self.screen, (180, 180, 200), self.text_field_rect, 2)
        
        # Draw entered text
        text_surface = self.input_font.render(self.text_value, True, (255, 255, 255))
        # Position text with left margin
        text_margin = 10
        text_pos = (self.text_field_rect.left + text_margin, self.text_field_rect.centery - text_surface.get_height() // 2)
        self.screen.blit(text_surface, text_pos)
        
        # Draw cursor when text field is active and cursor is visible
        if self.text_field_active and self.cursor_visible:
            cursor_x = text_pos[0] + text_surface.get_width() + 2
            cursor_y1 = self.text_field_rect.top + 8
            cursor_y2 = self.text_field_rect.bottom - 8
            pygame.draw.line(self.screen, (255, 255, 255), (cursor_x, cursor_y1), (cursor_x, cursor_y2), 2)
        
        # Draw error message if present
        if self.error_message:
            error_surface = self.small_font.render(self.error_message, True, (255, 100, 100))
            error_rect = error_surface.get_rect(center=(self.rect.centerx, self.text_field_rect.bottom + 20))
            self.screen.blit(error_surface, error_rect)
        
        # Draw buttons
        for button in self.buttons:
            button.draw(self.screen)
