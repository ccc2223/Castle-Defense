# storage_button_ui.py
"""
Storage Barn Button Component for Castle Defense
"""
import pygame
from .ui_component import UIComponent
from registry import STATE_MANAGER
from utils import scale_value

class StorageButtonUI(UIComponent):
    """
    UI Component for Storage Barn access button
    """
    def __init__(self, screen, registry):
        """
        Initialize the Storage Barn button
        
        Args:
            screen: pygame surface
            registry: component registry for game elements
        """
        super().__init__(screen, registry)
        
        # Store screen dimensions
        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()
        
        # Get state manager from registry
        self.state_manager = registry.get(STATE_MANAGER) if registry else None
        
        # Button properties
        self.button_width = scale_value(160)
        self.button_height = scale_value(40)
        
        # Position the button in the top-right area (but leaving space for other UI elements)
        self.button_x = self.screen_width - self.button_width - scale_value(20)
        self.button_y = scale_value(70)  # Below any other top UI elements
        
        # Create the button rectangle
        self.button_rect = pygame.Rect(
            self.button_x,
            self.button_y,
            self.button_width,
            self.button_height
        )
        
        # Button colors
        self.button_color = (80, 110, 70)  # Barn-like brown-green
        self.button_hover_color = (100, 130, 90)
        self.button_text_color = (240, 240, 230)
        
        # Track if button is being hovered
        self.is_hovered = False
        
        # Button is only visible in playing state
        self.visible_states = ["playing", "village"]
    
    def update(self, dt):
        """
        Update button state (hover effects)
        
        Args:
            dt: Time delta in seconds
        """
        # Check if mouse is hovering over button
        mouse_pos = pygame.mouse.get_pos()
        self.is_hovered = self.button_rect.collidepoint(mouse_pos)
    
    def draw(self):
        """Draw storage button to screen"""
        # Only draw if in a visible state
        if self.state_manager and hasattr(self.state_manager, 'current_state_name'):
            if self.state_manager.current_state_name not in self.visible_states:
                return
        
        # Determine button color based on hover state
        color = self.button_hover_color if self.is_hovered else self.button_color
        
        # Draw button
        pygame.draw.rect(self.screen, color, self.button_rect)
        pygame.draw.rect(self.screen, (150, 180, 150), self.button_rect, 2)  # Border
        
        # Draw text
        font = pygame.font.Font(None, scale_value(24))
        text = font.render("Storage Barn", True, self.button_text_color)
        text_rect = text.get_rect(center=self.button_rect.center)
        self.screen.blit(text, text_rect)
        
        # Draw a little barn icon to the left of the text
        barn_icon_size = scale_value(24)
        barn_icon_rect = pygame.Rect(
            self.button_rect.left + scale_value(10),
            self.button_rect.centery - barn_icon_size // 2,
            barn_icon_size,
            barn_icon_size
        )
        
        # Draw a simple barn icon (just a house shape)
        pygame.draw.polygon(self.screen, (180, 150, 120), [
            (barn_icon_rect.left, barn_icon_rect.centery),
            (barn_icon_rect.centerx, barn_icon_rect.top),
            (barn_icon_rect.right, barn_icon_rect.centery),
            (barn_icon_rect.right, barn_icon_rect.bottom),
            (barn_icon_rect.left, barn_icon_rect.bottom)
        ])
    
    def handle_event(self, event):
        """
        Handle button click events
        
        Args:
            event: pygame event object
            
        Returns:
            True if event was handled, False otherwise
        """
        # Only handle events if in a visible state
        if self.state_manager and hasattr(self.state_manager, 'current_state_name'):
            if self.state_manager.current_state_name not in self.visible_states:
                return False
            
        # Check for mouse click on button
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left mouse button
            if self.button_rect.collidepoint(event.pos):
                # Switch to storage state
                if self.state_manager:
                    self.state_manager.change_state("storage")
                return True
                
        return False
