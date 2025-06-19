# ui/components/ui_component.py
"""
Base class for UI components in Castle Defense
"""
from abc import ABC, abstractmethod

class UIComponent(ABC):
    """
    Abstract base class for all UI components.
    Provides a standard interface for update, draw, and event handling.
    """
    def __init__(self, screen, registry=None):
        """
        Initialize UI component
        
        Args:
            screen: Pygame surface to draw on
            registry: Optional ComponentRegistry for accessing game components
        """
        self.screen = screen
        self.registry = registry
        self.visible = True
        self.active = True
    
    @abstractmethod
    def update(self, dt):
        """
        Update component state
        
        Args:
            dt: Time delta in seconds
        """
        pass
    
    @abstractmethod
    def draw(self):
        """
        Draw component to screen
        """
        if not self.visible:
            return
    
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
        return False
    
    def set_visible(self, visible):
        """
        Set component visibility
        
        Args:
            visible: Boolean visibility state
        """
        self.visible = visible
    
    def set_active(self, active):
        """
        Set component active state (for event handling)
        
        Args:
            active: Boolean active state
        """
        self.active = active
