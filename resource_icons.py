# resource_icons.py
"""
Resource icon manager that generates icons procedurally using Pygame
No external dependencies required!
"""
import pygame
import math

class ResourceIconManager:
    def __init__(self, svg_file_path=None):
        """
        Initialize resource icon manager with programmatically generated icons
        
        Args:
            svg_file_path: Ignored in this implementation, kept for API compatibility
        """
        self.cache = {}  # Cache rendered surfaces by name and size
        
        # Define colors for each resource type
        self.resource_colors = {
            "stone": (128, 128, 128),          # Gray
            "iron": (176, 196, 222),           # Light steel blue
            "copper": (184, 115, 51),          # Copper
            "thorium": (75, 0, 130),           # Indigo
            "monster-coin": (212, 175, 55),    # Gold
            "force-core": (255, 0, 0),         # Red
            "spirit-core": (0, 206, 209),      # Turquoise
            "magic-core": (138, 43, 226),      # Blue violet
            "void-core": (25, 25, 25),         # Very dark gray
            "unstoppable-force": (255, 69, 0), # Red-orange
            "serene-spirit": (50, 205, 50),    # Lime green
            "multitudation-vortex": (150, 100, 255)  # Purple
        }
        
        # Define shapes for each resource type
        self.resource_shapes = {
            "stone": self._draw_stone,
            "iron": self._draw_iron,
            "copper": self._draw_copper,
            "thorium": self._draw_thorium,
            "monster-coin": self._draw_monster_coin,
            "force-core": self._draw_force_core,
            "spirit-core": self._draw_spirit_core,
            "magic-core": self._draw_magic_core,
            "void-core": self._draw_void_core,
            "unstoppable-force": self._draw_unstoppable_force,
            "serene-spirit": self._draw_serene_spirit,
            "multitudation-vortex": self._draw_multitudation_vortex
        }
        
        print("Resource icons initialized with procedural generation")
    
    def get_icon(self, icon_name, size=(32, 32)):
        """
        Get a Pygame surface for the specified icon at the given size
        
        Args:
            icon_name: ID of the icon to render
            size: Tuple of (width, height) for the rendered icon
            
        Returns:
            Pygame Surface with the rendered icon
        """
        # Create cache key
        cache_key = f"{icon_name}_{size[0]}x{size[1]}"
        
        # Return cached surface if available
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        # Create a new surface for the icon
        surface = pygame.Surface(size, pygame.SRCALPHA)
        
        # Get the drawing function for this resource type
        draw_func = self.resource_shapes.get(icon_name, self._draw_default)
        
        # Get the color for this resource type
        color = self.resource_colors.get(icon_name, (255, 0, 255))
        
        # Draw the icon
        draw_func(surface, color, size)
        
        # Cache the surface
        self.cache[cache_key] = surface
        
        return surface
    
    def _draw_circle_icon(self, surface, color, size, inner_shape=None):
        """Base function to draw a circular icon with optional inner shape"""
        # Draw outer circle
        radius = min(size[0], size[1]) // 2 - 2
        center = (size[0] // 2, size[1] // 2)
        pygame.draw.circle(surface, color, center, radius)
        
        # Draw darker border
        border_color = tuple(max(0, c - 40) for c in color)
        pygame.draw.circle(surface, border_color, center, radius, 2)
        
        # If there's an inner shape function, call it
        if inner_shape:
            inner_shape(surface, color, size, center, radius)
    
    def _draw_default(self, surface, color, size):
        """Default icon for unknown resource types"""
        self._draw_circle_icon(surface, color, size)
        
        # Draw question mark
        font = pygame.font.Font(None, size[0] // 2)
        text = font.render("?", True, (255, 255, 255))
        text_rect = text.get_rect(center=(size[0] // 2, size[1] // 2))
        surface.blit(text, text_rect)
    
    def _draw_stone(self, surface, color, size):
        """Draw stone icon"""
        def inner_shape(surface, color, size, center, radius):
            # Draw a stone-like shape inside
            points = []
            for i in range(7):
                angle = 2 * math.pi * i / 7
                r = radius * (0.6 + 0.2 * (i % 3))
                x = center[0] + r * math.cos(angle)
                y = center[1] + r * math.sin(angle)
                points.append((x, y))
            
            # Draw the inner shape with a slightly lighter color
            inner_color = tuple(min(255, c + 30) for c in color)
            pygame.draw.polygon(surface, inner_color, points)
        
        self._draw_circle_icon(surface, color, size, inner_shape)
    
    def _draw_iron(self, surface, color, size):
        """Draw iron icon"""
        def inner_shape(surface, color, size, center, radius):
            # Draw an iron bar/ingot in the center
            inner_color = tuple(min(255, c + 30) for c in color)
            rect_size = (radius * 1.2, radius * 0.8)
            rect = pygame.Rect(
                center[0] - rect_size[0] // 2,
                center[1] - rect_size[1] // 2,
                rect_size[0],
                rect_size[1]
            )
            pygame.draw.rect(surface, inner_color, rect)
            pygame.draw.rect(surface, tuple(max(0, c - 40) for c in color), rect, 1)
        
        self._draw_circle_icon(surface, color, size, inner_shape)
    
    def _draw_copper(self, surface, color, size):
        """Draw copper icon"""
        def inner_shape(surface, color, size, center, radius):
            # Draw a hexagon for copper
            points = []
            for i in range(6):
                angle = 2 * math.pi * i / 6
                x = center[0] + radius * 0.7 * math.cos(angle)
                y = center[1] + radius * 0.7 * math.sin(angle)
                points.append((x, y))
            
            # Draw the hexagon with a slightly lighter color
            inner_color = tuple(min(255, c + 40) for c in color)
            pygame.draw.polygon(surface, inner_color, points)
            
            # Add a small circle in the center
            smaller_color = tuple(min(255, c + 60) for c in color)
            pygame.draw.circle(surface, smaller_color, center, radius // 4)
        
        self._draw_circle_icon(surface, color, size, inner_shape)
    
    def _draw_thorium(self, surface, color, size):
        """Draw thorium icon"""
        def inner_shape(surface, color, size, center, radius):
            # Draw a radiation-like symbol
            inner_color = tuple(min(255, c + 60) for c in color)
            
            # Draw three circles in a triangular pattern
            for i in range(3):
                angle = 2 * math.pi * i / 3
                offset = radius * 0.4
                x = center[0] + offset * math.cos(angle)
                y = center[1] + offset * math.sin(angle)
                pygame.draw.circle(surface, inner_color, (int(x), int(y)), radius // 5)
            
            # Draw center circle
            pygame.draw.circle(surface, inner_color, center, radius // 4)
        
        self._draw_circle_icon(surface, color, size, inner_shape)
    
    def _draw_monster_coin(self, surface, color, size):
        """Draw monster coin icon"""
        def inner_shape(surface, color, size, center, radius):
            # Draw a monster face silhouette
            inner_color = (139, 0, 0)  # Dark red for monster
            
            # Draw monster head outline
            head_rect = pygame.Rect(
                center[0] - radius // 2,
                center[1] - radius // 2,
                radius,
                radius
            )
            pygame.draw.ellipse(surface, inner_color, head_rect)
            
            # Draw monster eyes (white circles)
            eye_radius = radius // 6
            left_eye_pos = (center[0] - radius // 4, center[1] - radius // 6)
            right_eye_pos = (center[0] + radius // 4, center[1] - radius // 6)
            
            pygame.draw.circle(surface, (255, 255, 255), left_eye_pos, eye_radius)
            pygame.draw.circle(surface, (255, 255, 255), right_eye_pos, eye_radius)
        
        self._draw_circle_icon(surface, color, size, inner_shape)
    
    def _draw_force_core(self, surface, color, size):
        """Draw force core icon"""
        def inner_shape(surface, color, size, center, radius):
            # Draw an arrow pointing right
            inner_color = (255, 255, 255)  # White arrow
            
            # Create arrow points
            points = [
                (center[0] - radius // 2, center[1] - radius // 3),  # Top left
                (center[0] + radius // 2, center[1]),                # Right point
                (center[0] - radius // 2, center[1] + radius // 3)   # Bottom left
            ]
            
            pygame.draw.polygon(surface, inner_color, points)
        
        self._draw_circle_icon(surface, color, size, inner_shape)
    
    def _draw_spirit_core(self, surface, color, size):
        """Draw spirit core icon"""
        def inner_shape(surface, color, size, center, radius):
            # Draw a wispy, ethereal shape
            inner_color = (224, 255, 255)  # Light cyan
            
            # Draw a gentle curve
            curve_points = []
            for i in range(6):
                t = i / 5  # 0 to 1
                x = center[0] - radius // 2 + radius * t
                y = center[1] + radius // 3 * math.sin(t * math.pi)
                curve_points.append((x, y))
            
            # Draw smooth line through points
            if len(curve_points) > 1:
                pygame.draw.lines(surface, inner_color, False, curve_points, 3)
        
        self._draw_circle_icon(surface, color, size, inner_shape)
    
    def _draw_magic_core(self, surface, color, size):
        """Draw magic core icon"""
        def inner_shape(surface, color, size, center, radius):
            # Draw a star
            inner_color = (255, 215, 0)  # Gold
            
            # Create star points
            points = []
            for i in range(10):
                angle = math.pi/2 + 2 * math.pi * i / 10
                r = radius * (0.7 if i % 2 == 0 else 0.4)  # Alternate radius to create star points
                x = center[0] + r * math.cos(angle)
                y = center[1] + r * math.sin(angle)
                points.append((x, y))
            
            pygame.draw.polygon(surface, inner_color, points)
        
        self._draw_circle_icon(surface, color, size, inner_shape)
    
    def _draw_void_core(self, surface, color, size):
        """Draw void core icon"""
        def inner_shape(surface, color, size, center, radius):
            # Create a dark center with lighter edges
            
            # Draw outer swirl
            lighter_color = tuple(min(255, c + 120) for c in color)
            
            # Draw swirl using multiple arcs
            for i in range(4):
                arc_radius = radius * (0.8 - i * 0.15)
                start_angle = i * math.pi / 2
                end_angle = (i + 1) * math.pi / 2
                rect = pygame.Rect(
                    center[0] - arc_radius,
                    center[1] - arc_radius,
                    arc_radius * 2,
                    arc_radius * 2
                )
                pygame.draw.arc(surface, lighter_color, rect, start_angle, end_angle, 2)
            
            # Draw black hole center
            pygame.draw.circle(surface, color, center, radius // 3)
        
        self._draw_circle_icon(surface, color, size, inner_shape)
    
    def _draw_unstoppable_force(self, surface, color, size):
        """Draw unstoppable force icon"""
        def inner_shape(surface, color, size, center, radius):
            # Draw a shield or battering ram shape
            inner_color = (255, 255, 255)  # White
            
            # Draw a rounded shield
            shield_rect = pygame.Rect(
                center[0] - radius // 2,
                center[1] - radius // 2,
                radius,
                radius
            )
            pygame.draw.ellipse(surface, inner_color, shield_rect)
            
            # Add a horizontal line through the middle
            line_y = center[1]
            pygame.draw.line(
                surface,
                (255, 215, 0),  # Gold
                (center[0] - radius // 1.5, line_y),
                (center[0] + radius // 1.5, line_y),
                3
            )
        
        self._draw_circle_icon(surface, color, size, inner_shape)
    
    def _draw_serene_spirit(self, surface, color, size):
        """Draw serene spirit icon"""
        def inner_shape(surface, color, size, center, radius):
            # Draw a cross/plus symbol
            inner_color = (255, 255, 255)  # White
            
            # Vertical bar
            v_rect = pygame.Rect(
                center[0] - radius // 8,
                center[1] - radius // 2,
                radius // 4,
                radius
            )
            
            # Horizontal bar
            h_rect = pygame.Rect(
                center[0] - radius // 2,
                center[1] - radius // 8,
                radius,
                radius // 4
            )
            
            pygame.draw.rect(surface, inner_color, v_rect)
            pygame.draw.rect(surface, inner_color, h_rect)
        
        self._draw_circle_icon(surface, color, size, inner_shape)
    
    def _draw_multitudation_vortex(self, surface, color, size):
        """Draw multitudation vortex icon"""
        def inner_shape(surface, color, size, center, radius):
            # Draw a vortex/spiral pattern
            inner_color = (255, 255, 255)  # White spiral on purple background
            
            # Draw spiral using multiple arcs with increasing distance
            for i in range(4):
                arc_radius = radius * (0.7 - i * 0.1)
                start_angle = i * math.pi / 2
                end_angle = (i + 2) * math.pi / 2  # Longer arcs for overlap
                rect = pygame.Rect(
                    center[0] - arc_radius,
                    center[1] - arc_radius,
                    arc_radius * 2,
                    arc_radius * 2
                )
                pygame.draw.arc(surface, inner_color, rect, start_angle, end_angle, 3)
            
            # Draw multiple small circles to represent bouncing projectiles
            dot_color = (220, 220, 255)  # Light purple/white
            for i in range(3):
                angle = 2 * math.pi * i / 3 + math.pi/6
                dist = radius * 0.6
                x = center[0] + dist * math.cos(angle)
                y = center[1] + dist * math.sin(angle)
                pygame.draw.circle(surface, dot_color, (int(x), int(y)), radius // 7)
        
        self._draw_circle_icon(surface, color, size, inner_shape)
    
    def get_resource_icon_id(self, resource_type):
        """
        Convert a resource type name to the corresponding icon ID
        
        Args:
            resource_type: Resource name used in the game
            
        Returns:
            Icon ID as defined in the SVG file
        """
        # Map resource names to icon IDs
        mapping = {
            "Stone": "stone",
            "Iron": "iron",
            "Copper": "copper",
            "Thorium": "thorium",
            "Monster Coins": "monster-coin",
            "Force Core": "force-core",
            "Spirit Core": "spirit-core",
            "Magic Core": "magic-core",
            "Void Core": "void-core",
            "Unstoppable Force": "unstoppable-force",
            "Serene Spirit": "serene-spirit",
            "Multitudation Vortex": "multitudation-vortex"
        }
        
        # Return the mapped ID or a fallback conversion
        return mapping.get(resource_type, resource_type.lower().replace(' ', '-'))
