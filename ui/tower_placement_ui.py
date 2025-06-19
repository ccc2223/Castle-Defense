# ui/tower_placement_ui.py
"""
Tower placement UI for Castle Defense
"""
import pygame
import math
from registry import RESOURCE_MANAGER

class TowerPlacementUI:
    """UI for placing towers on the game map"""
    def __init__(self, screen, game):
        """
        Initialize tower placement UI
        
        Args:
            screen: Pygame surface to draw on
            game: Game instance for callbacks
        """
        self.screen = screen
        self.game = game
        self.registry = game.registry if hasattr(game, 'registry') else None
        self.tower_type = None
        self.tower_preview = None
        self.valid_position = False
    
    def handle_event(self, event):
        """
        Handle pygame events
        
        Args:
            event: Pygame event
            
        Returns:
            True if event was handled, False otherwise
        """
        # No events to handle if no tower selected
        if not self.tower_type or not self.tower_preview:
            return False
            
        mouse_pos = pygame.mouse.get_pos()
        self.update_tower_position(mouse_pos)
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                # Attempt to place tower
                return self.place_tower(mouse_pos)
                
            elif event.button == 3:  # Right click
                # Cancel placement
                self.clear_preview()
                return True
                
        return False
    
    def update_tower_position(self, mouse_pos):
        """
        Update the tower preview position
        
        Args:
            mouse_pos: Current mouse position
        """
        if self.tower_preview:
            self.tower_preview.position = mouse_pos
            self.tower_preview.rect.center = mouse_pos
            self.valid_position = self.game.is_valid_tower_position(mouse_pos)
    
    def set_tower_type(self, tower_type):
        """
        Set the type of tower to place
        
        Args:
            tower_type: Type of tower being placed
        """
        self.tower_type = tower_type
        
        # Create tower preview
        if tower_type:
            try:
                from features.towers.factory import TowerFactory
                self.tower_preview = TowerFactory.create_tower(tower_type, (0, 0), self.registry)
            except (ValueError, ImportError):
                self.tower_preview = None
    
    def clear_preview(self):
        """Clear the current tower preview"""
        self.tower_type = None
        self.tower_preview = None
        self.valid_position = False
    
    def place_tower(self, position):
        """
        Attempt to place a tower at the current position
        
        Args:
            position: Position to place tower
            
        Returns:
            True if tower was placed, False otherwise
        """
        if not self.tower_type or not self.tower_preview:
            return False
            
        # Check if position is valid
        if not self.game.is_valid_tower_position(position):
            return False
            
        # Get resource manager from registry if available
        resource_manager = None
        if self.registry and self.registry.has(RESOURCE_MANAGER):
            resource_manager = self.registry.get(RESOURCE_MANAGER)
        else:
            resource_manager = self.game.resource_manager
            
        # Get tower costs from tower preview
        from config import TOWER_TYPES, TOWER_MONSTER_COIN_COSTS
        tower_cost = TOWER_TYPES.get(self.tower_type, {}).get("cost", {})
        monster_coin_cost = TOWER_MONSTER_COIN_COSTS.get(self.tower_type, 0)
        
        # Check if player has enough resources
        if not resource_manager.has_resources_for_tower(tower_cost, monster_coin_cost):
            return False
            
        # Spend resources
        if not resource_manager.spend_resources_for_tower(tower_cost, monster_coin_cost):
            return False
            
        # Create and place the tower
        from features.towers.factory import TowerFactory
        tower = TowerFactory.create_tower(self.tower_type, position, self.registry)
        self.game.towers.append(tower)
        
        # Clear preview
        self.clear_preview()
        
        # Exit tower placement mode
        self.game.state_manager.change_state("playing")
        
        return True
    
    def draw(self, resource_manager=None):
        """
        Draw tower placement preview
        
        Args:
            resource_manager: Optional ResourceManager to check resources
        """
        if not self.tower_preview:
            return
            
        # Get resource manager from parameter or registry
        res_mgr = resource_manager
        if not res_mgr and self.registry and self.registry.has(RESOURCE_MANAGER):
            res_mgr = self.registry.get(RESOURCE_MANAGER)
            
        # Get current mouse position
        mouse_pos = pygame.mouse.get_pos()
        self.update_tower_position(mouse_pos)
        
        # Get tower costs from tower preview
        from config import TOWER_TYPES, TOWER_MONSTER_COIN_COSTS
        tower_cost = TOWER_TYPES.get(self.tower_type, {}).get("cost", {})
        monster_coin_cost = TOWER_MONSTER_COIN_COSTS.get(self.tower_type, 0)
        
        # Check if player has enough resources
        has_resources = False
        if res_mgr:
            has_resources = res_mgr.has_resources_for_tower(tower_cost, monster_coin_cost)
            
        # Create transparent surface for preview
        alpha_surface = pygame.Surface(self.tower_preview.rect.size, pygame.SRCALPHA)
        
        # Set color based on validity and resources
        if self.valid_position and has_resources:
            # Valid position and has resources
            color = list(self.tower_preview.color) + [128]  # 50% transparency
        else:
            # Invalid position or not enough resources
            color = [255, 0, 0, 128]  # Red with 50% transparency
            
        # Draw tower preview
        pygame.draw.rect(alpha_surface, color, 
                        (0, 0, self.tower_preview.rect.width, self.tower_preview.rect.height))
        self.screen.blit(alpha_surface, self.tower_preview.rect.topleft)
        
        # Draw range indicator
        line_width = max(1, self.game.scale_value(1))
        if self.valid_position and has_resources:
            # Draw pulsing range indicator when valid
            pulse_factor = (math.sin(pygame.time.get_ticks() * 0.01) + 1) * 0.1 + 0.9
            pulse_range = int(self.tower_preview.range * pulse_factor)
            pygame.draw.circle(self.screen, (200, 255, 200), 
                            mouse_pos, 
                            pulse_range, line_width)
        else:
            # Draw normal range indicator when invalid
            pygame.draw.circle(self.screen, (255, 100, 100), 
                            mouse_pos, 
                            int(self.tower_preview.range), line_width)
