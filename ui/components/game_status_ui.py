# ui/components/game_status_ui.py
"""
Game status UI component for Castle Defense
Displays resources, castle health, and wave information
"""
import pygame
import math
from .ui_component import UIComponent
from ui.utils import ResourceFormatter
from registry import RESOURCE_MANAGER, CASTLE, WAVE_MANAGER, ICON_MANAGER
from config import WINDOW_WIDTH, WINDOW_HEIGHT

class GameStatusUI(UIComponent):
    """UI component for displaying game status information"""
    
    def __init__(self, screen, registry=None):
        """
        Initialize game status UI
        
        Args:
            screen: Pygame surface to draw on
            registry: Optional ComponentRegistry for accessing game components
        """
        super().__init__(screen, registry)
        
        # Initialize fonts
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 20)
        self.title_font = pygame.font.Font(None, 28)
        
        # Create background rectangle for resources panel
        self.resource_bg_rect = pygame.Rect(WINDOW_WIDTH - 320, 10, 310, 200)
        
        # Animation timers
        self.wave_pulse_time = 0
        
        # Flags to control what information is shown
        self.show_castle_info = True
        self.show_wave_info = True
    
    def update(self, dt):
        """
        Update UI animations
        
        Args:
            dt: Time delta in seconds
        """
        if not self.active:
            return
            
        # Update wave pulse animation
        self.wave_pulse_time += dt
    
    def draw(self):
        """Draw game status UI elements"""
        if not self.visible:
            return
            
        if not self.registry:
            return
            
        try:
            # Get required components from registry
            resource_manager = self.registry.get(RESOURCE_MANAGER)
            
            # Draw resources
            self.draw_resources(resource_manager)
            
            # Draw castle health if enabled
            if self.show_castle_info:
                castle = self.registry.get(CASTLE)
                self.draw_castle_health(castle)
            
            # Draw wave info if enabled
            if self.show_wave_info:
                wave_manager = self.registry.get(WAVE_MANAGER)
                self.draw_wave_info(wave_manager)
                
                # Draw next wave prompt if applicable
                if wave_manager.wave_completed and not self.is_game_paused():
                    self.draw_next_wave_prompt()
                
        except (KeyError, AttributeError) as e:
            # Print for debugging
            print(f"Error drawing game status: {e}")
    
    def draw_resources(self, resource_manager):
        """
        Draw resource display in the top right corner
        
        Args:
            resource_manager: ResourceManager with resource data
        """
        # Create semi-transparent background for resources panel
        bg_surface = pygame.Surface((self.resource_bg_rect.width, self.resource_bg_rect.height), pygame.SRCALPHA)
        bg_surface.fill((20, 20, 50, 180))  # Dark blue with transparency
        self.screen.blit(bg_surface, self.resource_bg_rect)
        
        # Draw panel border
        pygame.draw.rect(self.screen, (100, 100, 200), self.resource_bg_rect, 2)
        
        # Draw "Resources" header
        header = self.title_font.render("Resources", True, (220, 220, 255))
        header_rect = header.get_rect(midtop=(self.resource_bg_rect.centerx, self.resource_bg_rect.top + 10))
        self.screen.blit(header, header_rect)
        
        # Position for the first resource entry
        x = self.resource_bg_rect.right - 20
        y = self.resource_bg_rect.top + 40
        
        # Get icon manager if available
        icon_manager = None
        if self.registry.has(ICON_MANAGER):
            icon_manager = self.registry.get(ICON_MANAGER)
        
        # Categorize resources
        common_resources = ["Stone", "Iron", "Copper", "Thorium", "Monster Coins"]
        special_resources = ["Force Core", "Spirit Core", "Magic Core", "Void Core"]
        item_resources = ["Unstoppable Force", "Serene Spirit"]
        
        # Display common resources first
        y = self.draw_resource_category(resource_manager, common_resources, x, y, "Materials:", icon_manager)
        
        # Display special resources (cores) if any exist
        has_cores = any(resource_manager.get_resource(core) > 0 for core in special_resources)
        if has_cores:
            y += 10  # Add spacing between categories
            y = self.draw_resource_category(resource_manager, special_resources, x, y, "Cores:", icon_manager)
        
        # Display crafted items if any exist
        has_items = any(resource_manager.get_resource(item) > 0 for item in item_resources)
        if has_items:
            y += 10  # Add spacing between categories
            y = self.draw_resource_category(resource_manager, item_resources, x, y, "Items:", icon_manager)
    
    def draw_resource_category(self, resource_manager, resources, x, y, category_name, icon_manager=None):
        """
        Draw a category of resources with icons
        
        Args:
            resource_manager: ResourceManager with resource data
            resources: List of resource types to display
            x: X coordinate for right alignment
            y: Y coordinate for top alignment
            category_name: Name of the resource category
            icon_manager: Optional IconManager for resource icons
            
        Returns:
            Updated y position after drawing resources
        """
        # Draw category header
        category_text = self.small_font.render(category_name, True, (200, 200, 255))
        category_rect = category_text.get_rect(topright=(x, y))
        self.screen.blit(category_text, category_rect)
        y += 20
        
        # Define icon size
        icon_size = (24, 24)
        spacing = 5  # Space between icon and text
        
        # Draw each resource in the category
        for resource_type in resources:
            amount = resource_manager.get_resource(resource_type)
            if amount > 0 or resource_type in ["Stone", "Monster Coins"]:
                # Draw icon if icon manager is available
                if icon_manager:
                    # Get the corresponding icon ID
                    icon_id = icon_manager.get_resource_icon_id(resource_type)
                    
                    # Get the icon
                    icon = icon_manager.get_icon(icon_id, icon_size)
                    
                    # Position icon (right-aligned, with space for the text)
                    icon_rect = icon.get_rect(right=(x - 50), centery=y + icon_size[1]//2)
                    self.screen.blit(icon, icon_rect)
                
                # Draw resource name and amount right-aligned with appropriate color
                resource_color = ResourceFormatter.get_resource_color(resource_type)
                # Brighten color slightly for better visibility as text
                text_color = tuple(min(255, c + 40) for c in resource_color)
                
                # Only show the amount, not the resource name (since we have icons)
                text = f"{amount}"
                surface = self.font.render(text, True, text_color)
                text_rect = surface.get_rect(right=x, centery=y + icon_size[1]//2)
                self.screen.blit(surface, text_rect)
                
                y += 30  # More spacing with icons
        
        return y
    
    def draw_castle_health(self, castle):
        """
        Draw castle health display
        
        Args:
            castle: Castle instance with health data
        """
        # Draw health bar
        bar_width = 200
        bar_height = 20
        x = WINDOW_WIDTH // 2 - bar_width // 2
        y = WINDOW_HEIGHT - 30
        
        # Background
        pygame.draw.rect(self.screen, (100, 0, 0), (x, y, bar_width, bar_height))
        
        # Health
        health_percent = castle.health / castle.max_health
        pygame.draw.rect(self.screen, (0, 200, 0), 
                         (x, y, int(bar_width * health_percent), bar_height))
        
        # Border
        pygame.draw.rect(self.screen, (255, 255, 255), (x, y, bar_width, bar_height), 1)
        
        # Text
        text = f"Castle: {int(castle.health)}/{int(castle.max_health)}"
        surface = self.font.render(text, True, (255, 255, 255))
        text_rect = surface.get_rect(center=(WINDOW_WIDTH // 2, y - 15))
        self.screen.blit(surface, text_rect)
        
        # Additional castle stats
        stats_text = f"Damage Reduction: {int(castle.damage_reduction * 100)}%  Regen: {castle.health_regen:.1f}/s"
        stats_surface = self.small_font.render(stats_text, True, (200, 200, 200))
        stats_rect = stats_surface.get_rect(center=(WINDOW_WIDTH // 2, y - 35))
        self.screen.blit(stats_surface, stats_rect)
        
        # Add castle menu hint - now pointing to the Castle Upgrade Station
        hint_text = "Visit Castle Upgrade Station to improve defenses"
        hint_surface = self.small_font.render(hint_text, True, (255, 255, 200))
        hint_rect = hint_surface.get_rect(center=(WINDOW_WIDTH // 2, y - 55))
        self.screen.blit(hint_surface, hint_rect)
    
    def draw_wave_info(self, wave_manager):
        """
        Draw wave information in the top center
        
        Args:
            wave_manager: WaveManager with wave data
        """
        # Create wave info container
        wave_info_width = 200
        wave_info_bg = pygame.Rect(
            WINDOW_WIDTH // 2 - wave_info_width // 2, 
            10, 
            wave_info_width, 
            100 if (wave_manager.current_wave + 1) % 10 == 0 else 70
        )
        
        # Draw semi-transparent background
        bg_surface = pygame.Surface((wave_info_bg.width, wave_info_bg.height), pygame.SRCALPHA)
        bg_surface.fill((50, 20, 20, 180))  # Dark red with transparency
        self.screen.blit(bg_surface, wave_info_bg)
        
        # Draw border
        pygame.draw.rect(self.screen, (200, 100, 100), wave_info_bg, 2)
        
        # Wave number - centered at top
        text = f"Wave: {wave_manager.current_wave}"
        surface = self.title_font.render(text, True, (255, 255, 255))
        text_rect = surface.get_rect(midtop=(wave_info_bg.centerx, wave_info_bg.top + 10))
        self.screen.blit(surface, text_rect)
        
        # Monsters remaining - below wave number
        text = f"Monsters: {len(wave_manager.active_monsters)}"
        surface = self.font.render(text, True, (255, 255, 255))
        text_rect = surface.get_rect(midtop=(wave_info_bg.centerx, wave_info_bg.top + 40))
        self.screen.blit(surface, text_rect)
        
        # Next wave is boss wave indicator - below monsters
        if (wave_manager.current_wave + 1) % 10 == 0:
            text = "BOSS WAVE NEXT!"
            surface = self.font.render(text, True, (255, 100, 100))
            text_rect = surface.get_rect(midtop=(wave_info_bg.centerx, wave_info_bg.top + 70))
            self.screen.blit(surface, text_rect)
    
    def draw_next_wave_prompt(self):
        """Draw prompt to start next wave"""
        # Create a pulsing effect for the prompt
        pulse = (math.sin(self.wave_pulse_time * 5) + 1) / 2  # 0 to 1 over 0.4 seconds
        text_color = (int(255 * (0.7 + 0.3 * pulse)), int(255 * (0.7 + 0.3 * pulse)), 0)
        
        text = "Press SPACE to start next wave"
        surface = self.font.render(text, True, text_color)
        text_rect = surface.get_rect(center=(WINDOW_WIDTH // 2, 150))
        
        # Add a background to make text more visible
        bg_rect = text_rect.inflate(20, 10)
        bg_surface = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
        bg_surface.fill((0, 0, 0, 150))  # Semi-transparent black
        self.screen.blit(bg_surface, bg_rect)
        
        # Draw text
        self.screen.blit(surface, text_rect)
    
    def is_game_paused(self):
        """Check if game is currently paused"""
        try:
            # Try to get state manager from registry
            if self.registry and self.registry.has("state_manager"):
                state_manager = self.registry.get("state_manager")
                # Check if current state is paused
                return state_manager.current_state.__class__.__name__ == "PausedState"
        except (KeyError, AttributeError):
            pass
        
        return False
