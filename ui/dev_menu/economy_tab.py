# ui/dev_menu/economy_tab.py
"""
Economy tab for developer menu with resource and item spawning options
"""
import pygame
from .components import Tab, Slider, Button, DropdownMenu
from config import (
    LOOT_BOSS_BASE_COIN_DROP,
    LOOT_MONSTER_BASE_COIN_DROP,
    LOOT_WAVE_SCALING,
    ITEM_COSTS,
    RESOURCE_TYPES,
    SPECIAL_RESOURCES,
    FOOD_RESOURCES
)

class EconomyTab(Tab):
    """Tab for adjusting resource generation and spawning resources/items"""
    def __init__(self, rect, game_instance):
        """
        Initialize economy tab
        
        Args:
            rect: Pygame Rect defining the tab area
            game_instance: Reference to the Game instance
        """
        super().__init__(rect)
        self.game = game_instance
        
        # Store original values for reset
        self.original_item_costs = {
            item: costs.copy() for item, costs in ITEM_COSTS.items()
        }
        self.original_loot_boss_coin_drop = LOOT_BOSS_BASE_COIN_DROP
        self.original_loot_monster_coin_drop = LOOT_MONSTER_BASE_COIN_DROP
        self.original_loot_wave_scaling = LOOT_WAVE_SCALING
        
        # Local copies of values that we'll modify
        self.item_costs = {
            item: costs.copy() for item, costs in ITEM_COSTS.items()
        }
        self.loot_boss_coin_drop = LOOT_BOSS_BASE_COIN_DROP
        self.loot_monster_coin_drop = LOOT_MONSTER_BASE_COIN_DROP
        self.loot_wave_scaling = LOOT_WAVE_SCALING
        
        # Initialize controls
        self._init_controls()
    
    def _init_controls(self):
        """Initialize all controls for this tab"""
        y_pos = self.rect.top + 20
        width = self.rect.width - 40
        
        # Title
        title_text = "Economy Balance"
        title_surface = self.title_font.render(title_text, True, (255, 255, 200))
        title_pos = (self.rect.left + 20, y_pos)
        y_pos += 30
        
        # Section: Resource Spawning
        section_text = "Resource Spawning"
        section_surface = self.font.render(section_text, True, (200, 200, 255))
        section_pos = (self.rect.left + 20, y_pos)
        y_pos += 25
        
        # Create buttons for basic resources in a grid layout
        button_width = 120
        button_height = 30
        button_margin = 10
        buttons_per_row = 3
        col_width = button_width + button_margin
        
        # Basic Resources
        basic_resources = [
            ("Stone +50", lambda: self._add_resource("Stone", 50)),
            ("Iron +20", lambda: self._add_resource("Iron", 20)),
            ("Copper +15", lambda: self._add_resource("Copper", 15)),
            ("Thorium +10", lambda: self._add_resource("Thorium", 10)),
            ("Wood +30", lambda: self._add_resource("Wood", 30)),
            ("Monster Coins +10", lambda: self._add_resource("Monster Coins", 10)),
        ]
        
        col = 0
        for label, callback in basic_resources:
            btn_x = self.rect.left + 20 + (col % buttons_per_row) * col_width
            btn_y = y_pos + (col // buttons_per_row) * (button_height + button_margin)
            
            self.controls.append(Button(
                (btn_x, btn_y),
                (button_width, button_height),
                label,
                callback
            ))
            col += 1
        
        # Move to next section
        y_pos += ((col + buttons_per_row - 1) // buttons_per_row) * (button_height + button_margin) + 20
        
        # Section: Advanced Resources
        section_text = "Advanced Resources"
        section_surface = self.font.render(section_text, True, (200, 200, 255))
        section_pos = (self.rect.left + 20, y_pos)
        y_pos += 25
        
        # Advanced Resources (cores and talent points)
        advanced_resources = [
            ("Force Core +1", lambda: self._add_resource("Force Core", 1)),
            ("Spirit Core +1", lambda: self._add_resource("Spirit Core", 1)),
            ("Magic Core +1", lambda: self._add_resource("Magic Core", 1)),
            ("Void Core +1", lambda: self._add_resource("Void Core", 1)),
            ("Talent Points +5", self._add_talent_points),
            ("All Cores +1", self._add_all_cores),
        ]
        
        col = 0
        for label, callback in advanced_resources:
            btn_x = self.rect.left + 20 + (col % buttons_per_row) * col_width
            btn_y = y_pos + (col // buttons_per_row) * (button_height + button_margin)
            
            self.controls.append(Button(
                (btn_x, btn_y),
                (button_width, button_height),
                label,
                callback,
                color=(100, 70, 120)  # Different color for advanced resources
            ))
            col += 1
            
        # Move to next section
        y_pos += ((col + buttons_per_row - 1) // buttons_per_row) * (button_height + button_margin) + 20
        
        # Section: Food Resources
        section_text = "Food Resources"
        section_surface = self.font.render(section_text, True, (200, 200, 255))
        section_pos = (self.rect.left + 20, y_pos)
        y_pos += 25
        
        # Food Resources
        food_resources = [
            ("Grain +10", lambda: self._add_resource("Grain", 10)),
            ("Fruit +10", lambda: self._add_resource("Fruit", 10)),
            ("Meat +10", lambda: self._add_resource("Meat", 10)),
            ("Dairy +10", lambda: self._add_resource("Dairy", 10)),
            ("All Food +10", self._add_all_food),
        ]
        
        col = 0
        for label, callback in food_resources:
            btn_x = self.rect.left + 20 + (col % buttons_per_row) * col_width
            btn_y = y_pos + (col // buttons_per_row) * (button_height + button_margin)
            
            self.controls.append(Button(
                (btn_x, btn_y),
                (button_width, button_height),
                label,
                callback,
                color=(70, 120, 70)  # Green color for food resources
            ))
            col += 1
            
        # Move to next section
        y_pos += ((col + buttons_per_row - 1) // buttons_per_row) * (button_height + button_margin) + 20
        
        # Section: Items/Equipment
        section_text = "Items / Equipment"
        section_surface = self.font.render(section_text, True, (200, 200, 255))
        section_pos = (self.rect.left + 20, y_pos)
        y_pos += 25
        
        # Items buttons
        items = [
            ("Unstoppable Force +1", lambda: self._add_resource("Unstoppable Force", 1)),
            ("Serene Spirit +1", lambda: self._add_resource("Serene Spirit", 1)),
            ("Multitudation Vortex +1", lambda: self._add_resource("Multitudation Vortex", 1)),
            ("All Items +1", self._add_all_items),
        ]
        
        col = 0
        for label, callback in items:
            btn_x = self.rect.left + 20 + (col % buttons_per_row) * col_width
            btn_y = y_pos + (col // buttons_per_row) * (button_height + button_margin)
            
            self.controls.append(Button(
                (btn_x, btn_y),
                (button_width, button_height),
                label,
                callback,
                color=(120, 100, 70)  # Brown color for items
            ))
            col += 1
            
        # Move to next section
        y_pos += ((col + buttons_per_row - 1) // buttons_per_row) * (button_height + button_margin) + 20
        
        # Section: Loot Drops
        section_text = "Loot Drop Settings"
        section_surface = self.font.render(section_text, True, (200, 200, 255))
        section_pos = (self.rect.left + 20, y_pos)
        y_pos += 25
        
        # Monster coin drop
        self.controls.append(Slider(
            (self.rect.left + 20, y_pos),
            width,
            "Base Monster Coin Drop:",
            self.loot_monster_coin_drop,
            0.5,
            3.0,
            0.5,
            self._set_monster_coin_drop,
            lambda x: f"{x:.1f}"
        ))
        y_pos += 30
        
        # Boss coin drop
        self.controls.append(Slider(
            (self.rect.left + 20, y_pos),
            width,
            "Base Boss Coin Drop:",
            self.loot_boss_coin_drop,
            5,
            20,
            1,
            self._set_boss_coin_drop,
            lambda x: f"{int(x)}"
        ))
        y_pos += 30
        
        # Loot wave scaling
        self.controls.append(Slider(
            (self.rect.left + 20, y_pos),
            width,
            "Loot Wave Scaling:",
            self.loot_wave_scaling,
            0.01,
            0.2,
            0.01,
            self._set_loot_wave_scaling,
            lambda x: f"{x:.2f}"
        ))
        y_pos += 40
        
        # Reset button
        reset_button = Button(
            (self.rect.centerx - 60, self.rect.bottom - 40),
            (120, 30),
            "Reset to Defaults",
            self.reset
        )
        self.controls.append(reset_button)
    
    def _add_resource(self, resource_type, amount):
        """Add resources via the resource manager"""
        if self.game and hasattr(self.game, 'resource_manager'):
            self.game.resource_manager.add_resource(resource_type, amount)
            print(f"Added {amount} {resource_type}")
    
    def _add_talent_points(self):
        """Add talent points to village if available"""
        if self.game and hasattr(self.game, 'village'):
            self.game.village.add_talent_points(5)
            print("Added 5 Talent Points")
        else:
            print("Village not available, cannot add Talent Points")
    
    def _add_all_cores(self):
        """Add one of each core type"""
        core_types = ["Force Core", "Spirit Core", "Magic Core", "Void Core"]
        for core in core_types:
            self._add_resource(core, 1)
        print("Added 1 of each Core type")
    
    def _add_all_food(self):
        """Add 10 of each food resource"""
        for food in FOOD_RESOURCES:
            self._add_resource(food, 10)
        print("Added 10 of each Food resource")
    
    def _add_all_items(self):
        """Add one of each special item"""
        items = ["Unstoppable Force", "Serene Spirit", "Multitudation Vortex"]
        for item in items:
            self._add_resource(item, 1)
        print("Added 1 of each Item")
    
    def _set_monster_coin_drop(self, value):
        """Callback for monster coin drop slider"""
        self.loot_monster_coin_drop = value
        # Update global monster coin drop
        from config_extension import set_loot_monster_base_coin_drop
        set_loot_monster_base_coin_drop(value)
    
    def _set_boss_coin_drop(self, value):
        """Callback for boss coin drop slider"""
        self.loot_boss_coin_drop = int(value)
        # Update global boss coin drop
        from config_extension import set_loot_boss_base_coin_drop
        set_loot_boss_base_coin_drop(int(value))
    
    def _set_loot_wave_scaling(self, value):
        """Callback for loot wave scaling slider"""
        self.loot_wave_scaling = value
        # Update global loot wave scaling
        from config_extension import set_loot_wave_scaling
        set_loot_wave_scaling(value)
    
    def reset(self):
        """Reset all economy values to original values"""
        # Reset loot drops
        from config_extension import (
            set_loot_monster_base_coin_drop,
            set_loot_boss_base_coin_drop,
            set_loot_wave_scaling
        )
        set_loot_monster_base_coin_drop(self.original_loot_monster_coin_drop)
        set_loot_boss_base_coin_drop(self.original_loot_boss_coin_drop)
        set_loot_wave_scaling(self.original_loot_wave_scaling)
        
        # Reset local values
        self.loot_monster_coin_drop = self.original_loot_monster_coin_drop
        self.loot_boss_coin_drop = self.original_loot_boss_coin_drop
        self.loot_wave_scaling = self.original_loot_wave_scaling
        
        # Update sliders with default values
        for control in self.controls:
            if hasattr(control, 'reset'):
                control.reset()
    
    def draw(self, screen):
        """Draw the tab and its controls"""
        super().draw(screen)
        
        # Draw title
        title_text = "Economy Balance"
        title_surface = self.title_font.render(title_text, True, (255, 255, 200))
        title_rect = title_surface.get_rect(midtop=(self.rect.centerx, self.rect.top + 20))
        screen.blit(title_surface, title_rect)
        
        # Draw section headers
        y_pos = self.rect.top + 60
        
        section_text = "Resource Spawning"
        section_surface = self.font.render(section_text, True, (200, 200, 255))
        screen.blit(section_surface, (self.rect.left + 20, y_pos))
        
        # Calculate position for Advanced Resources section
        button_height = 30
        button_margin = 10
        buttons_per_row = 3
        basic_resources_count = 6
        rows_basic = (basic_resources_count + buttons_per_row - 1) // buttons_per_row
        y_pos += 25 + rows_basic * (button_height + button_margin) + 20
        
        section_text = "Advanced Resources"
        section_surface = self.font.render(section_text, True, (200, 200, 255))
        screen.blit(section_surface, (self.rect.left + 20, y_pos))
        
        # Calculate position for Food Resources section
        advanced_resources_count = 6
        rows_advanced = (advanced_resources_count + buttons_per_row - 1) // buttons_per_row
        y_pos += 25 + rows_advanced * (button_height + button_margin) + 20
        
        section_text = "Food Resources"
        section_surface = self.font.render(section_text, True, (200, 200, 255))
        screen.blit(section_surface, (self.rect.left + 20, y_pos))
        
        # Calculate position for Items/Equipment section
        food_resources_count = 5
        rows_food = (food_resources_count + buttons_per_row - 1) // buttons_per_row
        y_pos += 25 + rows_food * (button_height + button_margin) + 20
        
        section_text = "Items / Equipment"
        section_surface = self.font.render(section_text, True, (200, 200, 255))
        screen.blit(section_surface, (self.rect.left + 20, y_pos))
        
        # Calculate position for Loot Drop Settings section
        items_count = 4
        rows_items = (items_count + buttons_per_row - 1) // buttons_per_row
        y_pos += 25 + rows_items * (button_height + button_margin) + 20
        
        section_text = "Loot Drop Settings"
        section_surface = self.font.render(section_text, True, (200, 200, 255))
        screen.blit(section_surface, (self.rect.left + 20, y_pos))
