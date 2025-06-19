# ui/base_menu.py
"""
Base menu class for Castle Defense
"""
import pygame
from config import WINDOW_WIDTH, WINDOW_HEIGHT

class Menu:
    """Base class for all menus"""
    def __init__(self, screen):
        """
        Initialize menu
        
        Args:
            screen: Pygame surface to draw on
        """
        self.screen = screen
        self.active = False
        
        # Position all menus on the left side of the screen with a decent margin
        self.position = (60, 120)  # Moved further from left edge
        self.size = (320, 400)  # Default larger size
        self.rect = pygame.Rect(self.position, self.size)
        
        # Button storage
        self.buttons = []
        
        # Fonts
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 18)
        self.title = "Menu"
        
        # Common colors for styling
        self.HEADER_COLOR = (255, 200, 100)
        self.TEXT_COLOR = (220, 220, 220)
        self.SUBTEXT_COLOR = (180, 180, 180)
        self.BUTTON_COLOR = (80, 80, 80)
        self.BUTTON_HOVER_COLOR = (100, 100, 100)
        self.BUTTON_DISABLED_COLOR = (60, 60, 60)
        self.POSITIVE_COLOR = (100, 255, 100)
        self.NEGATIVE_COLOR = (255, 100, 100)
        self.CARD_BG_COLOR = (60, 60, 60)
        self.TAB_ACTIVE_COLOR = (70, 70, 70)
        self.TAB_INACTIVE_COLOR = (50, 50, 50)
        
        # Initialize scrolling
        self.init_scrolling()
        
        # Initialize tooltip
        self.init_tooltip()
    
    def init_scrolling(self):
        """Initialize scrolling support"""
        self.scroll_offset = 0
        self.max_scroll = 0
        self.scroll_speed = 15
        self.content_height = 0
    
    def init_tooltip(self):
        """Initialize tooltip support"""
        self.show_tooltip = False
        self.tooltip_text = ""
        self.tooltip_position = (0, 0)
    
    def toggle(self):
        """Toggle menu visibility"""
        self.active = not self.active
        
        # Reset scroll position when opening menu
        if self.active:
            self.scroll_offset = 0
    
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
        
        # Check if clicking outside menu to close it
        if event.type == pygame.MOUSEBUTTONDOWN:
            if not self.rect.collidepoint(event.pos):
                self.active = False
                return True
            
            # Check button clicks
            for button in self.buttons:
                button.update(event.pos)
                if button.rect.collidepoint(event.pos):
                    button.click()
                    return True
        
        # Handle scroll wheel for content scrolling
        elif event.type == pygame.MOUSEWHEEL:
            if self.rect.collidepoint(pygame.mouse.get_pos()):
                # Scroll up or down
                self.scroll_offset -= event.y * self.scroll_speed
                # Constrain scrolling
                self.scroll_offset = max(0, min(self.max_scroll, self.scroll_offset))
                return True
        
        # Update button hover states and tooltips
        elif event.type == pygame.MOUSEMOTION:
            # Reset tooltip
            self.show_tooltip = False
            
            # Update buttons
            for button in self.buttons:
                button.update(event.pos)
        
        return False
    
    def update_tooltip(self, rect, text, mouse_pos):
        """
        Update tooltip if mouse is over the given rect
        
        Args:
            rect: Rectangle to check for mouse hover
            text: Tooltip text to display
            mouse_pos: Current mouse position
        """
        if rect.collidepoint(mouse_pos):
            self.show_tooltip = True
            self.tooltip_text = text
            self.tooltip_position = (mouse_pos[0] + 15, mouse_pos[1] + 15)
    
    def draw_tooltip(self):
        """Draw tooltip at current mouse position"""
        if not self.show_tooltip:
            return
        
        # Split tooltip text into lines
        lines = self.tooltip_text.split("\n")
        
        # Calculate tooltip size
        line_height = self.small_font.get_height()
        tooltip_width = max(self.small_font.size(line)[0] for line in lines) + 20
        tooltip_height = len(lines) * line_height + 15
        
        # Create tooltip rectangle
        tooltip_rect = pygame.Rect(
            self.tooltip_position[0],
            self.tooltip_position[1],
            tooltip_width,
            tooltip_height
        )
        
        # Adjust if tooltip would go off screen
        if tooltip_rect.right > self.screen.get_width():
            tooltip_rect.right = self.tooltip_position[0] - 5
        if tooltip_rect.bottom > self.screen.get_height():
            tooltip_rect.bottom = self.tooltip_position[1] - 5
        
        # Draw tooltip background and border
        pygame.draw.rect(self.screen, (40, 40, 40), tooltip_rect)
        pygame.draw.rect(self.screen, (150, 150, 150), tooltip_rect, 1)
        
        # Draw each line of text
        for i, line in enumerate(lines):
            line_surface = self.small_font.render(line, True, self.TEXT_COLOR)
            line_pos = (tooltip_rect.left + 10, tooltip_rect.top + 8 + i * line_height)
            self.screen.blit(line_surface, line_pos)
    
    def draw_scroll_indicators(self, content_rect):
        """
        Draw scroll indicators if content is scrollable
        
        Args:
            content_rect: Rectangle defining the content area
        """
        # Draw up arrow if not at top
        if self.scroll_offset > 0:
            arrow_rect = pygame.Rect(
                content_rect.right - 25,
                content_rect.top + 5,
                20,
                20
            )
            pygame.draw.polygon(
                self.screen,
                (200, 200, 200),
                [
                    (arrow_rect.centerx, arrow_rect.top + 5),
                    (arrow_rect.left + 5, arrow_rect.bottom - 5),
                    (arrow_rect.right - 5, arrow_rect.bottom - 5)
                ]
            )
        
        # Draw down arrow if not at bottom
        if self.scroll_offset < self.max_scroll:
            arrow_rect = pygame.Rect(
                content_rect.right - 25,
                content_rect.bottom - 25,
                20,
                20
            )
            pygame.draw.polygon(
                self.screen,
                (200, 200, 200),
                [
                    (arrow_rect.centerx, arrow_rect.bottom - 5),
                    (arrow_rect.left + 5, arrow_rect.top + 5),
                    (arrow_rect.right - 5, arrow_rect.top + 5)
                ]
            )
    
    def draw_separator(self, y_position):
        """
        Draw a separator line
        
        Args:
            y_position: Y position for the line
        """
        pygame.draw.line(
            self.screen,
            (100, 100, 100),
            (self.rect.left + 15, y_position),
            (self.rect.right - 15, y_position),
            1
        )
    
    def draw_tab_buttons(self, tabs, current_tab, y_position=None):
        """
        Draw tab buttons
        
        Args:
            tabs: List of tab names
            current_tab: Currently selected tab
            y_position: Optional Y position (defaults to top of menu)
        """
        if y_position is None:
            y_position = self.rect.top + 30
            
        tab_width = self.rect.width / len(tabs)
        
        for i, tab in enumerate(tabs):
            tab_rect = pygame.Rect(
                self.rect.left + i * tab_width, 
                y_position, 
                tab_width, 
                30
            )
            
            # Draw tab background
            tab_color = self.TAB_ACTIVE_COLOR if tab == current_tab else self.TAB_INACTIVE_COLOR
            pygame.draw.rect(self.screen, tab_color, tab_rect)
            pygame.draw.rect(self.screen, (100, 100, 100), tab_rect, 1)
            
            # Draw tab text
            tab_text = self.small_font.render(tab, True, self.TEXT_COLOR)
            tab_text_rect = tab_text.get_rect(center=tab_rect.center)
            self.screen.blit(tab_text, tab_text_rect)
    
    def draw_card(self, rect, title=None, content=None, border_color=(100, 100, 100)):
        """
        Draw a card with optional title and content
        
        Args:
            rect: Rectangle for the card
            title: Optional title text
            content: Optional content text
            border_color: Color for card border
        """
        # Draw card background
        pygame.draw.rect(self.screen, self.CARD_BG_COLOR, rect)
        pygame.draw.rect(self.screen, border_color, rect, 1)
        
        y_pos = rect.top + 10
        
        # Draw title if provided
        if title:
            title_surface = self.small_font.render(title, True, self.TEXT_COLOR)
            self.screen.blit(title_surface, (rect.left + 10, y_pos))
            y_pos += 20
        
        # Draw content if provided
        if content:
            if isinstance(content, list):
                # Draw multiple lines
                for line in content:
                    line_surface = self.small_font.render(line, True, self.SUBTEXT_COLOR)
                    self.screen.blit(line_surface, (rect.left + 15, y_pos))
                    y_pos += 18
            else:
                # Draw single line
                content_surface = self.small_font.render(content, True, self.SUBTEXT_COLOR)
                self.screen.blit(content_surface, (rect.left + 15, y_pos))
    
    def draw(self):
        """Draw menu if active"""
        if not self.active:
            return
        
        # Draw menu background
        pygame.draw.rect(self.screen, (50, 50, 50), self.rect)
        pygame.draw.rect(self.screen, (200, 200, 200), self.rect, 2)
        
        # Draw title
        title_surface = self.font.render(self.title, True, (255, 255, 255))
        title_rect = title_surface.get_rect(center=(self.rect.centerx, self.rect.top + 20))
        self.screen.blit(title_surface, title_rect)
        
        # Draw buttons is now managed by individual menu subclasses
        # to account for scrolling and tabs
        
        # Draw tooltip if active
        if self.show_tooltip:
            self.draw_tooltip()
