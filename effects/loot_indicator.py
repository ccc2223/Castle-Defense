"""
Loot indicator system for Castle Defense
Shows floating text with icons when enemies drop items
"""
import pygame
import math

class LootIndicator:
    """
    Displays a floating text with icon for a single loot item
    """
    def __init__(self, position, item_name, quantity, icon_manager=None):
        """
        Initialize loot indicator
        
        Args:
            position: Tuple of (x, y) coordinates where the loot dropped
            item_name: String name of the dropped item
            quantity: Number of items dropped
            icon_manager: Optional ResourceIconManager for item icons
        """
        self.position = list(position)
        self.item_name = item_name
        self.quantity = quantity
        self.icon_manager = icon_manager
        
        # Animation properties
        self.max_life = 0.8  # 0.8 seconds total duration
        self.life = self.max_life
        self.dead = False
        
        # Movement properties
        self.rise_speed = 30  # Pixels per second
        self.initial_position = list(position)
        
        # Appearance properties
        self.background_color = (30, 30, 30, 180)  # Semi-transparent dark gray
        self.text_color = (255, 255, 255)  # White text
        self.font_size = 16
        self.icon_size = (20, 20)
        self.padding = 4
        
        # Setup text and surfaces
        self.font = pygame.font.Font(None, self.font_size)
        self.text = f"x{quantity}"
        self.text_surface = self.font.render(self.text, True, self.text_color)
        
        # Get icon if possible
        self.icon = None
        if self.icon_manager:
            icon_id = self.icon_manager.get_resource_icon_id(item_name)
            self.icon = self.icon_manager.get_icon(icon_id, self.icon_size)
        
        # Calculate background size
        if self.icon:
            self.width = self.icon_size[0] + self.padding + self.text_surface.get_width() + self.padding * 2
        else:
            self.width = self.text_surface.get_width() + self.padding * 2
        self.height = max(self.icon_size[1], self.text_surface.get_height()) + self.padding * 2
    
    def update(self, dt):
        """
        Update indicator state
        
        Args:
            dt: Time delta in seconds
            
        Returns:
            False if indicator is dead and should be removed
        """
        # Update life
        self.life -= dt
        if self.life <= 0:
            self.dead = True
            return False
        
        # Move upward
        self.position[1] -= self.rise_speed * dt
        
        return True
    
    def draw(self, screen):
        """
        Draw indicator to screen
        
        Args:
            screen: Pygame surface to draw on
        """
        if self.dead:
            return
        
        # Calculate alpha based on life (fade in/out)
        life_percent = self.life / self.max_life
        if life_percent > 0.8:  # Fade in during first 20% of life
            alpha = 255 * (1.0 - (life_percent - 0.8) * 5)
        elif life_percent < 0.2:  # Fade out during last 20% of life
            alpha = 255 * (life_percent * 5)
        else:
            alpha = 255
        
        alpha = max(0, min(255, int(alpha)))
        
        # Create background surface with proper alpha
        bg_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        bg_color = (self.background_color[0], self.background_color[1], 
                   self.background_color[2], int(self.background_color[3] * alpha / 255))
        pygame.draw.rect(bg_surface, bg_color, (0, 0, self.width, self.height), border_radius=4)
        
        # Position background
        bg_rect = bg_surface.get_rect(center=(self.position[0], self.position[1]))
        
        # Draw background
        screen.blit(bg_surface, bg_rect)
        
        # Calculate positions for icon and text
        if self.icon:
            icon_x = bg_rect.left + self.padding
            icon_y = bg_rect.centery - self.icon_size[1] // 2
            text_x = icon_x + self.icon_size[0] + self.padding
        else:
            text_x = bg_rect.left + self.padding
        
        text_y = bg_rect.centery - self.text_surface.get_height() // 2
        
        # Create text surface with alpha
        if alpha < 255:
            text_surface = self.text_surface.copy()
            alpha_surface = pygame.Surface(text_surface.get_size(), pygame.SRCALPHA)
            alpha_surface.fill((255, 255, 255, alpha))
            text_surface.blit(alpha_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        else:
            text_surface = self.text_surface
        
        # Draw icon if available
        if self.icon:
            if alpha < 255:
                icon = self.icon.copy()
                alpha_surface = pygame.Surface(icon.get_size(), pygame.SRCALPHA)
                alpha_surface.fill((255, 255, 255, alpha))
                icon.blit(alpha_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
                screen.blit(icon, (icon_x, icon_y))
            else:
                screen.blit(self.icon, (icon_x, icon_y))
        
        # Draw text
        screen.blit(text_surface, (text_x, text_y))

class LootDisplayManager:
    """Manages multiple loot indicators"""
    def __init__(self, icon_manager=None):
        """
        Initialize display manager
        
        Args:
            icon_manager: Optional ResourceIconManager for item icons
        """
        self.indicators = []
        self.icon_manager = icon_manager
    
    def create_indicator(self, position, item_name, quantity):
        """
        Create a new loot indicator
        
        Args:
            position: Tuple of (x, y) coordinates where the loot dropped
            item_name: String name of the dropped item
            quantity: Number of items dropped
        """
        indicator = LootIndicator(position, item_name, quantity, self.icon_manager)
        self.indicators.append(indicator)
    
    def create_indicators(self, position, loot_dict):
        """
        Create indicators for multiple loot items
        
        Args:
            position: Tuple of (x, y) coordinates where the loot dropped
            loot_dict: Dictionary of {item_name: quantity} pairs
        """
        # Sort items so more valuable/rare items appear at the top
        # Sort order: Special items first, then Monster Coins, then basic resources
        # For now a simple alphabetical sort will do
        sorted_items = sorted(loot_dict.items())
        
        # Calculate offset for stacking indicators
        vertical_spacing = 5  # Pixels between indicators
        
        # Create an indicator for each item, stacked vertically
        for i, (item_name, quantity) in enumerate(sorted_items):
            if quantity <= 0:
                continue
                
            # Offset position for stacking (moving upward)
            offset_y = i * (vertical_spacing + 20)  # 20 is approximate height
            item_pos = (position[0], position[1] - offset_y)
            
            self.create_indicator(item_pos, item_name, quantity)
    
    def update(self, dt):
        """
        Update all indicators
        
        Args:
            dt: Time delta in seconds
        """
        # Update indicators and remove dead ones
        self.indicators = [ind for ind in self.indicators if ind.update(dt)]
    
    def draw(self, screen):
        """
        Draw all indicators
        
        Args:
            screen: Pygame surface to draw on
        """
        for indicator in self.indicators:
            indicator.draw(screen)
    
    def clear(self):
        """Remove all indicators"""
        self.indicators = []
