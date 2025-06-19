# states/village_state.py
"""
Village state for Castle Defense
"""
import pygame
from .game_state import GameState
from utils import scale_position, scale_value, scale_size
from features.village.village import Village
from features.village.building_factory import VillageBuildingFactory
from config import VILLAGE_BUILDING_COSTS
from registry import RESOURCE_MANAGER, STATE_MANAGER, CASTLE
from ui.talent_tree_ui import TalentTreeUI

class VillageState(GameState):
    """
    State for village management and interaction
    """
    def __init__(self, game):
        """
        Initialize village state
        
        Args:
            game: Game instance
        """
        super().__init__(game)
        self.background_color = (10, 40, 10)  # Darker green background for village
        
        # Create the village if it doesn't exist
        if not hasattr(game, 'village') or game.village is None:
            # Position village at the center of the screen, not relative to castle
            screen_center = (game.WINDOW_WIDTH // 2, game.WINDOW_HEIGHT // 2)
            game.village = Village(
                game.registry,
                screen_center
            )
            
            # Auto-build Storage Barn when the village is first created
            self.auto_build_storage_barn()
        
        # Create a return button to go back to playing state
        button_size = scale_size((120, 40))
        button_pos = (10, 10)  # Top-left corner
        self.return_button_rect = pygame.Rect(
            button_pos[0], 
            button_pos[1], 
            button_size[0], 
            button_size[1]
        )
        self.return_button_color = (80, 80, 120)
        self.return_button_hover_color = (100, 100, 150)
        self.return_button_is_hovered = False
        
        # Create talent tree UI (lazily initialized when needed)
        self.talent_tree_ui = None
        self.current_town_hall = None
    
    def auto_build_storage_barn(self):
        """
        Automatically build the Storage Barn when the village is created
        """
        # Find and build the Storage Barn, Mine, Coresmith, and MonsterCodex plots
        free_buildings = ["StorageBarn", "Mine", "Coresmith", "MonsterCodex"]
        
        for building_type in free_buildings:
            # Find the plot
            plot = None
            for p in self.game.village.plots:
                if p["building_type"] == building_type:
                    plot = p
                    break
            
            # If we found the plot and it's not occupied, build the building
            if plot and not plot["occupied"]:
                # Create the building
                building = VillageBuildingFactory.create_building(
                    building_type,
                    plot["rect"].center,
                    self.game.registry
                )
                
                # Add it to the village
                self.game.village.add_building(building)
                
                # Mark plot as occupied
                plot["occupied"] = True
                plot["building"] = building
                
                # Print message with additional information for Monster Codex
                if building_type == "MonsterCodex":
                    print(f"{building_type} automatically built in the village - Monster tracking ready!")
                    # Verify that the Monster Codex is properly initialized
                    if hasattr(building, 'monster_data'):
                        print(f"Monster Codex initialized with {len(building.monster_data)} existing entries")
                else:
                    print(f"{building_type} automatically built in the village")
    
    def handle_events(self, events):
        """
        Handle all pygame events
        
        Args:
            events: List of pygame events
        """
        # If talent tree UI is visible, let it handle events first
        if self.talent_tree_ui and self.talent_tree_ui.visible:
            for event in events:
                if self.talent_tree_ui.handle_event(event):
                    return True
            return False
        
        # Normal event handling
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = pygame.mouse.get_pos()
                
                # Check if return button was clicked
                if self.return_button_rect.collidepoint(mouse_pos):
                    # Return to playing state
                    self.game.state_manager.change_state("playing")
                    return True
                
                # Check if any village plots or buildings were clicked
                if self.game.village.handle_click(mouse_pos):
                    # Check for specific building types that open new states
                    selected_building = None
                    for building in self.game.village.buildings:
                        if hasattr(building, 'is_selected') and building.is_selected:
                            selected_building = building
                            break
                    
                    if selected_building:
                        # Open monster codex when Monster Codex building is selected
                        if selected_building.__class__.__name__ == "MonsterCodex":
                            self.open_monster_codex(selected_building)
                            
                        # Open research lab when Research Lab building is selected
                        elif selected_building.__class__.__name__ == "ResearchLab":
                            self.open_research_lab(selected_building)
                    
                    return True
            
            # Check for button hover state
            elif event.type == pygame.MOUSEMOTION:
                mouse_pos = pygame.mouse.get_pos()
                self.return_button_is_hovered = self.return_button_rect.collidepoint(mouse_pos)
                
                # Update plot hover states
                self.game.village.update_plot_hover(mouse_pos)
        
        return False
    
    def update(self, dt):
        """
        Update village state
        
        Args:
            dt: Time delta in seconds
        """
        # Update the village
        self.game.village.update(dt)
        
        # Update talent tree UI if visible
        if self.talent_tree_ui:
            self.talent_tree_ui.update(dt)
    
    def draw(self, screen):
        """
        Draw village state
        
        Args:
            screen: Pygame surface to draw on
        """
        # Clear the screen with background color
        screen.fill(self.background_color)
        
        # Draw the village
        self.game.village.draw(screen)
        
        # Draw return button
        color = self.return_button_hover_color if self.return_button_is_hovered else self.return_button_color
        pygame.draw.rect(screen, color, self.return_button_rect)
        pygame.draw.rect(screen, (200, 200, 220), self.return_button_rect, 2)  # Border
        
        # Draw button text
        font_size = scale_value(20)
        font = pygame.font.Font(None, font_size)
        text = font.render("Return to Castle", True, (255, 255, 255))
        text_rect = text.get_rect(center=self.return_button_rect.center)
        screen.blit(text, text_rect)
        
        # Draw talent tree UI on top if visible
        if self.talent_tree_ui:
            self.talent_tree_ui.draw()
    
    def open_talent_tree(self, town_hall):
        """
        Open the talent tree UI for a town hall
        
        Args:
            town_hall: TownHall instance to show talents for
        """
        # Lazy initialization of talent tree UI
        if not self.talent_tree_ui or self.current_town_hall != town_hall:
            self.talent_tree_ui = TalentTreeUI(self.game.screen, town_hall, self.game.registry)
            self.current_town_hall = town_hall
        
        # Show the UI
        self.talent_tree_ui.toggle()
    

    def enter(self):
        """Called when entering the state"""
        # Nothing special needed here since the village is already created in __init__
        # and attached to the game instance as self.game.village
        pass
    
    def open_monster_codex(self, monster_codex):
        """
        Open the monster codex state
        
        Args:
            monster_codex: MonsterCodex building instance
        """
        # Deselect the building
        monster_codex.is_selected = False
        
        # Switch to monster codex state
        self.game.state_manager.change_state("monster_codex")
    
    def open_research_lab(self, research_lab):
        """
        Open the research lab state
        
        Args:
            research_lab: ResearchLab building instance
        """
        # Deselect the building
        research_lab.is_selected = False
        
        # Switch to research lab state
        self.game.state_manager.change_state("research_lab")
