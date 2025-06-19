# ui/building_menu.py
"""
Building menu implementation for Castle Defense
"""
import pygame
from .base_menu import Menu
from .elements import Button
from ui.utils import ResourceFormatter
from features.buildings import Coresmith
# Mine is now only in village features
from features.village.production_buildings import Mine
from config import ITEM_COSTS, ITEM_EFFECTS, MINE_PRODUCTION_INTERVAL
from registry import ICON_MANAGER

class BuildingMenu(Menu):
    """Menu for interacting with buildings"""
    def __init__(self, screen, registry=None):
        """
        Initialize building menu
        
        Args:
            screen: Pygame surface to draw on
            registry: Optional ComponentRegistry for accessing game components
        """
        super().__init__(screen)
        self.building = None
        self.building_type = None
        self.resource_manager = None
        self.registry = registry
        
        # Tab system for different building types
        self.tabs = {
            "mine": ["Info", "Upgrade"],
            "coresmith": ["Crafting", "Items"]
        }
        self.current_tab = "Info"  # Default tab
        
        # Content tracking
        self.craft_buttons = []
        
        # Resource icon size
        self.resource_icon_size = (16, 16)
    
    def set_building(self, building, building_type, resource_manager):
        """
        Set the building this menu controls
        
        Args:
            building: Building instance
            building_type: String type of building ("mine" or "coresmith")
            resource_manager: ResourceManager instance for resource costs
        """
        self.building = building
        self.building_type = building_type
        self.resource_manager = resource_manager
        self.title = f"{building_type.capitalize()}"
        
        # Reset tab selection based on building type
        self.current_tab = self.tabs[building_type][0]
        
        # Reset scrolling
        self.scroll_offset = 0
        
        # Clear existing buttons
        self.buttons = []
        self.craft_buttons = []
        
        # Create tab buttons based on building type
        self.create_tab_buttons()
        
        # Create content buttons based on building type and tab
        self.create_content_buttons()
    
    def create_tab_buttons(self):
        """Create tab selection buttons for the current building type"""
        if self.building_type not in self.tabs:
            return
            
        current_tabs = self.tabs[self.building_type]
        tab_width = self.rect.width / len(current_tabs)
        
        for i, tab in enumerate(current_tabs):
            tab_button = Button(
                (self.rect.left + i * tab_width, self.rect.top + 30),
                (tab_width, 30),
                tab,
                lambda t=tab: self.change_tab(t)
            )
            self.buttons.append(tab_button)
    
    def change_tab(self, tab):
        """
        Change the current tab
        
        Args:
            tab: Tab name to switch to
        """
        if tab in self.tabs.get(self.building_type, []):
            self.current_tab = tab
            self.scroll_offset = 0  # Reset scroll position
            
            # Update buttons for the new tab
            self.create_content_buttons()
    
    def create_content_buttons(self):
        """Create buttons specific to the current tab content"""
        # Remove old content buttons
        self.buttons = self.buttons[:len(self.tabs.get(self.building_type, []))]
        self.craft_buttons = []
        
        if self.building_type == "mine":
            if self.current_tab == "Upgrade":
                # Mine upgrade button
                upgrade_button = Button(
                    (self.rect.left + 20, self.rect.top + 80),
                    (self.rect.width - 40, 30),
                    "Upgrade Mine",
                    self.upgrade_mine
                )
                
                # Set button disabled state based on resources
                has_resources = self.resource_manager.has_resources(self.building.get_upgrade_cost())
                upgrade_button.set_disabled(not has_resources or self.building.upgrading)
                
                self.buttons.append(upgrade_button)
                
        elif self.building_type == "coresmith":
            if self.current_tab == "Crafting":
                # Item crafting buttons
                y_pos = self.rect.top + 80
                
                for i, item_name in enumerate(ITEM_COSTS.keys()):
                    # Check if player has resources for this item
                    has_resources = self.resource_manager.has_resources(ITEM_COSTS[item_name])
                    is_crafting = self.building.crafting and self.building.current_item == item_name
                    
                    craft_button = Button(
                        (self.rect.left + 20, y_pos),
                        (self.rect.width - 40, 30),
                        f"Craft {item_name}",
                        lambda item=item_name: self.craft_item(item)
                    )
                    
                    # Add item information for tooltip
                    craft_button.item_name = item_name
                    craft_button.item_costs = ITEM_COSTS[item_name]
                    craft_button.item_effect = ITEM_EFFECTS.get(item_name, {}).get("description", "No effect")
                    
                    # Disable button if already crafting or not enough resources
                    craft_button.set_disabled(not has_resources or self.building.crafting)
                    
                    self.buttons.append(craft_button)
                    self.craft_buttons.append(craft_button)
                    
                    y_pos += 80  # Space for button and item card
    
    def upgrade_mine(self):
        """Upgrade the mine"""
        if isinstance(self.building, Mine) and self.resource_manager:
            if self.building.start_upgrade(self.resource_manager):
                # Update buttons after successful upgrade start
                self.create_content_buttons()
    
    def craft_item(self, item_name):
        """
        Start crafting an item
        
        Args:
            item_name: Name of item to craft
        """
        if isinstance(self.building, Coresmith) and self.resource_manager:
            if self.building.start_crafting(item_name, self.resource_manager):
                # Update buttons after successful crafting start
                self.create_content_buttons()
    
    def update_button_states(self):
        """Update button disabled states based on current resources"""
        if not self.building or not self.resource_manager:
            return
            
        if self.building_type == "mine" and self.current_tab == "Upgrade":
            # Find upgrade button
            for button in self.buttons:
                if button.text == "Upgrade Mine":
                    has_resources = self.resource_manager.has_resources(self.building.get_upgrade_cost())
                    button.set_disabled(not has_resources or self.building.upgrading)
                    break
            
        elif self.building_type == "coresmith" and self.current_tab == "Crafting":
            # Update coresmith crafting buttons
            for button in self.craft_buttons:
                item_name = button.item_name
                has_resources = self.resource_manager.has_resources(ITEM_COSTS[item_name])
                button.set_disabled(not has_resources or self.building.crafting)
    
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
            
        # First check for tooltip updates on mouseover
        if event.type == pygame.MOUSEMOTION:
            self.show_tooltip = False
            
            # Check for tooltips on craft buttons
            for button in self.craft_buttons:
                if button.rect.collidepoint(event.pos):
                    formatted_cost = ResourceFormatter.format_cost(button.item_costs)
                    tooltip_text = f"{button.item_name}\nCost: {formatted_cost}\nEffect: {button.item_effect}"
                    self.tooltip_text = tooltip_text
                    self.tooltip_position = (event.pos[0] + 15, event.pos[1] + 15)
                    self.show_tooltip = True
        
        # Then handle other events
        return super().handle_event(event)
    
    def draw(self):
        """Draw building menu with building-specific info"""
        if not self.active or not self.building:
            return
        
        # Draw base menu (background and title)
        super().draw()
        
        # Update button states based on current resources
        self.update_button_states()
        
        # Draw tabs if we have a building type
        if self.building_type in self.tabs:
            self.draw_tab_buttons(self.tabs[self.building_type], self.current_tab)
        
        # Create content area below tabs
        content_rect = pygame.Rect(
            self.rect.left, 
            self.rect.top + 60,  # Below tabs
            self.rect.width,
            self.rect.height - 60
        )
        
        # Draw tab-specific content
        if self.building_type == "mine":
            if self.current_tab == "Info":
                self.draw_mine_info(content_rect)
            elif self.current_tab == "Upgrade":
                self.draw_mine_upgrade(content_rect)
                
        elif self.building_type == "coresmith":
            if self.current_tab == "Crafting":
                self.draw_coresmith_crafting(content_rect)
            elif self.current_tab == "Items":
                self.draw_coresmith_items(content_rect)
                
        # Draw buttons
        for button in self.buttons:
            # Only draw if in viewport
            if hasattr(button, "rect"):
                if (button.rect.top >= self.rect.top + 30 and 
                    button.rect.bottom <= self.rect.bottom - 10):
                    button.draw(self.screen)
    
    def draw_mine_info(self, content_rect):
        """
        Draw mine information tab
        
        Args:
            content_rect: Rectangle defining content area
        """
        mine = self.building
        y_pos = content_rect.top + 20 - self.scroll_offset
        
        # Draw mine stats card
        stats_rect = pygame.Rect(
            content_rect.left + 15,
            y_pos,
            content_rect.width - 30,
            100
        )
        
        # Draw card background
        self.draw_card(
            stats_rect,
            "Mine Statistics",
            [
                f"Level: {mine.level}",
                f"Resource: {mine.resource_type}",
                f"Production Rate: {mine.production_rate:.1f}/cycle",
                f"Cycle Time: {MINE_PRODUCTION_INTERVAL:.1f} seconds"
            ]
        )
        
        y_pos += 120
        
        # Draw production timer if not upgrading
        if not mine.upgrading:
            # Calculate production progress
            production_progress = mine.production_timer / MINE_PRODUCTION_INTERVAL
            progress_width = int((content_rect.width - 40) * production_progress)
            
            # Draw progress header
            progress_text = f"Production: {mine.production_timer:.1f}/{MINE_PRODUCTION_INTERVAL:.1f}s"
            progress_surface = self.small_font.render(progress_text, True, self.TEXT_COLOR)
            self.screen.blit(progress_surface, (content_rect.left + 20, y_pos))
            
            # Draw progress bar background
            progress_bg_rect = pygame.Rect(
                content_rect.left + 20,
                y_pos + 25,
                content_rect.width - 40,
                15
            )
            pygame.draw.rect(self.screen, (80, 80, 80), progress_bg_rect)
            
            # Draw progress bar fill
            if progress_width > 0:
                progress_fill_rect = pygame.Rect(
                    content_rect.left + 20,
                    y_pos + 25,
                    progress_width,
                    15
                )
                pygame.draw.rect(self.screen, (100, 200, 100), progress_fill_rect)
            
            # Draw border
            pygame.draw.rect(self.screen, (150, 150, 150), progress_bg_rect, 1)
        else:
            # Draw upgrade progress instead
            self.draw_upgrade_progress(content_rect, y_pos)
        
        # Update max scroll (no scrolling needed for this tab)
        self.max_scroll = 0
    
    def draw_upgrade_progress(self, content_rect, y_pos):
        """
        Draw upgrade progress information
        
        Args:
            content_rect: Rectangle defining content area
            y_pos: Y position to start drawing
        """
        mine = self.building
        
        # Draw upgrade header
        upgrade_text = f"Upgrading to Level {mine.level + 1}"
        upgrade_surface = self.small_font.render(upgrade_text, True, (100, 200, 255))
        self.screen.blit(upgrade_surface, (content_rect.left + 20, y_pos))
        
        y_pos += 25
        
        # Calculate upgrade progress
        upgrade_progress = mine.upgrade_timer / mine.upgrade_time
        progress_width = int((content_rect.width - 40) * upgrade_progress)
        
        # Draw time text
        time_text = f"Time Remaining: {int(mine.upgrade_time - mine.upgrade_timer)}s"
        time_surface = self.small_font.render(time_text, True, self.TEXT_COLOR)
        self.screen.blit(time_surface, (content_rect.left + 20, y_pos))
        
        y_pos += 20
        
        # Draw progress bar background
        progress_bg_rect = pygame.Rect(
            content_rect.left + 20,
            y_pos,
            content_rect.width - 40,
            15
        )
        pygame.draw.rect(self.screen, (80, 80, 80), progress_bg_rect)
        
        # Draw progress bar fill
        if progress_width > 0:
            progress_fill_rect = pygame.Rect(
                content_rect.left + 20,
                y_pos,
                progress_width,
                15
            )
            pygame.draw.rect(self.screen, (100, 150, 255), progress_fill_rect)
        
        # Draw border
        pygame.draw.rect(self.screen, (150, 150, 150), progress_bg_rect, 1)
    
    def draw_mine_upgrade(self, content_rect):
        """
        Draw mine upgrade tab
        
        Args:
            content_rect: Rectangle defining content area
        """
        mine = self.building
        y_pos = content_rect.top + 20 - self.scroll_offset
        
        # Draw current level info
        level_text = f"Current Level: {mine.level}"
        level_surface = self.small_font.render(level_text, True, self.TEXT_COLOR)
        self.screen.blit(level_surface, (content_rect.left + 20, y_pos))
        
        y_pos += 25
        
        # Draw production rate
        rate_text = f"Production Rate: {mine.production_rate:.1f} {mine.resource_type}/cycle"
        rate_surface = self.small_font.render(rate_text, True, self.TEXT_COLOR)
        self.screen.blit(rate_surface, (content_rect.left + 20, y_pos))
        
        y_pos += 40
        
        # Draw upgrade info card
        if not mine.upgrading:
            # Draw upgrade info
            upgrade_rect = pygame.Rect(
                content_rect.left + 15,
                y_pos,
                content_rect.width - 30,
                120
            )
            
            # Calculate next level benefits
            next_production = mine.production_rate * mine.production_multiplier
            
            # Check if player has enough resources
            upgrade_cost = mine.get_upgrade_cost()
            has_resources = self.resource_manager.has_resources(upgrade_cost)
            border_color = self.POSITIVE_COLOR if has_resources else self.NEGATIVE_COLOR
            
            # Draw card
            self.draw_card(
                upgrade_rect,
                f"Upgrade to Level {mine.level + 1}",
                [
                    f"New Production Rate: {next_production:.1f} {mine.resource_type}/cycle",
                    f"Upgrade Time: {mine.upgrade_time:.0f} seconds"
                ],
                border_color
            )
            
            # Get icon manager if available
            icon_manager = None
            if self.registry and self.registry.has(ICON_MANAGER):
                icon_manager = self.registry.get(ICON_MANAGER)
            
            # Draw resource costs with icons
            cost_y = upgrade_rect.top + 70
            sorted_resources = ResourceFormatter.sort_resources(upgrade_cost)
            
            for resource_type, amount in sorted_resources:
                has_resource = self.resource_manager.get_resource(resource_type) >= amount
                
                # Create resource display with icon
                surface, width, height = ResourceFormatter.render_resource_with_icon(
                    self.small_font,
                    resource_type,
                    amount,
                    self.registry,
                    self.resource_icon_size,
                    has_resource
                )
                
                # Position the resource display
                pos_x = upgrade_rect.left + 20
                pos_y = cost_y
                
                # Draw the resource
                self.screen.blit(surface, (pos_x, pos_y))
                
                # Increment position for next resource
                cost_y += height + 5
            
            # Position upgrade button
            for button in self.buttons:
                if button.text == "Upgrade Mine":
                    button.rect.topleft = (content_rect.left + 60, y_pos + 130)
                    button.position = button.rect.topleft
        else:
            # Draw upgrade progress
            self.draw_upgrade_progress(content_rect, y_pos)
        
        # Update max scroll (no scrolling needed for this tab)
        self.max_scroll = 0
    
    def draw_coresmith_crafting(self, content_rect):
        """
        Draw coresmith crafting tab
        
        Args:
            content_rect: Rectangle defining content area
        """
        coresmith = self.building
        y_pos = content_rect.top + 20 - self.scroll_offset
        
        # Draw current crafting status if active
        if coresmith.crafting:
            # Draw crafting status card
            crafting_rect = pygame.Rect(
                content_rect.left + 15,
                y_pos,
                content_rect.width - 30,
                100
            )
            
            # Calculate crafting progress
            crafting_progress = coresmith.crafting_timer / coresmith.crafting_time
            progress_width = int((crafting_rect.width - 20) * crafting_progress)
            
            # Draw card
            pygame.draw.rect(self.screen, self.CARD_BG_COLOR, crafting_rect)
            pygame.draw.rect(self.screen, (100, 100, 100), crafting_rect, 1)
            
            # Draw title
            craft_title = self.small_font.render(f"Crafting: {coresmith.current_item}", True, self.TEXT_COLOR)
            self.screen.blit(craft_title, (crafting_rect.left + 10, y_pos + 10))
            
            # Draw time text
            time_text = f"Time Remaining: {int(coresmith.crafting_time - coresmith.crafting_timer)}s"
            time_surface = self.small_font.render(time_text, True, self.TEXT_COLOR)
            self.screen.blit(time_surface, (crafting_rect.left + 10, y_pos + 35))
            
            # Draw progress bar background
            progress_bg_rect = pygame.Rect(
                crafting_rect.left + 10,
                y_pos + 60,
                crafting_rect.width - 20,
                15
            )
            pygame.draw.rect(self.screen, (80, 80, 80), progress_bg_rect)
            
            # Draw progress bar fill
            if progress_width > 0:
                progress_fill_rect = pygame.Rect(
                    crafting_rect.left + 10,
                    y_pos + 60,
                    progress_width,
                    15
                )
                pygame.draw.rect(self.screen, (100, 150, 255), progress_fill_rect)
            
            # Draw border
            pygame.draw.rect(self.screen, (150, 150, 150), progress_bg_rect, 1)
            
            y_pos += 120
        else:
            # Draw instructions
            instructions = "Select an item to craft:"
            instr_surface = self.small_font.render(instructions, True, self.TEXT_COLOR)
            self.screen.blit(instr_surface, (content_rect.left + 20, y_pos))
            
            y_pos += 40
        
        # Get icon manager if available
        icon_manager = None
        if self.registry and self.registry.has(ICON_MANAGER):
            icon_manager = self.registry.get(ICON_MANAGER)
        
        # Draw available items to craft
        for i, item_name in enumerate(ITEM_COSTS.keys()):
            # Create item card
            item_rect = pygame.Rect(
                content_rect.left + 15,
                y_pos,
                content_rect.width - 30,
                90
            )
            
            # Check if player has resources
            has_resources = self.resource_manager.has_resources(ITEM_COSTS[item_name])
            border_color = self.POSITIVE_COLOR if has_resources else self.NEGATIVE_COLOR
            
            # Draw card
            pygame.draw.rect(self.screen, self.CARD_BG_COLOR, item_rect)
            pygame.draw.rect(self.screen, border_color, item_rect, 1)
            
            # Draw item name with icon
            item_color = ResourceFormatter.get_resource_color(item_name)
            bright_color = tuple(min(255, c + 40) for c in item_color)
            
            # Draw item icon if available
            if icon_manager:
                icon_id = icon_manager.get_resource_icon_id(item_name)
                icon = icon_manager.get_icon(icon_id, (24, 24))
                icon_rect = icon.get_rect(topleft=(item_rect.left + 10, y_pos + 10))
                self.screen.blit(icon, icon_rect)
                name_left = icon_rect.right + 10
            else:
                name_left = item_rect.left + 10
            
            # Draw item name
            item_title = self.small_font.render(item_name, True, bright_color)
            self.screen.blit(item_title, (name_left, y_pos + 15))
            
            # Draw item effect
            effect_desc = ITEM_EFFECTS.get(item_name, {}).get("description", "No effect")
            effect_surface = self.small_font.render(effect_desc, True, self.SUBTEXT_COLOR)
            self.screen.blit(effect_surface, (item_rect.left + 20, y_pos + 40))
            
            # Draw cost with consistent formatting
            costs = ITEM_COSTS[item_name]
            cost_y = y_pos + 60
            
            # Draw resources with icons and colors
            for resource_type, amount in ResourceFormatter.sort_resources(costs):
                has_resource = self.resource_manager.get_resource(resource_type) >= amount
                
                # Create resource display with icon
                surface, width, height = ResourceFormatter.render_resource_with_icon(
                    self.small_font,
                    resource_type,
                    amount,
                    self.registry,
                    self.resource_icon_size,
                    has_resource
                )
                
                # Position the resource display
                self.screen.blit(surface, (item_rect.left + 20, cost_y))
                cost_y += height
            
            # Position craft button
            for button in self.craft_buttons:
                if button.item_name == item_name:
                    button.rect.topleft = (content_rect.left + 70, y_pos + item_rect.height + 5)
                    button.position = button.rect.topleft
            
            y_pos += item_rect.height + 40
        
        # Update content height and max scroll
        content_height = y_pos - content_rect.top + 20 + self.scroll_offset
        self.max_scroll = max(0, content_height - content_rect.height)
        
        # Draw scroll indicators if needed
        if self.max_scroll > 0:
            self.draw_scroll_indicators(content_rect)
    
    def draw_coresmith_items(self, content_rect):
        """
        Draw coresmith items information tab
        
        Args:
            content_rect: Rectangle defining content area
        """
        y_pos = content_rect.top + 20 - self.scroll_offset
        
        # Draw item information header
        header_text = "Available Items"
        header_surface = self.font.render(header_text, True, self.HEADER_COLOR)
        self.screen.blit(header_surface, (content_rect.left + 15, y_pos))
        
        y_pos += 40
        
        # Get icon manager if available
        icon_manager = None
        if self.registry and self.registry.has(ICON_MANAGER):
            icon_manager = self.registry.get(ICON_MANAGER)
        
        # Draw information for each item
        for item_name, costs in ITEM_COSTS.items():
            # Create item card
            item_rect = pygame.Rect(
                content_rect.left + 15,
                y_pos,
                content_rect.width - 30,
                120
            )
            
            # Draw card
            pygame.draw.rect(self.screen, self.CARD_BG_COLOR, item_rect)
            pygame.draw.rect(self.screen, (100, 100, 100), item_rect, 1)
            
            # Draw item name with icon
            item_color = ResourceFormatter.get_resource_color(item_name)
            bright_color = tuple(min(255, c + 40) for c in item_color)
            
            # Draw item icon if available
            if icon_manager:
                icon_id = icon_manager.get_resource_icon_id(item_name)
                icon = icon_manager.get_icon(icon_id, (24, 24))
                icon_rect = icon.get_rect(topleft=(item_rect.left + 10, y_pos + 10))
                self.screen.blit(icon, icon_rect)
                name_left = icon_rect.right + 10
            else:
                name_left = item_rect.left + 10
            
            # Draw item name
            item_title = self.small_font.render(item_name, True, bright_color)
            self.screen.blit(item_title, (name_left, y_pos + 15))
            
            # Draw item effect
            effect_desc = ITEM_EFFECTS.get(item_name, {}).get("description", "No effect")
            effect_surface = self.small_font.render(f"Effect: {effect_desc}", True, self.SUBTEXT_COLOR)
            self.screen.blit(effect_surface, (item_rect.left + 15, y_pos + 40))
            
            # Draw cost with consistent formatting
            cost_y = y_pos + 60
            
            # Draw resources with icons and colors
            for resource_type, amount in ResourceFormatter.sort_resources(costs):
                has_resource = self.resource_manager.get_resource(resource_type) >= amount
                
                # Create resource display with icon
                surface, width, height = ResourceFormatter.render_resource_with_icon(
                    self.small_font,
                    resource_type,
                    amount,
                    self.registry,
                    self.resource_icon_size,
                    has_resource
                )
                
                # Position the resource display
                self.screen.blit(surface, (item_rect.left + 20, cost_y))
                cost_y += height
            
            # Draw inventory count
            count = self.resource_manager.get_resource(item_name)
            count_color = self.POSITIVE_COLOR if count > 0 else self.SUBTEXT_COLOR
            count_text = f"In Inventory: {count}"
            count_surface = self.small_font.render(count_text, True, count_color)
            self.screen.blit(count_surface, (item_rect.left + 15, y_pos + 100))
            
            y_pos += 130
        
        # Update content height and max scroll
        content_height = y_pos - content_rect.top + 20 + self.scroll_offset
        self.max_scroll = max(0, content_height - content_rect.height)
        
        # Draw scroll indicators if needed
        if self.max_scroll > 0:
            self.draw_scroll_indicators(content_rect)