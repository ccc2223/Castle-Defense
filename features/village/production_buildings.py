# features/village/production_buildings.py
"""
Mine and Coresmith building implementations for Village
"""
import pygame
from features.village.buildings import VillageBuilding
from utils import scale_value, scale_position, scale_size, draw_health_bar
from config import (
    MINE_INITIAL_PRODUCTION,
    MINE_PRODUCTION_INTERVAL,
    MINE_PRODUCTION_MULTIPLIER,
    MINE_UPGRADE_TIME_MULTIPLIER,
    MINE_INITIAL_UPGRADE_TIME,
    MINE_UPGRADE_COST,
    CORESMITH_CRAFTING_TIME,
    ITEM_COSTS
)

class Mine(VillageBuilding):
    """Resource-producing building in the village"""
    def __init__(self, position, registry):
        """
        Initialize mine with position
        
        Args:
            position: Tuple of (x, y) coordinates
            registry: Component registry for accessing game components
        """
        super().__init__(position, registry)
        self.name = "Mine"
        self.description = "Produces stone, iron, copper, and thorium resources"
        self.color = (70, 70, 50)  # Brown-ish color for mine
        self.building_type = "mine"
        
        self.resource_type = "Stone"
        self.production_rate = MINE_INITIAL_PRODUCTION
        self.production_multiplier = MINE_PRODUCTION_MULTIPLIER
        self.production_timer = 0
        self.upgrade_timer = 0
        self.upgrading = False
        self.upgrade_time = MINE_INITIAL_UPGRADE_TIME
        
        # Get resource manager from registry
        self.resource_manager = self.registry.get("resource_manager") if self.registry else None
    
    def update(self, dt):
        """
        Update mine state - produce resources or progress upgrade
        
        Args:
            dt: Time delta in seconds
        """
        if self.upgrading:
            self.update_upgrade(dt)
        else:
            self.update_production(dt)
    
    def update_production(self, dt):
        """
        Update resource production
        
        Args:
            dt: Time delta in seconds
        """
        # Ensure we have the latest resource_manager reference
        if self.registry and not self.resource_manager:
            self.resource_manager = self.registry.get("resource_manager")
        
        self.production_timer += dt
        if self.production_timer >= MINE_PRODUCTION_INTERVAL:
            self.production_timer = 0
            if self.resource_manager:
                # Add resources to the global resource manager
                self.resource_manager.add_resource(self.resource_type, self.production_rate)
    
    def update_upgrade(self, dt):
        """
        Update upgrade progress
        
        Args:
            dt: Time delta in seconds
        """
        self.upgrade_timer += dt
        if self.upgrade_timer >= self.upgrade_time:
            self.complete_upgrade()
    
    def get_upgrade_cost(self):
        """
        Get the cost to upgrade this mine
        
        Returns:
            Dictionary of resource costs
        """
        return MINE_UPGRADE_COST
    
    def handle_click(self, position):
        """
        Handle click on the mine
        
        Args:
            position: Tuple of (x, y) coordinates
            
        Returns:
            True if mine was clicked, False otherwise
        """
        # Check if mine was clicked
        if self.rect.collidepoint(position):
            self.is_selected = not self.is_selected
            return True
            
        # Check for upgrade button click if selected
        if self.is_selected and hasattr(self, 'upgrade_button_rect') and self.upgrade_button_rect.collidepoint(position):
            self.start_upgrade()
            return True
            
        # Deselect if clicked elsewhere
        self.is_selected = False
        return False
    
    def start_upgrade(self):
        """
        Start upgrading the mine
        
        Returns:
            True if upgrade started, False if already upgrading or insufficient resources
        """
        if self.upgrading or not self.resource_manager:
            return False
        
        upgrade_cost = self.get_upgrade_cost()
        if self.resource_manager.spend_resources(upgrade_cost):
            self.upgrading = True
            self.upgrade_timer = 0
            return True
        return False
    
    def complete_upgrade(self):
        """Complete the upgrade and update mine stats"""
        self.level += 1
        self.upgrading = False
        self.upgrade_timer = 0
        self.update_resource_type()
        self.production_rate *= MINE_PRODUCTION_MULTIPLIER
        self.upgrade_time *= MINE_UPGRADE_TIME_MULTIPLIER
    
    def update_resource_type(self):
        """Update resource type based on mine level"""
        if self.level >= 30:
            self.resource_type = "Thorium"
            self.color = (150, 200, 150)  # Greenish for Thorium
        elif self.level >= 20:
            self.resource_type = "Copper"
            self.color = (180, 100, 50)  # Copper color
        elif self.level >= 10:
            self.resource_type = "Iron"
            self.color = (100, 100, 120)  # Iron color
    
    def draw(self, screen):
        """
        Draw mine to screen
        
        Args:
            screen: Pygame surface to draw on
        """
        # Draw the base building
        super().draw(screen)
        
        # Draw mining icon
        pickaxe_color = (180, 180, 180)
        pickaxe_start = (self.rect.centerx - scale_value(10), self.rect.centery - scale_value(10))
        pickaxe_end = (self.rect.centerx + scale_value(10), self.rect.centery + scale_value(10))
        pygame.draw.line(screen, pickaxe_color, pickaxe_start, pickaxe_end, scale_value(3))
        
        # Draw production progress bar
        if not self.upgrading:
            progress_pos = (self.rect.left, self.rect.top - scale_value(15))
            progress_size = (self.rect.width, scale_value(5))
            production_progress = self.production_timer / MINE_PRODUCTION_INTERVAL
            
            # Choose color based on resource type
            if self.resource_type == "Stone":
                progress_color = (180, 180, 180)  # Gray for Stone
            elif self.resource_type == "Iron":
                progress_color = (150, 150, 200)  # Bluish for Iron
            elif self.resource_type == "Copper":
                progress_color = (200, 120, 50)    # Orange for Copper
            elif self.resource_type == "Thorium":
                progress_color = (100, 220, 100)   # Green for Thorium
            else:
                progress_color = (200, 200, 200)   # Default color
                
            # Draw the production progress bar
            draw_health_bar(screen, progress_pos, progress_size, 
                            production_progress, 1.0, 
                            color=progress_color, bg_color=(50, 50, 50))
            
            # Draw current resource type
            small_font = pygame.font.Font(None, scale_value(14))
            resource_text = f"Mining: {self.resource_type}"
            resource_surface = small_font.render(resource_text, True, (220, 220, 220))
            resource_rect = resource_surface.get_rect(midbottom=(self.rect.centerx, self.rect.top - scale_value(17)))
            screen.blit(resource_surface, resource_rect)
        
        # Draw upgrade progress bar if upgrading
        if self.upgrading:
            progress_pos = (self.rect.left, self.rect.bottom + scale_value(5))
            progress_size = (self.rect.width, scale_value(5))
            draw_health_bar(screen, progress_pos, progress_size, 
                           self.upgrade_timer, self.upgrade_time, 
                           color=(0, 200, 255), bg_color=(50, 50, 50))
            
            # Add upgrade progress percentage text
            small_font = pygame.font.Font(None, scale_value(14))
            upgrade_pct = int((self.upgrade_timer / self.upgrade_time) * 100)
            upgrade_text = f"Upgrading: {upgrade_pct}%"
            upgrade_label = small_font.render(upgrade_text, True, (0, 200, 255))
            upgrade_rect = upgrade_label.get_rect(center=(self.rect.centerx, self.rect.bottom + scale_value(20)))
            screen.blit(upgrade_label, upgrade_rect)
        
        # Draw additional information when selected
        if self.is_selected:
            # Draw info panel
            info_rect = pygame.Rect(
                self.rect.left - scale_value(50),
                self.rect.bottom + scale_value(10),
                self.rect.width + scale_value(100),
                scale_value(120)
            )
            pygame.draw.rect(screen, (40, 40, 30), info_rect)
            pygame.draw.rect(screen, (100, 100, 80), info_rect, 2)
            
            # Draw mine info
            font = pygame.font.Font(None, scale_value(20))
            title_text = f"Mine (Level {self.level})"
            title = font.render(title_text, True, (220, 220, 180))
            screen.blit(title, (info_rect.left + scale_value(10), info_rect.top + scale_value(10)))
            
            # Draw resource type and production rate
            small_font = pygame.font.Font(None, scale_value(16))
            resource_info = f"Resource: {self.resource_type}"
            production_info = f"Production: {self.production_rate} per {MINE_PRODUCTION_INTERVAL}s"
            
            resource_surface = small_font.render(resource_info, True, (200, 200, 200))
            production_surface = small_font.render(production_info, True, (200, 200, 200))
            
            screen.blit(resource_surface, (info_rect.left + scale_value(15), info_rect.top + scale_value(35)))
            screen.blit(production_surface, (info_rect.left + scale_value(15), info_rect.top + scale_value(55)))
            
            # Draw upgrade info
            if not self.upgrading:
                # Format upgrade cost
                upgrade_cost = self.get_upgrade_cost()
                cost_text = "Upgrade Cost: "
                for resource, amount in upgrade_cost.items():
                    cost_text += f"{amount} {resource}, "
                cost_text = cost_text.rstrip(", ")
                
                # Check if player can afford upgrade
                can_afford = self.resource_manager and self.resource_manager.has_resources(upgrade_cost)
                cost_color = (100, 200, 100) if can_afford else (200, 100, 100)
                
                cost_surface = small_font.render(cost_text, True, cost_color)
                screen.blit(cost_surface, (info_rect.left + scale_value(15), info_rect.top + scale_value(75)))
                
                # Draw upgrade button
                button_rect = pygame.Rect(
                    info_rect.centerx - scale_value(50),
                    info_rect.bottom - scale_value(30),
                    scale_value(100),
                    scale_value(20)
                )
                
                # Store button rect for click detection
                self.upgrade_button_rect = button_rect
                
                # Button color based on affordability
                button_color = (80, 120, 80) if can_afford else (80, 80, 80)
                pygame.draw.rect(screen, button_color, button_rect)
                pygame.draw.rect(screen, (150, 150, 150), button_rect, 1)
                
                # Button text
                button_text = "Upgrade" if can_afford else "Can't Afford"
                button_surface = small_font.render(button_text, True, (220, 220, 220))
                button_rect = button_surface.get_rect(center=button_rect.center)
                screen.blit(button_surface, button_rect)
            else:
                # Show upgrading status
                upgrading_text = f"Upgrading... {int((self.upgrade_timer / self.upgrade_time) * 100)}%"
                upgrading_surface = small_font.render(upgrading_text, True, (100, 180, 220))
                screen.blit(upgrading_surface, (info_rect.left + scale_value(15), info_rect.top + scale_value(75)))
                
                next_level_text = f"Next Level: {self.level + 1}"
                next_level_surface = small_font.render(next_level_text, True, (200, 200, 200))
                screen.blit(next_level_surface, (info_rect.left + scale_value(15), info_rect.top + scale_value(95)))
    
    def get_info_text(self):
        """
        Get mine information text
        
        Returns:
            List of text lines with mine information
        """
        info = super().get_info_text()
        
        # Add mine-specific info
        info.extend([
            f"Resource: {self.resource_type}",
            f"Production: {self.production_rate} per {MINE_PRODUCTION_INTERVAL}s"
        ])
        
        if self.upgrading:
            upgrade_pct = int((self.upgrade_timer / self.upgrade_time) * 100)
            info.append(f"Upgrading: {upgrade_pct}%")
        
        return info


class Coresmith(VillageBuilding):
    """Building for crafting items in the village"""
    def __init__(self, position, registry):
        """
        Initialize coresmith with position
        
        Args:
            position: Tuple of (x, y) coordinates
            registry: Component registry for accessing game components
        """
        super().__init__(position, registry)
        self.name = "Coresmith"
        self.description = "Crafts special items from monster cores"
        self.color = (50, 80, 100)  # Bluish color for coresmith
        self.building_type = "coresmith"
        
        # Crafting properties
        self.crafting = False
        self.crafting_timer = 0
        self.crafting_time = CORESMITH_CRAFTING_TIME
        self.current_item = None
        
        # Get resource manager from registry
        self.resource_manager = self.registry.get("resource_manager") if self.registry else None
        
        # Track selected item for crafting
        self.selected_item = None
        
        # Available items to craft
        self.available_items = list(ITEM_COSTS.keys())
    
    def update(self, dt):
        """
        Update coresmith state - progress crafting
        
        Args:
            dt: Time delta in seconds
        """
        if self.crafting:
            self.crafting_timer += dt
            if self.crafting_timer >= self.crafting_time:
                self.complete_crafting()
    
    def start_crafting(self, item_type):
        """
        Start crafting an item
        
        Args:
            item_type: Type of item to craft
            
        Returns:
            True if crafting started, False if already crafting or insufficient resources
        """
        if self.crafting or not self.resource_manager:
            return False
        
        if item_type not in ITEM_COSTS:
            return False
        
        if self.resource_manager.spend_resources(ITEM_COSTS[item_type]):
            self.crafting = True
            self.current_item = item_type
            self.crafting_timer = 0
            self.selected_item = None  # Clear selection after starting craft
            return True
        return False
    
    def complete_crafting(self):
        """
        Complete crafting and add item to inventory
        """
        if self.current_item and self.resource_manager:
            self.resource_manager.add_resource(self.current_item, 1)
            self.crafting = False
            self.current_item = None
            self.crafting_timer = 0
    
    def handle_click(self, position):
        """
        Handle click on coresmith or its items
        
        Args:
            position: Tuple of (x, y) coordinates
            
        Returns:
            True if coresmith was clicked, False otherwise
        """
        # Check if coresmith was clicked
        if self.rect.collidepoint(position):
            # Now instead of toggling selection, open the coresmith state
            if self.registry and self.registry.has("game"):
                game = self.registry.get("game")
                if hasattr(game, 'state_manager'):
                    game.state_manager.change_state("coresmith")
                    return True
            # Fall back to old behavior if we can't access the state manager
            self.is_selected = not self.is_selected
            return True
        
        # Handle item selection if coresmith is selected
        if self.is_selected and hasattr(self, 'item_rects'):
            for i, item_rect in enumerate(self.item_rects):
                if item_rect.collidepoint(position) and i < len(self.available_items):
                    self.selected_item = self.available_items[i]
                    return True
        
        # Handle craft button click
        if self.is_selected and hasattr(self, 'craft_button_rect') and self.craft_button_rect.collidepoint(position):
            if self.selected_item:
                self.start_crafting(self.selected_item)
            return True
        
        # Deselect if clicked elsewhere
        self.is_selected = False
        return False
    
    def draw(self, screen):
        """
        Draw coresmith to screen
        
        Args:
            screen: Pygame surface to draw on
        """
        # Draw base building
        super().draw(screen)
        
        # Draw a forge/anvil icon
        anvil_color = (150, 150, 180)
        anvil_rect = pygame.Rect(
            self.rect.centerx - scale_value(10),
            self.rect.centery - scale_value(5),
            scale_value(20),
            scale_value(10)
        )
        pygame.draw.rect(screen, anvil_color, anvil_rect)
        
        # Draw progress bar if crafting
        if self.crafting:
            progress_pos = (self.rect.left, self.rect.top - scale_value(15))
            progress_size = (self.rect.width, scale_value(5))
            draw_health_bar(screen, progress_pos, progress_size, 
                           self.crafting_timer, self.crafting_time, 
                           color=(255, 200, 0), bg_color=(50, 50, 50))
            
            # Draw item being crafted
            small_font = pygame.font.Font(None, scale_value(14))
            craft_text = f"Crafting: {self.current_item}"
            text_surface = small_font.render(craft_text, True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=(self.rect.centerx, self.rect.top - scale_value(25)))
            screen.blit(text_surface, text_rect)
        
        # Draw additional information when selected
        if self.is_selected:
            # Draw info panel
            info_rect = pygame.Rect(
                self.rect.left - scale_value(50),
                self.rect.bottom + scale_value(10),
                self.rect.width + scale_value(100),
                scale_value(180)
            )
            pygame.draw.rect(screen, (30, 40, 50), info_rect)
            pygame.draw.rect(screen, (80, 100, 120), info_rect, 2)
            
            # Draw coresmith info
            font = pygame.font.Font(None, scale_value(20))
            title = font.render("Coresmith", True, (200, 220, 240))
            screen.blit(title, (info_rect.left + scale_value(10), info_rect.top + scale_value(10)))
            
            # Draw description
            small_font = pygame.font.Font(None, scale_value(16))
            desc_text = "Craft special items from monster cores."
            desc_surface = small_font.render(desc_text, True, (180, 200, 220))
            screen.blit(desc_surface, (info_rect.left + scale_value(15), info_rect.top + scale_value(35)))
            
            # Draw available items to craft
            items_text = "Available Items:"
            items_surface = small_font.render(items_text, True, (200, 200, 220))
            screen.blit(items_surface, (info_rect.left + scale_value(15), info_rect.top + scale_value(55)))
            
            # Draw item options with cost info
            item_y = info_rect.top + scale_value(75)
            self.item_rects = []
            
            for i, item_name in enumerate(self.available_items):
                # Calculate item rectangle
                item_rect = pygame.Rect(
                    info_rect.left + scale_value(15),
                    item_y,
                    info_rect.width - scale_value(30),
                    scale_value(20)
                )
                self.item_rects.append(item_rect)
                
                # Highlight selected item
                if self.selected_item == item_name:
                    pygame.draw.rect(screen, (80, 100, 120), item_rect)
                pygame.draw.rect(screen, (120, 140, 160), item_rect, 1)
                
                # Draw item name
                item_text = small_font.render(item_name, True, (220, 220, 220))
                screen.blit(item_text, (item_rect.left + scale_value(5), item_rect.centery - scale_value(7)))
                
                # Format cost string
                cost_text = "Cost: "
                for resource, amount in ITEM_COSTS[item_name].items():
                    cost_text += f"{amount} {resource}, "
                cost_text = cost_text.rstrip(", ")
                
                # Check if player can afford this item
                can_afford = self.resource_manager and self.resource_manager.has_resources(ITEM_COSTS[item_name])
                cost_color = (100, 200, 100) if can_afford else (200, 100, 100)
                
                cost_surface = pygame.font.Font(None, scale_value(14)).render(cost_text, True, cost_color)
                screen.blit(cost_surface, (item_rect.left + scale_value(5), item_rect.centery + scale_value(2)))
                
                # Move y position for next item
                item_y += scale_value(25)
            
            # Draw craft button if an item is selected
            if self.selected_item:
                button_rect = pygame.Rect(
                    info_rect.centerx - scale_value(40),
                    info_rect.bottom - scale_value(30),
                    scale_value(80),
                    scale_value(20)
                )
                self.craft_button_rect = button_rect
                
                # Check if player can afford the selected item
                can_afford = self.resource_manager and self.resource_manager.has_resources(ITEM_COSTS[self.selected_item])
                button_color = (80, 120, 160) if can_afford else (80, 80, 100)
                pygame.draw.rect(screen, button_color, button_rect)
                pygame.draw.rect(screen, (150, 170, 200), button_rect, 1)
                
                # Button text
                button_text = "Craft" if can_afford else "Can't Afford"
                button_surface = small_font.render(button_text, True, (220, 220, 240))
                button_text_rect = button_surface.get_rect(center=button_rect.center)
                screen.blit(button_surface, button_text_rect)
    
    def get_info_text(self):
        """
        Get coresmith information text
        
        Returns:
            List of text lines with coresmith information
        """
        info = super().get_info_text()
        
        if self.crafting:
            craft_pct = int((self.crafting_timer / self.crafting_time) * 100)
            info.append(f"Crafting {self.current_item}: {craft_pct}%")
        else:
            info.append("Available for crafting")
        
        return info
