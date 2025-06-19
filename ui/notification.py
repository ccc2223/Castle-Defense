# ui/notification.py
"""
Notification system for displaying temporary messages in Castle Defense
"""
import pygame
from utils import scale_value

class Notification:
    """Temporary on-screen notification message"""
    def __init__(self, text, duration=3.0, color=(220, 220, 180), position=None, size=None):
        """
        Initialize notification
        
        Args:
            text: Notification text
            duration: Display duration in seconds
            color: Text color
            position: Optional position override (centered by default)
            size: Optional font size override
        """
        self.text = text
        self.duration = duration
        self.color = color
        self.position = position
        self.remaining_time = duration
        self.font_size = size if size else scale_value(24)
        self.opacity = 255  # Start fully visible
        
        # Calculate dimensions
        self.font = pygame.font.Font(None, self.font_size)
        self.text_surface = self.font.render(text, True, color)
        self.text_rect = self.text_surface.get_rect()
        
        # Default position is center top
        if position is None:
            # We'll set the actual position when drawn
            self.position = (0, 0)
        else:
            self.text_rect.center = position
    
    def update(self, dt):
        """
        Update notification state
        
        Args:
            dt: Time delta in seconds
            
        Returns:
            True if notification is still active, False if expired
        """
        self.remaining_time -= dt
        
        # Fade out in the last second
        if self.remaining_time < 1.0:
            self.opacity = int(255 * self.remaining_time)
        
        return self.remaining_time > 0
    
    def draw(self, screen):
        """
        Draw notification to screen
        
        Args:
            screen: Pygame surface to draw on
        """
        if self.opacity <= 0:
            return
            
        # If position not set, center horizontally at the top
        if self.text_rect.centerx == 0:
            self.text_rect.centerx = screen.get_width() // 2
            self.text_rect.top = scale_value(100)
        
        # Create a copy with adjusted alpha
        if self.opacity < 255:
            alpha_surface = pygame.Surface(self.text_surface.get_size(), pygame.SRCALPHA)
            alpha_surface.fill((255, 255, 255, self.opacity))
            text_copy = self.text_surface.copy()
            text_copy.blit(alpha_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            screen.blit(text_copy, self.text_rect)
        else:
            screen.blit(self.text_surface, self.text_rect)

class NotificationManager:
    """Manages multiple notifications"""
    def __init__(self):
        """Initialize notification manager"""
        self.notifications = []
        self.max_notifications = 5  # Maximum number of notifications to show at once
        
    def add_notification(self, text, duration=3.0, color=(220, 220, 180), position=None, size=None):
        """
        Add a new notification
        
        Args:
            text: Notification text
            duration: Display duration in seconds
            color: Text color
            position: Optional position override (centered by default)
            size: Optional font size override
        """
        # Create new notification
        notification = Notification(text, duration, color, position, size)
        
        # Add to notifications list
        self.notifications.append(notification)
        
        # Remove oldest if we have too many
        if len(self.notifications) > self.max_notifications:
            self.notifications.pop(0)
    
    def update(self, dt):
        """
        Update all notifications
        
        Args:
            dt: Time delta in seconds
        """
        # Update notifications and remove expired ones
        self.notifications = [n for n in self.notifications if n.update(dt)]
        
        # Adjust positions to avoid overlap
        self.arrange_notifications()
    
    def draw(self, screen):
        """
        Draw all notifications
        
        Args:
            screen: Pygame surface to draw on
        """
        for notification in self.notifications:
            notification.draw(screen)
    
    def arrange_notifications(self):
        """Arrange notifications to prevent overlap"""
        # If no notifications, nothing to do
        if not self.notifications:
            return
        
        # Calculate vertical spacing
        spacing = scale_value(40)
        initial_y = scale_value(100)
        
        # Set positions for each notification
        for i, notification in enumerate(self.notifications):
            notification.text_rect.top = initial_y + i * spacing
