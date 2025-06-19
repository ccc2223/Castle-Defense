# features/village/storage_barn.py
"""
Storage Barn building implementation for Castle Defense
"""
import pygame
from features.village.buildings import VillageBuilding
from utils import scale_value, scale_position, scale_size

class StorageBarn(VillageBuilding):
    """
    Storage Barn building for viewing all resources and items in one place
    """
    def __init__(self, position, registry):
        """
        Initialize storage barn with position
        
        Args:
            position: Tuple of (x, y) coordinates
            registry: Component registry for accessing game components
        """
        super().__init__(position, registry)
        self.name = "Storage Barn"
        self.description = "Central inventory for all resources and items"
        self.color = (120, 90, 60)  # Warm brown for the barn
        self.building_type = "storage_barn"
        
        # No upgrade costs since it doesn't need upgrades
        self.upgrade_cost = {}
        
        # Track if inventory UI is open
        self.inventory_open = False
        
        # Button for accessing inventory
        self.view_inventory_button_rect = None
    
    def update(self, dt):
        """
        Update storage barn state
        
        Args:
            dt: Time delta in seconds
        """
        # Storage barn doesn't need active updates
        pass
    
    def draw(self, screen):
        """
        Draw storage barn to screen
        
        Args:
            screen: Pygame surface to draw on
        """
        # Draw basic building representation
        super().draw(screen)
        
        # Draw storage barn icon - simple barn roof shape
        roof_color = (150, 100, 50)  # Dark brown
        roof_points = [
            (self.rect.centerx - self.rect.width//3, self.rect.centery - self.rect.height//5),
            (self.rect.centerx, self.rect.centery - self.rect.height//2),
            (self.rect.centerx + self.rect.width//3, self.rect.centery - self.rect.height//5)
        ]
        pygame.draw.polygon(screen, roof_color, roof_points)
        
        # Draw more details when selected
        if self.is_selected:
            # Draw information panel
            info_rect = pygame.Rect(
                self.rect.left - 50,
                self.rect.bottom + 10,
                self.rect.width + 100,
                120
            )
            pygame.draw.rect(screen, (40, 30, 20), info_rect)
            pygame.draw.rect(screen, (120, 100, 70), info_rect, 2)
            
            # Draw storage barn info
            font = pygame.font.Font(None, scale_value(20))
            title = font.render("Storage Barn", True, (220, 200, 150))
            screen.blit(title, (info_rect.left + 10, info_rect.top + 10))
            
            # Draw description
            desc_font = pygame.font.Font(None, scale_value(18))
            desc_text = "View and organize all your resources and items."
            desc_surface = desc_font.render(desc_text, True, (200, 180, 150))
            screen.blit(desc_surface, (info_rect.left + 15, info_rect.top + 35))
            
            # Draw "View Inventory" button
            button_rect = pygame.Rect(
                info_rect.centerx - scale_value(75),
                info_rect.bottom - scale_value(40),
                scale_value(150),
                scale_value(30)
            )
            
            # Store button rect for click detection
            self.view_inventory_button_rect = button_rect
            
            # Check if mouse is hovering over button
            mouse_pos = pygame.mouse.get_pos()
            button_hovered = button_rect.collidepoint(mouse_pos)
            
            # Draw button with hover effect
            button_color = (140, 110, 70) if button_hovered else (120, 90, 50)
            pygame.draw.rect(screen, button_color, button_rect)
            pygame.draw.rect(screen, (180, 150, 100), button_rect, 2)
            
            # Draw button text
            button_text = font.render("View Inventory", True, (230, 220, 190))
            button_text_rect = button_text.get_rect(center=button_rect.center)
            screen.blit(button_text, button_text_rect)
    
    def handle_click(self, position):
        """
        Handle click on storage barn or its buttons
        
        Args:
            position: Tuple of (x, y) coordinates of click
            
        Returns:
            True if click was handled, False otherwise
        """
        # Check if building was clicked
        if self.rect.collidepoint(position):
            self.is_selected = not self.is_selected
            return True
        
        # Check if view inventory button was clicked
        if self.is_selected and self.view_inventory_button_rect and self.view_inventory_button_rect.collidepoint(position):
            # Access registry to transition to storage state
            if self.registry and self.registry.has("game"):
                game = self.registry.get("game")
                if hasattr(game, 'state_manager'):
                    game.state_manager.change_state("storage")
                    self.inventory_open = True
                    return True
            return True
            
        # Deselect if clicked elsewhere
        self.is_selected = False
        return False
    
    def get_info_text(self):
        """
        Get storage barn information text
        
        Returns:
            List of text lines with storage barn information
        """
        info = [
            f"{self.name}",
            f"{self.description}",
            "Access your complete inventory"
        ]
        return info
