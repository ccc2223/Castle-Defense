# states/monster_codex_state.py
"""
Monster Codex state for Castle Defense - handles monster database and challenges
"""
import pygame
from .game_state import GameState
from utils import scale_value, scale_position

class MonsterCodexState(GameState):
    """
    State for viewing monster information and starting challenges
    """
    def __init__(self, game):
        """
        Initialize monster codex state
        
        Args:
            game: Game instance
        """
        super().__init__(game)
        
        # Find the monster codex instance - it should be in the village
        self.monster_codex = None
        if hasattr(game, 'village') and game.village:
            for building in game.village.buildings:
                if building.__class__.__name__ == "MonsterCodex":
                    self.monster_codex = building
                    break
        
        # Set up UI elements
        self.setup_ui()
        
        # Currently selected monster type
        self.selected_monster = None
        
        # Challenge tier selection
        self.selected_challenge_tier = None
        
        # Scrolling offset for monster list
        self.scroll_offset = 0
        self.max_scroll = 0
        
        # Knowledge tier descriptions
        self.knowledge_tier_info = {
            1: "Basic information - monster type and appearance",
            2: "Combat data - health, damage, and speed values",
            3: "[Placeholder Tier 3 Information]",
            4: "[Placeholder Tier 4 Information]",
            5: "Master knowledge - complete monster database entry"
        }
        
    def setup_ui(self):
        """Set up UI elements for the monster codex"""
        self.screen_width = self.game.WINDOW_WIDTH
        self.screen_height = self.game.WINDOW_HEIGHT
        
        # Main panel
        panel_width = int(self.screen_width * 0.9)
        panel_height = int(self.screen_height * 0.85)
        self.main_panel = pygame.Rect(
            (self.screen_width - panel_width) // 2,
            (self.screen_height - panel_height) // 2,
            panel_width,
            panel_height
        )
        
        # Monster list panel (left side)
        list_width = int(panel_width * 0.3)
        self.monster_list_panel = pygame.Rect(
            self.main_panel.left,
            self.main_panel.top,
            list_width,
            panel_height
        )
        
        # Detail panel (right side)
        detail_width = panel_width - list_width
        self.detail_panel = pygame.Rect(
            self.main_panel.left + list_width,
            self.main_panel.top,
            detail_width,
            panel_height
        )
        
        # Challenge panel (bottom of detail panel)
        challenge_height = int(panel_height * 0.3)
        self.challenge_panel = pygame.Rect(
            self.detail_panel.left,
            self.detail_panel.bottom - challenge_height,
            detail_width,
            challenge_height
        )
        
        # Back button
        button_width = scale_value(120)
        button_height = scale_value(40)
        self.back_button = pygame.Rect(
            self.main_panel.right - button_width - scale_value(20),
            self.main_panel.bottom - button_height - scale_value(20),
            button_width,
            button_height
        )
        
        # Start challenge button
        self.start_challenge_button = pygame.Rect(
            self.challenge_panel.left + scale_value(20),
            self.challenge_panel.bottom - button_height - scale_value(20),
            button_width,
            button_height
        )
        
        # Challenge tier selection buttons
        self.challenge_tier_buttons = {}
        tiers = ["bronze", "silver", "gold", "platinum"]
        button_spacing = scale_value(10)
        tier_button_width = scale_value(100)
        
        for i, tier in enumerate(tiers):
            self.challenge_tier_buttons[tier] = pygame.Rect(
                self.challenge_panel.left + scale_value(20) + i * (tier_button_width + button_spacing),
                self.challenge_panel.top + scale_value(50),
                tier_button_width,
                scale_value(30)
            )
        
        # Scroll buttons for monster list
        self.scroll_up_button = pygame.Rect(
            self.monster_list_panel.right - scale_value(30),
            self.monster_list_panel.top + scale_value(10),
            scale_value(20),
            scale_value(20)
        )
        
        self.scroll_down_button = pygame.Rect(
            self.monster_list_panel.right - scale_value(30),
            self.monster_list_panel.bottom - scale_value(30),
            scale_value(20),
            scale_value(20)
        )
    
    def handle_events(self, events):
        """
        Handle events for monster codex state
        
        Args:
            events: List of pygame events
        """
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Handle mouse clicks
                mouse_pos = pygame.mouse.get_pos()
                
                # Back button
                if self.back_button.collidepoint(mouse_pos):
                    # Return to village state
                    self.game.state_manager.change_state("village")
                    return True
                
                # Challenge tier buttons
                for tier, button in self.challenge_tier_buttons.items():
                    if button.collidepoint(mouse_pos):
                        self.selected_challenge_tier = tier
                        return True
                
                # Start challenge button
                if self.start_challenge_button.collidepoint(mouse_pos):
                    if self.selected_monster and self.selected_challenge_tier:
                        self.start_monster_challenge()
                        return True
                
                # Scroll buttons
                if self.scroll_up_button.collidepoint(mouse_pos):
                    self.scroll_offset = max(0, self.scroll_offset - 1)
                    return True
                    
                if self.scroll_down_button.collidepoint(mouse_pos):
                    self.scroll_offset = min(self.max_scroll, self.scroll_offset + 1)
                    return True
                
                # Check monster list clicks
                if self.monster_list_panel.collidepoint(mouse_pos):
                    self.handle_monster_list_click(mouse_pos)
                    return True
                
            # Handle escape key to go back
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.game.state_manager.change_state("village")
                return True
                
        return False
    
    def handle_monster_list_click(self, mouse_pos):
        """
        Handle clicks on the monster list
        
        Args:
            mouse_pos: Mouse position tuple
        """
        if not self.monster_codex or not self.monster_codex.monster_data:
            return
            
        # Calculate item height and position
        item_height = scale_value(30)
        
        # Get list of monsters sorted by knowledge tier and name
        sorted_monsters = sorted(
            self.monster_codex.monster_data.items(),
            key=lambda x: (-self.monster_codex.get_knowledge_tier(x[0]), x[0])
        )
        
        # Limit to visible monsters based on scroll
        visible_range = range(self.scroll_offset, min(len(sorted_monsters), self.scroll_offset + self.get_visible_monster_count()))
        
        # Check which monster entry was clicked
        for i, index in enumerate(visible_range):
            monster_type, monster_info = sorted_monsters[index]
            
            # Calculate rectangle for this entry
            entry_rect = pygame.Rect(
                self.monster_list_panel.left + scale_value(10),
                self.monster_list_panel.top + scale_value(40) + i * item_height,
                self.monster_list_panel.width - scale_value(40),
                item_height
            )
            
            if entry_rect.collidepoint(mouse_pos):
                self.selected_monster = monster_type
                # Reset selected challenge tier when switching monsters
                self.selected_challenge_tier = None
                break
    
    def get_visible_monster_count(self):
        """
        Calculate how many monster entries are visible
        
        Returns:
            Number of visible entries
        """
        # Calculate based on panel height
        item_height = scale_value(30)
        visible_area_height = self.monster_list_panel.height - scale_value(80)  # Accounting for header and margins
        return max(1, visible_area_height // item_height)
    
    def update(self, dt):
        """
        Update monster codex state
        
        Args:
            dt: Time delta in seconds
        """
        # Calculate maximum scroll offset
        if self.monster_codex and self.monster_codex.monster_data:
            visible_count = self.get_visible_monster_count()
            total_monsters = len(self.monster_codex.monster_data)
            self.max_scroll = max(0, total_monsters - visible_count)
        else:
            self.max_scroll = 0
    
    def draw(self, screen):
        """
        Draw monster codex state
        
        Args:
            screen: Pygame surface to draw on
        """
        # Draw game background
        screen.fill(self.game.BACKGROUND_COLOR)
        
        # Draw main panel background
        pygame.draw.rect(screen, (40, 30, 30), self.main_panel)
        pygame.draw.rect(screen, (150, 100, 100), self.main_panel, 2)
        
        # Draw monster list panel
        pygame.draw.rect(screen, (50, 30, 30), self.monster_list_panel)
        pygame.draw.rect(screen, (150, 100, 100), self.monster_list_panel, 2)
        
        # Draw detail panel
        pygame.draw.rect(screen, (30, 20, 20), self.detail_panel)
        pygame.draw.rect(screen, (150, 100, 100), self.detail_panel, 2)
        
        # Draw challenge panel
        pygame.draw.rect(screen, (50, 30, 30), self.challenge_panel)
        pygame.draw.rect(screen, (150, 100, 100), self.challenge_panel, 2)
        
        # Draw panel titles
        title_font = pygame.font.Font(None, scale_value(28))
        header_font = pygame.font.Font(None, scale_value(24))
        text_font = pygame.font.Font(None, scale_value(20))
        small_font = pygame.font.Font(None, scale_value(16))
        
        # Draw title
        title_text = "Monster Codex"
        title_surface = title_font.render(title_text, True, (220, 180, 180))
        screen.blit(title_surface, (self.main_panel.centerx - title_surface.get_width() // 2, self.main_panel.top + scale_value(10)))
        
        # Draw monster list title
        list_title = "Monster Database"
        list_title_surface = header_font.render(list_title, True, (200, 160, 160))
        screen.blit(list_title_surface, (self.monster_list_panel.left + scale_value(10), self.monster_list_panel.top + scale_value(10)))
        
        # Draw monster list
        self.draw_monster_list(screen, text_font)
        
        # Draw scroll buttons
        pygame.draw.rect(screen, (100, 80, 80), self.scroll_up_button)
        pygame.draw.polygon(screen, (220, 220, 220), [
            (self.scroll_up_button.left + self.scroll_up_button.width // 2, self.scroll_up_button.top + scale_value(5)),
            (self.scroll_up_button.left + scale_value(5), self.scroll_up_button.bottom - scale_value(5)),
            (self.scroll_up_button.right - scale_value(5), self.scroll_up_button.bottom - scale_value(5))
        ])
        
        pygame.draw.rect(screen, (100, 80, 80), self.scroll_down_button)
        pygame.draw.polygon(screen, (220, 220, 220), [
            (self.scroll_down_button.left + self.scroll_down_button.width // 2, self.scroll_down_button.bottom - scale_value(5)),
            (self.scroll_down_button.left + scale_value(5), self.scroll_down_button.top + scale_value(5)),
            (self.scroll_down_button.right - scale_value(5), self.scroll_down_button.top + scale_value(5))
        ])
        
        # Draw selected monster details
        if self.selected_monster:
            self.draw_monster_details(screen, header_font, text_font, small_font)
            
            # Draw challenge panel
            challenge_title = "Monster Challenges"
            challenge_title_surface = header_font.render(challenge_title, True, (200, 160, 160))
            screen.blit(challenge_title_surface, (
                self.challenge_panel.left + scale_value(10), 
                self.challenge_panel.top + scale_value(10)
            ))
            
            # Draw challenge information
            self.draw_challenge_info(screen, text_font, small_font)
        else:
            # No monster selected message
            no_select_text = "Select a monster from the list to view details"
            no_select_surface = text_font.render(no_select_text, True, (180, 150, 150))
            screen.blit(no_select_surface, (
                self.detail_panel.centerx - no_select_surface.get_width() // 2,
                self.detail_panel.centery - no_select_surface.get_height() // 2
            ))
        
        # Draw back button
        mouse_pos = pygame.mouse.get_pos()
        back_button_color = (150, 80, 80) if self.back_button.collidepoint(mouse_pos) else (120, 60, 60)
        pygame.draw.rect(screen, back_button_color, self.back_button)
        pygame.draw.rect(screen, (200, 150, 150), self.back_button, 2)
        
        back_text = "Back"
        back_surface = text_font.render(back_text, True, (230, 230, 230))
        back_rect = back_surface.get_rect(center=self.back_button.center)
        screen.blit(back_surface, back_rect)
    
    def draw_monster_list(self, screen, font):
        """
        Draw the list of monsters
        
        Args:
            screen: Pygame surface to draw on
            font: Font to use for text
        """
        if not self.monster_codex or not self.monster_codex.monster_data:
            empty_text = "No monsters discovered yet"
            empty_surface = font.render(empty_text, True, (180, 140, 140))
            screen.blit(empty_surface, (
                self.monster_list_panel.centerx - empty_surface.get_width() // 2,
                self.monster_list_panel.top + scale_value(100)
            ))
            return
            
        # Get sorted monster list by knowledge tier (highest first) then name
        sorted_monsters = sorted(
            self.monster_codex.monster_data.items(),
            key=lambda x: (-self.monster_codex.get_knowledge_tier(x[0]), x[0])
        )
        
        # Calculate visible entries
        item_height = scale_value(30)
        visible_range = range(self.scroll_offset, min(len(sorted_monsters), self.scroll_offset + self.get_visible_monster_count()))
        
        # Draw each visible monster entry
        for i, index in enumerate(visible_range):
            monster_type, monster_info = sorted_monsters[index]
            
            # Calculate position
            pos_y = self.monster_list_panel.top + scale_value(40) + i * item_height
            
            # Create entry rectangle for selection highlighting
            entry_rect = pygame.Rect(
                self.monster_list_panel.left + scale_value(5),
                pos_y,
                self.monster_list_panel.width - scale_value(10),
                item_height
            )
            
            # Highlight selected monster
            if monster_type == self.selected_monster:
                pygame.draw.rect(screen, (80, 40, 40), entry_rect)
                pygame.draw.rect(screen, (180, 120, 120), entry_rect, 1)
            
            # Get knowledge tier
            tier = self.monster_codex.get_knowledge_tier(monster_type)
            
            # Format text based on knowledge tier
            if tier >= 1:
                # Basic info available
                text = f"{monster_type} (T{tier}) - {monster_info['kills']} kills"
                color = (200, 180, 160) if tier >= 4 else (180, 160, 140)
            else:
                # Unknown monster (shouldn't happen but just in case)
                text = f"Unknown Monster - {monster_info['kills']} kills"
                color = (150, 130, 130)
            
            # Draw text
            text_surface = font.render(text, True, color)
            screen.blit(text_surface, (self.monster_list_panel.left + scale_value(10), pos_y + (item_height - text_surface.get_height()) // 2))
    
    def draw_monster_details(self, screen, header_font, text_font, small_font):
        """
        Draw details for the selected monster
        
        Args:
            screen: Pygame surface to draw on
            header_font: Font for headers
            text_font: Font for main text
            small_font: Font for small text
        """
        if not self.monster_codex or not self.selected_monster:
            return
            
        monster_info = self.monster_codex.monster_data.get(self.selected_monster, None)
        if not monster_info:
            return
            
        # Get knowledge tier
        tier = self.monster_codex.get_knowledge_tier(self.selected_monster)
        
        # Draw monster name and tier
        monster_title = f"{self.selected_monster} - Tier {tier}/5"
        title_surface = header_font.render(monster_title, True, (220, 180, 160))
        screen.blit(title_surface, (self.detail_panel.left + scale_value(20), self.detail_panel.top + scale_value(20)))
        
        # Draw kill count
        kill_text = f"Total Kills: {monster_info['kills']}"
        kill_surface = text_font.render(kill_text, True, (200, 170, 150))
        screen.blit(kill_surface, (self.detail_panel.left + scale_value(20), self.detail_panel.top + scale_value(50)))
        
        # Draw progress to next tier
        next_tier = tier + 1 if tier < 5 else None
        if next_tier and next_tier in self.monster_codex.knowledge_tiers:
            next_threshold = self.monster_codex.knowledge_tiers[next_tier]
            progress = min(1.0, monster_info['kills'] / next_threshold)
            
            # Draw progress bar
            bar_width = scale_value(200)
            bar_height = scale_value(15)
            bar_left = self.detail_panel.left + scale_value(150)
            bar_top = self.detail_panel.top + scale_value(53)
            
            # Background bar
            pygame.draw.rect(screen, (80, 60, 60), (bar_left, bar_top, bar_width, bar_height))
            
            # Progress bar
            progress_width = int(bar_width * progress)
            pygame.draw.rect(screen, (150, 100, 100), (bar_left, bar_top, progress_width, bar_height))
            
            # Progress text
            progress_text = f"{monster_info['kills']}/{next_threshold} to Tier {next_tier}"
            progress_surface = small_font.render(progress_text, True, (200, 180, 160))
            screen.blit(progress_surface, (bar_left + bar_width + scale_value(10), bar_top))
        
        # Draw tier description
        if tier in self.knowledge_tier_info:
            tier_desc = f"Tier {tier}: {self.knowledge_tier_info[tier]}"
            tier_desc_surface = text_font.render(tier_desc, True, (180, 160, 140))
            screen.blit(tier_desc_surface, (self.detail_panel.left + scale_value(20), self.detail_panel.top + scale_value(80)))
        
        # Draw monster information based on knowledge tier
        y_offset = scale_value(120)
        line_height = scale_value(25)
        
        # Draw information panels
        info_left = self.detail_panel.left + scale_value(20)
        info_width = self.detail_panel.width - scale_value(40)
        
        # Tier 1: Basic Info
        if tier >= 1:
            info_panel = pygame.Rect(info_left, self.detail_panel.top + y_offset, info_width, line_height * 3)
            pygame.draw.rect(screen, (60, 40, 40), info_panel)
            pygame.draw.rect(screen, (120, 90, 90), info_panel, 1)
            
            basic_title = "Basic Information"
            basic_title_surface = text_font.render(basic_title, True, (200, 170, 150))
            screen.blit(basic_title_surface, (info_left + scale_value(10), self.detail_panel.top + y_offset + scale_value(5)))
            
            # Monster appearance info
            appearance_text = f"Appearance: {'Flying' if 'Flyer' in self.selected_monster else 'Ground'} monster"
            appearance_surface = small_font.render(appearance_text, True, (180, 160, 140))
            screen.blit(appearance_surface, (info_left + scale_value(20), self.detail_panel.top + y_offset + scale_value(30)))
            
            # Monster type info
            if 'Boss' in self.selected_monster:
                type_text = "Type: Boss Monster"
            else:
                type_text = "Type: Regular Monster"
            type_surface = small_font.render(type_text, True, (180, 160, 140))
            screen.blit(type_surface, (info_left + scale_value(20), self.detail_panel.top + y_offset + scale_value(50)))
            
            y_offset += line_height * 3 + scale_value(10)
        
        # Tier 2: Combat Data
        if tier >= 2:
            info_panel = pygame.Rect(info_left, self.detail_panel.top + y_offset, info_width, line_height * 4)
            pygame.draw.rect(screen, (60, 40, 40), info_panel)
            pygame.draw.rect(screen, (120, 90, 90), info_panel, 1)
            
            combat_title = "Combat Statistics"
            combat_title_surface = text_font.render(combat_title, True, (200, 170, 150))
            screen.blit(combat_title_surface, (info_left + scale_value(10), self.detail_panel.top + y_offset + scale_value(5)))
            
            # Get monster config (simulated for demonstration)
            health = "Medium" if "Tank" in self.selected_monster else "Low"
            speed = "Fast" if "Runner" in self.selected_monster else "Medium"
            damage = "High" if "Boss" in self.selected_monster else "Medium"
            
            # Health, speed, damage info
            health_text = f"Health: {health}"
            health_surface = small_font.render(health_text, True, (180, 160, 140))
            screen.blit(health_surface, (info_left + scale_value(20), self.detail_panel.top + y_offset + scale_value(30)))
            
            speed_text = f"Speed: {speed}"
            speed_surface = small_font.render(speed_text, True, (180, 160, 140))
            screen.blit(speed_surface, (info_left + scale_value(20), self.detail_panel.top + y_offset + scale_value(50)))
            
            damage_text = f"Damage: {damage}"
            damage_surface = small_font.render(damage_text, True, (180, 160, 140))
            screen.blit(damage_surface, (info_left + scale_value(20), self.detail_panel.top + y_offset + scale_value(70)))
            
            y_offset += line_height * 4 + scale_value(10)
        
        # Tier 3: Placeholder
        if tier >= 3:
            info_panel = pygame.Rect(info_left, self.detail_panel.top + y_offset, info_width, line_height * 2)
            pygame.draw.rect(screen, (60, 40, 40), info_panel)
            pygame.draw.rect(screen, (120, 90, 90), info_panel, 1)
            
            placeholder_title = "Tier 3 Information"
            placeholder_title_surface = text_font.render(placeholder_title, True, (200, 170, 150))
            screen.blit(placeholder_title_surface, (info_left + scale_value(10), self.detail_panel.top + y_offset + scale_value(5)))
            
            placeholder_text = "[Placeholder for Tier 3 information]"
            placeholder_surface = small_font.render(placeholder_text, True, (180, 160, 140))
            screen.blit(placeholder_surface, (info_left + scale_value(20), self.detail_panel.top + y_offset + scale_value(30)))
            
            y_offset += line_height * 2 + scale_value(10)
        
        # Tier 4: Placeholder
        if tier >= 4:
            info_panel = pygame.Rect(info_left, self.detail_panel.top + y_offset, info_width, line_height * 2)
            pygame.draw.rect(screen, (60, 40, 40), info_panel)
            pygame.draw.rect(screen, (120, 90, 90), info_panel, 1)
            
            placeholder_title = "Tier 4 Information"
            placeholder_title_surface = text_font.render(placeholder_title, True, (200, 170, 150))
            screen.blit(placeholder_title_surface, (info_left + scale_value(10), self.detail_panel.top + y_offset + scale_value(5)))
            
            placeholder_text = "[Placeholder for Tier 4 information]"
            placeholder_surface = small_font.render(placeholder_text, True, (180, 160, 140))
            screen.blit(placeholder_surface, (info_left + scale_value(20), self.detail_panel.top + y_offset + scale_value(30)))
            
            y_offset += line_height * 2 + scale_value(10)
    
    def draw_challenge_info(self, screen, text_font, small_font):
        """
        Draw challenge information
        
        Args:
            screen: Pygame surface to draw on
            text_font: Font for main text
            small_font: Font for small text
        """
        if not self.monster_codex or not self.selected_monster:
            return
            
        # Get challenge status for this monster
        challenge_status = self.monster_codex.get_challenge_status(self.selected_monster)
        
        # Draw tier selection buttons
        tiers = ["bronze", "silver", "gold", "platinum"]
        tier_colors = {
            "bronze": (180, 140, 80),
            "silver": (180, 180, 180),
            "gold": (220, 180, 50),
            "platinum": (150, 200, 220)
        }
        
        tier_text = text_font.render("Select Challenge Tier:", True, (200, 180, 160))
        screen.blit(tier_text, (self.challenge_panel.left + scale_value(20), self.challenge_panel.top + scale_value(40)))
        
        # Draw each tier button
        for tier in tiers:
            button = self.challenge_tier_buttons[tier]
            status = challenge_status.get(tier, {})
            available = status.get("available", False)
            completed = status.get("completed", False)
            
            # Determine button color based on state
            if tier == self.selected_challenge_tier:
                color = tier_colors[tier]  # Full color when selected
                border_color = (230, 230, 230)
                text_color = (240, 240, 240)
            elif completed:
                color = [c // 1.5 for c in tier_colors[tier]]  # Dimmed color when completed
                border_color = (150, 180, 150)
                text_color = (200, 220, 200)
            elif available:
                color = [c // 2 for c in tier_colors[tier]]  # Dimmed color when available but not selected
                border_color = (180, 180, 150)
                text_color = (220, 220, 200)
            else:
                color = (80, 70, 70)  # Gray when not available
                border_color = (120, 120, 120)
                text_color = (150, 150, 150)
            
            # Draw button
            pygame.draw.rect(screen, color, button)
            pygame.draw.rect(screen, border_color, button, 2)
            
            # Draw button text
            button_text = tier.capitalize()
            text_surface = small_font.render(button_text, True, text_color)
            text_rect = text_surface.get_rect(center=button.center)
            screen.blit(text_surface, text_rect)
        
        # Draw challenge description
        if self.selected_challenge_tier:
            status = challenge_status.get(self.selected_challenge_tier, {})
            available = status.get("available", False)
            completed = status.get("completed", False)
            threshold = status.get("threshold", 0)
            
            # Description box
            desc_rect = pygame.Rect(
                self.challenge_panel.left + scale_value(20),
                self.challenge_panel.top + scale_value(90),
                self.challenge_panel.width - scale_value(40),
                scale_value(60)
            )
            
            pygame.draw.rect(screen, (60, 45, 45), desc_rect)
            pygame.draw.rect(screen, (120, 100, 100), desc_rect, 1)
            
            # Challenge title
            challenge_title = f"{self.selected_challenge_tier.capitalize()} Challenge"
            title_color = tier_colors.get(self.selected_challenge_tier, (200, 200, 200))
            title_surface = text_font.render(challenge_title, True, title_color)
            screen.blit(title_surface, (desc_rect.left + scale_value(10), desc_rect.top + scale_value(10)))
            
            # Challenge description
            if completed:
                desc_text = f"COMPLETED: Survived 20 waves of {self.selected_monster} monsters"
                desc_color = (150, 200, 150)
            elif available:
                desc_text = f"Survive 20 waves of {self.selected_monster} monsters"
                desc_color = (200, 180, 150)
            else:
                desc_text = f"Requires {threshold} {self.selected_monster} kills (you have {status.get('kills', 0)})"
                desc_color = (180, 150, 150)
                
            desc_surface = small_font.render(desc_text, True, desc_color)
            screen.blit(desc_surface, (desc_rect.left + scale_value(10), desc_rect.top + scale_value(35)))
            
            # Draw start challenge button if available
            if available and not completed:
                # Start challenge button
                start_color = (100, 150, 100) if self.start_challenge_button.collidepoint(pygame.mouse.get_pos()) else (80, 120, 80)
                pygame.draw.rect(screen, start_color, self.start_challenge_button)
                pygame.draw.rect(screen, (150, 200, 150), self.start_challenge_button, 2)
                
                start_text = "Start Challenge"
                start_surface = text_font.render(start_text, True, (230, 230, 230))
                start_rect = start_surface.get_rect(center=self.start_challenge_button.center)
                screen.blit(start_surface, start_rect)
            elif completed:
                # Show completed message
                reward_text = f"Reward: {self.selected_monster} {self.selected_challenge_tier.capitalize()} Cup"
                reward_surface = text_font.render(reward_text, True, (150, 200, 150))
                reward_rect = reward_surface.get_rect(
                    center=(self.start_challenge_button.centerx, self.start_challenge_button.centery)
                )
                screen.blit(reward_surface, reward_rect)
    
    def start_monster_challenge(self):
        """Start the selected monster challenge"""
        if not self.monster_codex or not self.selected_monster or not self.selected_challenge_tier:
            return
            
        # Check if the challenge can be started
        if self.monster_codex.start_challenge(self.selected_monster, self.selected_challenge_tier):
            # Challenge started successfully
            print(f"Starting {self.selected_challenge_tier} challenge for {self.selected_monster}!")
            
            # Return to playing state for the challenge
            self.game.state_manager.change_state("playing")
