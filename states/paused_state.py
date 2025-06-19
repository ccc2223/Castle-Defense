# states/paused_state.py
"""
Paused state for Castle Defense
"""
import pygame
from .game_state import GameState
from registry import RESOURCE_MANAGER, SAVE_MANAGER
from ui.save_dialog import SaveDialog

class PausedState(GameState):
    """
    Paused game state - game is frozen but user can resume
    """
    def __init__(self, game):
        """
        Initialize paused state
        
        Args:
            game: Game instance
        """
        super().__init__(game)
        self.overlay_alpha = 180  # Semi-transparent overlay
        self.menu_options = [
            {
                "text": "Resume Game",
                "action": self.resume_game
            },
            {
                "text": "Save Game",
                "action": self.open_save_dialog
            },
            {
                "text": "Exit to Menu", 
                "action": self.exit_to_menu
            }
        ]
        self.selected_option = 0
        
        # Create save dialog
        self.save_dialog = SaveDialog(game.screen, game)
    
    def enter(self):
        """Called when entering paused state"""
        # Update the game UI play/pause button state via registry
        # Instead of directly accessing game_ui
        if hasattr(self.game, 'registry'):
            try:
                ui_container = self.game.registry.get("ui_container")
                if hasattr(ui_container, 'controls_ui'):
                    ui_container.controls_ui.is_paused = True
                    ui_container.controls_ui.play_pause_button.text = "▶"  # Play icon
            except (KeyError, AttributeError):
                pass
        
        # Set paused flag in playing state
        if hasattr(self.game.states["playing"], "paused"):
            self.game.states["playing"].paused = True
        
        # Make sure save dialog is inactive
        self.save_dialog.active = False
    
    def exit(self):
        """Called when exiting paused state"""
        # Update the game UI play/pause button state via registry
        if hasattr(self.game, 'registry'):
            try:
                ui_container = self.game.registry.get("ui_container")
                if hasattr(ui_container, 'controls_ui'):
                    ui_container.controls_ui.is_paused = False
                    ui_container.controls_ui.play_pause_button.text = "||"  # Pause icon
            except (KeyError, AttributeError):
                pass
        
        # Clear paused flag in playing state
        if hasattr(self.game.states["playing"], "paused"):
            self.game.states["playing"].paused = False
        
        # Make sure save dialog is inactive
        self.save_dialog.active = False
    
    def handle_events(self, events):
        """
        Handle events during paused state
        
        Args:
            events: List of pygame events
            
        Returns:
            Boolean indicating if events were handled
        """
        # Check if save dialog is active and handle its events first
        if self.save_dialog.active:
            for event in events:
                if self.save_dialog.handle_event(event):
                    return True
            return False
        
        # First check if play/pause button was clicked via GameUIContainer
        for event in events:
            if hasattr(self.game, 'game_ui') and self.game.game_ui.handle_event(event):
                return True
            
            # Also check if any UI components in registry handled the event
            elif hasattr(self.game, 'registry'):
                try:
                    ui_container = self.game.registry.get("ui_container")
                    if ui_container.handle_event(event):
                        return True
                except (KeyError, AttributeError):
                    pass
        
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    # Resume game on Escape
                    self.resume_game()
                    return True
                
                elif event.key == pygame.K_UP:
                    # Move selection up
                    self.selected_option = (self.selected_option - 1) % len(self.menu_options)
                    return True
                
                elif event.key == pygame.K_DOWN:
                    # Move selection down
                    self.selected_option = (self.selected_option + 1) % len(self.menu_options)
                    return True
                
                elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    # Activate selected option
                    option = self.menu_options[self.selected_option]
                    if option["action"]:
                        option["action"]()
                    return True
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    # Check if clicking on menu options
                    mouse_pos = pygame.mouse.get_pos()
                    for i, option in enumerate(self.menu_options):
                        option_rect = self.get_option_rect(i)
                        if option_rect.collidepoint(mouse_pos) and option["action"]:
                            option["action"]()
                            return True
        
        return False
    
    def update(self, dt):
        """
        Update paused state logic
        
        Args:
            dt: Time delta in seconds
        """
        # Update save dialog if active
        if self.save_dialog.active:
            self.save_dialog.update(dt)
        
        # Update UI components via registry
        if hasattr(self.game, 'registry'):
            try:
                ui_container = self.game.registry.get("ui_container")
                if ui_container:
                    ui_container.update(dt)
            except (KeyError, AttributeError):
                pass
        
        # Legacy UI update
        if hasattr(self.game, 'game_ui'):
            self.game.game_ui.update(dt)
    
    def draw(self, screen):
        """
        Draw paused state
        
        Args:
            screen: Pygame surface to draw on
        """
        # First draw the base game (frozen)
        self.game.states["playing"].draw(screen)
        
        # Draw semi-transparent overlay
        overlay = pygame.Surface((self.game.WINDOW_WIDTH, self.game.WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, self.overlay_alpha))
        screen.blit(overlay, (0, 0))
        
        # Draw UI components via registry
        if hasattr(self.game, 'registry'):
            try:
                ui_container = self.game.registry.get("ui_container")
                if ui_container:
                    ui_container.draw()
            except (KeyError, AttributeError):
                pass
                
        # Legacy UI drawing - only draw controls, not full UI
        elif hasattr(self.game, 'game_ui'):
            if hasattr(self.game.game_ui, 'play_pause_button'):
                self.game.game_ui.play_pause_button.draw(screen)
            
            if hasattr(self.game.game_ui, 'draw_game_speed_slider'):
                self.game.game_ui.draw_game_speed_slider()
        
        # Draw pause menu only if save dialog is not active
        if not self.save_dialog.active:
            self.draw_pause_menu(screen)
        else:
            # Draw save dialog on top
            self.save_dialog.draw()
    
    def draw_pause_menu(self, screen):
        """
        Draw the pause menu
        
        Args:
            screen: Pygame surface to draw on
        """
        # Draw background panel
        panel_width = self.game.scale_value(300)
        panel_height = self.game.scale_value(250)
        panel_rect = pygame.Rect(
            (self.game.WINDOW_WIDTH - panel_width) // 2,
            (self.game.WINDOW_HEIGHT - panel_height) // 2,
            panel_width,
            panel_height
        )
        
        # Draw panel with border
        pygame.draw.rect(screen, (40, 40, 60), panel_rect)
        pygame.draw.rect(screen, (100, 100, 150), panel_rect, self.game.scale_value(2))
        
        # Draw "PAUSED" text
        font_size = self.game.scale_value(36)
        font = pygame.font.Font(None, font_size)
        text = font.render("PAUSED", True, (255, 255, 255))
        text_rect = text.get_rect(midtop=(panel_rect.centerx, panel_rect.top + self.game.scale_value(20)))
        screen.blit(text, text_rect)
        
        # Draw menu options
        option_font_size = self.game.scale_value(24)
        option_font = pygame.font.Font(None, option_font_size)
        option_spacing = self.game.scale_value(40)
        
        for i, option in enumerate(self.menu_options):
            # Determine if this option is selected
            is_selected = (i == self.selected_option)
            
            # Set text color - brighter for selected option
            text_color = (255, 255, 100) if is_selected else (200, 200, 200)
            
            # Create text surface
            text = option_font.render(option["text"], True, text_color)
            
            # Position and draw text
            y_pos = panel_rect.top + self.game.scale_value(80) + i * option_spacing
            text_rect = text.get_rect(center=(panel_rect.centerx, y_pos))
            screen.blit(text, text_rect)
            
            # Draw selection indicator if this option is selected
            if is_selected:
                indicator_rect = text_rect.inflate(self.game.scale_value(20), self.game.scale_value(10))
                pygame.draw.rect(screen, (100, 100, 180), indicator_rect, self.game.scale_value(2))
    
    def get_option_rect(self, index):
        """
        Get the rect for a menu option
        
        Args:
            index: Index of the option
            
        Returns:
            Pygame Rect for the option
        """
        panel_width = self.game.scale_value(300)
        panel_rect_x = (self.game.WINDOW_WIDTH - panel_width) // 2
        panel_rect_y = (self.game.WINDOW_HEIGHT - self.game.scale_value(250)) // 2
        
        option_height = self.game.scale_value(30)
        option_width = self.game.scale_value(200)
        option_y = panel_rect_y + self.game.scale_value(80) + index * self.game.scale_value(40)
        
        return pygame.Rect(
            (self.game.WINDOW_WIDTH - option_width) // 2,
            option_y - option_height // 2,
            option_width,
            option_height
        )
    
    def resume_game(self):
        """Resume the game by changing back to playing state"""
        self.game.state_manager.change_state("playing")
    
    def open_save_dialog(self):
        """Open the save game dialog"""
        # Make sure dialog has updated default filename
        self.save_dialog.text_value = self.save_dialog.generate_default_filename()
        self.save_dialog.active = True
        self.save_dialog.text_field_active = True
    
    def exit_to_menu(self):
        """Exit to the main menu"""
        self.game.state_manager.change_state("main_menu")
        
        # Reset any necessary game state
        self.reset_game_for_menu()
    
    def reset_game_for_menu(self):
        """Reset necessary game state for return to main menu"""
        # Reset wave manager
        if hasattr(self.game, 'wave_manager'):
            self.game.wave_manager.active_monsters = []
            self.game.wave_manager.wave_active = False
            self.game.wave_manager.wave_completed = True
            self.game.wave_manager.monsters_to_spawn = 0
        
        # Reset castle health to full
        if hasattr(self.game, 'castle'):
            self.game.castle.health = self.game.castle.max_health
        
        # Clear the paused flag in playing state
        if hasattr(self.game.states["playing"], "paused"):
            self.game.states["playing"].paused = False
