# coresmith_state.py
"""
Coresmith crafting interface state for Castle Defense
"""
import pygame
from .game_state import GameState
from registry import RESOURCE_MANAGER, ICON_MANAGER
from config import ITEM_COSTS

class CoresmithState(GameState):
    """
    Coresmith state for crafting items using resources
    """
    def __init__(self, game):
        """
        Initialize coresmith state
        
        Args:
            game: Game instance
        """
        super().__init__(game)
        
        # Store references to commonly used components
        self.resource_manager = self.game.registry.get(RESOURCE_MANAGER)
        self.icon_manager = self.game.registry.get(ICON_MANAGER)
        
        # Track which tab is active
        self.active_tab = "Equipment"
        self.tabs = ["Equipment", "Special", "Future"] # Future can be used for expansion
        
        # Button to close the coresmith view
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
        
        # Item display settings
        self.grid_start_y = self.tab_y + self.tab_height + game.scale_value(20)
        self.grid_start_x = self.tab_start_x
        self.grid_cell_width = game.scale_value(180)
        self.grid_cell_height = game.scale_value(120)
        self.grid_margin = game.scale_value(15)
        self.grid_cols = 4
        
        # Item category mappings
        self.item_categories = {
            "Equipment": ["Unstoppable Force", "Serene Spirit", "Multitudation Vortex"],
            "Special": [],
            "Future": []
        }
        
        # Info panel settings (right side of screen)
        self.info_panel_width = game.scale_value(400)
        self.info_panel_height = game.WINDOW_HEIGHT - self.grid_start_y - game.scale_value(40)
        self.info_panel_x = game.WINDOW_WIDTH - self.info_panel_width - game.scale_value(50)
        self.info_panel_y = self.grid_start_y
        
        # Craft button settings
        self.craft_button_width = game.scale_value(150)
        self.craft_button_height = game.scale_value(50)
        self.craft_button_x = self.info_panel_x + (self.info_panel_width - self.craft_button_width) // 2
        self.craft_button_y = self.info_panel_y + self.info_panel_height - self.craft_button_height - game.scale_value(20)
        self.craft_button_rect = pygame.Rect(
            self.craft_button_x, 
            self.craft_button_y, 
            self.craft_button_width, 
            self.craft_button_height
        )
        self.craft_button_color = (80, 120, 160)
        self.craft_button_disabled_color = (80, 80, 100)
        self.craft_button_hover_color = (100, 140, 180)
        self.craft_button_is_hovered = False
        
        # Track selected item
        self.selected_item = None
        
        # Crafting status
        self.crafting = False
        self.crafting_timer = 0
        self.crafting_time = 3.0  # 3 seconds to craft an item
        self.crafting_item = None
    
    def handle_events(self, events):
        """
        Handle input events for coresmith state
        
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
                
                # Track craft button hover
                if self.selected_item and not self.crafting:
                    self.craft_button_is_hovered = self.craft_button_rect.collidepoint(mouse_pos)
                else:
                    self.craft_button_is_hovered = False
                
                # Reset selected item on hover for grid items
                grid_hover = False
                items = self.get_filtered_items()
                for i, item in enumerate(items):
                    row = i // self.grid_cols
                    col = i % self.grid_cols
                    cell_rect = pygame.Rect(
                        self.grid_start_x + col * (self.grid_cell_width + self.grid_margin),
                        self.grid_start_y + row * (self.grid_cell_height + self.grid_margin),
                        self.grid_cell_width,
                        self.grid_cell_height
                    )
                    if cell_rect.collidepoint(mouse_pos):
                        grid_hover = True
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
                        self.selected_item = None  # Reset selected item when changing tabs
                        return True
                
                # Check if an item in the grid was clicked
                items = self.get_filtered_items()
                for i, item in enumerate(items):
                    row = i // self.grid_cols
                    col = i % self.grid_cols
                    cell_rect = pygame.Rect(
                        self.grid_start_x + col * (self.grid_cell_width + self.grid_margin),
                        self.grid_start_y + row * (self.grid_cell_height + self.grid_margin),
                        self.grid_cell_width,
                        self.grid_cell_height
                    )
                    if cell_rect.collidepoint(mouse_pos):
                        self.selected_item = item
                        return True
                
                # Check if craft button was clicked
                if (self.selected_item and not self.crafting and 
                        self.craft_button_rect.collidepoint(mouse_pos)):
                    if self.start_crafting(self.selected_item):
                        return True
                
                # If clicked elsewhere, deselect current item
                self.selected_item = None
                
            # Escape key to exit coresmith view
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.game.state_manager.change_state("village")
                return True
        
        return False
    
    def update(self, dt):
        """
        Update coresmith state
        
        Args:
            dt: Time delta in seconds
        """
        # Update crafting progress if crafting
        if self.crafting:
            self.crafting_timer += dt
            if self.crafting_timer >= self.crafting_time:
                self.complete_crafting()
    
    def get_filtered_items(self):
        """
        Get items filtered by active tab
        
        Returns:
            List of item names matching current filters
        """
        # Get items for the active tab
        items = self.item_categories.get(self.active_tab, [])
        return items
    
    def start_crafting(self, item_name):
        """
        Start crafting an item
        
        Args:
            item_name: Name of the item to craft
            
        Returns:
            True if crafting started, False otherwise
        """
        if self.crafting or not self.resource_manager:
            return False
        
        # Check if item is valid and has a cost defined
        if item_name not in ITEM_COSTS:
            return False
        
        # Check if player has required resources
        if not self.resource_manager.has_resources(ITEM_COSTS[item_name]):
            return False
        
        # Spend resources
        if self.resource_manager.spend_resources(ITEM_COSTS[item_name]):
            self.crafting = True
            self.crafting_timer = 0
            self.crafting_item = item_name
            return True
        
        return False
    
    def complete_crafting(self):
        """
        Complete crafting and add item to inventory
        """
        if self.crafting_item and self.resource_manager:
            # Add crafted item to inventory
            self.resource_manager.add_resource(self.crafting_item, 1)
            
            # Reset crafting state
            self.crafting = False
            self.crafting_item = None
            self.crafting_timer = 0
    
    def draw(self, screen):
        """
        Draw coresmith state to screen
        
        Args:
            screen: Pygame surface to draw on
        """
        # Draw a semi-transparent overlay
        overlay = pygame.Surface((self.game.WINDOW_WIDTH, self.game.WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))  # Black with 80% opacity
        screen.blit(overlay, (0, 0))
        
        # Draw coresmith title
        font_large = pygame.font.Font(None, self.game.scale_value(48))
        title_text = font_large.render("Coresmith Workshop", True, (255, 255, 255))
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
        
        # Draw item grid
        items = self.get_filtered_items()
        
        if not items:
            # Draw a message if no items in this category
            font_empty = pygame.font.Font(None, self.game.scale_value(32))
            empty_text = font_empty.render("No items available in this category", True, (180, 180, 180))
            empty_rect = empty_text.get_rect(center=(
                self.grid_start_x + self.grid_cols * (self.grid_cell_width + self.grid_margin) // 2,
                self.grid_start_y + self.game.scale_value(100)
            ))
            screen.blit(empty_text, empty_rect)
        else:
            # Draw the item grid
            for i, item in enumerate(items):
                row = i // self.grid_cols
                col = i % self.grid_cols
                
                # Calculate cell position
                cell_rect = pygame.Rect(
                    self.grid_start_x + col * (self.grid_cell_width + self.grid_margin),
                    self.grid_start_y + row * (self.grid_cell_height + self.grid_margin),
                    self.grid_cell_width,
                    self.grid_cell_height
                )
                
                # Determine cell color - highlight if selected
                if item == self.selected_item:
                    cell_color = (100, 120, 150)
                    border_color = (150, 170, 200)
                else:
                    cell_color = (70, 90, 110)
                    border_color = (120, 140, 170)
                
                # Draw cell background
                pygame.draw.rect(screen, cell_color, cell_rect)
                pygame.draw.rect(screen, border_color, cell_rect, 2)  # Border
                
                # Draw item icon
                if self.icon_manager and hasattr(self.icon_manager, 'get_icon'):
                    try:
                        # Convert item name to icon ID
                        icon_id = self.icon_manager.get_resource_icon_id(item)
                        # Get the icon at a larger size
                        icon = self.icon_manager.get_icon(icon_id, (48, 48))
                        if icon:
                            # Determine icon position (centered in upper part of cell)
                            icon_rect = icon.get_rect(midtop=(cell_rect.centerx, cell_rect.top + self.game.scale_value(10)))
                            screen.blit(icon, icon_rect)
                    except Exception as e:
                        # If icon retrieval fails, print error but continue
                        print(f"Error getting icon for {item}: {e}")
                
                # Draw item name
                font_name = pygame.font.Font(None, self.game.scale_value(22))
                name_text = font_name.render(item, True, (255, 255, 255))
                name_rect = name_text.get_rect(midtop=(cell_rect.centerx, cell_rect.centery - self.game.scale_value(10)))
                screen.blit(name_text, name_rect)
                
                # Draw item cost
                if item in ITEM_COSTS:
                    cost_text = ""
                    for resource, amount in ITEM_COSTS[item].items():
                        cost_text += f"{amount} {resource}, "
                    cost_text = cost_text.rstrip(", ")
                    
                    # Check if player can afford this item
                    can_afford = self.resource_manager and self.resource_manager.has_resources(ITEM_COSTS[item])
                    cost_color = (100, 200, 100) if can_afford else (200, 100, 100)
                    
                    font_cost = pygame.font.Font(None, self.game.scale_value(18))
                    cost_surface = font_cost.render(cost_text, True, cost_color)
                    cost_rect = cost_surface.get_rect(midbottom=(cell_rect.centerx, cell_rect.bottom - self.game.scale_value(10)))
                    screen.blit(cost_surface, cost_rect)
        
        # Draw item info panel if an item is selected
        if self.selected_item:
            self.draw_item_info_panel(screen)
        
        # Draw crafting progress if currently crafting
        if self.crafting:
            self.draw_crafting_progress(screen)
    
    def draw_item_info_panel(self, screen):
        """
        Draw detailed information about the selected item
        
        Args:
            screen: Pygame surface to draw on
        """
        # Draw panel background
        panel_rect = pygame.Rect(
            self.info_panel_x,
            self.info_panel_y,
            self.info_panel_width,
            self.info_panel_height
        )
        pygame.draw.rect(screen, (40, 50, 70), panel_rect)
        pygame.draw.rect(screen, (80, 100, 130), panel_rect, 2)  # Border
        
        # Draw item name as title
        font_title = pygame.font.Font(None, self.game.scale_value(32))
        title_text = font_title.render(self.selected_item, True, (220, 220, 220))
        title_rect = title_text.get_rect(midtop=(panel_rect.centerx, panel_rect.top + self.game.scale_value(20)))
        screen.blit(title_text, title_rect)
        
        # Draw item icon (larger)
        if self.icon_manager and hasattr(self.icon_manager, 'get_icon'):
            try:
                # Convert item name to icon ID
                icon_id = self.icon_manager.get_resource_icon_id(self.selected_item)
                # Get a larger icon for the info panel
                icon = self.icon_manager.get_icon(icon_id, (64, 64))
                if icon:
                    # Position below the title
                    icon_rect = icon.get_rect(midtop=(panel_rect.centerx, title_rect.bottom + self.game.scale_value(15)))
                    screen.blit(icon, icon_rect)
                    
                    # Adjust y_pos for subsequent content
                    y_pos = icon_rect.bottom + self.game.scale_value(20)
                else:
                    # If no icon, just use a default y_pos
                    y_pos = title_rect.bottom + self.game.scale_value(60)
            except:
                # Fall back if icon retrieval fails
                y_pos = title_rect.bottom + self.game.scale_value(60)
        else:
            y_pos = title_rect.bottom + self.game.scale_value(60)
        
        # Draw item description
        font_desc = pygame.font.Font(None, self.game.scale_value(24))
        
        # Get item description based on item type
        if self.selected_item == "Unstoppable Force":
            description = "Increases tower AoE radius by 30%. For single-target towers, adds splash damage."
        elif self.selected_item == "Serene Spirit":
            description = "Converts 5% of tower damage into healing for the castle walls."
        else:
            description = "A crafted item with special properties."
        
        # Wrap text for the description
        desc_lines = self.wrap_text(description, font_desc, panel_rect.width - self.game.scale_value(40))
        for line in desc_lines:
            line_surface = font_desc.render(line, True, (200, 200, 200))
            line_rect = line_surface.get_rect(midtop=(panel_rect.centerx, y_pos))
            screen.blit(line_surface, line_rect)
            y_pos += line_rect.height + self.game.scale_value(5)
        
        # Add some spacing
        y_pos += self.game.scale_value(20)
        
        # Draw required resources title
        req_title = font_desc.render("Required Resources:", True, (180, 180, 220))
        req_title_rect = req_title.get_rect(midtop=(panel_rect.centerx, y_pos))
        screen.blit(req_title, req_title_rect)
        y_pos += req_title_rect.height + self.game.scale_value(10)
        
        # Draw required resources
        font_req = pygame.font.Font(None, self.game.scale_value(22))
        
        if self.selected_item in ITEM_COSTS:
            resources_shown = False
            for resource, amount in ITEM_COSTS[self.selected_item].items():
                # Check if player has enough of this resource
                has_enough = self.resource_manager.get_resource(resource) >= amount
                resource_color = (100, 200, 100) if has_enough else (200, 100, 100)
                
                # Draw resource icon if available
                resource_x = panel_rect.left + self.game.scale_value(50)
                resource_y = y_pos
                
                if self.icon_manager and hasattr(self.icon_manager, 'get_icon'):
                    try:
                        # Get resource icon
                        icon_id = self.icon_manager.get_resource_icon_id(resource)
                        icon = self.icon_manager.get_icon(icon_id, (24, 24))
                        if icon:
                            # Position icon
                            icon_rect = icon.get_rect(midleft=(resource_x, resource_y + self.game.scale_value(10)))
                            screen.blit(icon, icon_rect)
                            resource_x = icon_rect.right + self.game.scale_value(10)
                    except:
                        pass
                
                # Draw resource text
                resource_text = f"{resource}: {amount}"
                resource_surface = font_req.render(resource_text, True, resource_color)
                resource_rect = resource_surface.get_rect(midleft=(resource_x, resource_y + self.game.scale_value(10)))
                screen.blit(resource_surface, resource_rect)
                
                # Add player's current amount
                current_amount = self.resource_manager.get_resource(resource)
                current_text = f"(Have: {current_amount})"
                current_surface = font_req.render(current_text, True, resource_color)
                current_rect = current_surface.get_rect(midleft=(resource_rect.right + self.game.scale_value(10), resource_y + self.game.scale_value(10)))
                screen.blit(current_surface, current_rect)
                
                y_pos += self.game.scale_value(30)
                resources_shown = True
                
            if not resources_shown:
                no_req_text = font_req.render("No resources required", True, (150, 150, 150))
                no_req_rect = no_req_text.get_rect(midtop=(panel_rect.centerx, y_pos))
                screen.blit(no_req_text, no_req_rect)
                y_pos += no_req_rect.height + self.game.scale_value(30)
        else:
            no_cost_text = font_req.render("No cost information available", True, (150, 150, 150))
            no_cost_rect = no_cost_text.get_rect(midtop=(panel_rect.centerx, y_pos))
            screen.blit(no_cost_text, no_cost_rect)
            y_pos += no_cost_rect.height + self.game.scale_value(30)
        
        # Draw craft button if not already crafting
        if not self.crafting:
            # Check if player can afford crafting
            can_afford = (self.selected_item in ITEM_COSTS and 
                         self.resource_manager.has_resources(ITEM_COSTS[self.selected_item]))
            
            # Set button color based on affordability and hover state
            if can_afford:
                if self.craft_button_is_hovered:
                    button_color = self.craft_button_hover_color
                else:
                    button_color = self.craft_button_color
            else:
                button_color = self.craft_button_disabled_color
            
            # Draw the button
            pygame.draw.rect(screen, button_color, self.craft_button_rect)
            pygame.draw.rect(screen, (150, 170, 200), self.craft_button_rect, 2)  # Border
            
            # Draw button text
            button_text = "Craft Item" if can_afford else "Cannot Craft"
            button_surface = font_desc.render(button_text, True, (220, 220, 220))
            button_text_rect = button_surface.get_rect(center=self.craft_button_rect.center)
            screen.blit(button_surface, button_text_rect)
    
    def draw_crafting_progress(self, screen):
        """
        Draw crafting progress bar and information
        
        Args:
            screen: Pygame surface to draw on
        """
        # Calculate progress percentage
        progress = self.crafting_timer / self.crafting_time
        
        # Draw progress bar background
        bar_width = self.game.WINDOW_WIDTH // 3
        bar_height = self.game.scale_value(30)
        bar_x = (self.game.WINDOW_WIDTH - bar_width) // 2
        bar_y = self.game.WINDOW_HEIGHT - bar_height - self.game.scale_value(50)
        
        bar_bg_rect = pygame.Rect(bar_x, bar_y, bar_width, bar_height)
        pygame.draw.rect(screen, (50, 50, 60), bar_bg_rect)
        
        # Draw progress fill
        fill_width = int(bar_width * progress)
        fill_rect = pygame.Rect(bar_x, bar_y, fill_width, bar_height)
        pygame.draw.rect(screen, (80, 150, 200), fill_rect)
        
        # Draw border
        pygame.draw.rect(screen, (120, 180, 220), bar_bg_rect, 2)
        
        # Draw crafting text
        font = pygame.font.Font(None, self.game.scale_value(28))
        progress_text = f"Crafting {self.crafting_item}... {int(progress * 100)}%"
        text_surface = font.render(progress_text, True, (220, 220, 220))
        text_rect = text_surface.get_rect(midbottom=(self.game.WINDOW_WIDTH // 2, bar_y - self.game.scale_value(10)))
        screen.blit(text_surface, text_rect)
    
    def wrap_text(self, text, font, max_width):
        """
        Wrap text to fit within a specified width
        
        Args:
            text: Text to wrap
            font: Font to use for measuring text
            max_width: Maximum width in pixels
            
        Returns:
            List of lines
        """
        words = text.split(' ')
        lines = []
        line = []
        
        for word in words:
            test_line = ' '.join(line + [word])
            test_width = font.size(test_line)[0]
            
            if test_width <= max_width:
                line.append(word)
            else:
                lines.append(' '.join(line))
                line = [word]
        
        if line:
            lines.append(' '.join(line))
        
        return lines
