"""
Resource formatter utility for Castle Defense
Provides consistent formatting and styling for resource display across UI
"""
import pygame
from registry import ICON_MANAGER

# Standardized resource colors (matching the existing color scheme)
RESOURCE_COLORS = {
    "Stone": (128, 128, 128),          # Gray
    "Iron": (176, 196, 222),           # Light steel blue
    "Copper": (184, 115, 51),          # Copper
    "Thorium": (75, 0, 130),           # Indigo
    "Monster Coins": (212, 175, 55),   # Gold
    "Force Core": (255, 0, 0),         # Red
    "Spirit Core": (0, 206, 209),      # Turquoise
    "Magic Core": (138, 43, 226),      # Blue violet
    "Void Core": (25, 25, 25),         # Very dark gray
    "Unstoppable Force": (255, 69, 0), # Red-orange
    "Serene Spirit": (50, 205, 50),    # Lime green
    "Multitudation Vortex": (150, 100, 255)  # Purple
}

# Standard order for resource display
RESOURCE_DISPLAY_ORDER = [
    "Monster Coins", 
    "Stone", 
    "Iron", 
    "Copper", 
    "Thorium",
    "Force Core",
    "Spirit Core",
    "Magic Core",
    "Void Core",
    "Unstoppable Force",
    "Serene Spirit",
    "Multitudation Vortex"
]

class ResourceFormatter:
    """Utility class for consistent resource formatting across UI"""
    
    @staticmethod
    def get_resource_color(resource_type):
        """
        Get standardized color for a resource type
        
        Args:
            resource_type: Resource name
            
        Returns:
            RGB color tuple
        """
        return RESOURCE_COLORS.get(resource_type, (200, 200, 200))  # Default to light gray
    
    @staticmethod
    def format_cost(resource_cost, separator=", "):
        """
        Format a dictionary of resource costs into a consistent string
        Uses "Resource: Amount" format
        
        Args:
            resource_cost: Dictionary mapping resource type to amount
            separator: String to use between resource entries
            
        Returns:
            Formatted cost string
        """
        if not resource_cost:
            return "Free"
            
        # Sort resources according to standard order
        sorted_resources = []
        
        for resource in RESOURCE_DISPLAY_ORDER:
            if resource in resource_cost:
                sorted_resources.append(f"{resource}: {resource_cost[resource]}")
        
        # Add any resources not in the standard order
        for resource, amount in resource_cost.items():
            if resource not in RESOURCE_DISPLAY_ORDER:
                sorted_resources.append(f"{resource}: {amount}")
        
        return separator.join(sorted_resources)
    
    @staticmethod
    def render_resource_text(font, resource_type, amount, default_color=(255, 255, 255)):
        """
        Render resource text with appropriate color
        
        Args:
            font: Pygame font to use
            resource_type: Resource name
            amount: Amount of resource
            default_color: Default text color if not using resource colors
            
        Returns:
            Rendered pygame surface
        """
        color = ResourceFormatter.get_resource_color(resource_type)
        # Brighten color slightly for better visibility as text
        bright_color = tuple(min(255, c + 40) for c in color)
        return font.render(f"{resource_type}: {amount}", True, bright_color)
    
    @staticmethod
    def render_resource_with_icon(font, resource_type, amount, registry, icon_size=(16, 16), 
                                 has_resource=True, show_name=True):
        """
        Create a surface with resource icon and text
        
        Args:
            font: Pygame font to use
            resource_type: Resource name
            amount: Amount of resource
            registry: Component registry for accessing icon manager
            icon_size: Size tuple for the icon
            has_resource: Whether the player has enough of this resource
            show_name: Whether to show the resource name (or just amount)
            
        Returns:
            (surface, width, height) tuple
        """
        # Get icon manager from registry
        icon_manager = None
        if registry and registry.has(ICON_MANAGER):
            icon_manager = registry.get(ICON_MANAGER)
            
        # Determine text color based on availability
        text_color = (100, 255, 100) if has_resource else (255, 100, 100)
            
        # Create text surface
        if show_name:
            text = f"{resource_type}: {amount}"
        else:
            text = f"{amount}"
            
        text_surface = font.render(text, True, text_color)
        text_rect = text_surface.get_rect()
        
        # Calculate total width and height
        spacing = 5  # Space between icon and text
        total_width = icon_size[0] + spacing + text_rect.width
        total_height = max(icon_size[1], text_rect.height)
        
        # Create the surface
        surface = pygame.Surface((total_width, total_height), pygame.SRCALPHA)
        
        # Draw icon
        if icon_manager:
            icon_id = icon_manager.get_resource_icon_id(resource_type)
            icon = icon_manager.get_icon(icon_id, icon_size)
            icon_rect = icon.get_rect(midleft=(0, total_height // 2))
            surface.blit(icon, icon_rect)
        else:
            # Fallback - draw colored circle
            circle_radius = min(icon_size) // 2
            circle_center = (circle_radius, total_height // 2)
            circle_color = ResourceFormatter.get_resource_color(resource_type)
            pygame.draw.circle(surface, circle_color, circle_center, circle_radius)
            
        # Draw text
        text_pos = (icon_size[0] + spacing, (total_height - text_rect.height) // 2)
        surface.blit(text_surface, text_pos)
        
        return surface, total_width, total_height
    
    @staticmethod
    def sort_resources(resource_dict):
        """
        Sort resources according to standard order
        
        Args:
            resource_dict: Dictionary mapping resource types to amounts
            
        Returns:
            List of (resource_type, amount) tuples in standard order
        """
        sorted_resources = []
        
        # Add resources in standard order
        for resource in RESOURCE_DISPLAY_ORDER:
            if resource in resource_dict:
                sorted_resources.append((resource, resource_dict[resource]))
        
        # Add any resources not in the standard order
        for resource, amount in resource_dict.items():
            if resource not in RESOURCE_DISPLAY_ORDER:
                sorted_resources.append((resource, amount))
        
        return sorted_resources
