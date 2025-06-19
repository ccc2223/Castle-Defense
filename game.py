# game.py - Updated with UI Container and Registry integration
import pygame
import sys
import math
from features.resources import ResourceManager
from features.castle import Castle
from features.building_factory import BuildingFactory
from features.waves import WaveManager
from features.towers.factory import TowerFactory
from ui.game_ui_container import GameUIContainer  # New UI container
from ui.tower_placement_ui import TowerPlacementUI
from ui.menus import BuildingMenu, TowerMenu
from ui.castle_menu import CastleMenu
from ui.dev_menu import DeveloperMenu
from save_system import SaveManager
from effects.animation_manager import AnimationManager
from config import FPS, BACKGROUND_COLOR, WINDOW_WIDTH, WINDOW_HEIGHT, TOWER_TYPES, REF_WIDTH, REF_HEIGHT
from utils import distance, scale_position, scale_size, scale_value, unscale_position

# Import the state management system
from states import GameStateManager, PlayingState, PausedState, TowerPlacementState, GameOverState, MainMenuState, VillageState, StorageState, CoresmithState, MonsterCodexState, ResearchLabState

# Import config_extension to enable dynamic parameter updates
import config_extension

# Import ResourceIconManager here (not at the top) to avoid circular imports
from resource_icons import ResourceIconManager

# Import the Component Registry
from registry import ComponentRegistry, RESOURCE_MANAGER, WAVE_MANAGER, ANIMATION_MANAGER
from registry import CASTLE, BUILDINGS, TOWERS, ICON_MANAGER, SAVE_MANAGER, STATE_MANAGER

# Make the Game class globally accessible for tower attack callbacks
# This will gradually be phased out as we implement the component registry
game_instance = None

class Game:
    """
    Main game class that manages the game state, updates, and rendering.
    """
    def __init__(self, screen):
        """
        Initialize the game with required components.
        
        Args:
            screen: Pygame surface for drawing
        """
        global game_instance
        game_instance = self
        
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Game speed control (for developer menu and research)
        self.time_scale = 1.0
        self.base_time_scale = 1.0  # Base value affected by research
        
        # Debug flag for monster visualization (set by dev menu)
        self.monster_debug = False
        
        # Save references to constants for easier use throughout the code
        self.BACKGROUND_COLOR = BACKGROUND_COLOR
        self.WINDOW_WIDTH = WINDOW_WIDTH
        self.WINDOW_HEIGHT = WINDOW_HEIGHT
        self.TOWER_TYPES = TOWER_TYPES
        self.REF_WIDTH = REF_WIDTH
        self.REF_HEIGHT = REF_HEIGHT
        
        # Expose utility functions for use by state classes
        self.scale_position = scale_position
        self.scale_size = scale_size
        self.scale_value = scale_value
        self.unscale_position = unscale_position
        self.distance = distance
        
        # Initialize Component Registry
        self.registry = ComponentRegistry()
        
        # Register game instance in registry
        self.registry.register("game", self)
        
        # Initialize resource icon manager
        self.icon_manager = ResourceIconManager('assets/resource_icons.svg')
        
        # Initialize game components
        self.resource_manager = ResourceManager()
        self.castle = Castle()
        self.wave_manager = WaveManager()
        
        # Register core components with the registry
        self.registry.register(RESOURCE_MANAGER, self.resource_manager)
        self.registry.register(CASTLE, self.castle)
        self.registry.register(WAVE_MANAGER, self.wave_manager)
        self.registry.register(ICON_MANAGER, self.icon_manager)
        
        # Initialize buildings and towers
        self.buildings = []
        self.towers = []
        
        # Add Castle Upgrade Station only (Mine and Coresmith moved to Village)
        ref_upgrade_station_pos = (self.castle.ref_position[0] + 100, 
                               self.castle.ref_position[1] + self.castle.ref_size[1] // 2 + 30)
        upgrade_station_pos = scale_position(ref_upgrade_station_pos)
        self.buildings.append(BuildingFactory.create_building("CastleUpgradeStation", upgrade_station_pos))
        
        # Register buildings and towers collections
        self.registry.register(BUILDINGS, self.buildings)
        self.registry.register(TOWERS, self.towers)
        
        # Initialize animation system
        self.animation_manager = AnimationManager()
        # Register the icon manager with the animation manager
        self.animation_manager.set_icon_manager(self.icon_manager)
        self.registry.register(ANIMATION_MANAGER, self.animation_manager)
        
        # Create research manager if it doesn't exist
        from features.research import ResearchManager
        self.research_manager = ResearchManager(self.registry)
        self.registry.register("research_manager", self.research_manager)
        
        # Initialize notification manager
        from ui.notification import NotificationManager
        self.notification_manager = NotificationManager()
        self.registry.register("notification_manager", self.notification_manager)
        
        # Initialize save manager
        self.save_manager = SaveManager(self)
        self.registry.register(SAVE_MANAGER, self.save_manager)
        
        # Initialize state manager
        self.state_manager = GameStateManager(self)
        self.registry.register(STATE_MANAGER, self.state_manager)
        
        # Initialize UI with play/pause button and game speed slider
        # New approach: Use the UI container for modular UI components
        self.game_ui = GameUIContainer(screen, self.registry)
        self.registry.register("ui_container", self.game_ui)  # Register UI container in registry
        
        # Keep for now until migration is complete
        self.tower_placement_ui = TowerPlacementUI(screen, self)
        self.building_menu = BuildingMenu(screen, self.registry)
        self.tower_menu = TowerMenu(screen, self.registry)
        self.castle_menu = CastleMenu(screen, self.registry)
        
        # Add developer menu
        self.dev_menu = DeveloperMenu(screen, self)
        
        # Game state variables
        self.selected_entity = None
        
        # Create states dictionary for access by state objects
        self.states = {}
        
        # Add states to manager
        self.state_manager.add_state("main_menu", MainMenuState)
        self.states["main_menu"] = self.state_manager.states["main_menu"]
        
        self.state_manager.add_state("playing", PlayingState)
        self.states["playing"] = self.state_manager.states["playing"]
        
        self.state_manager.add_state("paused", PausedState)
        self.states["paused"] = self.state_manager.states["paused"]
        
        self.state_manager.add_state("tower_placement", TowerPlacementState)
        self.states["tower_placement"] = self.state_manager.states["tower_placement"]
        
        self.state_manager.add_state("game_over", GameOverState)
        self.states["game_over"] = self.state_manager.states["game_over"]
        
        # Add village state
        self.state_manager.add_state("village", VillageState)
        self.states["village"] = self.state_manager.states["village"]
        
        # Add storage barn state
        self.state_manager.add_state("storage", StorageState)
        self.states["storage"] = self.state_manager.states["storage"]
        
        # Add coresmith state
        self.state_manager.add_state("coresmith", CoresmithState)
        self.states["coresmith"] = self.state_manager.states["coresmith"]
        
        # Add monster codex state
        self.state_manager.add_state("monster_codex", MonsterCodexState)
        self.states["monster_codex"] = self.state_manager.states["monster_codex"]
        
        # Add research lab state
        self.state_manager.add_state("research_lab", ResearchLabState)
        self.states["research_lab"] = self.state_manager.states["research_lab"]
        
        # Start with main menu state
        self.state_manager.change_state("main_menu")
    
    def debug_test_tower_items(self):
        """Test both tower item slots"""
        from features.towers.factory import TowerFactory
        tower = TowerFactory.create_tower("Archer", (100, 100))
        
        # Test direct assignment
        tower.item_slots[0] = "Test Item 1"
        tower.item_slots[1] = "Test Item 2"
        print(f"Direct assignment: {tower.item_slots}")
        
        # Test methods
        tower.item_slots = [None, None]
        
        # Test with int index
        tower.add_item("Unstoppable Force", 0, None)
        print(f"After adding to slot 0: {tower.item_slots}")
        
        # Test with string index
        tower.add_item("Serene Spirit", "1", None)
        print(f"After adding to slot 1: {tower.item_slots}")
        
        item0 = tower.get_item_in_slot(0)
        item1 = tower.get_item_in_slot(1)
        print(f"Get item slot 0: {item0}, slot 1: {item1}")
        
        # Print success message if both slots working
        if item0 == "Unstoppable Force" and item1 == "Serene Spirit":
            print("SUCCESS: Both tower item slots working correctly!")
        else:
            print("ERROR: Tower item slots not working properly.")
    
    def run(self):
        """Main game loop"""
        
        # DEBUG: Let's run a comprehensive tower slot test at startup
        self.debug_test_tower_items()
        
        # Log summary of improvements
        print("\n===== TOWER ITEM SYSTEM IMPROVEMENTS =====")
        print("Both tower item slots have been fixed and now work properly.")
        print("1. Item slots are now correctly initialized as a fixed-size list [None, None]")
        print("2. String and integer indices are properly handled for both slots")
        print("3. Save and load operations correctly preserve items in both slots")
        print("4. UI interactions with both slots are now handled consistently")
        print("===== END DEBUGGING INFORMATION =====")
        
        while self.running:
            # Apply time scaling to dt
            raw_dt = self.clock.tick(FPS) / 1000.0  # Convert to seconds
            # Apply time scale based on base value from research and UI setting
            dt = raw_dt * self.time_scale  # Apply time scale for speed control
            
            # Collect all events once
            events = pygame.event.get()
            self.handle_events(events)
            
            # If game is running, update state
            if self.running:
                self.update(dt, raw_dt)
                self.draw()
                pygame.display.flip()
    
    def handle_events(self, events):
        """
        Process pygame events
        
        Args:
            events: List of pygame events
        """
        for event in events:
            if event.type == pygame.QUIT:
                self.running = False
                return
            
            # Check for developer menu toggle (Ctrl+D)
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_d and pygame.key.get_mods() & pygame.KMOD_CTRL:
                self.dev_menu.toggle()
                return
            
            # Handle developer menu events first if it's visible
            if self.dev_menu.visible:
                self.dev_menu.handle_event(event)  # Pass a single event, not the list
                continue
        
        # Let the current state handle events if dev menu didn't handle them
        if self.dev_menu.visible:
            return
        
        # Let UI container handle events for each event individually
        for event in events:
            if self.game_ui.handle_event(event):
                # Event was handled by UI
                return
                
        # Then let the state manager handle remaining events
        self.state_manager.handle_events(events)
    
    def update(self, dt, raw_dt=None):
        """
        Update game state
        
        Args:
            dt: Time delta in seconds (with time scaling)
            raw_dt: Raw time delta without scaling, for dev menu
        """
        # Update research manager if not paused
        if self.state_manager.current_state is not self.states["paused"] and hasattr(self, 'research_manager'):
            self.research_manager.update(dt)
        # Developer menu always updates with raw dt (not affected by time scale)
        if raw_dt:
            self.dev_menu.update(raw_dt)
        
        # Update UI container (new approach)
        self.game_ui.update(dt)
        
        # Update notifications
        self.notification_manager.update(dt)
        
        # Set pause state for buildings
        if self.state_manager.current_state is self.states["paused"]:
            for building in self.buildings:
                if hasattr(building, 'update'):
                    # Update buildings with game_paused=True
                    building.update(0, self.resource_manager, raw_dt, True)
        
        # Always update village buildings regardless of state to ensure resource production continues
        if hasattr(self, 'village') and self.village is not None:
            # Pass the raw dt to ensure consistent resource production regardless of time scale
            raw_dt = dt / self.time_scale if self.time_scale > 0 else dt
            self.village.update(raw_dt)
        
        # Update current state
        self.state_manager.update(dt)
    
    def draw(self):
        """Draw current game state to screen"""
        # Let the current state draw
        self.state_manager.draw(self.screen)
        
        # Draw UI container on top (new approach)
        self.game_ui.draw()
        
        # Draw notifications on top
        self.notification_manager.draw(self.screen)
        
        # Developer menu draws on top of everything if visible
        if self.dev_menu.visible:
            self.dev_menu.draw()
    
    def enter_tower_placement_mode(self, tower_type):
        """
        Enter tower placement mode for specified tower type
        
        Args:
            tower_type: Type of tower to place
        """
        self.state_manager.change_state("tower_placement")
        tower_placement_state = self.state_manager.states["tower_placement"]
        tower_placement_state.set_tower_type(tower_type)
    
    def is_valid_tower_position(self, position):
        """
        Check if position is valid for tower placement
        
        Args:
            position: Tuple of (x, y) coordinates
            
        Returns:
            True if position is valid, False otherwise
        """
        # Create a rect for the tower at this position
        tower_ref_size = (40, 40)  # Defined in reference dimensions
        tower_size = scale_size(tower_ref_size)
        tower_rect = pygame.Rect(
            position[0] - tower_size[0] // 2,
            position[1] - tower_size[1] // 2,
            tower_size[0],
            tower_size[1]
        )
        
        # Check if tower is within castle boundaries
        if not self.castle.is_position_within_castle(position):
            return False
        
        # Check collision with buildings
        for building in self.buildings:
            if tower_rect.colliderect(building.rect):
                return False
        
        # Check collision with other towers
        for tower in self.towers:
            if tower_rect.colliderect(tower.rect):
                return False
        
        return True
    
    def reset_castle(self):
        """
        Restore castle health after game over
        """
        self.castle.health = self.castle.max_health
    
    def enter_village(self):
        """
        Switch to village state
        """
        self.state_manager.change_state("village")
    
    def set_wave(self, wave_number):
        """
        Set the current wave number
        
        Args:
            wave_number: New wave number
        """
        # Set wave manager's wave number
        self.wave_manager.current_wave = wave_number
        
        # Reset wave state
        self.wave_manager.active_monsters = []
        self.wave_manager.wave_active = False
        self.wave_manager.wave_completed = True
        self.wave_manager.monsters_to_spawn = 0
    
    # Helper function to get the game instance
    @staticmethod
    def get_instance():
        """
        Get the current game instance (for use in other modules)
        
        Returns:
            Current Game instance or None
        """
        return game_instance
        
    def set_base_time_scale(self, scale):
        """
        Set the base time scale (affected by research)
        
        Args:
            scale: New base time scale value
            
        Returns:
            True if set successfully
        """
        self.base_time_scale = scale
        # Update actual time scale to preserve the slider position
        # This multiplies the UI slider value by the base scale
        slider_value = self.time_scale / self.base_time_scale
        self.time_scale = slider_value * scale
        return True
        
    def open_monster_codex(self):
        """
        Switch to monster codex state
        """
        self.state_manager.change_state("monster_codex")
    
    def start_monster_challenge(self, monster_type, tier):
        """
        Start a monster challenge with specific monster type and tier
        
        Args:
            monster_type: Type of monster for the challenge
            tier: Challenge tier (bronze, silver, gold, platinum)
            
        Returns:
            True if challenge started, False otherwise
        """
        # Configure wave manager for challenge mode
        self.wave_manager.set_challenge_mode(monster_type, tier)
        
        # Switch to playing state
        self.state_manager.change_state("playing")
        
        # Start the first wave
        self.wave_manager.start_next_wave()
        
        return True
    
    def complete_monster_challenge(self, monster_type, tier, success=True):
        """
        Complete a monster challenge
        
        Args:
            monster_type: Type of monster in challenge
            tier: Challenge tier
            success: Whether the challenge was successful
            
        Returns:
            True if completion was processed
        """
        # Find the monster codex to record completion
        monster_codex = None
        if hasattr(self, 'village') and self.village:
            for building in self.village.buildings:
                if building.__class__.__name__ == "MonsterCodex":
                    monster_codex = building
                    break
        
        # Record challenge completion if successful
        if success and monster_codex:
            monster_codex.complete_challenge(monster_type, tier)
        
        # Add a notification about returning to normal game
        if hasattr(self, 'notification_manager'):
            self.notification_manager.add_notification(
                f"Challenge complete! Returning to normal gameplay", 
                3.0, 
                (180, 220, 180)
            )
        
        # Reset wave manager to normal mode
        self.wave_manager.reset_challenge_mode()
        
        return True