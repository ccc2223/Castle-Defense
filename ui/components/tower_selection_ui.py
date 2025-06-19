# ui/components/tower_selection_ui.py
"""
Tower selection UI component for Castle Defense
Handles tower menu button and selection cards
"""
import pygame
import math
from .ui_component import UIComponent
from ui.elements import Button
from ui.tower_card import TowerCard
from registry import RESOURCE_MANAGER
from config import WINDOW_WIDTH, WINDOW_HEIGHT, TOWER_TYPES, TOWER_MONSTER_COIN_COSTS

class TowerSelectionUI(UIComponent):
    """UI component for selecting and placing towers"""
    
    def __init__(self, screen, registry=None):
        """
        Initialize tower selection UI
        
        Args:
            screen: Pygame surface to draw on
            registry: Optional ComponentRegistry for accessing game components
        """
        super().__init__(screen, registry)
        
        # Create tower menu button in bottom left corner
        button_size = (80, 80)
        button_margin = 20
        button_pos = (button_margin, WINDOW_HEIGHT - button_size[1] - button_margin)
        
        self.tower_menu_button = Button(
            button_pos,
            button_size,
            "Build\nTower",
            self.toggle_tower_menu,
            color=(60, 70, 100),
            hover_color=(80, 90, 120),
            text_color=(220, 220, 220)
        )
        
        # Initialize the tower menu panel state
        self.menu_open = False
        self.menu_animation_time = 0
        self.menu_animation_duration = 0.3  # Time to fully open/close in seconds
        
        # Create tower cards for each tower type
        self.tower_cards = []
        tower_types = list(TOWER_TYPES.keys())
        
        # Calculate card size
        self.card_width = 110
        self.card_height = 230  # Increased height for resources
        self.card_spacing = 10  # Space between cards
        
        # Calculate total width needed for all cards
        total_cards_width = len(tower_types) * self.card_width + (len(tower_types) - 1) * self.card_spacing
        
        # Panel dimensions - positioned to the right of the Build Tower button
        panel_x_margin = 20  # Margin from sides
        panel_y_margin = 10  # Margin from button to panel
        
        # Panel starts at the same left position as the button
        self.panel_x = button_pos[0]
        
        # Panel width is just enough to fit all cards + margins
        self.panel_width = total_cards_width + panel_x_margin * 2
        
        # Panel height is enough for cards + header + margins (30% taller)
        self.panel_height = int(self.card_height * 1.3) + 50  # 50px for header and margins
        
        # Position panel bottom just above the button top
        self.panel_y = button_pos[1] - self.panel_height - panel_y_margin
        
        # Card positions within the panel
        card_start_x = self.panel_x + panel_x_margin
        card_y = self.panel_y + 40  # 40px from panel top (leave room for header)
        
        for i, tower_type in enumerate(tower_types):
            card_x = card_start_x + i * (self.card_width + self.card_spacing)
            
            self.tower_cards.append(TowerCard(
                (card_x, card_y),
                (self.card_width, self.card_height),
                tower_type,
                lambda t=tower_type: self.select_tower(t),
                registry  # Pass registry to tower cards for icon access
            ))
        
        # Track currently selected card
        self.selected_card_index = -1
        
        # Close button for the panel
        close_button_size = (24, 24)
        self.close_button = Button(
            (self.panel_x + self.panel_width - close_button_size[0] - 10, self.panel_y + 10),
            close_button_size,
            "X",
            self.close_tower_menu,
            color=(100, 60, 60),
            hover_color=(150, 80, 80)
        )
    
    def update(self, dt):
        """
        Update UI animations
        
        Args:
            dt: Time delta in seconds
        """
        if not self.active:
            return
            
        # Update menu animation
        if (self.menu_open and self.menu_animation_time < self.menu_animation_duration) or \
           (not self.menu_open and self.menu_animation_time < self.menu_animation_duration):
            self.menu_animation_time += dt
        
        # Update card animations if menu is visible
        if self.menu_open or self.menu_animation_time < self.menu_animation_duration:
            for card in self.tower_cards:
                card.update_animation(dt)
    
    def draw(self):
        """Draw tower selection UI elements"""
        if not self.visible:
            return
            
        # Always draw the tower menu button
        self.tower_menu_button.draw(self.screen)
        
        # Draw tower selection panel if open or animating
        if self.menu_open or self.menu_animation_time < self.menu_animation_duration:
            # Calculate animation progress
            if self.menu_open:
                progress = min(1, self.menu_animation_time / self.menu_animation_duration)
                # Ease out quad
                eased_progress = 1 - (1 - progress) ** 2
            else:
                progress = 1 - min(1, self.menu_animation_time / self.menu_animation_duration)
                # Ease in quad
                eased_progress = progress ** 2
                
            # Apply animation: slide up from bottom and fade in
            panel_y_offset = (1 - eased_progress) * 100  # Slide up 100px
            panel_opacity = int(eased_progress * 220)  # Fade in to 220 alpha (semi-transparent)
            
            # Only draw if panel has some visibility
            if eased_progress > 0:
                animated_panel_y = self.panel_y + panel_y_offset
                
                # Draw panel background
                panel_rect = pygame.Rect(self.panel_x, animated_panel_y, self.panel_width, self.panel_height)
                panel_surface = pygame.Surface((panel_rect.width, panel_rect.height), pygame.SRCALPHA)
                panel_surface.fill((30, 30, 40, panel_opacity))  # Dark semi-transparent background
                self.screen.blit(panel_surface, panel_rect.topleft)
                
                # Draw panel border
                pygame.draw.rect(self.screen, (100, 100, 150, panel_opacity), 
                               panel_rect, 2)
                
                # Draw title for tower selection panel
                title_font = pygame.font.Font(None, 24)
                title_text = "Select Tower"
                title_surface = title_font.render(title_text, True, (220, 220, 255))
                title_rect = title_surface.get_rect(midtop=(panel_rect.left + panel_rect.width // 2, panel_rect.top + 10))
                self.screen.blit(title_surface, title_rect)
                
                # Update close button position and draw it
                self.close_button.position = (panel_rect.right - 34, panel_rect.top + 10)
                self.close_button.rect.topleft = self.close_button.position
                self.close_button.draw(self.screen)
                
                # Update card positions based on animation
                for i, card in enumerate(self.tower_cards):
                    # Original x position doesn't change
                    original_x = card.position[0]
                    # Y position moves with panel
                    card.position = (original_x, self.panel_y + 40 + panel_y_offset)
                    card.rect.topleft = card.position
                    
                    # Set selected state if this is the selected card
                    card.selected = (i == self.selected_card_index)
                    
                    # Only draw the card if the panel has enough opacity
                    if eased_progress > 0.1:
                        # Set disabled state if player doesn't have enough resources
                        if self.registry and self.registry.has(RESOURCE_MANAGER):
                            resource_manager = self.registry.get(RESOURCE_MANAGER)
                            tower_cost = TOWER_TYPES.get(card.tower_type, {}).get("cost", {})
                            monster_coin_cost = TOWER_MONSTER_COIN_COSTS.get(card.tower_type, 0)
                            has_resources = resource_manager.has_resources_for_tower(tower_cost, monster_coin_cost)
                            card.set_disabled(not has_resources)
                            
                            # Draw the card
                            card.draw(self.screen, resource_manager)
                        else:
                            # Draw card without resource check
                            card.draw(self.screen, None)
    
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
            
        mouse_pos = pygame.mouse.get_pos()
        
        # First check for tower menu button clicks
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Check main menu button
            if self.tower_menu_button.rect.collidepoint(mouse_pos):
                self.tower_menu_button.click()
                return True
                
            # If menu is open or animating, check panel clicks
            if self.menu_open or self.menu_animation_time < self.menu_animation_duration:
                # Calculate current panel opacity based on animation
                if self.menu_open:
                    progress = min(1, self.menu_animation_time / self.menu_animation_duration)
                else:
                    progress = 1 - min(1, self.menu_animation_time / self.menu_animation_duration)
                
                # Only process clicks if panel is visible enough
                if progress > 0.5:
                    animated_panel_y = self.panel_y
                    if not self.menu_open:
                        # Calculate slide position if closing
                        if self.menu_animation_time < self.menu_animation_duration:
                            eased_progress = progress ** 2
                            panel_y_offset = (1 - eased_progress) * 100
                            animated_panel_y += panel_y_offset
                    
                    panel_rect = pygame.Rect(self.panel_x, animated_panel_y, self.panel_width, self.panel_height)
                    
                    if panel_rect.collidepoint(mouse_pos):
                        # Check close button
                        if self.close_button.rect.collidepoint(mouse_pos):
                            self.close_button.click()
                            return True
                            
                        # Check card clicks
                        for i, card in enumerate(self.tower_cards):
                            if card.rect.collidepoint(mouse_pos) and not card.disabled:
                                card.click()
                                # Mark this card as selected
                                self.selected_card_index = i
                                return True
                        # Clicked on panel but not on any clickable element
                        return True
        
        # Check for mouse motion for hover effects
        elif event.type == pygame.MOUSEMOTION:
            # Update tower menu button hover state
            self.tower_menu_button.update(mouse_pos)
                
            # Update close button and card hover states if menu is open
            if self.menu_open or self.menu_animation_time < self.menu_animation_duration:
                # Close button hover
                self.close_button.update(mouse_pos)
                
                # Card hover states
                for card in self.tower_cards:
                    card.update(mouse_pos)
        
        return False
    
    def toggle_tower_menu(self):
        """Toggle the tower menu panel open/closed"""
        self.menu_open = not self.menu_open
        self.menu_animation_time = 0
    
    def close_tower_menu(self):
        """Close the tower menu panel"""
        self.menu_open = False
        self.menu_animation_time = 0
    
    def select_tower(self, tower_type):
        """
        Callback when tower type is selected
        
        Args:
            tower_type: Type of tower to place
        """
        # Find the index of the selected card
        for i, card in enumerate(self.tower_cards):
            if card.tower_type == tower_type:
                self.selected_card_index = i
                break
        
        # Close the menu and enter tower placement mode
        self.close_tower_menu()
        
        # Use registry to enter tower placement mode if available
        if self.registry and self.registry.has("game"):
            game = self.registry.get("game")
            if hasattr(game, "enter_tower_placement_mode"):
                game.enter_tower_placement_mode(tower_type)
        else:
            # Fallback to global instance
            try:
                from game import Game
                game_instance = Game.get_instance()
                if game_instance:
                    game_instance.enter_tower_placement_mode(tower_type)
            except (ImportError, AttributeError):
                pass
