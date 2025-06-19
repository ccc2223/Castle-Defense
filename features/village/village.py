# features/village/village.py
"""
Village implementation for Castle Defense
Represents the village area and manages village buildings
"""
import pygame
from utils import scale_position, scale_size, scale_value
from config import VILLAGE_BUILDING_COSTS

# Village constants
VILLAGE_WIDTH = 800  # Increased to use more screen space
VILLAGE_HEIGHT = 600  # Increased to use more screen space

class Village:
    """
    Represents the village area
    Manages village buildings and interactions
    """
    def __init__(self, registry, position):
        """
        Initialize village with position
        
        Args:
            registry: Component registry for accessing game components
            position: Tuple of (x, y) coordinates for village center
        """
        self.registry = registry
        self.position = position
        
        # Define village area
        self.ref_size = (VILLAGE_WIDTH, VILLAGE_HEIGHT)
        self.size = scale_size(self.ref_size)
        self.rect = pygame.Rect(
            self.position[0] - self.size[0] // 2,
            self.position[1] - self.size[1] // 2,
            self.size[0],
            self.size[1]
        )
        
        # Initialize buildings list
        self.buildings = []
        
        # Track development level
        self.development_level = 1
        
        # Initialize talent points
        self.talent_points = 0
        
        # Initialize village capacity
        self.capacity = 10  # Increased starting capacity for buildings to accommodate auto-built and player buildings
        self.used_capacity = 0  # Track how much capacity is used
        
        # Create building plots
        self.plots = []
        self.selected_plot = None
        self.init_building_plots()
        
        # Purchase confirmation
        self.show_purchase_dialog = False
        self.purchase_building_type = None
    
    def init_building_plots(self):
        """
        Initialize the predefined building plots for the village
        """
        plot_size = scale_size((100, 100))
        
        # We need to ensure all plots stay within the village rectangle
        # Use the village rect for positioning, not arbitrary spacing values
        
        # Calculate relative positions within the village rect
        # Leave margins to prevent buildings from being cut off
        margin = scale_value(20)  # Margin from the edge of the village
        
        # Available area for building placement
        available_width = self.rect.width - (2 * margin)
        available_height = self.rect.height - (2 * margin)
        
        # Coordinate references for positioning relative to village rect
        left = self.rect.left + margin
        right = self.rect.right - margin - plot_size[0]
        top = self.rect.top + margin
        bottom = self.rect.bottom - margin - plot_size[1]
        center_x = self.rect.centerx - (plot_size[0] // 2)
        center_y = self.rect.centery - (plot_size[1] // 2)
        
        # Calculate horizontal placement positions (divide available width into 5 sections)
        h_step = available_width // 4  # Use 4 steps for 5 positions
        pos_x = [left, left + h_step, center_x, right - h_step, right]
        
        # Calculate vertical placement positions (divide available height into 5 sections)
        v_step = available_height // 4  # Use 4 steps for 5 positions
        pos_y = [top, top + v_step, center_y, bottom - v_step, bottom]
        
        # Create plots with their designated positions and building types
        # Town Hall (center top)
        town_hall_plot = {
            "rect": pygame.Rect(
                pos_x[2],  # Center horizontal position
                pos_y[1],  # Upper part of the village
                plot_size[0],
                plot_size[1]
            ),
            "building_type": "TownHall",
            "occupied": False,
            "building": None,
            "name": "Town Hall",
            "description": "Central management building and talent hub",
            "color": (150, 120, 80),
            "is_hovered": False
        }
        self.plots.append(town_hall_plot)
        
        # Storage Barn (upper center right)
        storage_barn_plot = {
            "rect": pygame.Rect(
                pos_x[4],  # Right section
                pos_y[1],  # Upper part of the village
                plot_size[0],
                plot_size[1]
            ),
            "building_type": "StorageBarn",
            "occupied": False,
            "building": None,
            "name": "Storage Barn",
            "description": "Central inventory for all resources and items",
            "color": (120, 90, 60),
            "is_hovered": False
        }
        self.plots.append(storage_barn_plot)
        
        # Research Lab (upper right)
        research_lab_plot = {
            "rect": pygame.Rect(
                pos_x[3],  # Right section
                pos_y[2],  # Center vertical
                plot_size[0],
                plot_size[1]
            ),
            "building_type": "ResearchLab",
            "occupied": False,
            "building": None,
            "name": "Research Lab",
            "description": "Discovers and develops technological improvements",
            "color": (50, 100, 150),
            "is_hovered": False
        }
        self.plots.append(research_lab_plot)
        
        # Monster Codex (upper left)
        monster_codex_plot = {
            "rect": pygame.Rect(
                pos_x[1],  # Left section
                pos_y[2],  # Center vertical
                plot_size[0],
                plot_size[1]
            ),
            "building_type": "MonsterCodex",
            "occupied": False,
            "building": None,
            "name": "Monster Codex",
            "description": "Catalogues monsters and provides monster-specific upgrades",
            "color": (150, 50, 50),
            "is_hovered": False
        }
        self.plots.append(monster_codex_plot)
        
        # Mine (left)
        mine_plot = {
            "rect": pygame.Rect(
                pos_x[0],  # Far left
                pos_y[2],  # Center vertical
                plot_size[0],
                plot_size[1]
            ),
            "building_type": "Mine",
            "occupied": False,
            "building": None,
            "name": "Mine",
            "description": "Produces stone, iron, copper, and thorium resources",
            "color": (70, 70, 50),
            "is_hovered": False
        }
        self.plots.append(mine_plot)
        
        # Coresmith (far right)
        coresmith_plot = {
            "rect": pygame.Rect(
                pos_x[4],  # Far right
                pos_y[2],  # Center vertical
                plot_size[0],
                plot_size[1]
            ),
            "building_type": "Coresmith",
            "occupied": False,
            "building": None,
            "name": "Coresmith",
            "description": "Crafts special items from monster cores",
            "color": (50, 80, 100),
            "is_hovered": False
        }
        self.plots.append(coresmith_plot)
        
        # Crop Farm (bottom left)
        crop_farm_plot = {
            "rect": pygame.Rect(
                pos_x[1],  # Left section
                pos_y[3],  # Lower section
                plot_size[0],
                plot_size[1]
            ),
            "building_type": "CropFarm",
            "occupied": False,
            "building": None,
            "name": "Crop Farm",
            "description": "Produces grain and fruit resources",
            "color": (100, 150, 50),
            "is_hovered": False
        }
        self.plots.append(crop_farm_plot)
        
        # Livestock Farm (bottom right)
        livestock_farm_plot = {
            "rect": pygame.Rect(
                pos_x[3],  # Right section
                pos_y[3],  # Lower section
                plot_size[0],
                plot_size[1]
            ),
            "building_type": "LivestockFarm",
            "occupied": False,
            "building": None,
            "name": "Livestock Farm",
            "description": "Produces meat and dairy resources",
            "color": (150, 120, 80),
            "is_hovered": False
        }
        self.plots.append(livestock_farm_plot)
    
    def update(self, dt):
        """
        Update village state
        
        Args:
            dt: Time delta in seconds
        """
        # Update all buildings
        for building in self.buildings:
            # Ensure each building's resource_manager reference is refreshed
            if hasattr(building, 'resource_manager') and self.registry and self.registry.has("resource_manager"):
                building.resource_manager = self.registry.get("resource_manager")
            
            # Then update the building
            building.update(dt)
    
    def update_plot_hover(self, mouse_pos):
        """
        Update hover state for plots
        
        Args:
            mouse_pos: Current mouse position
        """
        for plot in self.plots:
            plot["is_hovered"] = plot["rect"].collidepoint(mouse_pos) and not plot["occupied"]
    
    def draw(self, screen):
        """
        Draw village to screen
        
        Args:
            screen: Pygame surface to draw on
        """
        # Draw a subtle ground texture/pattern for the village
        # This helps visually distinguish the village area
        ground_color = (30, 60, 30)  # Dark green base
        
        for y in range(0, self.rect.height, 20):
            for x in range(0, self.rect.width, 20):
                # Add some subtle variation to the ground color
                variation = (x * y) % 10 - 5
                tile_color = (ground_color[0] + variation, 
                             ground_color[1] + variation, 
                             ground_color[2] + variation)
                
                # Draw a small square for the ground tile
                tile_rect = pygame.Rect(
                    self.rect.left + x,
                    self.rect.top + y,
                    10, 10
                )
                pygame.draw.rect(screen, tile_color, tile_rect)
        
        # Draw building plots
        self.draw_building_plots(screen)
        
        # Draw all buildings
        for building in self.buildings:
            building.draw(screen)
            
        # Draw purchase dialog if active
        if self.show_purchase_dialog and self.selected_plot:
            self.draw_purchase_dialog(screen)
            
        # Draw village name and capacity info
        font = pygame.font.Font(None, scale_value(36))
        title = font.render("Village", True, (200, 220, 180))
        title_rect = title.get_rect(midtop=(self.rect.centerx, self.rect.top + 10))
        screen.blit(title, title_rect)
        
        # Draw capacity info beneath the title
        capacity_font = pygame.font.Font(None, scale_value(20))
        capacity_text = f"Buildings: {self.used_capacity}/{self.capacity}"
        capacity_color = (180, 220, 180) if self.used_capacity < self.capacity else (220, 150, 150)
        capacity_surface = capacity_font.render(capacity_text, True, capacity_color)
        capacity_rect = capacity_surface.get_rect(midtop=(self.rect.centerx, title_rect.bottom + 5))
        screen.blit(capacity_surface, capacity_rect)
    
    def draw_building_plots(self, screen):
        """
        Draw building plots and their states
        
        Args:
            screen: Pygame surface to draw on
        """
        font = pygame.font.Font(None, scale_value(18))
        small_font = pygame.font.Font(None, scale_value(14))
        
        for plot in self.plots:
            # Determine how to draw based on whether it's occupied
            if plot["occupied"]:
                # If occupied, don't draw the plot - the building itself will be drawn
                continue
            
            # Draw empty plot with dashed outline
            if plot["is_hovered"]:
                # Brighter color when hovered
                border_color = (200, 200, 200)
                bg_color = (plot["color"][0] + 20, plot["color"][1] + 20, plot["color"][2] + 20, 80)
            else:
                border_color = (150, 150, 150)
                bg_color = (*plot["color"], 50)  # Semi-transparent background
                
            # Draw plot background
            bg_surface = pygame.Surface(plot["rect"].size, pygame.SRCALPHA)
            bg_surface.fill(bg_color)
            screen.blit(bg_surface, plot["rect"])
            
            # Draw dashed border
            self.draw_dashed_rect(screen, plot["rect"], border_color, 2)
            
            # Draw building icon or placeholder
            icon_size = scale_value(30)
            icon_rect = pygame.Rect(
                plot["rect"].centerx - icon_size // 2,
                plot["rect"].centery - icon_size // 2,
                icon_size,
                icon_size
            )
            pygame.draw.rect(screen, plot["color"], icon_rect)
            
            # Draw building name
            name_surface = font.render(plot["name"], True, (220, 220, 220))
            name_rect = name_surface.get_rect(center=(plot["rect"].centerx, plot["rect"].top - 10))
            screen.blit(name_surface, name_rect)
            
            # When hovered, show more info
            if plot["is_hovered"]:
                # Draw cost info
                cost_text = "Cost: "
                building_cost = VILLAGE_BUILDING_COSTS.get(plot["building_type"], {})
                for resource, amount in building_cost.items():
                    cost_text += f"{amount} {resource}, "
                
                # Remove trailing comma and space
                if cost_text.endswith(", "):
                    cost_text = cost_text[:-2]
                
                # Get resource manager and check if player can afford it
                resource_manager = self.registry.get("resource_manager")
                has_resources = resource_manager.has_resources(building_cost)
                
                # Color based on affordability
                cost_color = (100, 200, 100) if has_resources else (200, 100, 100)
                
                cost_surface = small_font.render(cost_text, True, cost_color)
                cost_rect = cost_surface.get_rect(midtop=(plot["rect"].centerx, plot["rect"].bottom + 5))
                screen.blit(cost_surface, cost_rect)
                
                # Description on hover
                desc_surface = small_font.render(plot["description"], True, (200, 200, 200))
                desc_rect = desc_surface.get_rect(midtop=(plot["rect"].centerx, plot["rect"].bottom + 25))
                screen.blit(desc_surface, desc_rect)
                
                # Draw "Click to build" prompt
                prompt_surface = small_font.render("Click to build", True, (180, 220, 180))
                prompt_rect = prompt_surface.get_rect(midtop=(plot["rect"].centerx, plot["rect"].bottom + 45))
                screen.blit(prompt_surface, prompt_rect)
    
    def draw_dashed_rect(self, screen, rect, color, width=1, dash_length=10):
        """
        Draw a dashed rectangle outline
        
        Args:
            screen: Pygame surface to draw on
            rect: Rectangle to draw
            color: Color tuple
            width: Line width
            dash_length: Length of each dash
        """
        # Draw top line
        x, y = rect.topleft
        x2, y2 = rect.topright
        for i in range(0, int(x2 - x), dash_length * 2):
            start_pos = (x + i, y)
            end_pos = (min(x + i + dash_length, x2), y)
            pygame.draw.line(screen, color, start_pos, end_pos, width)
        
        # Draw right line
        x, y = rect.topright
        x2, y2 = rect.bottomright
        for i in range(0, int(y2 - y), dash_length * 2):
            start_pos = (x, y + i)
            end_pos = (x, min(y + i + dash_length, y2))
            pygame.draw.line(screen, color, start_pos, end_pos, width)
        
        # Draw bottom line
        x, y = rect.bottomleft
        x2, y2 = rect.bottomright
        for i in range(0, int(x2 - x), dash_length * 2):
            start_pos = (x + i, y)
            end_pos = (min(x + i + dash_length, x2), y)
            pygame.draw.line(screen, color, start_pos, end_pos, width)
        
        # Draw left line
        x, y = rect.topleft
        x2, y2 = rect.bottomleft
        for i in range(0, int(y2 - y), dash_length * 2):
            start_pos = (x, y + i)
            end_pos = (x, min(y + i + dash_length, y2))
            pygame.draw.line(screen, color, start_pos, end_pos, width)
    
    def draw_purchase_dialog(self, screen):
        """
        Draw the purchase confirmation dialog
        
        Args:
            screen: Pygame surface to draw on
        """
        if not self.selected_plot:
            return
            
        # Get information about the building being purchased
        plot = self.selected_plot
        building_type = plot["building_type"]
        building_name = plot["name"]
        building_cost = VILLAGE_BUILDING_COSTS.get(building_type, {})
        resource_manager = self.registry.get("resource_manager")
        has_resources = resource_manager.has_resources(building_cost)
        
        # Dialog dimensions
        dialog_width = scale_value(400)
        dialog_height = scale_value(220)
        dialog_rect = pygame.Rect(
            screen.get_width() // 2 - dialog_width // 2,
            screen.get_height() // 2 - dialog_height // 2,
            dialog_width,
            dialog_height
        )
        
        # Draw dialog background
        bg_surface = pygame.Surface((dialog_width, dialog_height), pygame.SRCALPHA)
        bg_surface.fill((30, 40, 30, 230))  # Dark green with high opacity
        screen.blit(bg_surface, dialog_rect)
        
        # Draw border
        pygame.draw.rect(screen, (150, 150, 150), dialog_rect, 2)
        
        # Draw title
        title_font = pygame.font.Font(None, scale_value(30))
        title_text = f"Build {building_name}?"
        title_surface = title_font.render(title_text, True, (220, 220, 180))
        title_rect = title_surface.get_rect(midtop=(dialog_rect.centerx, dialog_rect.top + 20))
        screen.blit(title_surface, title_rect)
        
        # Draw building description
        desc_font = pygame.font.Font(None, scale_value(20))
        desc_surface = desc_font.render(plot["description"], True, (200, 200, 200))
        desc_rect = desc_surface.get_rect(midtop=(dialog_rect.centerx, title_rect.bottom + 15))
        screen.blit(desc_surface, desc_rect)
        
        # Draw cost information
        cost_y = desc_rect.bottom + 20
        cost_font = pygame.font.Font(None, scale_value(22))
        cost_title = cost_font.render("Cost:", True, (220, 220, 220))
        cost_title_rect = cost_title.get_rect(midtop=(dialog_rect.centerx, cost_y))
        screen.blit(cost_title, cost_title_rect)
        
        # List individual resource costs
        resource_font = pygame.font.Font(None, scale_value(20))
        resource_y = cost_title_rect.bottom + 10
        resource_x = dialog_rect.centerx - scale_value(100)
        
        for resource, amount in building_cost.items():
            # Check if player has enough of this resource
            has_enough = resource_manager.get_resource(resource) >= amount
            resource_color = (100, 200, 100) if has_enough else (200, 100, 100)
            
            resource_text = f"{resource}: {amount}"
            resource_surface = resource_font.render(resource_text, True, resource_color)
            resource_rect = resource_surface.get_rect(topleft=(resource_x, resource_y))
            screen.blit(resource_surface, resource_rect)
            
            resource_y += scale_value(22)
        
        # Draw buttons
        button_y = dialog_rect.bottom - scale_value(60)
        button_width = scale_value(120)
        button_height = scale_value(40)
        
        # Confirm button
        confirm_rect = pygame.Rect(
            dialog_rect.centerx - button_width - scale_value(10),
            button_y,
            button_width,
            button_height
        )
        confirm_color = (80, 150, 80) if has_resources else (80, 80, 80)  # Greyed out if can't afford
        pygame.draw.rect(screen, confirm_color, confirm_rect)
        pygame.draw.rect(screen, (150, 150, 150), confirm_rect, 2)
        
        confirm_text = "Build" if has_resources else "Can't Afford"
        confirm_surface = desc_font.render(confirm_text, True, (220, 220, 220))
        confirm_text_rect = confirm_surface.get_rect(center=confirm_rect.center)
        screen.blit(confirm_surface, confirm_text_rect)
        
        # Cancel button
        cancel_rect = pygame.Rect(
            dialog_rect.centerx + scale_value(10),
            button_y,
            button_width,
            button_height
        )
        pygame.draw.rect(screen, (150, 80, 80), cancel_rect)
        pygame.draw.rect(screen, (150, 150, 150), cancel_rect, 2)
        
        cancel_surface = desc_font.render("Cancel", True, (220, 220, 220))
        cancel_text_rect = cancel_surface.get_rect(center=cancel_rect.center)
        screen.blit(cancel_surface, cancel_text_rect)
        
        # Store button rects for click detection
        self.confirm_button_rect = confirm_rect
        self.cancel_button_rect = cancel_rect
    
    def handle_click(self, position):
        """
        Handle click on village or plots
        
        Args:
            position: Tuple of (x, y) coordinates of click
            
        Returns:
            True if click was handled, False otherwise
        """
        # Handle purchase dialog if active
        if self.show_purchase_dialog:
            return self.handle_purchase_dialog_click(position)
        
        # Check if click is within village area
        if not self.rect.collidepoint(position):
            return False
        
        # First check if any existing building was clicked
        for building in self.buildings:
            if building.handle_click(position):
                return True
        
        # Then check if a plot was clicked
        for plot in self.plots:
            if plot["rect"].collidepoint(position) and not plot["occupied"]:
                # Show purchase dialog for this plot
                self.selected_plot = plot
                self.show_purchase_dialog = True
                return True
        
        return False
    
    def handle_purchase_dialog_click(self, position):
        """
        Handle clicks in the purchase dialog
        
        Args:
            position: Tuple of (x, y) coordinates of click
            
        Returns:
            True if click was handled, False otherwise
        """
        # Check if confirm button was clicked
        if hasattr(self, 'confirm_button_rect') and self.confirm_button_rect.collidepoint(position):
            # Check if player has resources
            resource_manager = self.registry.get("resource_manager")
            building_type = self.selected_plot["building_type"]
            building_cost = VILLAGE_BUILDING_COSTS.get(building_type, {})
            
            if resource_manager.has_resources(building_cost):
                # Spend resources
                resource_manager.spend_resources(building_cost)
                
                # Build the building
                from features.village.building_factory import VillageBuildingFactory
                
                # Create the building at the plot position
                building = VillageBuildingFactory.create_building(
                    building_type, 
                    self.selected_plot["rect"].center,
                    self.registry
                )
                
                # Add building to village
                if self.add_building(building):
                    print(f"Successfully added {building_type} to the village")
                    
                    # Make sure the building has the correct position
                    building.position = self.selected_plot["rect"].center
                    
                    # Ensure the rect is created properly
                    building.rect = pygame.Rect(
                        building.position[0] - building.size[0] // 2,
                        building.position[1] - building.size[1] // 2,
                        building.size[0],
                        building.size[1]
                    )
                    
                    # Mark plot as occupied and store reference to the building
                    self.selected_plot["occupied"] = True
                    self.selected_plot["building"] = building
                else:
                    print(f"Failed to add {building_type} to the village - possibly at capacity")
            
            # Close dialog regardless of whether purchase was successful
            self.show_purchase_dialog = False
            self.selected_plot = None
            return True
            
        # Check if cancel button was clicked
        elif hasattr(self, 'cancel_button_rect') and self.cancel_button_rect.collidepoint(position):
            self.show_purchase_dialog = False
            self.selected_plot = None
            return True
        
        # Click outside buttons but within dialog - keep dialog open
        return True
    
    def add_building(self, building):
        """
        Add a building to the village
        
        Args:
            building: Building instance
            
        Returns:
            True if building was added, False if village is at capacity
        """
        if self.used_capacity >= self.capacity:
            print(f"Cannot add building: capacity limit reached ({self.used_capacity}/{self.capacity})")
            return False
        
        self.buildings.append(building)
        self.used_capacity += 1
        print(f"Building added to village. Capacity: {self.used_capacity}/{self.capacity}")
        return True
    
    def remove_building(self, building):
        """
        Remove a building from the village
        
        Args:
            building: Building instance
            
        Returns:
            True if building was removed, False if not found
        """
        if building in self.buildings:
            self.buildings.remove(building)
            self.used_capacity -= 1
            return True
        return False
    
    def increase_capacity(self, amount=1):
        """
        Increase village capacity
        
        Args:
            amount: Amount to increase by
        """
        self.capacity += amount
    
    def increase_development_level(self):
        """
        Increase village development level
        """
        self.development_level += 1
    
    def add_talent_points(self, amount=1):
        """
        Add talent points
        
        Args:
            amount: Amount to add
        """
        self.talent_points += amount
    
    def spend_talent_points(self, amount=1):
        """
        Spend talent points
        
        Args:
            amount: Amount to spend
            
        Returns:
            True if points were spent, False if insufficient
        """
        if self.talent_points >= amount:
            self.talent_points -= amount
            return True
        return False