# ui/talent_tree_ui.py
"""
Talent Tree UI system for Castle Defense
"""
import pygame
import math
from utils import scale_position, scale_size, scale_value
from registry import RESOURCE_MANAGER

class TalentTreeUI:
    """
    UI for displaying and interacting with the talent tree
    """
    def __init__(self, screen, town_hall, registry=None):
        """
        Initialize talent tree UI
        
        Args:
            screen: Pygame surface to draw on
            town_hall: TownHall instance with talent data
            registry: Optional ComponentRegistry for accessing game components
        """
        self.screen = screen
        self.town_hall = town_hall
        self.registry = registry
        
        # Set up UI dimensions - use nearly full screen
        self.margin = scale_value(30)
        self.width = screen.get_width() - (self.margin * 2)
        self.height = screen.get_height() - (self.margin * 2)
        self.rect = pygame.Rect(
            self.margin,
            self.margin,
            self.width,
            self.height
        )
        
        # Talent node dimensions
        self.node_size = scale_value(60)
        self.connection_thickness = scale_value(4)
        
        # Spacing between nodes
        self.node_spacing_x = scale_value(120)
        self.node_spacing_y = scale_value(100)
        
        # Panel dimensions
        self.panel_width = scale_value(250)
        self.tree_view_width = self.width - self.panel_width - scale_value(20)
        
        # UI state
        self.visible = False
        self.selected_tree = "defense"  # Default tree to show
        self.selected_talent = None
        self.hovered_talent = None
        
        # Animation properties
        self.fade_in = 0.0  # 0 to 1 for fade-in effect
        self.fade_in_speed = 4.0  # Fade in speed
        
        # Create close button
        self.close_button_size = scale_value(30)
        self.close_button_rect = pygame.Rect(
            self.rect.right - self.close_button_size - scale_value(10),
            self.rect.top + scale_value(10),
            self.close_button_size,
            self.close_button_size
        )
    
    def toggle(self):
        """Toggle UI visibility"""
        self.visible = not self.visible
        if self.visible:
            # Reset fade-in when opening
            self.fade_in = 0.0
    
    def update(self, dt):
        """
        Update talent tree UI
        
        Args:
            dt: Time delta in seconds
        """
        if not self.visible:
            return
        
        # Update fade-in animation
        if self.fade_in < 1.0:
            self.fade_in = min(1.0, self.fade_in + dt * self.fade_in_speed)
    
    def handle_event(self, event):
        """
        Handle pygame events
        
        Args:
            event: Pygame event
            
        Returns:
            True if event was handled, False otherwise
        """
        if not self.visible:
            return False
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Close button
            if self.close_button_rect.collidepoint(event.pos):
                self.visible = False
                return True
            
            # Tree selection tabs
            for i, tree_name in enumerate(self.town_hall.talent_trees.keys()):
                tab_rect = self.get_tab_rect(i)
                if tab_rect.collidepoint(event.pos):
                    self.selected_tree = tree_name
                    self.selected_talent = None
                    return True
            
            # Talent node clicks
            tree_data = self.town_hall.talent_trees[self.selected_tree]
            for talent_id, talent_data in tree_data["talents"].items():
                node_rect = self.get_talent_node_rect(talent_data["position"])
                if node_rect.collidepoint(event.pos):
                    self.selected_talent = talent_id
                    return True
            
            # Upgrade button
            if self.selected_talent and hasattr(self, 'upgrade_button_rect'):
                if self.upgrade_button_rect.collidepoint(event.pos):
                    # Try to upgrade the selected talent
                    self.town_hall.spend_talent_points(
                        self.selected_tree, 
                        self.selected_talent
                    )
                    return True
            
            # Click outside any interactive element
            return True
        
        elif event.type == pygame.MOUSEMOTION:
            # Update hover state
            self.hovered_talent = None
            
            # Check for talent node hovers
            tree_data = self.town_hall.talent_trees[self.selected_tree]
            for talent_id, talent_data in tree_data["talents"].items():
                node_rect = self.get_talent_node_rect(talent_data["position"])
                if node_rect.collidepoint(event.pos):
                    self.hovered_talent = talent_id
                    break
        
        return False
    
    def draw(self):
        """Draw talent tree UI"""
        if not self.visible:
            return
        
        # Apply fade-in effect
        bg_alpha = int(200 * self.fade_in)
        content_alpha = int(255 * self.fade_in)
        
        # Create background surface with transparency
        bg_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        bg_surface.fill((20, 30, 40, bg_alpha))
        
        # Draw main background
        self.screen.blit(bg_surface, (self.margin, self.margin))
        
        # Draw border with fade-in effect
        border_color = (100, 120, 180, content_alpha)
        pygame.draw.rect(self.screen, border_color, self.rect, scale_value(2))
        
        # Draw tree tabs
        self.draw_tree_tabs()
        
        # Draw tree connections and nodes
        self.draw_talent_tree()
        
        # Draw right side panel
        self.draw_info_panel()
        
        # Draw close button
        pygame.draw.rect(self.screen, (150, 70, 70), self.close_button_rect)
        pygame.draw.rect(self.screen, (200, 200, 200), self.close_button_rect, 2)
        
        # Draw X on close button
        x_margin = scale_value(8)
        pygame.draw.line(
            self.screen,
            (230, 230, 230),
            (self.close_button_rect.left + x_margin, self.close_button_rect.top + x_margin),
            (self.close_button_rect.right - x_margin, self.close_button_rect.bottom - x_margin),
            2
        )
        pygame.draw.line(
            self.screen,
            (230, 230, 230),
            (self.close_button_rect.left + x_margin, self.close_button_rect.bottom - x_margin),
            (self.close_button_rect.right - x_margin, self.close_button_rect.top + x_margin),
            2
        )
    
    def draw_tree_tabs(self):
        """Draw tabs for selecting talent trees"""
        # Calculate tab properties
        num_trees = len(self.town_hall.talent_trees)
        tab_width = scale_value(150)
        tab_height = scale_value(35)
        padding = scale_value(5)
        
        # Total width of all tabs
        total_width = (tab_width + padding) * num_trees - padding
        start_x = self.rect.centerx - (total_width // 2)
        
        # Draw each tab
        for i, (tree_name, tree_data) in enumerate(self.town_hall.talent_trees.items()):
            tab_rect = self.get_tab_rect(i)
            
            # Determine if this tab is selected
            is_selected = tree_name == self.selected_tree
            
            # Draw tab background
            bg_color = (60, 80, 120) if is_selected else (40, 50, 80)
            pygame.draw.rect(self.screen, bg_color, tab_rect)
            
            # Draw tab border
            border_color = (120, 160, 240) if is_selected else (80, 100, 150)
            pygame.draw.rect(self.screen, border_color, tab_rect, 2)
            
            # Draw tab text
            font = pygame.font.Font(None, scale_value(22))
            text = font.render(tree_data["name"], True, (220, 220, 220))
            text_rect = text.get_rect(center=tab_rect.center)
            self.screen.blit(text, text_rect)
    
    def get_tab_rect(self, index):
        """
        Get rectangle for a tree selection tab
        
        Args:
            index: Tab index
            
        Returns:
            Pygame Rect
        """
        num_trees = len(self.town_hall.talent_trees)
        tab_width = scale_value(150)
        tab_height = scale_value(35)
        padding = scale_value(5)
        
        # Total width of all tabs
        total_width = (tab_width + padding) * num_trees - padding
        start_x = self.rect.centerx - (total_width // 2)
        
        # Calculate tab position
        tab_x = start_x + (tab_width + padding) * index
        tab_y = self.rect.top + scale_value(15)
        
        return pygame.Rect(tab_x, tab_y, tab_width, tab_height)
    
    def draw_talent_tree(self):
        """Draw talent tree connections and nodes"""
        # Get the current tree data
        tree_data = self.town_hall.talent_trees[self.selected_tree]
        
        # Define the tree area to draw in
        tree_area = pygame.Rect(
            self.rect.left + scale_value(20),
            self.rect.top + scale_value(60),
            self.tree_view_width,
            self.height - scale_value(80)
        )
        
        # Calculate the center position for the root talent
        center_x = tree_area.centerx
        center_y = tree_area.top + scale_value(120)
        
        # Draw connections first (so they appear behind nodes)
        for talent_id, talent_data in tree_data["talents"].items():
            # Draw connections to prerequisite talents
            for req_id, req_level in talent_data["requires"].items():
                if req_id in tree_data["talents"]:
                    req_talent = tree_data["talents"][req_id]
                    
                    # Get positions of both talents
                    pos1 = self.get_talent_node_position(req_talent["position"])
                    pos2 = self.get_talent_node_position(talent_data["position"])
                    
                    # Determine color based on whether requirements are met
                    if req_talent["current_level"] >= req_level:
                        # Requirement met
                        connection_color = (100, 150, 100)
                    else:
                        # Requirement not met
                        connection_color = (100, 100, 100)
                    
                    # Draw the connection line
                    pygame.draw.line(
                        self.screen,
                        connection_color,
                        pos1,
                        pos2,
                        self.connection_thickness
                    )
                    
                    # Draw requirement text near the line
                    if req_level > 1:
                        # Determine position for requirement text (midpoint of connection)
                        mid_x = (pos1[0] + pos2[0]) // 2
                        mid_y = (pos1[1] + pos2[1]) // 2
                        
                        # Draw requirement text
                        req_font = pygame.font.Font(None, scale_value(16))
                        req_text = f"Lvl {req_level}"
                        req_surface = req_font.render(req_text, True, connection_color)
                        req_rect = req_surface.get_rect(center=(mid_x, mid_y))
                        
                        # Draw background for better readability
                        padding = scale_value(3)
                        bg_rect = req_rect.inflate(padding * 2, padding * 2)
                        pygame.draw.rect(self.screen, (30, 40, 60), bg_rect)
                        
                        # Draw text
                        self.screen.blit(req_surface, req_rect)
        
        # Now draw talent nodes
        for talent_id, talent_data in tree_data["talents"].items():
            node_rect = self.get_talent_node_rect(talent_data["position"])
            
            # Determine node appearance based on state
            is_selected = talent_id == self.selected_talent
            is_hovered = talent_id == self.hovered_talent
            is_maxed = talent_data["current_level"] >= talent_data["levels"]
            is_available = self.can_upgrade_talent(talent_id)
            
            # Draw node background
            if is_maxed:
                # Maxed out talent
                bg_color = (80, 120, 80)
            elif is_available:
                # Available to upgrade
                bg_color = (60, 80, 120)
            else:
                # Locked or unavailable
                bg_color = (60, 60, 60)
            
            # Apply selected/hover effects
            if is_selected:
                bg_color = tuple(min(c + 40, 255) for c in bg_color)
            elif is_hovered:
                bg_color = tuple(min(c + 20, 255) for c in bg_color)
            
            # Draw main node
            pygame.draw.circle(self.screen, bg_color, node_rect.center, self.node_size // 2)
            
            # Draw border
            border_color = talent_data["icon_color"] if not is_maxed else (150, 200, 150)
            pygame.draw.circle(self.screen, border_color, node_rect.center, self.node_size // 2, scale_value(2))
            
            # Draw level indicator
            if talent_data["current_level"] > 0:
                level_font = pygame.font.Font(None, scale_value(16))
                level_text = f"{talent_data['current_level']}/{talent_data['levels']}"
                level_surface = level_font.render(level_text, True, (220, 220, 220))
                level_rect = level_surface.get_rect(center=(node_rect.centerx, node_rect.bottom + scale_value(10)))
                self.screen.blit(level_surface, level_rect)
            
            # Draw icon or first letter of talent name
            icon_font = pygame.font.Font(None, scale_value(28))
            icon_text = talent_data["name"][0]  # First letter
            icon_surface = icon_font.render(icon_text, True, (230, 230, 230))
            icon_rect = icon_surface.get_rect(center=node_rect.center)
            self.screen.blit(icon_surface, icon_rect)
            
            # Draw talent name below
            name_font = pygame.font.Font(None, scale_value(18))
            name_text = talent_data["name"]
            name_surface = name_font.render(name_text, True, (200, 200, 200))
            name_rect = name_surface.get_rect(midtop=(node_rect.centerx, node_rect.bottom + scale_value(15)))
            self.screen.blit(name_surface, name_rect)
    
    def get_talent_node_position(self, position):
        """
        Calculate screen position for a talent node
        
        Args:
            position: Tuple of (x, y) relative position in tree
            
        Returns:
            Tuple of (x, y) screen coordinates
        """
        # Calculate the center position for the root talent
        tree_area = pygame.Rect(
            self.rect.left + scale_value(20),
            self.rect.top + scale_value(60),
            self.tree_view_width,
            self.height - scale_value(80)
        )
        center_x = tree_area.centerx
        center_y = tree_area.top + scale_value(120)
        
        # Calculate node position based on tree layout
        x = center_x + (position[0] * self.node_spacing_x)
        y = center_y + (position[1] * self.node_spacing_y)
        
        return (x, y)
    
    def get_talent_node_rect(self, position):
        """
        Get rectangle for a talent node
        
        Args:
            position: Tuple of (x, y) relative position in tree
            
        Returns:
            Pygame Rect
        """
        pos = self.get_talent_node_position(position)
        return pygame.Rect(
            pos[0] - self.node_size // 2,
            pos[1] - self.node_size // 2,
            self.node_size,
            self.node_size
        )
    
    def draw_info_panel(self):
        """Draw info panel for selected talent"""
        # Define panel area
        panel_rect = pygame.Rect(
            self.rect.right - self.panel_width - scale_value(10),
            self.rect.top + scale_value(60),
            self.panel_width,
            self.height - scale_value(80)
        )
        
        # Draw panel background
        pygame.draw.rect(self.screen, (30, 40, 60), panel_rect)
        pygame.draw.rect(self.screen, (80, 100, 150), panel_rect, scale_value(2))
        
        # Draw talent info if a talent is selected
        if self.selected_talent:
            talent_data = self.town_hall.talent_trees[self.selected_tree]["talents"][self.selected_talent]
            
            # Add padding
            padding = scale_value(15)
            content_width = panel_rect.width - (padding * 2)
            
            # Draw talent name
            y_offset = panel_rect.top + padding
            name_font = pygame.font.Font(None, scale_value(28))
            name_text = talent_data["name"]
            name_surface = name_font.render(name_text, True, (220, 220, 200))
            self.screen.blit(name_surface, (panel_rect.left + padding, y_offset))
            y_offset += name_surface.get_height() + scale_value(10)
            
            # Draw current level
            level_font = pygame.font.Font(None, scale_value(22))
            level_text = f"Level: {talent_data['current_level']}/{talent_data['levels']}"
            level_surface = level_font.render(level_text, True, (200, 200, 220))
            self.screen.blit(level_surface, (panel_rect.left + padding, y_offset))
            y_offset += level_surface.get_height() + scale_value(20)
            
            # Draw description
            desc_font = pygame.font.Font(None, scale_value(20))
            desc_text = talent_data["description"]
            desc_surface = desc_font.render(desc_text, True, (200, 200, 200))
            self.screen.blit(desc_surface, (panel_rect.left + padding, y_offset))
            y_offset += desc_surface.get_height() + scale_value(20)
            
            # Draw current effect
            current_font = pygame.font.Font(None, scale_value(18))
            
            # Format effect based on type
            for effect_type, effect_value in talent_data["effects_per_level"].items():
                current_effect = effect_value * talent_data["current_level"]
                next_effect = effect_value * (talent_data["current_level"] + 1) if talent_data["current_level"] < talent_data["levels"] else None
                
                effect_name = self.format_effect_name(effect_type)
                effect_text = self.format_effect_value(effect_type, current_effect)
                
                if current_effect > 0:
                    effect_line = f"{effect_name}: {effect_text}"
                    effect_surface = current_font.render(effect_line, True, (180, 200, 180))
                    self.screen.blit(effect_surface, (panel_rect.left + padding, y_offset))
                    y_offset += effect_surface.get_height() + scale_value(5)
                
                # Show next level effect if not maxed
                if next_effect is not None:
                    next_effect_text = self.format_effect_value(effect_type, next_effect)
                    next_line = f"Next level: {next_effect_text}"
                    next_surface = current_font.render(next_line, True, (180, 180, 220))
                    self.screen.blit(next_surface, (panel_rect.left + padding + scale_value(20), y_offset))
                    y_offset += next_surface.get_height() + scale_value(10)
            
            # Draw requirements if not met
            can_upgrade, reason = self.town_hall.can_upgrade_talent(self.selected_tree, self.selected_talent)
            if not can_upgrade:
                if reason:
                    # Draw requirement text in red
                    req_font = pygame.font.Font(None, scale_value(20))
                    req_surface = req_font.render(reason, True, (220, 120, 120))
                    self.screen.blit(req_surface, (panel_rect.left + padding, y_offset))
                    y_offset += req_surface.get_height() + scale_value(15)
            
            # Draw upgrade button if available
            if not talent_data["current_level"] >= talent_data["levels"]:
                button_width = content_width
                button_height = scale_value(40)
                button_rect = pygame.Rect(
                    panel_rect.left + padding,
                    panel_rect.bottom - button_height - padding,
                    button_width,
                    button_height
                )
                
                # Store button rect for click detection
                self.upgrade_button_rect = button_rect
                
                # Determine button color based on availability
                if can_upgrade:
                    button_color = (80, 150, 80)
                    text_color = (230, 230, 230)
                else:
                    button_color = (80, 80, 80)
                    text_color = (150, 150, 150)
                
                # Draw button
                pygame.draw.rect(self.screen, button_color, button_rect)
                pygame.draw.rect(self.screen, (150, 150, 150), button_rect, scale_value(2))
                
                # Draw button text
                cost_text = f"Upgrade ({talent_data['cost']} point{'s' if talent_data['cost'] > 1 else ''})"
                button_font = pygame.font.Font(None, scale_value(22))
                button_text = button_font.render(cost_text, True, text_color)
                button_text_rect = button_text.get_rect(center=button_rect.center)
                self.screen.blit(button_text, button_text_rect)
        else:
            # No talent selected
            info_font = pygame.font.Font(None, scale_value(24))
            info_text = "Select a talent to view details"
            info_surface = info_font.render(info_text, True, (200, 200, 200))
            info_rect = info_surface.get_rect(center=(panel_rect.centerx, panel_rect.top + scale_value(50)))
            self.screen.blit(info_surface, info_rect)
        
        # Always show talent points available
        points_font = pygame.font.Font(None, scale_value(22))
        points_text = f"Available Talent Points: {self.town_hall.talent_points}"
        points_surface = points_font.render(points_text, True, (220, 220, 100))
        points_rect = points_surface.get_rect(
            bottom=panel_rect.bottom - scale_value(15),
            centerx=panel_rect.centerx
        )
        self.screen.blit(points_surface, points_rect)
    
    def format_effect_name(self, effect_type):
        """
        Format effect type into readable name
        
        Args:
            effect_type: Effect type string
            
        Returns:
            Formatted effect name
        """
        # Format from snake_case to Title Case and remove "multiplier"
        effect_name = effect_type.replace("_", " ").title()
        effect_name = effect_name.replace("Multiplier", "")
        return effect_name
    
    def format_effect_value(self, effect_type, value):
        """
        Format effect value based on type
        
        Args:
            effect_type: Effect type string
            value: Effect value
            
        Returns:
            Formatted effect value
        """
        if "multiplier" in effect_type or "chance" in effect_type:
            # Percentage format
            return f"+{int(value * 100)}%"
        elif effect_type == "tower_upgrade_paths":
            # Integer quantity
            return f"+{int(value)} path{'s' if value > 1 else ''}"
        elif effect_type == "auto_repair_trigger":
            # Boolean trigger
            return "Enabled" if value > 0 else "Disabled"
        else:
            # Generic format
            return f"+{value:.2f}"
    
    def can_upgrade_talent(self, talent_id):
        """
        Check if talent can be upgraded
        
        Args:
            talent_id: Talent identifier
            
        Returns:
            True if talent can be upgraded, False otherwise
        """
        can_upgrade, _ = self.town_hall.can_upgrade_talent(self.selected_tree, talent_id)
        return can_upgrade
