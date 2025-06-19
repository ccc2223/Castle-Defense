# states/tower_placement_state.py
"""
Tower placement state for Castle Defense
"""
import pygame
import math
from .game_state import GameState

class TowerPlacementState(GameState):
    """
    State for placing towers on the game map
    """
    def __init__(self, game):
        """
        Initialize tower placement state
        
        Args:
            game: Game instance
        """
        super().__init__(game)
        self.tower_type = None
    
    def enter(self):
        """
        Called when entering tower placement state
        """
        # Tower type will be set by the method that triggers state change
        self.tower_type = None
    
    def exit(self):
        """
        Called when exiting tower placement state
        """
        # Clear the tower preview when exiting
        if hasattr(self.game, 'tower_placement_ui'):
            self.game.tower_placement_ui.clear_preview()
        self.tower_type = None
    
    def set_tower_type(self, tower_type):
        """
        Set the type of tower to place
        
        Args:
            tower_type: String tower type (e.g., "Archer", "Sniper")
        """
        self.tower_type = tower_type
        
        # Set the tower type in the tower placement UI
        if hasattr(self.game, 'tower_placement_ui'):
            self.game.tower_placement_ui.set_tower_type(tower_type)
    
    def handle_events(self, events):
        """
        Handle events during tower placement
        
        Args:
            events: List of pygame events
            
        Returns:
            Boolean indicating if events were handled
        """
        for event in events:
            # Handle cancel with escape key
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    # Cancel tower placement
                    self.game.state_manager.change_state("playing")
                    return True
            
            # Let tower placement UI handle mouse events
            if hasattr(self.game, 'tower_placement_ui'):
                if self.game.tower_placement_ui.handle_event(event):
                    return True
                    
            # Handle right-click cancel
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
                # Cancel tower placement
                self.game.state_manager.change_state("playing")
                return True
        
        return False
    
    def update(self, dt):
        """
        Update tower placement logic
        
        Args:
            dt: Time delta in seconds
        """
        # Tower placement UI handles most of the logic, nothing to update here
        pass
    
    def draw(self, screen):
        """
        Draw the game with tower placement overlay
        
        Args:
            screen: Pygame surface to draw on
        """
        # First draw the base game (playing state)
        # This keeps the background, castle, existing towers, etc.
        if "playing" in self.game.states:
            self.game.states["playing"].draw(screen)
            
        # Tower placement UI will draw the tower preview on top
        # The UI components will be drawn by the game class
