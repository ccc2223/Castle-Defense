# ui/tower_card.py
"""
Tower card UI element for Castle Defense
"""
import pygame
import math
import random
from utils import scale_value, scale_size
from ui.utils import ResourceFormatter
from config import TOWER_TYPES, TOWER_MONSTER_COIN_COSTS
from registry import ICON_MANAGER

class TowerCard:
    """Visual card-style UI element for tower selection"""
    def __init__(self, position, size, tower_type, callback, registry=None):
        """
        Initialize tower card
        
        Args:
            position: Tuple of (x, y) position for top-left corner
            size: Tuple of (width, height)
            tower_type: String indicating tower type
            callback: Function to call when clicked
            registry: Optional Component Registry for icon manager
        """
        self.position = position
        self.size = size
        self.tower_type = tower_type
        self.callback = callback
        self.registry = registry
        
        # Card states
        self.hovered = False
        self.selected = False
        self.disabled = False
        
        # Colors
        self.bg_color = (60, 60, 80)
        self.hover_color = (80, 80, 100)
        self.selected_color = (100, 100, 160)
        self.disabled_color = (40, 40, 50)
        self.border_color = (120, 120, 180)
        self.text_color = (220, 220, 220)
        self.disabled_text_color = (120, 120, 120)
        
        # Set card rectangle
        self.rect = pygame.Rect(position, size)
        
        # Tower icon parameters
        tower_icon_ratio = 0.3  # Smaller tower icon to leave more room for costs
        self.icon_size = (int(size[0] * tower_icon_ratio), int(size[0] * tower_icon_ratio))
        self.icon_pos = (position[0] + size[0]//2 - self.icon_size[0]//2, 
                         position[1] + int(size[1] * 0.18) - self.icon_size[1]//2)
        self.icon_rect = pygame.Rect(self.icon_pos, self.icon_size)
        
        # Tower specific color and shape
        self.tower_color = self.get_tower_color(tower_type)
        
        # Font for text
        self.title_font = pygame.font.Font(None, scale_value(20))
        self.cost_font = pygame.font.Font(None, scale_value(14))  # Smaller font for resource costs
        
        # Animation properties
        self.pulse_time = 0
        self.shake_offset = (0, 0)
        self.shake_time = 0
        
        # Resource requirements
        self.tower_cost = TOWER_TYPES.get(tower_type, {}).get("cost", {})
        self.monster_coin_cost = TOWER_MONSTER_COIN_COSTS.get(tower_type, 0)
        
        # Resource display configuration
        self.resource_icon_size = (scale_value(12), scale_value(12))  # Smaller resource icons
        self.resource_line_height = scale_value(14)  # Smaller height for each resource line
        
        # Resource area layout
        self.cost_area_y = int(self.size[1] * 0.35)  # Start costs area after tower name
    
    def get_tower_color(self, tower_type):
        """
        Get color based on tower type
        
        Args:
            tower_type: String indicating tower type
            
        Returns:
            RGB color tuple
        """
        colors = {
            "Archer": (100, 150, 100),  # Green
            "Sniper": (150, 100, 100),  # Red
            "Splash": (150, 150, 100),  # Yellow
            "Frozen": (100, 150, 150)   # Cyan
        }
        return colors.get(tower_type, (100, 100, 100))
    
    def update(self, mouse_pos):
        """
        Update card state based on mouse position
        
        Args:
            mouse_pos: Tuple of (x, y) mouse coordinates
        """
        if not self.disabled:
            self.hovered = self.rect.collidepoint(mouse_pos)
    
    def click(self):
        """Execute callback when clicked"""
        if not self.disabled and self.callback:
            # Add click animation - slight shake
            self.shake_time = 0.2  # Shake for 0.2 seconds
            self.callback()
    
    def set_disabled(self, disabled):
        """
        Set card disabled state
        
        Args:
            disabled: Boolean indicating if card should be disabled
        """
        self.disabled = disabled
    
    def update_animation(self, dt):
        """
        Update animation effects
        
        Args:
            dt: Time delta in seconds
        """
        # Update pulse animation for hover effect
        self.pulse_time += dt * 3  # Adjust speed
        
        # Update shake animation
        if self.shake_time > 0:
            self.shake_time -= dt
            # Generate random offset for shake effect
            if self.shake_time > 0:
                shake_amount = int(self.shake_time * 10)
                self.shake_offset = (
                    random.randint(-shake_amount, shake_amount),
                    random.randint(-shake_amount, shake_amount)
                )
            else:
                self.shake_offset = (0, 0)
    
    def draw(self, screen, resource_manager):
        """
        Draw tower card with icon, name, and resource costs
        
        Args:
            screen: Pygame surface to draw on
            resource_manager: ResourceManager to check resource availability
        """
        # Apply shake offset for click animation
        draw_pos = (self.position[0] + self.shake_offset[0], 
                    self.position[1] + self.shake_offset[1])
        draw_rect = pygame.Rect(draw_pos, self.size)
        
        # Calculate pulse scale for hover
        pulse = 0
        if self.hovered:
            pulse = (math.sin(self.pulse_time) + 1) * 0.1  # 0 to 0.2 range for subtle effect
        
        # Get card color based on state
        if self.disabled:
            bg_color = self.disabled_color
            border_color = (80, 80, 100)
        elif self.selected:
            bg_color = self.selected_color
            border_color = (180, 180, 255)
        elif self.hovered:
            bg_color = self.hover_color
            border_color = (150, 150, 230)
        else:
            bg_color = self.bg_color
            border_color = self.border_color
        
        # Draw card background
        pygame.draw.rect(screen, bg_color, draw_rect)
        
        # Draw tower icon
        self.draw_tower_icon(screen, draw_rect)
        
        # Draw title
        title_color = self.disabled_text_color if self.disabled else self.text_color
        title_surface = self.title_font.render(self.tower_type, True, title_color)
        title_rect = title_surface.get_rect(
            centerx=draw_rect.centerx,
            y=draw_rect.top + int(self.size[1] * 0.25)
        )
        screen.blit(title_surface, title_rect)
        
        # Draw resources - simple vertical list
        self.draw_vertical_resources(screen, draw_rect, resource_manager)
        
        # Draw border
        border_width = 2 + int(pulse * 3)  # Thicker border when hovered
        pygame.draw.rect(screen, border_color, draw_rect, border_width)
        
        # Check if player has enough resources and indicate with colored outline
        has_resources = self.check_resources(resource_manager)
        indicator_color = (0, 255, 0) if has_resources else (255, 0, 0)
        indicator_rect = draw_rect.copy()
        indicator_rect.inflate_ip(4, 4)
        pygame.draw.rect(screen, indicator_color, indicator_rect, 2)
    
    def draw_tower_icon(self, screen, draw_rect):
        """
        Draw tower icon on card
        
        Args:
            screen: Pygame surface to draw on
            draw_rect: Rectangle with current drawing position
        """
        # Adjust icon position based on current draw_rect
        icon_pos = (draw_rect.left + draw_rect.width//2 - self.icon_size[0]//2, 
                    draw_rect.top + int(draw_rect.height * 0.12))
        icon_rect = pygame.Rect(icon_pos, self.icon_size)
        
        # Draw icon shape based on tower type
        if self.tower_type == "Archer":
            # Draw archer tower icon (rectangle with bow)
            pygame.draw.rect(screen, self.tower_color, icon_rect)
            # Draw simple bow
            bow_start = (icon_rect.left + icon_rect.width * 0.3, icon_rect.centery)
            bow_end = (icon_rect.right - icon_rect.width * 0.3, icon_rect.centery)
            pygame.draw.arc(screen, (200, 200, 200), 
                          (bow_start[0], bow_start[1] - icon_rect.height * 0.3, 
                           bow_end[0] - bow_start[0], icon_rect.height * 0.6), 
                          -math.pi/2, math.pi/2, 2)
            
        elif self.tower_type == "Sniper":
            # Draw sniper tower icon (taller rectangle with scope)
            sniper_rect = icon_rect.copy()
            sniper_rect.height += 5
            sniper_rect.y -= 5
            pygame.draw.rect(screen, self.tower_color, sniper_rect)
            # Draw scope
            scope_radius = int(icon_rect.width * 0.2)
            pygame.draw.circle(screen, (200, 200, 200), 
                             (icon_rect.centerx, icon_rect.top + int(icon_rect.height * 0.3)), 
                             scope_radius)
            
        elif self.tower_type == "Splash":
            # Draw splash tower icon (rectangle with explosion)
            pygame.draw.rect(screen, self.tower_color, icon_rect)
            # Draw explosion
            explosion_points = [
                (icon_rect.centerx, icon_rect.top + int(icon_rect.height * 0.3)),
                (icon_rect.centerx + int(icon_rect.width * 0.25), icon_rect.centery),
                (icon_rect.centerx, icon_rect.bottom - int(icon_rect.height * 0.3)),
                (icon_rect.centerx - int(icon_rect.width * 0.25), icon_rect.centery)
            ]
            pygame.draw.polygon(screen, (255, 150, 50), explosion_points)
            
        elif self.tower_type == "Frozen":
            # Draw frozen tower icon (rectangle with snowflake)
            pygame.draw.rect(screen, self.tower_color, icon_rect)
            # Draw snowflake
            center = (icon_rect.centerx, icon_rect.centery)
            radius = int(icon_rect.width * 0.3)
            for i in range(3):
                angle = i * math.pi / 3
                start_x = center[0] + radius * math.cos(angle)
                start_y = center[1] + radius * math.sin(angle)
                end_x = center[0] + radius * math.cos(angle + math.pi)
                end_y = center[1] + radius * math.sin(angle + math.pi)
                pygame.draw.line(screen, (200, 200, 255), (start_x, start_y), (end_x, end_y), 2)
        else:
            # Default tower icon (simple rectangle)
            pygame.draw.rect(screen, self.tower_color, icon_rect)
    
    def draw_vertical_resources(self, screen, draw_rect, resource_manager):
        """
        Draw resource costs in a simple vertical list
        
        Args:
            screen: Pygame surface to draw on
            draw_rect: Rectangle with current drawing position
            resource_manager: ResourceManager to check resource availability
        """
        # If no resource manager, display simple placeholder
        if not resource_manager:
            text_surface = self.cost_font.render("Resources Required", True, (200, 200, 200))
            text_rect = text_surface.get_rect(centerx=draw_rect.centerx, 
                                            y=draw_rect.top + self.cost_area_y)
            screen.blit(text_surface, text_rect)
            return
        
        # Get icon manager if available from registry
        icon_manager = None
        if self.registry and self.registry.has(ICON_MANAGER):
            icon_manager = self.registry.get(ICON_MANAGER)
            
        # Prepare all costs to display
        all_costs = {}
        
        # Add Monster Coins cost
        if self.monster_coin_cost > 0:
            all_costs["Monster Coins"] = self.monster_coin_cost
        
        # Add standard resources
        for resource_type, amount in self.tower_cost.items():
            all_costs[resource_type] = amount
        
        # Get sorted resources
        sorted_resources = ResourceFormatter.sort_resources(all_costs)
        
        # Draw resources in a vertical list
        margin = scale_value(5)
        y = draw_rect.top + self.cost_area_y
        
        # Draw "Cost:" header
        cost_label = self.cost_font.render("Cost:", True, (200, 200, 200))
        cost_rect = cost_label.get_rect(centerx=draw_rect.centerx, y=y)
        screen.blit(cost_label, cost_rect)
        y += cost_rect.height + scale_value(2)

        # Calculate available width for resource display
        available_width = draw_rect.width - margin * 2

        # Draw each resource on a separate line with color and icon
        for resource_type, amount in sorted_resources:
            # Check if player has enough of this resource
            has_resource = resource_manager.get_resource(resource_type) >= amount
            
            # Create surface with icon and text (don't show resource name, just amount)
            resource_surface, width, height = ResourceFormatter.render_resource_with_icon(
                self.cost_font, 
                resource_type, 
                amount, 
                self.registry, 
                self.resource_icon_size,
                has_resource,
                show_name=False
            )
            
            # Center the resource display
            surface_x = draw_rect.centerx - width // 2
            surface_y = y
            
            # Draw the resource display
            screen.blit(resource_surface, (surface_x, surface_y))
            
            # Move to next line
            y += self.resource_line_height
    
    def check_resources(self, resource_manager):
        """
        Check if player has enough resources to build this tower
        
        Args:
            resource_manager: ResourceManager to check resource availability
            
        Returns:
            True if player has enough resources, False otherwise
        """
        if not resource_manager:
            return True  # Default to true if no resource manager provided
            
        # Check standard resources
        for resource_type, amount in self.tower_cost.items():
            if resource_manager.get_resource(resource_type) < amount:
                return False
        
        # Check Monster Coins
        if resource_manager.get_resource("Monster Coins") < self.monster_coin_cost:
            return False
            
        return True