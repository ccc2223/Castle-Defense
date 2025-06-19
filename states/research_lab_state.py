"""
Research lab state for Castle Defense
"""
import pygame
from .game_state import GameState
from utils import scale_position, scale_value, scale_size

class ResearchLabState(GameState):
    """
    State for research lab management and research tree
    """
    def __init__(self, game):
        """
        Initialize research lab state
        
        Args:
            game: Game instance
        """
        super().__init__(game)
        self.background_color = (10, 30, 50)  # Dark blue background for research lab
        
        # Get research manager from registry if available
        self.research_manager = None
        if hasattr(game, 'registry') and game.registry.has("research_manager"):
            self.research_manager = game.registry.get("research_manager")
        
        # If research manager doesn't exist yet, create it
        if not self.research_manager and hasattr(game, 'registry'):
            try:
                from features.research.research_manager import ResearchManager
                self.research_manager = ResearchManager(game.registry)
                
                # Register it with the registry
                game.registry.register("research_manager", self.research_manager)
                print("Created new research manager")
            except ImportError as e:
                print(f"Error importing ResearchManager: {e}")
                # Create minimal research manager as fallback
                self.research_manager = self.create_minimal_research_manager()
            except Exception as e:
                print(f"Error creating research manager: {e}")
                # Create minimal research manager as fallback
                self.research_manager = self.create_minimal_research_manager()
        
        # Create minimal research manager if we still don't have one
        if not self.research_manager:
            self.research_manager = self.create_minimal_research_manager()
            print("Created minimal research manager fallback")
        
        # Create a return button to go back to village state
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
        
        # Research tree layout parameters
        self.tree_rect = pygame.Rect(
            int(game.WINDOW_WIDTH * 0.05),  # 5% margin from left
            int(game.WINDOW_HEIGHT * 0.15),  # 15% margin from top
            int(game.WINDOW_WIDTH * 0.9),    # 90% of screen width
            int(game.WINDOW_HEIGHT * 0.6)    # 60% of screen height
        )
        
        # Node size and spacing
        self.node_size = scale_size((120, 100))
        self.column_spacing = int(self.tree_rect.width / 5)  # Further increase horizontal spacing
        
        # Track hover and selected nodes
        self.hovered_node = None
        self.selected_node = None
        
        # Create start research button (shown when a researchable node is selected)
        research_button_size = scale_size((180, 40))
        research_button_pos = (
            game.WINDOW_WIDTH // 2 - research_button_size[0] // 2,
            int(game.WINDOW_HEIGHT * 0.85)
        )
        self.research_button_rect = pygame.Rect(
            research_button_pos[0],
            research_button_pos[1],
            research_button_size[0],
            research_button_size[1]
        )
        self.research_button_color = (60, 120, 60)
        self.research_button_hover_color = (80, 150, 80)
        self.research_button_is_hovered = False
        self.research_button_visible = False
        
        # Create cancel research button (shown when research is in progress)
        cancel_button_size = scale_size((180, 40))
        cancel_button_pos = (
            game.WINDOW_WIDTH // 2 - cancel_button_size[0] // 2 - 250,  # Move further left
            int(game.WINDOW_HEIGHT * 0.85)
        )
        self.cancel_button_rect = pygame.Rect(
            cancel_button_pos[0],
            cancel_button_pos[1],
            cancel_button_size[0],
            cancel_button_size[1]
        )
        self.cancel_button_color = (120, 60, 60)
        self.cancel_button_hover_color = (150, 80, 80)
        self.cancel_button_is_hovered = False
        self.cancel_button_visible = False
        
        # Create finish research button (shown when research is complete)
        finish_button_size = scale_size((180, 40))
        finish_button_pos = (
            game.WINDOW_WIDTH // 2 - finish_button_size[0] // 2 + 250,  # Move further right
            int(game.WINDOW_HEIGHT * 0.85)
        )
        self.finish_button_rect = pygame.Rect(
            finish_button_pos[0],
            finish_button_pos[1],
            finish_button_size[0],
            finish_button_size[1]
        )
        self.finish_button_color = (60, 120, 100)
        self.finish_button_hover_color = (80, 150, 120)
        self.finish_button_is_hovered = False
        self.finish_button_visible = False
        
        # Track animation state for research completion
        self.completion_animation = False
        self.completion_animation_timer = 0.0
        self.completion_animation_duration = 2.0  # Animation lasts 2 seconds
        self.completed_research_id = None
        self.glow_intensity = 0.0
        self.progress_panel_rect = None
        
        # Calculate node positions
        self.calculate_node_positions()
    
    def create_minimal_research_manager(self):
        """Create a minimal research manager for fallback"""
        # Simple dictionary-based object with required attributes/methods
        class MinimalResearchManager:
            def __init__(self):
                self.research_tree = {1: {"basic_research": {"name": "Basic Research", "description": "Research lab under construction", "current_level": 0, "max_level": 1, "unlocked": True, "prerequisites": [], "time_cost": 60}}}
                self.active_research = None
                self.active_research_id = None
                self.research_progress = 0
                self.research_complete = False
            
            def get_research_by_id(self, research_id):
                for column in self.research_tree.values():
                    if research_id in column:
                        return column[research_id]
                return None
            
            def get_column_for_research(self, research_id):
                for column, researches in self.research_tree.items():
                    if research_id in researches:
                        return column
                return 1
            
            def start_research(self, research_id):
                research = self.get_research_by_id(research_id)
                if not research:
                    return False
                self.active_research = research
                self.active_research_id = research_id
                self.research_progress = 0
                self.research_complete = False
                return True
            
            def cancel_research(self):
                if not self.active_research:
                    return False
                self.active_research = None
                self.active_research_id = None
                self.research_progress = 0
                self.research_complete = False
                return True
            
            def finish_research(self):
                if not self.active_research or not self.research_complete:
                    return False
                research = self.active_research
                research["current_level"] += 1
                self.active_research = None
                self.active_research_id = None
                self.research_progress = 0
                self.research_complete = False
                return True
            
            def update(self, dt):
                if not self.active_research:
                    return False
                if self.research_complete:
                    return False
                self.research_progress += dt
                if self.research_progress >= self.active_research["time_cost"]:
                    self.research_complete = True
                    return True
                return False
                
        return MinimalResearchManager()
        
    def calculate_node_positions(self):
        """Calculate positions for all research nodes in the tree"""
        self.node_positions = {}
        
        # Verify research_manager exists and has research_tree attribute
        if not self.research_manager or not hasattr(self.research_manager, 'research_tree'):
            print("Research manager missing or invalid - cannot calculate node positions")
            return
            
        # Calculate for each column
        for column, researches in self.research_manager.research_tree.items():
            # Determine number of nodes in this column
            num_nodes = len(researches)
            
            # Calculate x position for this column
            x = self.tree_rect.left + (column - 1) * self.column_spacing + self.column_spacing // 2
            
            # Calculate y positions for nodes in this column
            if num_nodes == 1:
                # Single node - center it
                y = self.tree_rect.centery
                
                # Get the first (and only) research in this column
                research_id = list(researches.keys())[0]
                self.node_positions[research_id] = (x, y)
            else:
                # Multiple nodes - distribute evenly with more vertical spacing
                total_height = (num_nodes - 1) * (self.node_size[1] + 60)  # Increased vertical spacing
                start_y = self.tree_rect.centery - total_height // 2
                
                for i, research_id in enumerate(researches.keys()):
                    y = start_y + i * (self.node_size[1] + 60)  # Increased vertical spacing
                    self.node_positions[research_id] = (x, y)
    
    def handle_events(self, events):
        """
        Handle research lab events
        
        Args:
            events: List of pygame events
        """
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = pygame.mouse.get_pos()
                
                # Check if return button was clicked
                if self.return_button_rect.collidepoint(mouse_pos):
                    # Return to village state
                    self.game.state_manager.change_state("village")
                    return True
                
                # Check if start research button was clicked
                if self.research_button_visible and self.research_button_rect.collidepoint(mouse_pos):
                    if self.selected_node:
                        if self.research_manager.start_research(self.selected_node):
                            print(f"Started research: {self.selected_node}")
                            
                            # Update button visibility
                            self.research_button_visible = False
                            self.cancel_button_visible = True
                            self.finish_button_visible = False
                            
                            return True
                
                # Check if cancel research button was clicked
                if self.cancel_button_visible and self.cancel_button_rect.collidepoint(mouse_pos):
                    if self.research_manager.cancel_research():
                        print("Cancelled research")
                        
                        # Update button visibility - reset all buttons
                        self.cancel_button_visible = False
                        self.finish_button_visible = False
                        
                        # Show research button only if a researchable node is selected
                        if self.selected_node:
                            research = self.research_manager.get_research_by_id(self.selected_node)
                            if research and research["unlocked"] and research["current_level"] < research["max_level"]:
                                self.research_button_visible = True
                        
                        return True
                
                # Check if finish research button was clicked
                if self.finish_button_visible and self.finish_button_rect.collidepoint(mouse_pos):
                    if self.research_manager.finish_research():
                        print("Finished research")
                        
                        # Reset all button states
                        self.cancel_button_visible = False
                        self.finish_button_visible = False
                        
                        # Show research button only if a researchable node is selected
                        if self.selected_node:
                            research = self.research_manager.get_research_by_id(self.selected_node)
                            if research and research["unlocked"] and research["current_level"] < research["max_level"]:
                                self.research_button_visible = True
                        
                        return True
                
                # Check if a research node was clicked
                for research_id, position in self.node_positions.items():
                    node_rect = pygame.Rect(
                        position[0] - self.node_size[0] // 2,
                        position[1] - self.node_size[1] // 2,
                        self.node_size[0],
                        self.node_size[1]
                    )
                    
                    if node_rect.collidepoint(mouse_pos):
                        # Get research data
                        research = self.research_manager.get_research_by_id(research_id)
                        
                        # Select this node if it's unlocked
                        if research and research["unlocked"]:
                            self.selected_node = research_id
                            
                            # Update all button visibility after node selection
                            if not self.research_manager.active_research:
                                # No active research - show research button if node can be researched
                                if research["current_level"] < research["max_level"]:
                                    self.research_button_visible = True
                                    self.cancel_button_visible = False
                                    self.finish_button_visible = False
                                else:
                                    self.research_button_visible = False
                            # If research is active, maintain current button state
                            # based on research completion state
                                
                            return True
            
            # Check for button hover states
            elif event.type == pygame.MOUSEMOTION:
                mouse_pos = pygame.mouse.get_pos()
                
                # Return button hover
                self.return_button_is_hovered = self.return_button_rect.collidepoint(mouse_pos)
                
                # Research button hover
                self.research_button_is_hovered = (self.research_button_visible and 
                                                  self.research_button_rect.collidepoint(mouse_pos))
                
                # Cancel button hover
                self.cancel_button_is_hovered = (self.cancel_button_visible and 
                                               self.cancel_button_rect.collidepoint(mouse_pos))
                
                # Finish button hover
                self.finish_button_is_hovered = (self.finish_button_visible and 
                                               self.finish_button_rect.collidepoint(mouse_pos))
                
                # Node hover
                self.hovered_node = None
                for research_id, position in self.node_positions.items():
                    node_rect = pygame.Rect(
                        position[0] - self.node_size[0] // 2,
                        position[1] - self.node_size[1] // 2,
                        self.node_size[0],
                        self.node_size[1]
                    )
                    
                    if node_rect.collidepoint(mouse_pos):
                        # Only hover on unlocked nodes
                        research = self.research_manager.get_research_by_id(research_id)
                        if research and research["unlocked"]:
                            self.hovered_node = research_id
                            break
        
        return False
    
    def update_button_visibility(self):
        """
        Update all button visibility states based on current state
        """
        # Reset all buttons first
        self.research_button_visible = False
        self.cancel_button_visible = False
        self.finish_button_visible = False
        
        # Check current research state
        if self.research_manager.active_research:
            if self.research_manager.research_complete:
                # Research is complete - show finish button
                self.finish_button_visible = True
            else:
                # Research is in progress - show cancel button
                self.cancel_button_visible = True
        elif self.selected_node:
            # No active research, but a node is selected
            research = self.research_manager.get_research_by_id(self.selected_node)
            if research and research["unlocked"] and research["current_level"] < research["max_level"]:
                # Selected node can be researched
                self.research_button_visible = True
    
    def update(self, dt):
        """
        Update research lab state
        
        Args:
            dt: Time delta in seconds
        """
        # Update research progress
        if self.research_manager:
            # Store the previous state to detect changes
            was_complete = self.research_manager.research_complete
            
            # Update research and check if it completed just now
            completed = self.research_manager.update(dt)
            
            # Research just completed
            if completed:
                print("Research completed")
                # IMPORTANT: Always hide cancel button when research is complete
                self.cancel_button_visible = False
                self.finish_button_visible = True
                
                # Start completion animation
                self.completion_animation = True
                self.completion_animation_timer = 0.0
                self.completed_research_id = self.research_manager.active_research_id
            
            # Ensure UI state is always in sync with research state
            if self.research_manager.active_research:
                if self.research_manager.research_complete:
                    # Force correct button visibility for completed research
                    self.cancel_button_visible = False
                    self.finish_button_visible = True
                else:
                    # Force correct button visibility for in-progress research
                    self.cancel_button_visible = True
                    self.finish_button_visible = False
            else:
                # No active research
                self.cancel_button_visible = False
                self.finish_button_visible = False
                # Update research button visibility if node is selected
                if self.selected_node:
                    research = self.research_manager.get_research_by_id(self.selected_node)
                    if research and research["unlocked"] and research["current_level"] < research["max_level"]:
                        self.research_button_visible = True
        
        # Update completion animation
        if self.completion_animation:
            self.completion_animation_timer += dt
            
            # Calculate glow intensity based on animation time (pulsing effect)
            progress = self.completion_animation_timer / self.completion_animation_duration
            if progress < 0.5:
                # Ramp up intensity to max in first half
                self.glow_intensity = progress * 2.0
            else:
                # Ramp down intensity in second half
                self.glow_intensity = 2.0 - progress * 2.0
            
            # End animation after duration
            if self.completion_animation_timer >= self.completion_animation_duration:
                self.completion_animation = False
                self.glow_intensity = 0.0
    
    def draw(self, screen):
        """
        Draw research lab state
        
        Args:
            screen: Pygame surface to draw on
        """
        # Clear the screen with background color
        screen.fill(self.background_color)
        
        # Draw the research tree
        self.draw_research_tree(screen)
        
        # Draw research details panel
        self.draw_research_details(screen)
        
        # Draw active research panel
        self.draw_active_research(screen)
        
        # Draw return button
        color = self.return_button_hover_color if self.return_button_is_hovered else self.return_button_color
        pygame.draw.rect(screen, color, self.return_button_rect)
        pygame.draw.rect(screen, (200, 200, 220), self.return_button_rect, 2)  # Border
        
        # Draw button text
        font_size = scale_value(18)
        font = pygame.font.Font(None, font_size)
        text = font.render("Return to Village", True, (255, 255, 255))
        text_rect = text.get_rect(center=self.return_button_rect.center)
        screen.blit(text, text_rect)
        
        # Draw start research button if a node is selected
        if self.research_button_visible:
            color = self.research_button_hover_color if self.research_button_is_hovered else self.research_button_color
            pygame.draw.rect(screen, color, self.research_button_rect)
            pygame.draw.rect(screen, (150, 200, 150), self.research_button_rect, 2)  # Border
            
            # Button text
            font_size = scale_value(22)
            font = pygame.font.Font(None, font_size)
            text = font.render("Start Research", True, (255, 255, 255))
            text_rect = text.get_rect(center=self.research_button_rect.center)
            screen.blit(text, text_rect)
        
        # Draw cancel research button if research is in progress
        if self.cancel_button_visible:
            color = self.cancel_button_hover_color if self.cancel_button_is_hovered else self.cancel_button_color
            pygame.draw.rect(screen, color, self.cancel_button_rect)
            pygame.draw.rect(screen, (200, 150, 150), self.cancel_button_rect, 2)  # Border
            
            # Button text
            font_size = scale_value(22)
            font = pygame.font.Font(None, font_size)
            text = font.render("Cancel Research", True, (255, 255, 255))
            text_rect = text.get_rect(center=self.cancel_button_rect.center)
            screen.blit(text, text_rect)
        
        # Draw finish research button if research is complete
        if self.finish_button_visible:
            color = self.finish_button_hover_color if self.finish_button_is_hovered else self.finish_button_color
            pygame.draw.rect(screen, color, self.finish_button_rect)
            pygame.draw.rect(screen, (150, 200, 180), self.finish_button_rect, 2)  # Border
            
            # Button text
            font_size = scale_value(22)
            font = pygame.font.Font(None, font_size)
            text = font.render("Complete Research", True, (255, 255, 255))
            text_rect = text.get_rect(center=self.finish_button_rect.center)
            screen.blit(text, text_rect)
    
    def draw_research_tree(self, screen):
        """
        Draw the research tree visualization
        
        Args:
            screen: Pygame surface to draw on
        """
        # Draw tree background
        pygame.draw.rect(screen, (20, 40, 60), self.tree_rect)
        pygame.draw.rect(screen, (40, 60, 80), self.tree_rect, 2)  # Border
        
        # Draw connections between nodes
        self.draw_node_connections(screen)
        
        # Draw each research node
        for research_id, position in self.node_positions.items():
            research = self.research_manager.get_research_by_id(research_id)
            if not research:
                continue
                
            # Create node rect
            node_rect = pygame.Rect(
                position[0] - self.node_size[0] // 2,
                position[1] - self.node_size[1] // 2,
                self.node_size[0],
                self.node_size[1]
            )
            
            # Determine node color based on state
            node_color = self.get_node_color(research_id, research)
            
            # Draw node
            pygame.draw.rect(screen, node_color, node_rect, border_radius=5)
            
            # Draw node border (thicker if selected)
            border_width = 3 if research_id == self.selected_node else 1
            border_color = (220, 220, 100) if research_id == self.selected_node else (150, 150, 180)
            pygame.draw.rect(screen, border_color, node_rect, border_width, border_radius=5)
            
            # Draw node title
            font_size = scale_value(16)
            font = pygame.font.Font(None, font_size)
            title_text = research["name"]
            title_surface = font.render(title_text, True, (255, 255, 255))
            title_rect = title_surface.get_rect(center=(node_rect.centerx, node_rect.top + scale_value(15)))
            screen.blit(title_surface, title_rect)
            
            # Draw node level
            level_text = f"Level {research['current_level']}/{research['max_level']}"
            level_surface = font.render(level_text, True, (200, 200, 200))
            level_rect = level_surface.get_rect(center=(node_rect.centerx, node_rect.top + scale_value(35)))
            screen.blit(level_surface, level_rect)
            
            # Draw a short preview of the effect
            if research["current_level"] > 0:
                # Show current effect
                effect_text = self.get_effect_text(research_id, research)
                effect_surface = font.render(effect_text, True, (180, 220, 180))
                effect_rect = effect_surface.get_rect(center=(node_rect.centerx, node_rect.bottom - scale_value(20)))
                screen.blit(effect_surface, effect_rect)
            elif research["unlocked"]:
                # Show "Unlock this research"
                unlock_text = "Click to research"
                unlock_surface = font.render(unlock_text, True, (180, 180, 220))
                unlock_rect = unlock_surface.get_rect(center=(node_rect.centerx, node_rect.bottom - scale_value(20)))
                screen.blit(unlock_surface, unlock_rect)
            else:
                # Show "Locked"
                locked_text = "Locked"
                locked_surface = font.render(locked_text, True, (150, 150, 150))
                locked_rect = locked_surface.get_rect(center=(node_rect.centerx, node_rect.bottom - scale_value(20)))
                screen.blit(locked_surface, locked_rect)
    
    def draw_node_connections(self, screen):
        """
        Draw connecting lines between research nodes
        
        Args:
            screen: Pygame surface to draw on
        """
        # For each column, draw connections to the previous column
        for column in range(2, 6):  # Start from column 2 (first column has no incoming connections)
            if column not in self.research_manager.research_tree:
                continue
                
            # Get all nodes in this column
            current_nodes = []
            for research_id in self.research_manager.research_tree.get(column, {}).keys():
                if research_id in self.node_positions:
                    current_nodes.append((research_id, self.node_positions[research_id]))
            
            # Get all nodes in previous column
            prev_nodes = []
            for research_id in self.research_manager.research_tree.get(column-1, {}).keys():
                if research_id in self.node_positions:
                    prev_nodes.append((research_id, self.node_positions[research_id]))
            
            # Skip if no nodes in either column
            if not current_nodes or not prev_nodes:
                continue
            
            # Draw connections from each previous node to each current node that depends on it
            for current_id, current_pos in current_nodes:
                current_research = self.research_manager.get_research_by_id(current_id)
                if not current_research or not current_research["prerequisites"]:
                    continue
                    
                # For each prerequisite in previous column
                for prereq_id in current_research["prerequisites"]:
                    # Find if this prerequisite is in the previous column
                    prereq_pos = None
                    for prev_id, pos in prev_nodes:
                        if prev_id == prereq_id:
                            prereq_pos = pos
                            break
                    
                    if not prereq_pos:
                        continue
                    
                    # Determine line color based on completion status
                    prereq = self.research_manager.get_research_by_id(prereq_id)
                    
                    if prereq and prereq["current_level"] > 0:
                        # Prerequisite completed - green line
                        line_color = (100, 200, 100)
                        line_width = 2
                    else:
                        # Prerequisite not completed - gray line
                        line_color = (100, 100, 120)
                        line_width = 1
                    
                    # Calculate connection points 
                    start_x = prereq_pos[0] + self.node_size[0] // 2  # Right edge of prerequisite node
                    end_x = current_pos[0] - self.node_size[0] // 2    # Left edge of current node
                    
                    # Draw the connecting line with bezier curve for better appearance
                    # Simple approach: draw three segments with the middle one horizontal
                    mid_x = (start_x + end_x) // 2
                    
                    # Draw three segments to make a nicer path
                    pygame.draw.line(
                        screen, 
                        line_color,
                        (start_x, prereq_pos[1]),                # Start from right of prereq node
                        (start_x + (mid_x - start_x) // 2, prereq_pos[1]),  # Go horizontally halfway
                        line_width
                    )
                    
                    # Middle segment - connecting the two levels
                    pygame.draw.line(
                        screen, 
                        line_color,
                        (start_x + (mid_x - start_x) // 2, prereq_pos[1]),
                        (mid_x + (end_x - mid_x) // 2, current_pos[1]),
                        line_width
                    )
                    
                    # Last segment - horizontal to current node
                    pygame.draw.line(
                        screen, 
                        line_color,
                        (mid_x + (end_x - mid_x) // 2, current_pos[1]),
                        (end_x, current_pos[1]),                 # End at left of current node
                        line_width
                    )
    
    def get_node_color(self, research_id, research):
        """
        Get the color for a research node based on its state
        
        Args:
            research_id: ID of the research
            research: Research data
            
        Returns:
            RGB color tuple
        """
        # Determine base color based on column
        column = self.research_manager.get_column_for_research(research_id)
        base_colors = {
            1: (80, 80, 120),   # Column 1 - Blue-purple
            2: (80, 120, 80),   # Column 2 - Green
            3: (120, 80, 80),   # Column 3 - Red
            4: (120, 120, 80),  # Column 4 - Yellow
            5: (80, 120, 120),  # Column 5 - Cyan
        }
        base_color = base_colors.get(column, (100, 100, 100))
        
        # Adjust color based on state
        if not research["unlocked"]:
            # Locked - darker
            return (base_color[0] // 2, base_color[1] // 2, base_color[2] // 2)
        elif research["current_level"] >= research["max_level"]:
            # Max level - brighter
            return (min(255, base_color[0] * 1.5), min(255, base_color[1] * 1.5), min(255, base_color[2] * 1.5))
        elif research_id == self.hovered_node:
            # Hovered - brighter
            return (min(255, base_color[0] * 1.3), min(255, base_color[1] * 1.3), min(255, base_color[2] * 1.3))
        elif research_id == self.selected_node:
            # Selected - slightly brighter
            return (min(255, base_color[0] * 1.2), min(255, base_color[1] * 1.2), min(255, base_color[2] * 1.2))
        elif research["current_level"] > 0:
            # Researched but not max - normal brightness
            return base_color
        else:
            # Not researched - slightly darker
            return (base_color[0] * 0.8, base_color[1] * 0.8, base_color[2] * 0.8)
    
    def get_effect_text(self, research_id, research):
        """
        Get a short description of the current effect level
        
        Args:
            research_id: ID of the research
            research: Research data
            
        Returns:
            String describing the effect
        """
        if research_id == "double_loot":
            chance = research["base_chance"] * research["current_level"] * 100
            return f"{chance:.1f}% double loot chance"
        
        elif research_id == "castle_healer":
            heal = research["heal_amount"] * research["current_level"]
            return f"+{heal} HP on boss kill"
        
        elif research_id == "free_upgrades":
            chance = research["base_chance"] * research["current_level"] * 100
            return f"{chance:.1f}% free upgrade chance"
        
        elif research_id == "clockwork_speed":
            speed = research["speed_increase"] * research["current_level"]
            return f"+{speed:.1f}x game speed"
        
        elif research_id == "monster_weakness":
            damage = research["damage_multiplier"] * research["current_level"] * 100
            return f"+{damage:.1f}% tower damage"
        
        elif research_id == "resource_efficiency":
            reduction = research["cost_reduction"] * research["current_level"] * 100
            return f"-{reduction:.1f}% building costs"
        
        elif research_id == "advanced_engineering":
            speed = research["attack_speed_multiplier"] * research["current_level"] * 100
            return f"+{speed:.1f}% tower attack speed"
        
        return "Unknown effect"
    
    def draw_research_details(self, screen):
        """
        Draw detailed information for the selected research
        
        Args:
            screen: Pygame surface to draw on
        """
        # Don't draw if no node is selected
        if not self.selected_node:
            return
            
        # Get research data
        research = self.research_manager.get_research_by_id(self.selected_node)
        if not research:
            return
            
        # Create details panel
        panel_width = int(self.game.WINDOW_WIDTH * 0.25)
        panel_height = int(self.game.WINDOW_HEIGHT * 0.3)
        panel_rect = pygame.Rect(
            self.game.WINDOW_WIDTH - panel_width - 20,
            20,
            panel_width,
            panel_height
        )
        
        # Draw panel background
        pygame.draw.rect(screen, (30, 40, 60), panel_rect)
        pygame.draw.rect(screen, (60, 80, 100), panel_rect, 2)  # Border
        
        # Draw research name
        font_size = scale_value(24)
        font = pygame.font.Font(None, font_size)
        name_text = research["name"]
        name_surface = font.render(name_text, True, (220, 220, 150))
        name_rect = name_surface.get_rect(topleft=(panel_rect.left + 15, panel_rect.top + 15))
        screen.blit(name_surface, name_rect)
        
        # Draw level
        level_text = f"Level {research['current_level']}/{research['max_level']}"
        level_surface = font.render(level_text, True, (180, 180, 220))
        level_rect = level_surface.get_rect(topright=(panel_rect.right - 15, panel_rect.top + 15))
        screen.blit(level_surface, level_rect)
        
        # Draw description
        font_size = scale_value(18)
        font = pygame.font.Font(None, font_size)
        description_text = research["description"]
        
        # Word wrap description
        words = description_text.split()
        lines = []
        current_line = words[0]
        
        for word in words[1:]:
            # Check if adding this word would make the line too long
            test_line = current_line + " " + word
            test_surface = font.render(test_line, True, (200, 200, 200))
            
            if test_surface.get_width() < panel_rect.width - 30:
                # Word fits, add it to the current line
                current_line = test_line
            else:
                # Word doesn't fit, start a new line
                lines.append(current_line)
                current_line = word
        
        # Add the last line
        lines.append(current_line)
        
        # Draw each line
        y_offset = name_rect.bottom + 15
        for line in lines:
            line_surface = font.render(line, True, (200, 200, 200))
            screen.blit(line_surface, (panel_rect.left + 15, y_offset))
            y_offset += line_surface.get_height() + 5
        
        # Draw current effect
        y_offset += 15
        effect_title = font.render("Current Effect:", True, (180, 220, 180))
        screen.blit(effect_title, (panel_rect.left + 15, y_offset))
        y_offset += effect_title.get_height() + 5
        
        effect_text = self.get_effect_text(self.selected_node, research)
        effect_surface = font.render(effect_text, True, (200, 220, 200))
        screen.blit(effect_surface, (panel_rect.left + 25, y_offset))
        
        # Draw next level effect if not at max
        if research["current_level"] < research["max_level"]:
            y_offset += effect_surface.get_height() + 15
            next_title = font.render("Next Level:", True, (220, 180, 180))
            screen.blit(next_title, (panel_rect.left + 15, y_offset))
            y_offset += next_title.get_height() + 5
            
            # Calculate next level effect
            next_level = research["current_level"] + 1
            
            if self.selected_node == "double_loot":
                chance = research["base_chance"] * next_level * 100
                next_effect = f"{chance:.1f}% double loot chance"
            
            elif self.selected_node == "castle_healer":
                heal = research["heal_amount"] * next_level
                next_effect = f"+{heal} HP on boss kill"
            
            elif self.selected_node == "free_upgrades":
                chance = research["base_chance"] * next_level * 100
                next_effect = f"{chance:.1f}% free upgrade chance"
            
            elif self.selected_node == "clockwork_speed":
                speed = research["speed_increase"] * next_level
                next_effect = f"+{speed:.1f}x game speed"
            
            elif self.selected_node == "monster_weakness":
                damage = research["damage_multiplier"] * next_level * 100
                next_effect = f"+{damage:.1f}% tower damage"
            
            elif self.selected_node == "resource_efficiency":
                reduction = research["cost_reduction"] * next_level * 100
                next_effect = f"-{reduction:.1f}% building costs"
            
            elif self.selected_node == "advanced_engineering":
                speed = research["attack_speed_multiplier"] * next_level * 100
                next_effect = f"+{speed:.1f}% tower attack speed"
            
            else:
                next_effect = "Unknown effect"
            
            next_surface = font.render(next_effect, True, (220, 200, 200))
            screen.blit(next_surface, (panel_rect.left + 25, y_offset))
            
            # Draw time requirement
            y_offset += next_surface.get_height() + 15
            time_text = f"Research Time: {research['time_cost']} seconds"
            time_surface = font.render(time_text, True, (200, 200, 220))
            screen.blit(time_surface, (panel_rect.left + 15, y_offset))
    
    def draw_active_research(self, screen):
        """
        Draw information about the currently active research
        
        Args:
            screen: Pygame surface to draw on
        """
        # Check if research is active
        if not self.research_manager.active_research:
            # Make sure buttons are properly hidden when there's no active research
            self.cancel_button_visible = False
            self.finish_button_visible = False
            return
            
        # Create active research panel
        panel_width = int(self.game.WINDOW_WIDTH * 0.3)
        panel_height = int(self.game.WINDOW_HEIGHT * 0.1)
        panel_rect = pygame.Rect(
            (self.game.WINDOW_WIDTH - panel_width) // 2,
            self.game.WINDOW_HEIGHT - panel_height - 150,  # Move higher up from bottom
            panel_width,
            panel_height
        )
        
        # Update button positions to be relative to panel
        cancel_button_pos = (panel_rect.left - 100, panel_rect.bottom + 20)
        self.cancel_button_rect.topleft = cancel_button_pos
        
        finish_button_pos = (panel_rect.right - 80, panel_rect.bottom + 20)
        self.finish_button_rect.topleft = finish_button_pos
        
        # Save the panel rect for animation reference
        self.progress_panel_rect = panel_rect
        
        # Draw glowing effect if animation is active
        if self.completion_animation and self.glow_intensity > 0:
            # Create a larger rectangle for the glow
            glow_size = int(10 * self.glow_intensity)  # Size of glow based on intensity
            glow_rect = panel_rect.inflate(glow_size, glow_size)
            
            # Create a surface for the glow with alpha
            glow_surface = pygame.Surface((glow_rect.width, glow_rect.height), pygame.SRCALPHA)
            
            # Determine glow color (green for completion)
            glow_alpha = int(100 * self.glow_intensity)  # Alpha based on intensity
            glow_color = (100, 255, 100, glow_alpha)
            
            # Draw the glow
            pygame.draw.rect(glow_surface, glow_color, 
                         (0, 0, glow_rect.width, glow_rect.height), 
                         border_radius=5)
            
            # Blit the glow surface
            screen.blit(glow_surface, 
                      (glow_rect.left, glow_rect.top))
            
            # If we have a completed research node, draw a beam to it
            if self.completed_research_id and self.completed_research_id in self.node_positions:
                node_pos = self.node_positions[self.completed_research_id]
                
                # Create a connecting beam
                start_pos = (panel_rect.centerx, panel_rect.top)
                end_pos = (node_pos[0], node_pos[1] + self.node_size[1] // 2)
                
                # Calculate control points for a bezier curve
                control1 = (start_pos[0], start_pos[1] - 50)
                control2 = (end_pos[0], end_pos[1] + 50)
                
                # Draw the beam as segments for a curve-like effect
                segments = 10
                beam_color = (150, 255, 150, int(200 * self.glow_intensity))
                beam_width = int(3 * self.glow_intensity)
                
                # Simple approach: draw a direct line with glow
                # Create a surface for the beam
                beam_surface = pygame.Surface((self.game.WINDOW_WIDTH, self.game.WINDOW_HEIGHT), pygame.SRCALPHA)
                pygame.draw.line(beam_surface, beam_color, start_pos, end_pos, max(1, beam_width))
                
                # Apply the beam
                screen.blit(beam_surface, (0, 0))
                
                # Also add glow to the research node
                node_rect = pygame.Rect(
                    node_pos[0] - self.node_size[0] // 2,
                    node_pos[1] - self.node_size[1] // 2,
                    self.node_size[0],
                    self.node_size[1]
                )
                
                # Create node glow
                node_glow_rect = node_rect.inflate(glow_size, glow_size)
                node_glow_surface = pygame.Surface((node_glow_rect.width, node_glow_rect.height), pygame.SRCALPHA)
                pygame.draw.rect(node_glow_surface, glow_color, 
                             (0, 0, node_glow_rect.width, node_glow_rect.height), 
                             border_radius=5)
                
                # Apply node glow
                screen.blit(node_glow_surface, 
                          (node_glow_rect.left, node_glow_rect.top))
                          
        # Draw panel background
        pygame.draw.rect(screen, (30, 50, 40), panel_rect)
        
        # Draw panel border (different color if research is complete)
        if self.research_manager.research_complete:
            border_color = (100, 200, 100)  # Green for complete
        else:
            border_color = (80, 100, 120)  # Blue for in progress
        pygame.draw.rect(screen, border_color, panel_rect, 2)  # Border
        
        # Draw research name and progress
        font_size = scale_value(20)
        font = pygame.font.Font(None, font_size)
        
        # Research name
        name_text = f"Researching: {self.research_manager.active_research['name']}"
        name_surface = font.render(name_text, True, (220, 220, 220))
        name_rect = name_surface.get_rect(topleft=(panel_rect.left + 15, panel_rect.top + 15))
        screen.blit(name_surface, name_rect)
        
        # Calculate progress percentage
        progress_pct = min(1.0, self.research_manager.research_progress / self.research_manager.active_research["time_cost"])
        
        # Time remaining text
        if self.research_manager.research_complete:
            time_text = "Research Complete!"
            time_color = (150, 255, 150)
        else:
            time_left = self.research_manager.active_research["time_cost"] - self.research_manager.research_progress
            time_text = f"Time remaining: {time_left:.1f}s"
            time_color = (200, 200, 200)
        
        time_surface = font.render(time_text, True, time_color)
        time_rect = time_surface.get_rect(bottomright=(panel_rect.right - 15, panel_rect.bottom - 15))
        screen.blit(time_surface, time_rect)
        
        # Draw progress bar
        bar_rect = pygame.Rect(
            panel_rect.left + 15,
            name_rect.bottom + 10,
            panel_rect.width - 30,
            10
        )
        
        # Background bar
        pygame.draw.rect(screen, (50, 50, 50), bar_rect)
        
        # Progress bar
        progress_width = int(bar_rect.width * progress_pct)
        progress_rect = pygame.Rect(
            bar_rect.left,
            bar_rect.top,
            progress_width,
            bar_rect.height
        )
        
        if self.research_manager.research_complete:
            # Green for complete
            pygame.draw.rect(screen, (100, 200, 100), progress_rect)
        else:
            # Blue for in progress
            pygame.draw.rect(screen, (80, 150, 200), progress_rect)
    
    def enter(self):
        """Called when entering the research lab state"""
        # Reset UI state
        self.hovered_node = None
        self.selected_node = None
        
        # Clear button states first
        self.research_button_visible = False
        self.cancel_button_visible = False
        self.finish_button_visible = False
        
        # Update button visibility based on research manager state
        if self.research_manager:
            if self.research_manager.active_research:
                if self.research_manager.research_complete:
                    # Research is complete - show finish button
                    self.finish_button_visible = True
                else:
                    # Research is in progress - show cancel button
                    self.cancel_button_visible = True
        
        # Recalculate node positions to ensure proper layout
        self.calculate_node_positions()