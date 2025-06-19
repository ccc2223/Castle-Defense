# ui/castle_menu.py
"""
Castle upgrade menu UI for Castle Defense
"""
import pygame
from ui.base_menu import Menu
from ui.elements import Button
from ui.utils import ResourceFormatter
from registry import ICON_MANAGER

class CastleMenu(Menu):
    """Menu for upgrading the castle"""
    def __init__(self, screen, registry=None):
        """
        Initialize castle menu
        
        Args:
            screen: Pygame surface to draw on
            registry: Optional ComponentRegistry for accessing game components
        """
        super().__init__(screen)
        self.castle = None
        self.resource_manager = None
        self.registry = registry
        self.title = "Castle Upgrades"
        
        # Set up tabs
        self.tabs = ["Walls", "Armor", "Repair"]
        self.current_tab = "Walls"
        
        # Track upgrade buttons
        self.upgrade_buttons = {}
        
        # Resource icon size
        self.resource_icon_size = (16, 16)
    
    def set_castle(self, castle, resource_manager):
        """
        Set the castle this menu controls
        
        Args:
            castle: Castle instance
            resource_manager: ResourceManager for resources
        """
        self.castle = castle
        self.resource_manager = resource_manager
        
        # Reset scroll position
        self.scroll_offset = 0
        
        # Clear existing buttons
        self.buttons = []
        self.upgrade_buttons = {}
        
        # Create tab buttons
        self.create_tab_buttons()
        
        # Create upgrade buttons
        self.create_upgrade_buttons()
    
    def create_tab_buttons(self):
        """Create tab selection buttons"""
        tab_width = self.rect.width / len(self.tabs)
        
        for i, tab in enumerate(self.tabs):
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
        if tab in self.tabs:
            self.current_tab = tab
            self.scroll_offset = 0  # Reset scroll position
    
    def create_upgrade_buttons(self):
        """Create upgrade buttons for each tab"""
        button_width = self.rect.width - 60
        button_height = 40
        y_pos = self.rect.top + 300  # Position below stats
        
        # Health upgrade button
        health_cost = self.castle.get_health_upgrade_cost()
        can_upgrade_health = self.resource_manager.has_resources(health_cost)
        
        health_button = Button(
            (self.rect.left + 30, y_pos),
            (button_width, button_height),
            "Upgrade Castle Walls",
            self.upgrade_castle_health
        )
        health_button.set_disabled(not can_upgrade_health)
        self.buttons.append(health_button)
        self.upgrade_buttons["Walls"] = health_button
        
        # Damage reduction upgrade button
        dr_cost = self.castle.get_damage_reduction_upgrade_cost()
        can_upgrade_dr = self.resource_manager.has_resources(dr_cost)
        
        dr_button = Button(
            (self.rect.left + 30, y_pos),
            (button_width, button_height),
            "Upgrade Damage Reduction",
            self.upgrade_castle_damage_reduction
        )
        dr_button.set_disabled(not can_upgrade_dr)
        self.buttons.append(dr_button)
        self.upgrade_buttons["Armor"] = dr_button
        
        # Health regen upgrade button
        regen_cost = self.castle.get_health_regen_upgrade_cost()
        can_upgrade_regen = self.resource_manager.has_resources(regen_cost)
        
        regen_button = Button(
            (self.rect.left + 30, y_pos),
            (button_width, button_height),
            "Upgrade Health Regeneration",
            self.upgrade_castle_health_regen
        )
        regen_button.set_disabled(not can_upgrade_regen)
        self.buttons.append(regen_button)
        self.upgrade_buttons["Repair"] = regen_button
    
    def upgrade_castle_health(self):
        """Upgrade castle health"""
        if self.castle and self.resource_manager:
            if self.castle.upgrade_health(self.resource_manager):
                # Refresh the menu to update costs and button states
                self.set_castle(self.castle, self.resource_manager)
    
    def upgrade_castle_damage_reduction(self):
        """Upgrade castle damage reduction"""
        if self.castle and self.resource_manager:
            if self.castle.upgrade_damage_reduction(self.resource_manager):
                # Refresh the menu to update costs and button states
                self.set_castle(self.castle, self.resource_manager)
    
    def upgrade_castle_health_regen(self):
        """Upgrade castle health regeneration"""
        if self.castle and self.resource_manager:
            if self.castle.upgrade_health_regen(self.resource_manager):
                # Refresh the menu to update costs and button states
                self.set_castle(self.castle, self.resource_manager)
    
    def update_button_states(self):
        """Update button enabled/disabled states based on available resources"""
        if not self.castle or not self.resource_manager:
            return
        
        # Update health upgrade button
        health_cost = self.castle.get_health_upgrade_cost()
        can_upgrade_health = self.resource_manager.has_resources(health_cost)
        self.upgrade_buttons["Walls"].set_disabled(not can_upgrade_health)
        
        # Update damage reduction upgrade button
        dr_cost = self.castle.get_damage_reduction_upgrade_cost()
        can_upgrade_dr = self.resource_manager.has_resources(dr_cost)
        self.upgrade_buttons["Armor"].set_disabled(not can_upgrade_dr)
        
        # Update health regen upgrade button
        regen_cost = self.castle.get_health_regen_upgrade_cost()
        can_upgrade_regen = self.resource_manager.has_resources(regen_cost)
        self.upgrade_buttons["Repair"].set_disabled(not can_upgrade_regen)
    
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
            
            # Check for tooltips on upgrade buttons
            if self.current_tab == "Walls" and self.upgrade_buttons["Walls"].rect.collidepoint(event.pos):
                cost = self.castle.get_health_upgrade_cost()
                tooltip_text = f"Upgrade Castle Walls\nCost: {ResourceFormatter.format_cost(cost)}"
                self.tooltip_text = tooltip_text
                self.tooltip_position = (event.pos[0] + 15, event.pos[1] + 15)
                self.show_tooltip = True
                
            elif self.current_tab == "Armor" and self.upgrade_buttons["Armor"].rect.collidepoint(event.pos):
                cost = self.castle.get_damage_reduction_upgrade_cost()
                tooltip_text = f"Upgrade Damage Reduction\nCost: {ResourceFormatter.format_cost(cost)}"
                self.tooltip_text = tooltip_text
                self.tooltip_position = (event.pos[0] + 15, event.pos[1] + 15)
                self.show_tooltip = True
                
            elif self.current_tab == "Repair" and self.upgrade_buttons["Repair"].rect.collidepoint(event.pos):
                cost = self.castle.get_health_regen_upgrade_cost()
                tooltip_text = f"Upgrade Health Regeneration\nCost: {ResourceFormatter.format_cost(cost)}"
                self.tooltip_text = tooltip_text
                self.tooltip_position = (event.pos[0] + 15, event.pos[1] + 15)
                self.show_tooltip = True
        
        # Then handle other events
        return super().handle_event(event)
    
    def draw(self):
        """Draw castle menu with upgrade options"""
        if not self.active or not self.castle:
            return
        
        # Draw base menu (background and title)
        super().draw()
        
        # Update button states
        self.update_button_states()
        
        # Draw tabs
        self.draw_tab_buttons(self.tabs, self.current_tab)
        
        # Create content area below tabs
        content_rect = pygame.Rect(
            self.rect.left, 
            self.rect.top + 60,  # Below tabs
            self.rect.width,
            self.rect.height - 60
        )
        
        # Draw tab-specific content
        if self.current_tab == "Walls":
            self.draw_walls_tab(content_rect)
        elif self.current_tab == "Armor":
            self.draw_armor_tab(content_rect)
        elif self.current_tab == "Repair":
            self.draw_repair_tab(content_rect)
    
    def draw_walls_tab(self, content_rect):
        """
        Draw castle walls (health) upgrade tab
        
        Args:
            content_rect: Rectangle defining content area
        """
        castle = self.castle
        y_pos = content_rect.top + 20 - self.scroll_offset
        
        # Draw status card
        status_rect = pygame.Rect(
            content_rect.left + 15,
            y_pos,
            content_rect.width - 30,
            80
        )
        
        # Calculate health percentage
        health_pct = min(100, max(0, int(castle.health / castle.max_health * 100)))
        health_color = (100, 255, 100)  # Green for good health
        
        if health_pct < 50:
            health_color = (255, 200, 0)  # Yellow for warning
        if health_pct < 20:
            health_color = (255, 100, 100)  # Red for danger
        
        # Draw status card
        self.draw_card(status_rect, "Current Status")
        
        # Draw health text
        health_text = f"Health: {int(castle.health)}/{int(castle.max_health)}"
        health_surface = self.small_font.render(health_text, True, self.TEXT_COLOR)
        self.screen.blit(health_surface, (status_rect.left + 15, y_pos + 35))
        
        # Draw health bar background
        health_bar_rect = pygame.Rect(
            status_rect.left + 15,
            y_pos + 60,
            status_rect.width - 30,
            15
        )
        pygame.draw.rect(self.screen, (80, 80, 80), health_bar_rect)
        
        # Draw health bar fill
        health_width = int(health_bar_rect.width * (health_pct / 100))
        if health_width > 0:
            health_fill_rect = pygame.Rect(
                health_bar_rect.left,
                health_bar_rect.top,
                health_width,
                health_bar_rect.height
            )
            pygame.draw.rect(self.screen, health_color, health_fill_rect)
        
        # Draw border
        pygame.draw.rect(self.screen, (150, 150, 150), health_bar_rect, 1)
        
        y_pos += 100
        
        # Draw upgrade card
        upgrade_rect = pygame.Rect(
            content_rect.left + 15,
            y_pos,
            content_rect.width - 30,
            120
        )
        
        # Calculate next level stats
        next_health = castle.max_health * 1.5
        
        # Check if player has enough resources
        cost = castle.get_health_upgrade_cost()
        has_resources = self.resource_manager.has_resources(cost)
        border_color = self.POSITIVE_COLOR if has_resources else self.NEGATIVE_COLOR
        
        # Get icon manager if available
        icon_manager = None
        if self.registry and self.registry.has(ICON_MANAGER):
            icon_manager = self.registry.get(ICON_MANAGER)
        
        # Draw the upgrade card
        self.draw_card(
            upgrade_rect,
            f"Walls Upgrade (Level {castle.health_upgrade_level})",
            [
                f"Current Max Health: {int(castle.max_health)}",
                f"Next Level: {int(next_health)}",
                f"Improvement: +{int(next_health - castle.max_health)} HP"
            ],
            border_color
        )
        
        # Draw resource costs with icons
        cost_y = upgrade_rect.top + 80
        sorted_resources = ResourceFormatter.sort_resources(cost)
        
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
        self.upgrade_buttons["Walls"].rect.topleft = (content_rect.left + 30, y_pos + 130)
        self.upgrade_buttons["Walls"].position = self.upgrade_buttons["Walls"].rect.topleft
        self.upgrade_buttons["Walls"].draw(self.screen)
        
        # No scrolling needed for this tab
        self.max_scroll = 0
    
    def draw_armor_tab(self, content_rect):
        """
        Draw castle armor (damage reduction) upgrade tab
        
        Args:
            content_rect: Rectangle defining content area
        """
        castle = self.castle
        y_pos = content_rect.top + 20 - self.scroll_offset
        
        # Draw status card
        status_rect = pygame.Rect(
            content_rect.left + 15,
            y_pos,
            content_rect.width - 30,
            80
        )
        
        # Calculate damage reduction percentage
        dr_pct = int(castle.damage_reduction * 100)
        
        # Draw status card
        self.draw_card(status_rect, "Current Status")
        
        # Draw damage reduction text
        dr_text = f"Damage Reduction: {dr_pct}%"
        dr_surface = self.small_font.render(dr_text, True, self.TEXT_COLOR)
        self.screen.blit(dr_surface, (status_rect.left + 15, y_pos + 35))
        
        # Draw damage reduction bar background
        dr_bar_rect = pygame.Rect(
            status_rect.left + 15,
            y_pos + 60,
            status_rect.width - 30,
            15
        )
        pygame.draw.rect(self.screen, (80, 80, 80), dr_bar_rect)
        
        # Draw damage reduction bar fill
        dr_width = int(dr_bar_rect.width * (dr_pct / 100))
        if dr_width > 0:
            dr_fill_rect = pygame.Rect(
                dr_bar_rect.left,
                dr_bar_rect.top,
                dr_width,
                dr_bar_rect.height
            )
            pygame.draw.rect(self.screen, (100, 150, 200), dr_fill_rect)
        
        # Draw border
        pygame.draw.rect(self.screen, (150, 150, 150), dr_bar_rect, 1)
        
        y_pos += 100
        
        # Draw upgrade card
        upgrade_rect = pygame.Rect(
            content_rect.left + 15,
            y_pos,
            content_rect.width - 30,
            120
        )
        
        # Calculate next level stats
        next_dr = min(0.9, castle.damage_reduction * 1.2)
        next_dr_pct = int(next_dr * 100)
        improvement = next_dr_pct - dr_pct
        
        # Check if player has enough resources
        cost = castle.get_damage_reduction_upgrade_cost()
        has_resources = self.resource_manager.has_resources(cost)
        border_color = self.POSITIVE_COLOR if has_resources else self.NEGATIVE_COLOR
        
        # Draw the card
        self.draw_card(
            upgrade_rect,
            f"Armor Upgrade (Level {castle.damage_reduction_upgrade_level})",
            [
                f"Current Damage Reduction: {dr_pct}%",
                f"Next Level: {next_dr_pct}%",
                f"Improvement: +{improvement}% damage reduction"
            ],
            border_color
        )
        
        # Draw resource costs with icons
        cost_y = upgrade_rect.top + 80
        sorted_resources = ResourceFormatter.sort_resources(cost)
        
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
        self.upgrade_buttons["Armor"].rect.topleft = (content_rect.left + 30, y_pos + 130)
        self.upgrade_buttons["Armor"].position = self.upgrade_buttons["Armor"].rect.topleft
        self.upgrade_buttons["Armor"].draw(self.screen)
        
        # No scrolling needed for this tab
        self.max_scroll = 0
    
    def draw_repair_tab(self, content_rect):
        """
        Draw castle repair (health regen) upgrade tab
        
        Args:
            content_rect: Rectangle defining content area
        """
        castle = self.castle
        y_pos = content_rect.top + 20 - self.scroll_offset
        
        # Draw status card
        status_rect = pygame.Rect(
            content_rect.left + 15,
            y_pos,
            content_rect.width - 30,
            80
        )
        
        # Draw status card
        self.draw_card(status_rect, "Current Status")
        
        # Draw health regeneration text
        regen_text = f"Health Regeneration: {castle.health_regen:.1f} HP/s"
        regen_surface = self.small_font.render(regen_text, True, self.TEXT_COLOR)
        self.screen.blit(regen_surface, (status_rect.left + 15, y_pos + 35))
        
        # Draw time to full health calculation
        if castle.health < castle.max_health and castle.health_regen > 0:
            time_to_full = (castle.max_health - castle.health) / castle.health_regen
            time_text = f"Time to Full Health: {int(time_to_full)}s"
        else:
            time_text = "Health is Full"
        
        time_surface = self.small_font.render(time_text, True, self.SUBTEXT_COLOR)
        self.screen.blit(time_surface, (status_rect.left + 15, y_pos + 55))
        
        y_pos += 100
        
        # Draw upgrade card
        upgrade_rect = pygame.Rect(
            content_rect.left + 15,
            y_pos,
            content_rect.width - 30,
            120
        )
        
        # Calculate next level stats
        next_regen = castle.health_regen * 1.3
        improvement = next_regen - castle.health_regen
        
        # Check if player has enough resources
        cost = castle.get_health_regen_upgrade_cost()
        has_resources = self.resource_manager.has_resources(cost)
        border_color = self.POSITIVE_COLOR if has_resources else self.NEGATIVE_COLOR
        
        # Draw the card
        self.draw_card(
            upgrade_rect,
            f"Repair Upgrade (Level {castle.health_regen_upgrade_level})",
            [
                f"Current Health Regen: {castle.health_regen:.1f} HP/s",
                f"Next Level: {next_regen:.1f} HP/s",
                f"Improvement: +{improvement:.1f} HP/s"
            ],
            border_color
        )
        
        # Draw resource costs with icons
        cost_y = upgrade_rect.top + 80
        sorted_resources = ResourceFormatter.sort_resources(cost)
        
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
        self.upgrade_buttons["Repair"].rect.topleft = (content_rect.left + 30, y_pos + 130)
        self.upgrade_buttons["Repair"].position = self.upgrade_buttons["Repair"].rect.topleft
        self.upgrade_buttons["Repair"].draw(self.screen)
        
        # No scrolling needed for this tab
        self.max_scroll = 0