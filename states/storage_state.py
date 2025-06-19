# storage_state.py
"""
Storage Barn inventory state for Castle Defense
"""
import pygame
from .game_state import GameState
from registry import RESOURCE_MANAGER, ICON_MANAGER

class StorageState(GameState):
    """
    Storage Barn state for viewing all resources and items in one place
    """
    def __init__(self, game):
        """
        Initialize storage state
        
        Args:
            game: Game instance
        """
        super().__init__(game)
        
        # Store references to commonly used components
        self.resource_manager = self.game.registry.get(RESOURCE_MANAGER)
        self.icon_manager = self.game.registry.get(ICON_MANAGER)
        
        # Track which tab is active
        self.active_tab = "Resources"
        self.tabs = ["Resources", "Special", "Cores", "Food", "Items"]
        
        # Button to close the storage view
        button_size = game.scale_size((120, 40))
        button_pos = (game.WINDOW_WIDTH - button_size[0] - 10, 10)  # Top-right corner
        self.close_button_rect = pygame.Rect(
            button_pos[0], 
            button_pos[1], 
            button_size[0], 
            button_size[1]
        )
        self.close_button_color = (150, 70, 70)
        self.close_button_hover_color = (200, 90, 90)
        self.close_button_is_hovered = False
        
        # Tab buttons
        self.tab_width = game.scale_value(120)
        self.tab_height = game.scale_value(40)
        self.tab_margin = game.scale_value(10)
        self.tab_start_x = game.scale_value(50)
        self.tab_y = game.scale_value(50)
        
        self.tab_rects = []
        for i, tab in enumerate(self.tabs):
            tab_rect = pygame.Rect(
                self.tab_start_x + i * (self.tab_width + self.tab_margin),
                self.tab_y,
                self.tab_width,
                self.tab_height
            )
            self.tab_rects.append((tab, tab_rect))
        
        # Search bar
        self.search_rect = pygame.Rect(
            self.tab_start_x + len(self.tabs) * (self.tab_width + self.tab_margin) + self.tab_margin,
            self.tab_y,
            game.scale_value(200),
            self.tab_height
        )
        self.search_text = ""
        self.search_active = False
        
        # Resource display settings
        self.grid_start_y = self.tab_y + self.tab_height + game.scale_value(20)
        self.grid_start_x = self.tab_start_x
        self.grid_cell_width = game.scale_value(180)
        self.grid_cell_height = game.scale_value(90)
        self.grid_margin = game.scale_value(15)
        self.grid_cols = 5
        
        # Resource category mappings
        self.resource_categories = {
            "Resources": ["Stone", "Iron", "Copper", "Thorium"],
            "Special": ["Monster Coins"],
            "Cores": ["Force Core", "Spirit Core", "Magic Core", "Void Core"],
            "Food": ["Grain", "Fruit", "Meat", "Dairy"],
            "Items": ["Unstoppable Force", "Serene Spirit", "Multitudation Vortex"]
        }
        
        # Track hovered resource for tooltips
        self.hovered_resource = None
        
        # Sort order
        self.sort_by = "name"  # "name" or "quantity"
        self.sort_ascending = True
    
    def handle_events(self, events):
        """
        Handle input events for storage state
        
        Args:
            events: List of pygame events
            
        Returns:
            Boolean indicating if events were handled
        """
        for event in events:
            # Track mouse position for button hover
            if event.type == pygame.MOUSEMOTION:
                mouse_pos = event.pos
                self.close_button_is_hovered = self.close_button_rect.collidepoint(mouse_pos)
                
                # Track tab hovers
                self.hovered_resource = None
                
                # Check for resource hovers in the grid
                resources = self.get_filtered_resources()
                for i, resource in enumerate(resources):
                    row = i // self.grid_cols
                    col = i % self.grid_cols
                    cell_rect = pygame.Rect(
                        self.grid_start_x + col * (self.grid_cell_width + self.grid_margin),
                        self.grid_start_y + row * (self.grid_cell_height + self.grid_margin),
                        self.grid_cell_width,
                        self.grid_cell_height
                    )
                    if cell_rect.collidepoint(mouse_pos):
                        self.hovered_resource = resource
                        break
                
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                
                # Check if close button was clicked
                if self.close_button_rect.collidepoint(mouse_pos):
                    self.game.state_manager.change_state("village")
                    return True
                
                # Check if a tab was clicked
                for tab, rect in self.tab_rects:
                    if rect.collidepoint(mouse_pos):
                        self.active_tab = tab
                        return True
                
                # Check if search bar was clicked
                if self.search_rect.collidepoint(mouse_pos):
                    self.search_active = True
                    return True
                else:
                    self.search_active = False
                
                # Check for sort button clicks (will add sorting UI later)
                
            elif event.type == pygame.KEYDOWN and self.search_active:
                # Handle search text input
                if event.key == pygame.K_BACKSPACE:
                    self.search_text = self.search_text[:-1]
                elif event.key == pygame.K_RETURN:
                    self.search_active = False
                elif len(self.search_text) < 20:  # Limit search text length
                    self.search_text += event.unicode
                return True
                
            # Escape key to exit storage view
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.game.state_manager.change_state("village")
                return True
        
        return False
    
    def update(self, dt):
        """
        Update storage state
        
        Args:
            dt: Time delta in seconds
        """
        # No animation or continuous updates needed for now
        pass
    
    def get_filtered_resources(self):
        """
        Get resources filtered by active tab and search text
        
        Returns:
            List of resource names matching current filters
        """
        # Get resources for the active tab
        resources = self.resource_categories.get(self.active_tab, [])
        
        # Filter by search text if any
        if self.search_text:
            search_lower = self.search_text.lower()
            resources = [r for r in resources if search_lower in r.lower()]
        
        # Sort resources
        if self.sort_by == "name":
            resources.sort(reverse=not self.sort_ascending)
        elif self.sort_by == "quantity":
            resources.sort(key=lambda r: self.resource_manager.get_resource(r), 
                          reverse=not self.sort_ascending)
        
        return resources
    
    def draw(self, screen):
        """
        Draw storage state to screen
        
        Args:
            screen: Pygame surface to draw on
        """
        # Draw a semi-transparent overlay
        overlay = pygame.Surface((self.game.WINDOW_WIDTH, self.game.WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))  # Black with 80% opacity
        screen.blit(overlay, (0, 0))
        
        # Draw storage title
        font_large = pygame.font.Font(None, self.game.scale_value(48))
        title_text = font_large.render("Storage Barn", True, (255, 255, 255))
        title_rect = title_text.get_rect(midtop=(self.game.WINDOW_WIDTH // 2, self.game.scale_value(10)))
        screen.blit(title_text, title_rect)
        
        # Draw close button
        color = self.close_button_hover_color if self.close_button_is_hovered else self.close_button_color
        pygame.draw.rect(screen, color, self.close_button_rect)
        pygame.draw.rect(screen, (200, 150, 150), self.close_button_rect, 2)  # Border
        
        # Draw close button text
        font = pygame.font.Font(None, self.game.scale_value(22))
        text = font.render("Close", True, (230, 230, 230))
        text_rect = text.get_rect(center=self.close_button_rect.center)
        screen.blit(text, text_rect)
        
        # Draw tabs
        font_tab = pygame.font.Font(None, self.game.scale_value(26))
        for tab, rect in self.tab_rects:
            # Highlight active tab
            if tab == self.active_tab:
                color = (100, 130, 160)
                border_color = (150, 180, 220)
                text_color = (255, 255, 255)
            else:
                color = (70, 90, 110)
                border_color = (120, 140, 170)
                text_color = (200, 200, 200)
            
            pygame.draw.rect(screen, color, rect)
            pygame.draw.rect(screen, border_color, rect, 2)  # Border
            
            # Draw tab text
            tab_text = font_tab.render(tab, True, text_color)
            tab_text_rect = tab_text.get_rect(center=rect.center)
            screen.blit(tab_text, tab_text_rect)
        
        # Draw search bar
        search_color = (100, 100, 120) if self.search_active else (80, 80, 90)
        pygame.draw.rect(screen, search_color, self.search_rect)
        pygame.draw.rect(screen, (150, 150, 170), self.search_rect, 2)  # Border
        
        # Draw search text and placeholder
        if self.search_text:
            search_display = self.search_text
            text_color = (255, 255, 255)
        else:
            search_display = "Search..." if not self.search_active else ""
            text_color = (180, 180, 180)
        
        search_text = font.render(search_display, True, text_color)
        search_text_rect = search_text.get_rect(midleft=(self.search_rect.left + 10, self.search_rect.centery))
        screen.blit(search_text, search_text_rect)
        
        # Draw resource grid
        resources = self.get_filtered_resources()
        
        for i, resource in enumerate(resources):
            row = i // self.grid_cols
            col = i % self.grid_cols
            
            # Calculate cell position
            cell_rect = pygame.Rect(
                self.grid_start_x + col * (self.grid_cell_width + self.grid_margin),
                self.grid_start_y + row * (self.grid_cell_height + self.grid_margin),
                self.grid_cell_width,
                self.grid_cell_height
            )
            
            # Get resource color based on category
            if resource in self.resource_categories["Resources"]:
                cell_color = (80, 100, 120)
                border_color = (120, 140, 170)
            elif resource in self.resource_categories["Special"]:
                cell_color = (120, 100, 150)
                border_color = (160, 140, 190)
            elif resource in self.resource_categories["Cores"]:
                cell_color = (150, 100, 100)
                border_color = (190, 140, 140)
            elif resource in self.resource_categories["Food"]:
                cell_color = (100, 130, 80)
                border_color = (140, 170, 120)
            elif resource in self.resource_categories["Items"]:
                cell_color = (130, 110, 80)
                border_color = (170, 150, 120)
            else:
                cell_color = (100, 100, 100)
                border_color = (150, 150, 150)
            
            # Highlight if this cell is hovered
            if resource == self.hovered_resource:
                cell_color = tuple(min(c + 30, 255) for c in cell_color)
                border_color = tuple(min(c + 30, 255) for c in border_color)
                
            # Draw cell background
            pygame.draw.rect(screen, cell_color, cell_rect)
            pygame.draw.rect(screen, border_color, cell_rect, 2)  # Border
            
            # Draw resource icon if available
            if self.icon_manager and hasattr(self.icon_manager, 'get_icon'):
                try:
                    # Convert resource name to icon ID before getting the icon
                    icon_id = self.icon_manager.get_resource_icon_id(resource)
                    # Get the icon
                    icon = self.icon_manager.get_icon(icon_id)
                    if icon:
                        # Determine icon position (centered in upper part of cell)
                        icon_rect = icon.get_rect(midtop=(cell_rect.centerx, cell_rect.top + self.game.scale_value(10)))
                        screen.blit(icon, icon_rect)
                except Exception as e:
                    # If icon retrieval fails, print error but continue
                    print(f"Error getting icon for {resource}: {e}")
            
            # Draw resource name
            font_name = pygame.font.Font(None, self.game.scale_value(22))
            name_text = font_name.render(resource, True, (255, 255, 255))
            name_rect = name_text.get_rect(midtop=(cell_rect.centerx, cell_rect.centery - self.game.scale_value(10)))
            screen.blit(name_text, name_rect)
            
            # Draw resource quantity
            quantity = self.resource_manager.get_resource(resource)
            font_quantity = pygame.font.Font(None, self.game.scale_value(26))
            quantity_text = font_quantity.render(str(quantity), True, (255, 255, 255))
            quantity_rect = quantity_text.get_rect(midbottom=(cell_rect.centerx, cell_rect.bottom - self.game.scale_value(10)))
            screen.blit(quantity_text, quantity_rect)
        
        # Draw tooltip for hovered resource
        if self.hovered_resource:
            tooltip_font = pygame.font.Font(None, self.game.scale_value(18))
            
            # Determine tooltip text based on resource type
            tooltip_text = f"Resource: {self.hovered_resource}"
            
            # Add special descriptions for different resource types
            if self.hovered_resource in self.resource_categories["Resources"]:
                tooltip_text += " - Building material"
            elif self.hovered_resource == "Monster Coins":
                tooltip_text += " - Special currency from defeated monsters"
            elif self.hovered_resource in self.resource_categories["Cores"]:
                tooltip_text += " - Rare drop from boss monsters, used for crafting"
            elif self.hovered_resource in self.resource_categories["Food"]:
                tooltip_text += " - Food resource from farms"
            elif self.hovered_resource == "Unstoppable Force":
                tooltip_text += " - Tower item: Increases AoE by 30%"
            elif self.hovered_resource == "Serene Spirit":
                tooltip_text += " - Tower item: Converts 5% damage to castle healing"
            elif self.hovered_resource == "Multitudation Vortex":
                tooltip_text += " - Tower item: 10% chance for projectiles to bounce to a second target"
            
            # Render tooltip
            tooltip_surface = tooltip_font.render(tooltip_text, True, (255, 255, 255))
            
            # Get mouse position for tooltip placement
            mouse_pos = pygame.mouse.get_pos()
            tooltip_rect = tooltip_surface.get_rect(topleft=(mouse_pos[0] + 15, mouse_pos[1] + 15))
            
            # Ensure tooltip stays within screen bounds
            if tooltip_rect.right > self.game.WINDOW_WIDTH:
                tooltip_rect.right = self.game.WINDOW_WIDTH - 5
            if tooltip_rect.bottom > self.game.WINDOW_HEIGHT:
                tooltip_rect.bottom = self.game.WINDOW_HEIGHT - 5
            
            # Draw tooltip background and text
            pygame.draw.rect(screen, (50, 50, 60), tooltip_rect.inflate(10, 10))
            pygame.draw.rect(screen, (100, 100, 120), tooltip_rect.inflate(10, 10), 2)
            screen.blit(tooltip_surface, tooltip_rect)
