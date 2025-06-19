# states/playing_state.py
"""
Playing state for Castle Defense - handles main gameplay
"""
import pygame
from .game_state import GameState
# Import the building classes directly - Mine is now only in village
from features.buildings import Coresmith, CastleUpgradeStation

class PlayingState(GameState):
    """
    Main gameplay state where the player defends the castle
    """
    def __init__(self, game):
        """
        Initialize playing state
        
        Args:
            game: Game instance
        """
        super().__init__(game)
        # Store references to commonly used components for cleaner code
        self.castle = self.game.castle
        self.wave_manager = self.game.wave_manager
        self.resource_manager = self.game.resource_manager
        self.animation_manager = self.game.animation_manager
        self.buildings = self.game.buildings
        self.towers = self.game.towers
        
        # Registry reference
        self.registry = game.registry if hasattr(game, 'registry') else None
        
        # Track if game is paused
        self.paused = False
        
        # Create village button
        button_size = game.scale_size((120, 40))
        button_pos = (game.WINDOW_WIDTH - button_size[0] - 10, game.WINDOW_HEIGHT - button_size[1] - 10)  # Bottom-right corner
        self.village_button_rect = pygame.Rect(
            button_pos[0], 
            button_pos[1], 
            button_size[0], 
            button_size[1]
        )
        self.village_button_color = (70, 120, 70)
        self.village_button_hover_color = (90, 150, 90)
        self.village_button_is_hovered = False
    
    def handle_events(self, events):
        """
        Handle gameplay events
        
        Args:
            events: List of pygame events
            
        Returns:
            Boolean indicating if events were handled
        """
        # Note: UI events are now handled in the game class first
        # through the GameUIContainer, so only game-specific events
        # are handled here
        
        for event in events:
            # Track mouse position for button hover
            if event.type == pygame.MOUSEMOTION:
                self.village_button_is_hovered = self.village_button_rect.collidepoint(event.pos)
                
            # Space to start next wave
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.wave_manager.start_next_wave()
                # Escape to pause
                elif event.key == pygame.K_ESCAPE:
                    self.game.state_manager.change_state("paused")
                    # Update the UI play/pause button state
                    if hasattr(self.game, 'game_ui') and hasattr(self.game.game_ui, 'controls_ui'):
                        self.game.game_ui.controls_ui.is_paused = True
                        self.game.game_ui.controls_ui.play_pause_button.text = "▶"  # Play icon
                    return True
            
            # Check for building and tower clicks
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                
                # Check if tower placement UI is clicked
                if self.game.tower_placement_ui.handle_event(event):
                    # Tower placement UI handled the event
                    continue
                
                # Check if village button was clicked
                if self.village_button_rect.collidepoint(mouse_pos):
                    self.game.enter_village()
                    return True
                
                # Check if clicking on a building
                building_clicked = False
                for building in self.buildings:
                    if building.rect.collidepoint(mouse_pos):
                        # Deselect previous entity
                        if self.game.selected_entity and hasattr(self.game.selected_entity, 'selected'):
                            self.game.selected_entity.selected = False
                            
                        self.game.selected_entity = building
                        # Use the imported class types directly for instanceof checks
                        if isinstance(building, Coresmith):
                            self.game.building_menu.set_building(building, "coresmith", self.resource_manager)
                            self.game.building_menu.toggle()
                        elif isinstance(building, CastleUpgradeStation):
                            # Open the castle menu for the upgrade station
                            self.game.castle_menu.set_castle(self.castle, self.resource_manager)
                            self.game.castle_menu.toggle()
                        building_clicked = True
                        break
                
                if not building_clicked:
                    # Check if clicking on a tower
                    tower_clicked = False
                    for tower in self.towers:
                        if tower.rect.collidepoint(mouse_pos):
                            # Deselect previous entity
                            if self.game.selected_entity and hasattr(self.game.selected_entity, 'selected'):
                                self.game.selected_entity.selected = False
                            
                            self.game.selected_entity = tower
                            tower.selected = True  # Set selected flag for range display
                            self.game.tower_menu.set_tower(tower, self.resource_manager)
                            self.game.tower_menu.toggle()
                            tower_clicked = True
                            break
                    
                    if not tower_clicked:
                        # Check for deselection
                        if self.game.selected_entity and hasattr(self.game.selected_entity, 'selected'):
                            self.game.selected_entity.selected = False
                            self.game.selected_entity = None
                            
                        # Handle menu clicks
                        self.game.building_menu.handle_event(event)
                        self.game.tower_menu.handle_event(event)
                        self.game.castle_menu.handle_event(event)
        
        return False
    
    def update(self, dt):
        """
        Update gameplay logic
        
        Args:
            dt: Time delta in seconds
        """
        # Update animation manager
        self.animation_manager.update(dt)
        
        # Update castle
        self.castle.update(dt)
        
        # Get the raw (unscaled) dt for buildings to maintain consistent production
        raw_dt = dt / self.game.time_scale if self.game.time_scale > 0 else dt
        
        # Update buildings - use raw_dt for consistent production regardless of game speed
        # Also pass the pause state
        for building in self.buildings:
            building.update(dt, self.resource_manager, raw_dt, self.paused)
        
        # Update wave manager and monsters
        self.wave_manager.update(dt, self.castle, self.animation_manager)
        
        # Update towers
        for tower in self.towers:
            tower.update(dt, self.wave_manager.active_monsters, self.animation_manager)
        
        # Check for auto-save
        self.game.save_manager.check_autosave()
        
        # Check for game over
        if self.castle.health <= 0:
            self.game.state_manager.change_state("game_over")
        
        # Continuous wave mode (from developer menu)
        if hasattr(self.wave_manager, 'continuous_wave') and self.wave_manager.continuous_wave:
            if self.wave_manager.wave_completed and not self.wave_manager.wave_active:
                self.wave_manager.start_next_wave()
    
    def draw(self, screen):
        """
        Draw gameplay elements to screen
        
        Args:
            screen: Pygame surface to draw on
        """
        # Clear screen with background color
        screen.fill(self.game.BACKGROUND_COLOR)
        
        # Draw castle first (as the base area)
        self.castle.draw(screen)
        
        # Draw buildings
        for building in self.buildings:
            building.draw(screen)
        
        # Draw towers
        for tower in self.towers:
            tower.draw(screen)
        
        # Draw monsters
        self.wave_manager.draw(screen)
        
        # Draw animations (particles, effects)
        self.animation_manager.draw(screen)
        
        # Draw tower placement UI
        self.game.tower_placement_ui.draw(self.resource_manager)
        
        # Draw menus
        self.game.building_menu.draw()
        self.game.tower_menu.draw()
        self.game.castle_menu.draw()
        
        # Debug visualization for monsters (helps identify invisible ones)
        # Toggled via developer menu
        if self.game.monster_debug and self.wave_manager.active_monsters:
            # Draw a marker for all active monsters
            font = pygame.font.Font(None, self.game.scale_value(14))
            for i, monster in enumerate(self.wave_manager.active_monsters):
                # Draw a bright magenta circle at monster's position
                pygame.draw.circle(screen, (255, 0, 255), 
                                  (int(monster.position[0]), int(monster.position[1])), 
                                  self.game.scale_value(8), 2)
                
                # Draw monster info (index, type, health)
                info_text = f"M{i}: {monster.monster_type} H:{int(monster.health)}"
                text_surface = font.render(info_text, True, (255, 255, 0))
                screen.blit(text_surface, (int(monster.position[0]) + 10, int(monster.position[1]) - 10))
                
                # Draw additional position info
                pos_text = f"Pos: ({int(monster.position[0])}, {int(monster.position[1])})"
                pos_surface = font.render(pos_text, True, (255, 255, 0))
                screen.blit(pos_surface, (int(monster.position[0]) + 10, int(monster.position[1]) + 5))
            
            # Draw wave info at the top of the screen
            wave_info = f"Wave: {self.wave_manager.current_wave} | Active Monsters: {len(self.wave_manager.active_monsters)} | To Spawn: {self.wave_manager.monsters_to_spawn}"
            info_surface = font.render(wave_info, True, (255, 255, 0))
            screen.blit(info_surface, (10, 10))
        
        # Draw game speed indicator if not at normal speed
        if self.game.time_scale != 1.0:
            font = pygame.font.Font(None, self.game.scale_value(24))
            speed_text = f"Game Speed: {self.game.time_scale:.1f}x"
            speed_color = (255, 200, 100) if self.game.time_scale > 1.0 else (100, 200, 255)
            speed_surface = font.render(speed_text, True, speed_color)
            speed_rect = speed_surface.get_rect(topright=(self.game.WINDOW_WIDTH - 20, 20))
            screen.blit(speed_surface, speed_rect)
        
        # Draw village button
        color = self.village_button_hover_color if self.village_button_is_hovered else self.village_button_color
        pygame.draw.rect(screen, color, self.village_button_rect)
        pygame.draw.rect(screen, (150, 200, 150), self.village_button_rect, 2)  # Border
        
        # Draw button text
        font = pygame.font.Font(None, self.game.scale_value(22))
        text = font.render("Village", True, (230, 230, 230))
        text_rect = text.get_rect(center=self.village_button_rect.center)
        screen.blit(text, text_rect)
        
        # Draw challenge mode indicator if active
        if self.wave_manager.challenge_mode:
            challenge_font = pygame.font.Font(None, self.game.scale_value(28))
            
            # Format text based on tier
            tier_colors = {
                "bronze": (180, 140, 80),
                "silver": (180, 180, 180),
                "gold": (220, 180, 50),
                "platinum": (150, 200, 220)
            }
            
            tier_color = tier_colors.get(self.wave_manager.challenge_tier, (200, 200, 200))
            
            # Create challenge info text
            challenge_text = f"{self.wave_manager.challenge_monster_type} {self.wave_manager.challenge_tier.capitalize()} Challenge"
            wave_progress = f"Wave {self.wave_manager.challenge_wave_count}/{self.wave_manager.challenge_total_waves}"
            
            # Draw background panel
            panel_width = self.game.scale_value(350)
            panel_height = self.game.scale_value(60)
            panel_rect = pygame.Rect(
                (self.game.WINDOW_WIDTH - panel_width) // 2,
                self.game.scale_value(20),
                panel_width,
                panel_height
            )
            
            # Semi-transparent dark background
            bg_surface = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
            bg_surface.fill((30, 30, 30, 180))
            screen.blit(bg_surface, panel_rect)
            
            # Draw border with tier color
            pygame.draw.rect(screen, tier_color, panel_rect, 2)
            
            # Draw challenge text
            challenge_surface = challenge_font.render(challenge_text, True, tier_color)
            challenge_rect = challenge_surface.get_rect(center=(panel_rect.centerx, panel_rect.top + self.game.scale_value(20)))
            screen.blit(challenge_surface, challenge_rect)
            
            # Draw wave progress
            progress_font = pygame.font.Font(None, self.game.scale_value(22))
            progress_surface = progress_font.render(wave_progress, True, (220, 220, 220))
            progress_rect = progress_surface.get_rect(center=(panel_rect.centerx, panel_rect.bottom - self.game.scale_value(15)))
            screen.blit(progress_surface, progress_rect)
