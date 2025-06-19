# ui/game_ui_container.py
"""
Main UI container for Castle Defense
Manages all UI components and their interactions
"""
import pygame
from ui.components.ui_component import UIComponent
from ui.components.game_status_ui import GameStatusUI
from ui.components.game_controls_ui import GameControlsUI
from ui.components.tower_selection_ui import TowerSelectionUI
from registry import RESOURCE_MANAGER, CASTLE, WAVE_MANAGER, STATE_MANAGER

class GameUIContainer:
    """Container for all UI components with state awareness"""
    
    def __init__(self, screen, registry=None):
        """
        Initialize UI container with components
        
        Args:
            screen: Pygame surface to draw on
            registry: Optional ComponentRegistry for accessing game components
        """
        self.screen = screen
        self.registry = registry
        self.components = []
        
        # Initialize components with registry
        self.status_ui = GameStatusUI(screen, registry)
        self.controls_ui = GameControlsUI(screen, registry)
        self.tower_selection_ui = TowerSelectionUI(screen, registry)
        
        # Add components to list
        self.components.append(self.status_ui)
        self.components.append(self.controls_ui)
        self.components.append(self.tower_selection_ui)
        
        # Track current game state
        self.current_state = None
        self.update_current_state()
    
    def update(self, dt):
        """
        Update all UI components that should be visible in current state
        
        Args:
            dt: Time delta in seconds
        """
        # Update current state info
        self.update_current_state()
        
        # Only update components that should be visible in current state
        for component in self.components:
            if self.should_component_be_active(component):
                component.update(dt)
    
    def draw(self):
        """Draw all UI components that should be visible in current state"""
        # Update current state info (in case it changed)
        self.update_current_state()
        
        # Only draw components that should be visible in current state
        for component in self.components:
            if self.should_component_be_visible(component):
                component.draw()
    
    def handle_event(self, event):
        """
        Handle events for all UI components that should be active in current state
        
        Args:
            event: Pygame event
            
        Returns:
            True if event was handled, False otherwise
        """
        # Update current state info (in case it changed)
        self.update_current_state()
        
        # Only handle events in components that should be active in current state
        for component in self.components:
            if self.should_component_be_active(component):
                if component.handle_event(event):
                    return True
        
        return False
    
    def update_current_state(self):
        """Update current state information from registry"""
        if not self.registry:
            return
            
        try:
            # Get current state from state manager
            state_manager = self.registry.get(STATE_MANAGER)
            if state_manager and state_manager.current_state:
                self.current_state = state_manager.current_state.__class__.__name__
        except (KeyError, AttributeError):
            pass
    
    def should_component_be_visible(self, component):
        """
        Check if component should be visible in current state
        
        Args:
            component: UI component to check
            
        Returns:
            True if component should be visible, False otherwise
        """
        # If no state info available, show everything
        if not self.current_state:
            return True
        
        # Handle GameStatusUI (resources, castle health, wave info)
        if isinstance(component, GameStatusUI):
            # Show in gameplay states, but in village only show resources (not castle health/wave info)
            if self.current_state == "VillageState":
                # Only update/draw the resources section, not castle health or wave info
                component.show_castle_info = False
                component.show_wave_info = False
                return True
            else:
                # Reset to show everything in other states
                component.show_castle_info = True
                component.show_wave_info = True
                return self.current_state in ["PlayingState", "PausedState", "TowerPlacementState", "VillageState"]
        
        # Handle GameControlsUI (play/pause, game speed)
        elif isinstance(component, GameControlsUI):
            # Only show in gameplay states, not menu or game over, not in village
            return self.current_state in ["PlayingState", "PausedState"]
        
        # Handle TowerSelectionUI (tower buttons)
        elif isinstance(component, TowerSelectionUI):
            # Only show in active gameplay, not paused, menu or game over, not in village
            return self.current_state in ["PlayingState"]
        
        # Default to visible
        return True
    
    def should_component_be_active(self, component):
        """
        Check if component should receive updates and handle events
        
        Args:
            component: UI component to check
            
        Returns:
            True if component should be active, False otherwise
        """
        # Components that aren't visible shouldn't be active
        if not self.should_component_be_visible(component):
            return False
        
        # Additional active/inactive logic
        if isinstance(component, TowerSelectionUI):
            # Tower selection should be inactive when placing a tower
            return self.current_state != "TowerPlacementState"
        
        # By default, visible components are active
        return True
    
    def is_paused(self):
        """
        Check if the game is currently paused
        
        Returns:
            True if paused, False otherwise
        """
        return self.current_state == "PausedState"
