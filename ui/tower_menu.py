# ui/tower_menu.py
"""
Tower menu implementation for Castle Defense
"""
import pygame
import math
from .base_menu import Menu
from .elements import Button
from ui.utils import ResourceFormatter
from features.towers import ArcherTower, SniperTower, SplashTower, FrozenTower
from config import (
    TOWER_TYPES, 
    TOWER_MONSTER_COIN_COSTS, 
    TOWER_MONSTER_COIN_UPGRADE_MULTIPLIER,
    ITEM_COSTS, 
    ITEM_EFFECTS
)
from registry import ICON_MANAGER

class TowerMenu(Menu):
    """Menu for interacting with towers"""
    def __init__(self, screen, registry=None):
        """
        Initialize tower menu
        
        Args:
            screen: Pygame surface to draw on
            registry: Optional ComponentRegistry for accessing game components
        """
        super().__init__(screen)
        self.tower = None
        self.resource_manager = None
        self.registry = registry
        
        # Tab system
        self.tabs = ["Upgrades", "Items", "Stats"]
        self.current_tab = "Upgrades"
        
        # Scrolling
        self.scroll_offset = 0
        self.max_scroll = 0
        self.scroll_speed = 15
        
        # Tooltip system
        self.show_tooltip = False
        self.tooltip_text = ""
        self.tooltip_position = (0, 0)
        
        # Colors for visual styling
        self.HEADER_COLOR = (255, 200, 100)
        self.TEXT_COLOR = (220, 220, 220)
        self.SUBTEXT_COLOR = (180, 180, 180)
        self.BUTTON_COLOR = (80, 80, 80)
        self.BUTTON_HOVER_COLOR = (100, 100, 100)
        self.BUTTON_DISABLED_COLOR = (60, 60, 60)
        self.POSITIVE_COLOR = (100, 255, 100)
        self.NEGATIVE_COLOR = (255, 100, 100)
        self.TAB_ACTIVE_COLOR = (70, 70, 70)
        self.TAB_INACTIVE_COLOR = (50, 50, 50)
        self.CARD_BG_COLOR = (60, 60, 60)
        self.SLOT_COLOR = (80, 80, 100)
        self.SLOT_HOVER_COLOR = (100, 100, 120)
        self.SLOT_SELECTED_COLOR = (100, 120, 150)
        
        # Content areas
        self.upgrade_buttons = []
        self.item_buttons = []
        self.visible_buttons = []  # Buttons currently visible in active tab
        
        # Item submenu state
        self.show_item_submenu = False
        self.selected_slot = None
        self.item_submenu_rect = None
        
        # Default menu size
        self.menu_width = 320
        self.menu_height = 500
        self.size = (self.menu_width, self.menu_height)
        self.rect = pygame.Rect(self.position, self.size)
        
        # Resource icon size
        self.resource_icon_size = (16, 16)
    
    def set_tower(self, tower, resource_manager):
        """
        Set the tower this menu controls
        
        Args:
            tower: Tower instance
            resource_manager: ResourceManager instance for resource costs
        """
        self.tower = tower
        self.resource_manager = resource_manager
        self.title = f"{tower.tower_type} Tower"
        
        # Reset tab and scroll position
        self.current_tab = "Upgrades"
        self.scroll_offset = 0
        
        # Reset item submenu state
        self.show_item_submenu = False
        self.selected_slot = None
        
        # Calculate dynamic menu size based on tower type
        self.calculate_menu_size()
        
        # Clear existing buttons
        self.buttons = []
        self.upgrade_buttons = []
        self.item_buttons = []
        
        # Create the tab buttons
        self.create_tab_buttons()
        
        # Create upgrade buttons
        self.create_upgrade_buttons()
        
        # Set the visible buttons based on the current tab
        self.update_visible_buttons()
    
    def calculate_menu_size(self):
        """Calculate dynamic menu size based on tower type and content"""
        # Base menu width
        self.menu_width = 320
        
        # Calculate content height based on tower type
        base_height = 250  # Minimum height for basic content
        
        # Tower-specific adjustments
        if isinstance(self.tower, SplashTower):
            base_height += 60  # Extra space for AoE upgrade
        elif isinstance(self.tower, FrozenTower):
            base_height += 120  # Extra space for slow effect and duration upgrades
        
        # Constrain to reasonable bounds
        self.menu_height = min(550, max(400, base_height))
        
        # Update menu size and position
        self.size = (self.menu_width, self.menu_height)
        self.rect = pygame.Rect(
            self.position[0],
            self.position[1], 
            self.menu_width, 
            self.menu_height
        )
    
    def create_tab_buttons(self):
        """Create tab selection buttons"""
        tab_width = self.rect.width / len(self.tabs)
        for i, tab in enumerate(self.tabs):
            tab_button = Button(
                (self.rect.left + i * tab_width, self.rect.top + 30),
                (tab_width, 30),
                tab,
                lambda t=tab: self.change_tab(t)
            )
            # Add to main buttons list
            self.buttons.append(tab_button)
    
    def change_tab(self, tab):
        """
        Change the current tab
        
        Args:
            tab: Tab name to switch to
        """
        if tab in self.tabs:
            self.current_tab = tab
            self.scroll_offset = 0  # Reset scroll position
            
            # Close item submenu when changing tabs
            self.show_item_submenu = False
            self.selected_slot = None
            
            self.update_visible_buttons()
    
    def update_visible_buttons(self):
        """Update which buttons are visible based on the current tab"""
        # First remove all buttons except the tab buttons
        self.buttons = self.buttons[:len(self.tabs)]
        
        # Add the appropriate buttons for the current tab
        if self.current_tab == "Upgrades":
            self.buttons.extend(self.upgrade_buttons)
            self.visible_buttons = self.upgrade_buttons
        elif self.current_tab == "Items":
            # For items tab, we're now handling clicks separately
            # to detect slot clicks, so we don't add item buttons here
            self.visible_buttons = []
        else:
            # Stats tab has no buttons
            self.visible_buttons = []
    
    def create_upgrade_buttons(self):
        """Create tower upgrade buttons"""
        # Starting Y position for the first button
        y_pos = self.rect.top + 80
        button_width = self.rect.width - 40
        button_height = 30
        
        # Damage upgrade button
        damage_cost = self.tower.calculate_damage_upgrade_cost()
        damage_mc_cost = self.tower.calculate_damage_upgrade_monster_coin_cost()
        
        # Add Monster Coins to the cost dictionary for consistent display
        full_damage_cost = damage_cost.copy()
        full_damage_cost["Monster Coins"] = damage_mc_cost
        
        has_damage_resources = (self.resource_manager.has_resources(damage_cost) and 
                               self.resource_manager.get_resource("Monster Coins") >= damage_mc_cost)
        
        damage_button = Button(
            (self.rect.left + 20, y_pos),
            (button_width, button_height),
            "Upgrade Damage",
            self.upgrade_damage
        )
        damage_button.set_disabled(not has_damage_resources)
        damage_button.tag = "damage"  # Add tag for identification
        damage_button.cost_info = {
            "resource_cost": full_damage_cost,
            "has_resources": has_damage_resources
        }
        self.upgrade_buttons.append(damage_button)
        y_pos += 70  # Space for button and cost info
        
        # Attack speed upgrade button
        speed_cost = self.tower.calculate_attack_speed_upgrade_cost()
        speed_mc_cost = self.tower.calculate_attack_speed_upgrade_monster_coin_cost()
        
        # Add Monster Coins to the cost dictionary
        full_speed_cost = speed_cost.copy()
        full_speed_cost["Monster Coins"] = speed_mc_cost
        
        has_speed_resources = (self.resource_manager.has_resources(speed_cost) and
                              self.resource_manager.get_resource("Monster Coins") >= speed_mc_cost)
        
        speed_button = Button(
            (self.rect.left + 20, y_pos),
            (button_width, button_height),
            "Upgrade Attack Speed",
            self.upgrade_attack_speed
        )
        speed_button.set_disabled(not has_speed_resources)
        speed_button.tag = "speed"
        speed_button.cost_info = {
            "resource_cost": full_speed_cost,
            "has_resources": has_speed_resources
        }
        self.upgrade_buttons.append(speed_button)
        y_pos += 70
        
        # Range upgrade button
        range_cost = self.tower.calculate_range_upgrade_cost()
        range_mc_cost = self.tower.calculate_range_upgrade_monster_coin_cost()
        
        # Add Monster Coins to the cost dictionary
        full_range_cost = range_cost.copy()
        full_range_cost["Monster Coins"] = range_mc_cost
        
        has_range_resources = (self.resource_manager.has_resources(range_cost) and
                              self.resource_manager.get_resource("Monster Coins") >= range_mc_cost)
        
        range_button = Button(
            (self.rect.left + 20, y_pos),
            (button_width, button_height),
            "Upgrade Range",
            self.upgrade_range
        )
        range_button.set_disabled(not has_range_resources)
        range_button.tag = "range"
        range_button.cost_info = {
            "resource_cost": full_range_cost,
            "has_resources": has_range_resources
        }
        self.upgrade_buttons.append(range_button)
        y_pos += 70
        
        # Tower-specific upgrade buttons
        if isinstance(self.tower, SplashTower):
            # AoE upgrade button
            aoe_cost = self.tower.calculate_aoe_radius_upgrade_cost()
            aoe_mc_cost = self.tower.calculate_aoe_radius_upgrade_monster_coin_cost()
            
            # Add Monster Coins to the cost dictionary
            full_aoe_cost = aoe_cost.copy()
            full_aoe_cost["Monster Coins"] = aoe_mc_cost
            
            has_aoe_resources = (self.resource_manager.has_resources(aoe_cost) and
                               self.resource_manager.get_resource("Monster Coins") >= aoe_mc_cost)
            
            aoe_button = Button(
                (self.rect.left + 20, y_pos),
                (button_width, button_height),
                "Upgrade AoE Radius",
                self.upgrade_aoe
            )
            aoe_button.set_disabled(not has_aoe_resources)
            aoe_button.tag = "aoe"
            aoe_button.cost_info = {
                "resource_cost": full_aoe_cost,
                "has_resources": has_aoe_resources
            }
            self.upgrade_buttons.append(aoe_button)
            
        elif isinstance(self.tower, FrozenTower):
            # Slow effect upgrade button
            slow_cost = self.tower.calculate_slow_effect_upgrade_cost()
            slow_mc_cost = self.tower.calculate_slow_effect_upgrade_monster_coin_cost()
            
            # Add Monster Coins to the cost dictionary
            full_slow_cost = slow_cost.copy()
            full_slow_cost["Monster Coins"] = slow_mc_cost
            
            has_slow_resources = (self.resource_manager.has_resources(slow_cost) and
                                self.resource_manager.get_resource("Monster Coins") >= slow_mc_cost)
            
            slow_button = Button(
                (self.rect.left + 20, y_pos),
                (button_width, button_height),
                "Upgrade Slow Effect",
                self.upgrade_slow
            )
            slow_button.set_disabled(not has_slow_resources)
            slow_button.tag = "slow"
            slow_button.cost_info = {
                "resource_cost": full_slow_cost,
                "has_resources": has_slow_resources
            }
            self.upgrade_buttons.append(slow_button)
            y_pos += 70
            
            # Slow duration upgrade button
            duration_cost = self.tower.calculate_slow_duration_upgrade_cost()
            duration_mc_cost = self.tower.calculate_slow_duration_upgrade_monster_coin_cost()
            
            # Add Monster Coins to the cost dictionary
            full_duration_cost = duration_cost.copy()
            full_duration_cost["Monster Coins"] = duration_mc_cost
            
            has_duration_resources = (self.resource_manager.has_resources(duration_cost) and
                                    self.resource_manager.get_resource("Monster Coins") >= duration_mc_cost)
            
            duration_button = Button(
                (self.rect.left + 20, y_pos),
                (button_width, button_height),
                "Upgrade Slow Duration",
                self.upgrade_slow_duration
            )
            duration_button.set_disabled(not has_duration_resources)
            duration_button.tag = "duration"
            duration_button.cost_info = {
                "resource_cost": full_duration_cost,
                "has_resources": has_duration_resources
            }
            self.upgrade_buttons.append(duration_button)
    
    def handle_add_item_button_click(self):
        """Generic handler for add item button clicks"""
        for button in self.item_buttons:
            if hasattr(button, 'clicked') and button.clicked:
                button.clicked = False
                
                if hasattr(button, 'item_name') and hasattr(button, 'slot_index'):
                    item_name = str(button.item_name)
                    slot_index = int(button.slot_index)
                    return self.add_item_to_slot(item_name, slot_index)
        return False
        
    def handle_remove_item_button_click(self):
        """Generic handler for remove item button clicks"""
        for button in self.item_buttons:
            if hasattr(button, 'clicked') and button.clicked:
                button.clicked = False
                
                if hasattr(button, 'slot_index'):
                    slot_index = int(button.slot_index)
                    return self.remove_item_from_slot(slot_index)
        return False
    
    def create_item_submenu_buttons(self):
        """Create buttons for the item submenu dynamically"""
        # Clear previous item buttons
        self.item_buttons = []
        
        # Debug print to verify the selected slot
        print(f"Creating item submenu buttons for slot {self.selected_slot}")
        
        # Check available items
        available_items = []
        for item_name in ["Unstoppable Force", "Serene Spirit", "Multitudation Vortex"]:
            item_count = self.resource_manager.get_resource(item_name)
            if item_count > 0:
                # Check compatibility for Multitudation Vortex
                compatible = True
                if item_name == "Multitudation Vortex":
                    # Get compatible towers from item effects
                    compatible_towers = ITEM_EFFECTS.get(item_name, {}).get("compatible_towers", [])
                    compatible = self.tower.tower_type in compatible_towers
                    
                available_items.append({
                    "name": item_name,
                    "count": item_count,
                    "effect": ITEM_EFFECTS.get(item_name, {}).get("description", "No effect"),
                    "compatible": compatible
                })
        
        # Get current item in selected slot
        current_item = None
        if self.selected_slot is not None:
            current_item = self.tower.get_item_in_slot(self.selected_slot)
            print(f"Current item in slot {self.selected_slot}: {current_item}")
        
        # Create button for removing current item
        if current_item:
            button_y = self.item_submenu_rect.top + 80  # Position below item info
            button_width = self.item_submenu_rect.width - 20
            button_height = 30
            
            # Convert slot index to int and store directly
            slot_index = int(self.selected_slot)
            
            # Create a simpler remove button that stores data directly
            remove_button = Button(
                (self.item_submenu_rect.left + 10, button_y),
                (button_width, button_height),
                f"Remove {current_item}",
                self.handle_remove_item_button_click,  # Use a generic handler
                color=(120, 60, 60),  # Red-ish color for remove button
                hover_color=(150, 80, 80)
            )
            # Store the slot index directly on the button
            remove_button.slot_index = slot_index
            remove_button.tag = f"remove_item{slot_index}"
            self.item_buttons.append(remove_button)
        
        # Create buttons for adding items
        if not current_item:
            button_y = self.item_submenu_rect.top + 80
            
            # First check if we have any available items
            # Filter out incompatible items
            compatible_items = [item for item in available_items if item['compatible']]
            
            if not compatible_items:
                # No compatible items available
                return
                
            # Use filtered list for display
            available_items = compatible_items
                
            # Group items by type or effect for better organization
            # For example, we could group by effect type, rarity, etc.
            for item_info in available_items:
                button_width = self.item_submenu_rect.width - 20
                button_height = 30
                
                # Customize button appearance based on item type
                if "Force" in item_info['name']:
                    color = (140, 80, 50)  # Orange-ish for Force items
                    hover_color = (160, 100, 70)
                elif "Spirit" in item_info['name']:
                    color = (60, 120, 60)  # Green-ish for Spirit items
                    hover_color = (80, 140, 80)
                elif "Vortex" in item_info['name']:
                    color = (80, 60, 120)  # Purple-ish for Vortex items
                    hover_color = (100, 80, 140)
                else:
                    color = (80, 80, 80)  # Default gray
                    hover_color = (100, 100, 100)
                
                # Store both the item name and slot index using primitives
                # to avoid any reference issues
                item_name = str(item_info['name'])
                slot_index = int(self.selected_slot)
                
                # Print debug information
                print(f"Creating button to add {item_name} to slot {slot_index}")
                
                # Create a button with item count displayed in the text
                button_text = f"Add {item_info['name']} (x{item_info['count']})"
                
                add_button = Button(
                    (self.item_submenu_rect.left + 10, button_y),
                    (button_width, button_height),
                    button_text,
                    self.handle_add_item_button_click,  # Use a generic handler
                    color=color,
                    hover_color=hover_color
                )
                
                # Store data as primitive types to avoid reference issues
                add_button.item_name = item_name  # string
                add_button.slot_index = slot_index  # int
                add_button.tag = f"add_{item_info['name'].replace(' ', '_')}"
                add_button.item_info = item_info
                self.item_buttons.append(add_button)
                
                # Add more space between item buttons for readability
                button_y += 60
                
    def create_item_submenu(self, source_slot_rect):
        """
        Create the item submenu rectangle based on the selected slot
        
        Args:
            source_slot_rect: The rectangle of the slot that was clicked
        """
        submenu_width = 250
        submenu_height = 300
        
        # Position the submenu next to the slot
        submenu_x = source_slot_rect.right + 10
        submenu_y = source_slot_rect.top
        
        # Adjust if it would go off the right edge of the screen
        if submenu_x + submenu_width > self.screen.get_width():
            submenu_x = source_slot_rect.left - submenu_width - 10
            
        # Adjust if it would go off the bottom of the screen
        if submenu_y + submenu_height > self.screen.get_height():
            submenu_y = self.screen.get_height() - submenu_height - 10
        
        self.item_submenu_rect = pygame.Rect(
            submenu_x,
            submenu_y,
            submenu_width,
            submenu_height
        )
        
        # Create buttons for the submenu
        self.create_item_submenu_buttons()
        
    def get_slot_rect(self, slot_index, content_rect):
        """
        Get the rectangle for an item slot
        
        Args:
            slot_index: The slot index (0 or 1)
            content_rect: The content area rectangle
            
        Returns:
            Pygame.Rect for the slot
        """
        # Make slots larger and more visually distinct
        slot_size = (120, 120)
        slot_spacing = 40
        total_width = (slot_size[0] * 2) + slot_spacing
        
        # Center the slots horizontally
        start_x = content_rect.left + (content_rect.width - total_width) // 2
        
        # Place slots with enough vertical space for header text
        slot_y = content_rect.top + 100 - self.scroll_offset
        
        return pygame.Rect(
            start_x + (slot_size[0] + slot_spacing) * slot_index,
            slot_y,
            slot_size[0],
            slot_size[1]
        )
    
    def add_item_to_slot(self, item, slot_index):
        """Add item to tower slot"""
        if self.tower and self.resource_manager:
            # Ensure proper type handling
            slot_index = int(slot_index) if str(slot_index) in ['0', '1'] else 0
            
            # Call tower method with explicit string and int
            success = self.tower.add_item(str(item), int(slot_index), self.resource_manager)
            
            if success:
                self.show_item_submenu = False
                self.selected_slot = None
                self.current_tab = "Items"
                return True
        return False
    
    def remove_item_from_slot(self, slot_index):
        """Remove item from tower slot"""
        if self.tower and self.resource_manager:
            # Ensure proper type handling
            slot_index = int(slot_index) if str(slot_index) in ['0', '1'] else 0
            
            # Call tower method with explicit int
            removed_item = self.tower.remove_item(int(slot_index), self.resource_manager)
            
            if removed_item:
                self.show_item_submenu = False
                self.selected_slot = None
                self.current_tab = "Items"
                return True
        return False
    
    def upgrade_damage(self):
        """Upgrade tower damage"""
        if self.tower and self.resource_manager:
            if self.tower.upgrade_damage(self.resource_manager):
                # Update menu after successful upgrade
                self.set_tower(self.tower, self.resource_manager)
    
    def upgrade_attack_speed(self):
        """Upgrade tower attack speed"""
        if self.tower and self.resource_manager:
            if self.tower.upgrade_attack_speed(self.resource_manager):
                # Update menu after successful upgrade
                self.set_tower(self.tower, self.resource_manager)
    
    def upgrade_range(self):
        """Upgrade tower range"""
        if self.tower and self.resource_manager:
            if self.tower.upgrade_range(self.resource_manager):
                # Update menu after successful upgrade
                self.set_tower(self.tower, self.resource_manager)
    
    def upgrade_aoe(self):
        """Upgrade splash tower AoE radius"""
        if isinstance(self.tower, SplashTower) and self.resource_manager:
            if self.tower.upgrade_aoe_radius(self.resource_manager):
                # Update menu after successful upgrade
                self.set_tower(self.tower, self.resource_manager)
    
    def upgrade_slow(self):
        """Upgrade frozen tower slow effect"""
        if isinstance(self.tower, FrozenTower) and self.resource_manager:
            if self.tower.upgrade_slow_effect(self.resource_manager):
                # Update menu after successful upgrade
                self.set_tower(self.tower, self.resource_manager)
    
    def upgrade_slow_duration(self):
        """Upgrade frozen tower slow duration"""
        if isinstance(self.tower, FrozenTower) and self.resource_manager:
            if self.tower.upgrade_slow_duration(self.resource_manager):
                # Update menu after successful upgrade
                self.set_tower(self.tower, self.resource_manager)
    
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
        
        # Get current mouse position
        mouse_pos = pygame.mouse.get_pos()
        
        # Check if clicking outside menu to close it
        if event.type == pygame.MOUSEBUTTONDOWN:
            if not self.rect.collidepoint(mouse_pos):
                # Close the menu entirely
                self.active = False
                self.show_item_submenu = False
                self.selected_slot = None
                return True
            
            # Handle item submenu if it's open
            if self.show_item_submenu and self.item_submenu_rect:
                if not self.item_submenu_rect.collidepoint(mouse_pos):
                    # Close the submenu if clicking outside it but inside the main menu
                    self.show_item_submenu = False
                    self.selected_slot = None
                    return True
                else:
                    # Check button clicks in the submenu
                    for button in self.item_buttons:
                        if button.rect.collidepoint(mouse_pos):
                            button.click()
                            return True
                    return True
            
            # Check tab button clicks
            for button in self.buttons[:len(self.tabs)]:
                if button.rect.collidepoint(mouse_pos):
                    button.click()
                    return True
            
            # Handle item slot clicks in Items tab
            if self.current_tab == "Items":
                # Get content rect
                content_rect = pygame.Rect(
                    self.rect.left, 
                    self.rect.top + 60,  # Below tabs
                    self.rect.width,
                    self.rect.height - 60
                )
                
                # Check slot 1 click
                slot1_rect = self.get_slot_rect(0, content_rect)
                if slot1_rect.collidepoint(mouse_pos):
                    self.selected_slot = 0
                    self.show_item_submenu = True
                    
                    # Create submenu rect
                    self.create_item_submenu(slot1_rect)
                    return True
                
                # Check slot 2 click
                slot2_rect = self.get_slot_rect(1, content_rect)
                if slot2_rect.collidepoint(mouse_pos):
                    # Explicitly set selected_slot to 1 (second slot)
                    self.selected_slot = 1
                    print(f"Slot 2 clicked, setting selected_slot to {self.selected_slot}")
                    self.show_item_submenu = True
                    
                    # Create submenu rect
                    self.create_item_submenu(slot2_rect)
                    return True
            
            # Check other button clicks based on current tab
            if self.current_tab == "Upgrades":
                for button in self.upgrade_buttons:
                    if button.rect.collidepoint(mouse_pos):
                        button.click()
                        return True
                
        # Handle scroll wheel for content scrolling
        elif event.type == pygame.MOUSEWHEEL:
            if self.rect.collidepoint(mouse_pos):
                # Don't scroll if item submenu is open
                if not self.show_item_submenu:
                    # Scroll up or down
                    self.scroll_offset -= event.y * self.scroll_speed
                    # Constrain scrolling
                    self.scroll_offset = max(0, min(self.max_scroll, self.scroll_offset))
                return True
                
        # Handle mouse movement for hover states
        elif event.type == pygame.MOUSEMOTION:
            # Reset tooltip
            self.show_tooltip = False
            
            # Update buttons for hover state
            for button in self.buttons:
                button.update(mouse_pos)
            
            # Update item buttons if submenu is visible
            if self.show_item_submenu:
                for button in self.item_buttons:
                    button.update(mouse_pos)
                    
                    # Show tooltip for item buttons
                    if button.rect.collidepoint(mouse_pos) and hasattr(button, 'item_info'):
                        item_info = button.item_info
                        tooltip_text = f"{item_info['name']} (Available: {item_info['count']})\n{item_info['effect']}"
                        
                        self.show_tooltip = True
                        self.tooltip_text = tooltip_text
                        self.tooltip_position = mouse_pos
            
            # Update upgrade button tooltips
            if self.current_tab == "Upgrades":
                for button in self.upgrade_buttons:
                    if button.rect.collidepoint(mouse_pos) and hasattr(button, 'cost_info'):
                        cost_info = button.cost_info
                        tooltip_text = "Costs: " + ResourceFormatter.format_cost(cost_info["resource_cost"])
                        
                        self.show_tooltip = True
                        self.tooltip_text = tooltip_text
                        self.tooltip_position = mouse_pos
        
        return False
        
    def draw(self):
        """Draw tower menu with tower-specific info"""
        if not self.active or not self.tower:
            return
        
        # Draw base menu
        super().draw()
        
        # Draw tab buttons
        tab_width = self.rect.width / len(self.tabs)
        for i, tab in enumerate(self.tabs):
            tab_rect = pygame.Rect(
                self.rect.left + i * tab_width, 
                self.rect.top + 30, 
                tab_width, 
                30
            )
            
            # Draw tab background
            tab_color = self.TAB_ACTIVE_COLOR if tab == self.current_tab else self.TAB_INACTIVE_COLOR
            pygame.draw.rect(self.screen, tab_color, tab_rect)
            pygame.draw.rect(self.screen, (100, 100, 100), tab_rect, 1)
            
            # Draw tab text
            tab_text = self.small_font.render(tab, True, self.TEXT_COLOR)
            tab_text_rect = tab_text.get_rect(center=tab_rect.center)
            self.screen.blit(tab_text, tab_text_rect)
        
        # Create content clipping rect
        content_rect = pygame.Rect(
            self.rect.left, 
            self.rect.top + 60,  # Below tabs
            self.rect.width,
            self.rect.height - 60
        )
        
        # Draw current tab content
        if self.current_tab == "Upgrades":
            self.draw_upgrades_tab(content_rect)
        elif self.current_tab == "Items":
            self.draw_items_tab(content_rect)
        elif self.current_tab == "Stats":
            self.draw_stats_tab(content_rect)
            
        # Draw item submenu if it's visible
        if self.show_item_submenu and self.item_submenu_rect:
            self.draw_item_submenu()
            
        # Draw tooltip if active
        if self.show_tooltip:
            self.draw_tooltip()
    
    def draw_upgrades_tab(self, content_rect):
        """
        Draw the upgrades tab content
        
        Args:
            content_rect: Rectangle defining the content area
        """
        # Set up scrolling content area
        content_height = 0
        
        # Get icon manager if available
        icon_manager = None
        if self.registry and self.registry.has(ICON_MANAGER):
            icon_manager = self.registry.get(ICON_MANAGER)
        
        # Draw upgrade cards
        for i, button in enumerate(self.upgrade_buttons):
            # Calculate card position with scroll offset
            card_y = content_rect.top + 10 + i * 70 - self.scroll_offset
            card_height = 60
            
            # Only draw if within visible area
            if card_y + card_height > content_rect.top and card_y < content_rect.bottom:
                # Draw card background
                card_rect = pygame.Rect(
                    content_rect.left + 10,
                    card_y,
                    content_rect.width - 20,
                    card_height
                )
                pygame.draw.rect(self.screen, self.CARD_BG_COLOR, card_rect)
                pygame.draw.rect(self.screen, (100, 100, 100), card_rect, 1)
                
                # Draw upgrade information
                # Title based on button tag
                title = "Unknown Upgrade"
                level = 1
                
                if button.tag == "damage":
                    title = "Damage"
                    level = self.tower.damage_level
                elif button.tag == "speed":
                    title = "Attack Speed"
                    level = self.tower.attack_speed_level
                elif button.tag == "range":
                    title = "Range"
                    level = self.tower.range_level
                elif button.tag == "aoe":
                    title = "AoE Radius"
                    level = self.tower.aoe_radius_level
                elif button.tag == "slow":
                    title = "Slow Effect"
                    level = self.tower.slow_effect_level
                elif button.tag == "duration":
                    title = "Slow Duration"
                    level = self.tower.slow_duration_level
                
                # Draw title with level
                title_text = f"{title} (Level {level})"
                title_surface = self.small_font.render(title_text, True, self.TEXT_COLOR)
                self.screen.blit(title_surface, (card_rect.left + 10, card_y + 10))
                
                # Draw cost information with icons
                if hasattr(button, 'cost_info') and button.cost_info:
                    cost_info = button.cost_info
                    resource_cost = cost_info["resource_cost"]
                    has_resources = cost_info["has_resources"]
                    
                    # Format and draw costs using ResourceFormatter
                    sorted_resources = ResourceFormatter.sort_resources(resource_cost)
                    
                    # Format the cost display with appropriate colors
                    cost_color = self.POSITIVE_COLOR if has_resources else self.NEGATIVE_COLOR
                    cost_text = "Cost: " + ResourceFormatter.format_cost(resource_cost)
                    cost_surface = self.small_font.render(cost_text, True, cost_color)
                    
                    # Draw the cost text
                    self.screen.blit(cost_surface, (card_rect.left + 10, card_y + 35))
                
                # Draw the button itself (positioned on right side of card)
                button_rect = pygame.Rect(
                    card_rect.right - 100,
                    card_rect.centery - 15,
                    90,
                    30
                )
                
                # Update button position to match card
                button.rect = button_rect
                button.position = (button_rect.left, button_rect.top)
                button.draw(self.screen)
            
            # Update content height
            content_height += card_height + 10
        
        # Update max scroll
        self.max_scroll = max(0, content_height - (content_rect.height - 20))
        
        # Draw scroll indicators if needed
        if self.max_scroll > 0:
            self.draw_scroll_indicators(content_rect)
    
    def draw_items_tab(self, content_rect):
        """
        Draw the items tab content with slot selection
        
        Args:
            content_rect: Rectangle defining the content area
        """
        # Draw header background
        header_bg_rect = pygame.Rect(
            content_rect.left,
            content_rect.top,
            content_rect.width,
            40
        )
        pygame.draw.rect(self.screen, (40, 40, 50), header_bg_rect)
        
        # Draw section header
        header_y = content_rect.top + 10 - self.scroll_offset
        
        # Only draw if visible
        if header_y > content_rect.top - 30 and header_y < content_rect.bottom:
            header_text = self.font.render("Tower Item Slots", True, self.HEADER_COLOR)
            header_rect = header_text.get_rect(centerx=content_rect.centerx, top=content_rect.top + 10)
            self.screen.blit(header_text, header_rect)
        
        # Draw explanatory text
        info_y = header_bg_rect.bottom + 10
        info_text = "Click on a slot to manage items"
        info_surface = self.small_font.render(info_text, True, self.SUBTEXT_COLOR)
        info_rect = info_surface.get_rect(centerx=content_rect.centerx, top=info_y)
        self.screen.blit(info_surface, info_rect)
        
        # Get mouse position for hover effects
        mouse_pos = pygame.mouse.get_pos()
        
        # Get icon manager if available
        icon_manager = None
        if self.registry and self.registry.has(ICON_MANAGER):
            icon_manager = self.registry.get(ICON_MANAGER)
            
        # Draw a visual separator
        separator_y = info_rect.bottom + 10
        pygame.draw.line(
            self.screen,
            (100, 100, 120),
            (content_rect.left + 20, separator_y),
            (content_rect.right - 20, separator_y),
            1
        )
        
        # Draw the item slots
        for i in range(2):
            slot_rect = self.get_slot_rect(i, content_rect)
            slot_title_text = f"Item Slot {i+1}"
            
            # Only draw if slot is in the visible area
            if slot_rect.bottom > content_rect.top and slot_rect.top < content_rect.bottom:
                # Determine slot color based on state
                is_hovered = slot_rect.collidepoint(mouse_pos)
                is_selected = self.selected_slot == i
                
                # Create a glowing effect for hovered/selected slots
                if is_selected:
                    # Draw a pulsing glow effect around selected slot
                    pulse = (math.sin(pygame.time.get_ticks() * 0.005) + 1) * 0.5  # 0 to 1 pulsing
                    glow_size = int(5 + pulse * 3)
                    glow_rect = slot_rect.inflate(glow_size, glow_size)
                    pygame.draw.rect(self.screen, self.SLOT_SELECTED_COLOR, glow_rect, 3)
                    slot_color = self.SLOT_SELECTED_COLOR
                elif is_hovered:
                    slot_color = self.SLOT_HOVER_COLOR
                else:
                    slot_color = self.SLOT_COLOR
                
                # Draw slot background with a subtle gradient effect
                for y in range(slot_rect.height):
                    # Create a slight gradient from top to bottom
                    gradient_factor = y / slot_rect.height
                    gradient_color = (
                        min(255, slot_color[0] + int(20 * gradient_factor)),
                        min(255, slot_color[1] + int(20 * gradient_factor)),
                        min(255, slot_color[2] + int(20 * gradient_factor))
                    )
                    pygame.draw.line(
                        self.screen,
                        gradient_color,
                        (slot_rect.left, slot_rect.top + y),
                        (slot_rect.right, slot_rect.top + y)
                    )
                
                # Draw slot border
                border_color = (180, 180, 180) if is_hovered or is_selected else (150, 150, 150)
                pygame.draw.rect(self.screen, border_color, slot_rect, 2)
                
                # Draw slot title with a background
                title_bg_rect = pygame.Rect(
                    slot_rect.left,
                    slot_rect.top - 25,
                    slot_rect.width,
                    20
                )
                pygame.draw.rect(self.screen, (60, 60, 70), title_bg_rect)
                pygame.draw.rect(self.screen, (120, 120, 140), title_bg_rect, 1)
                
                slot_title = self.small_font.render(slot_title_text, True, self.TEXT_COLOR)
                title_rect = slot_title.get_rect(center=title_bg_rect.center)
                self.screen.blit(slot_title, title_rect)
                
                # Get current item in slot
                item = self.tower.get_item_in_slot(i)
                
                if item:
                    # Draw item icon if available
                    if icon_manager:
                        icon_id = icon_manager.get_resource_icon_id(item)
                        icon_size = (48, 48)  # Larger icon for better visibility
                        icon = icon_manager.get_icon(icon_id, icon_size)
                        icon_rect = icon.get_rect(center=(slot_rect.centerx, slot_rect.centery - 15))
                        self.screen.blit(icon, icon_rect)
                    
                    # Draw item name with a background for better readability
                    item_color = ResourceFormatter.get_resource_color(item)
                    bright_color = tuple(min(255, c + 40) for c in item_color)
                    
                    item_text = self.small_font.render(item, True, bright_color)
                    item_rect = item_text.get_rect(midtop=(slot_rect.centerx, slot_rect.centery + 20))
                    
                    # Draw text shadow for better visibility
                    shadow_surface = self.small_font.render(item, True, (0, 0, 0))
                    shadow_rect = shadow_surface.get_rect(midtop=(item_rect.midtop[0] + 1, item_rect.midtop[1] + 1))
                    self.screen.blit(shadow_surface, shadow_rect)
                    self.screen.blit(item_text, item_rect)
                    
                    # Draw brief effect summary
                    effect_desc = ITEM_EFFECTS.get(item, {}).get("description", "No effect")
                    # Shorten if too long
                    if len(effect_desc) > 30:
                        effect_desc = effect_desc[:27] + "..."
                    effect_text = self.small_font.render(effect_desc, True, self.SUBTEXT_COLOR)
                    effect_rect = effect_text.get_rect(midtop=(slot_rect.centerx, item_rect.bottom + 5))
                    self.screen.blit(effect_text, effect_rect)
                    
                    # Draw click instruction
                    if is_hovered:
                        instruction_bg = pygame.Rect(
                            slot_rect.left, 
                            slot_rect.bottom - 25,
                            slot_rect.width,
                            25
                        )
                        # Semi-transparent background for instruction
                        instruction_surf = pygame.Surface((instruction_bg.width, instruction_bg.height), pygame.SRCALPHA)
                        instruction_surf.fill((40, 40, 60, 180))
                        self.screen.blit(instruction_surf, instruction_bg)
                        
                        instruction_text = "Click to manage"
                        instruction = self.small_font.render(instruction_text, True, (220, 220, 220))
                        instruction_rect = instruction.get_rect(center=instruction_bg.center)
                        self.screen.blit(instruction, instruction_rect)
                else:
                    # Draw empty slot indicator
                    empty_text = self.small_font.render("Empty Slot", True, self.SUBTEXT_COLOR)
                    empty_rect = empty_text.get_rect(center=slot_rect.center)
                    self.screen.blit(empty_text, empty_rect)
                    
                    # Draw click instruction for empty slot
                    if is_hovered:
                        instruction_bg = pygame.Rect(
                            slot_rect.left, 
                            slot_rect.bottom - 25,
                            slot_rect.width,
                            25
                        )
                        # Semi-transparent background for instruction
                        instruction_surf = pygame.Surface((instruction_bg.width, instruction_bg.height), pygame.SRCALPHA)
                        instruction_surf.fill((40, 60, 40, 180))
                        self.screen.blit(instruction_surf, instruction_bg)
                        
                        instruction_text = "Click to add item"
                        instruction = self.small_font.render(instruction_text, True, (180, 220, 180))
                        instruction_rect = instruction.get_rect(center=instruction_bg.center)
                        self.screen.blit(instruction, instruction_rect)
    
    def draw_stats_tab(self, content_rect):
        """
        Draw the stats tab content
        
        Args:
            content_rect: Rectangle defining the content area
        """
        tower = self.tower
        
        # Starting positions
        y_pos = content_rect.top + 10 - self.scroll_offset
        padding = 25
        
        # Tower level information
        level_text = f"Tower Level: {tower.level}"
        level_surface = self.font.render(level_text, True, self.HEADER_COLOR)
        
        # Only draw if visible
        if y_pos > content_rect.top - 30 and y_pos < content_rect.bottom:
            self.screen.blit(level_surface, (content_rect.left + 15, y_pos))
        
        y_pos += 40
        
        # Draw separator
        if y_pos > content_rect.top - 5 and y_pos < content_rect.bottom:
            pygame.draw.line(
                self.screen,
                (100, 100, 100),
                (content_rect.left + 15, y_pos),
                (content_rect.right - 15, y_pos),
                1
            )
        
        y_pos += 15
        
        # Base stats with item effect indicators
        base_damage = tower.base_damage
        base_attack_speed = tower.base_attack_speed
        base_range = tower.base_range
        
        stats = [
            {
                "name": "Damage",
                "value": f"{tower.damage:.1f}",
                "level": tower.damage_level,
                "base": f"{base_damage:.1f}" if tower.damage != base_damage else None
            },
            {
                "name": "Attack Speed",
                "value": f"{tower.attack_speed:.2f}/s",
                "level": tower.attack_speed_level,
                "base": f"{base_attack_speed:.2f}/s" if tower.attack_speed != base_attack_speed else None
            },
            {
                "name": "Range",
                "value": f"{tower.range:.0f}",
                "level": tower.range_level,
                "base": f"{base_range:.0f}" if tower.range != base_range else None
            }
        ]
        
        # Add tower-specific stats
        if isinstance(tower, SplashTower):
            base_aoe = tower.base_aoe_radius
            stats.append({
                "name": "AoE Radius",
                "value": f"{tower.aoe_radius:.0f}",
                "level": tower.aoe_radius_level,
                "base": f"{base_aoe:.0f}" if tower.aoe_radius != base_aoe else None
            })
        elif isinstance(tower, FrozenTower):
            base_slow = tower.base_slow_effect
            base_duration = tower.base_slow_duration
            stats.append({
                "name": "Slow Effect",
                "value": f"{tower.slow_effect*100:.0f}%",
                "level": tower.slow_effect_level,
                "base": f"{base_slow*100:.0f}%" if tower.slow_effect != base_slow else None
            })
            stats.append({
                "name": "Slow Duration",
                "value": f"{tower.slow_duration:.1f}s",
                "level": tower.slow_duration_level,
                "base": f"{base_duration:.1f}s" if tower.slow_duration != base_duration else None
            })
        
        # Draw each stat
        for stat in stats:
            # Only draw if visible
            if y_pos > content_rect.top - padding and y_pos < content_rect.bottom:
                # Draw stat name with level
                name_text = f"{stat['name']} (Level {stat['level']}): "
                name_surface = self.small_font.render(name_text, True, self.TEXT_COLOR)
                self.screen.blit(name_surface, (content_rect.left + 20, y_pos))
                
                # Draw stat value
                value_surface = self.small_font.render(stat['value'], True, self.POSITIVE_COLOR)
                self.screen.blit(value_surface, (content_rect.left + 200, y_pos))
                
                # Draw base value if different
                if stat['base']:
                    base_text = f"(Base: {stat['base']})"
                    base_surface = self.small_font.render(base_text, True, self.SUBTEXT_COLOR)
                    self.screen.blit(base_surface, (content_rect.left + 240, y_pos))
            
            y_pos += padding
        
        y_pos += 15
        
        # Draw item effects section if there are any items equipped
        if any(tower.item_slots):
            # Only draw if visible
            if y_pos > content_rect.top - 5 and y_pos < content_rect.bottom:
                pygame.draw.line(
                    self.screen,
                    (100, 100, 100),
                    (content_rect.left + 15, y_pos),
                    (content_rect.right - 15, y_pos),
                    1
                )
            
            y_pos += 15
            
            # Item effects header
            if y_pos > content_rect.top - 30 and y_pos < content_rect.bottom:
                effects_header = self.font.render("Item Effects", True, self.HEADER_COLOR)
                self.screen.blit(effects_header, (content_rect.left + 15, y_pos))
            
            y_pos += 30
            
            # Get icon manager if available
            icon_manager = None
            if self.registry and self.registry.has(ICON_MANAGER):
                icon_manager = self.registry.get(ICON_MANAGER)
            
            # List equipped items and their effects
            for i, item in enumerate(tower.item_slots):
                if item:
                    if y_pos > content_rect.top - padding and y_pos < content_rect.bottom:
                        # Draw item icon if available
                        if icon_manager:
                            icon_id = icon_manager.get_resource_icon_id(item)
                            icon = icon_manager.get_icon(icon_id, self.resource_icon_size)
                            icon_rect = icon.get_rect(midleft=(content_rect.left + 20, y_pos + self.resource_icon_size[1]//2))
                            self.screen.blit(icon, icon_rect)
                            item_text_x = icon_rect.right + 5
                        else:
                            item_text_x = content_rect.left + 20
                        
                        # Get item color
                        item_color = ResourceFormatter.get_resource_color(item)
                        bright_color = tuple(min(255, c + 40) for c in item_color)
                        
                        # Draw item name
                        item_text = self.small_font.render(f"{item}:", True, bright_color)
                        self.screen.blit(item_text, (item_text_x, y_pos))
                    
                    y_pos += 20
                    
                    # Draw item effect
                    effect_desc = ITEM_EFFECTS.get(item, {}).get("description", "No effect")
                    if y_pos > content_rect.top - padding and y_pos < content_rect.bottom:
                        effect_text = self.small_font.render(effect_desc, True, self.SUBTEXT_COLOR)
                        self.screen.blit(effect_text, (content_rect.left + 40, y_pos))
                    
                    y_pos += padding
            
            # If splash damage enabled from Unstoppable Force item
            if tower.splash_damage_enabled and tower.tower_type in ["Archer", "Sniper"]:
                if y_pos > content_rect.top - 30 and y_pos < content_rect.bottom:
                    splash_text = f"Splash Damage Radius: {tower.splash_damage_radius:.0f}"
                    splash_surface = self.small_font.render(splash_text, True, self.POSITIVE_COLOR)
                    self.screen.blit(splash_surface, (content_rect.left + 30, y_pos))
                
                y_pos += padding
        
        # Update content height and max scroll
        content_height = y_pos - content_rect.top + 20
        self.max_scroll = max(0, content_height - content_rect.height)
        
        # Draw scroll indicators if needed
        if self.max_scroll > 0:
            self.draw_scroll_indicators(content_rect)
            
    def draw_item_submenu(self):
        """Draw the item submenu for the selected slot"""
        if not self.item_submenu_rect or self.selected_slot is None:
            return
        
        # Draw submenu background with semi-transparency
        submenu_bg = pygame.Surface(self.item_submenu_rect.size, pygame.SRCALPHA)
        submenu_bg.fill((40, 40, 50, 240))  # Semi-transparent background
        self.screen.blit(submenu_bg, self.item_submenu_rect)
        pygame.draw.rect(self.screen, (120, 120, 150), self.item_submenu_rect, 2)
        
        # Draw submenu title
        current_item = self.tower.get_item_in_slot(self.selected_slot)
        if current_item:
            title_text = f"Manage Item in Slot {self.selected_slot + 1}"
        else:
            title_text = f"Add Item to Slot {self.selected_slot + 1}"
            
        title_surface = self.font.render(title_text, True, self.HEADER_COLOR)
        title_rect = title_surface.get_rect(centerx=self.item_submenu_rect.centerx, top=self.item_submenu_rect.top + 10)
        self.screen.blit(title_surface, title_rect)
        
        # Get icon manager if available
        icon_manager = None
        if self.registry and self.registry.has(ICON_MANAGER):
            icon_manager = self.registry.get(ICON_MANAGER)
            
        # If item is equipped, show current item details
        if current_item:
            # Draw separator below title
            pygame.draw.line(
                self.screen,
                (100, 100, 120),
                (self.item_submenu_rect.left + 10, title_rect.bottom + 10),
                (self.item_submenu_rect.right - 10, title_rect.bottom + 10),
                1
            )
            
            # Get item color
            item_color = ResourceFormatter.get_resource_color(current_item)
            bright_color = tuple(min(255, c + 40) for c in item_color)
            
            # Draw item icon if available
            if icon_manager:
                icon_id = icon_manager.get_resource_icon_id(current_item)
                icon_size = (32, 32)  # Larger icon for better visibility
                icon = icon_manager.get_icon(icon_id, icon_size)
                icon_rect = icon.get_rect(center=(self.item_submenu_rect.centerx, title_rect.bottom + 30))
                self.screen.blit(icon, icon_rect)
                
                # Update current_rect Y position to account for icon
                current_y = icon_rect.bottom + 10
            else:
                current_y = title_rect.bottom + 20
            
            # Draw current item name
            current_text = f"Current Item: {current_item}"
            current_surface = self.small_font.render(current_text, True, bright_color)
            current_rect = current_surface.get_rect(midtop=(self.item_submenu_rect.centerx, current_y))
            self.screen.blit(current_surface, current_rect)
            
            # Draw item effect
            effect_desc = ITEM_EFFECTS.get(current_item, {}).get("description", "No effect")
            effect_surface = self.small_font.render(effect_desc, True, self.SUBTEXT_COLOR)
            effect_rect = effect_surface.get_rect(midtop=(self.item_submenu_rect.centerx, current_rect.bottom + 10))
            self.screen.blit(effect_surface, effect_rect)
            
            # Draw remove button
            for button in self.item_buttons:
                button.draw(self.screen)
                
        else:
            # Draw available items section
            available_header = self.small_font.render("Available Items:", True, self.TEXT_COLOR)
            available_rect = available_header.get_rect(midtop=(self.item_submenu_rect.centerx, title_rect.bottom + 10))
            self.screen.blit(available_header, available_rect)
            
            # Draw separator below header
            pygame.draw.line(
                self.screen,
                (100, 100, 120),
                (self.item_submenu_rect.left + 10, available_rect.bottom + 5),
                (self.item_submenu_rect.right - 10, available_rect.bottom + 5),
                1
            )
            
            # Check if we have any available items
            if not self.item_buttons:
                # Check if there are compatible items or just no items at all
                has_incompatible = any(item_name for item_name in ["Unstoppable Force", "Serene Spirit", "Multitudation Vortex"]
                                     if self.resource_manager.get_resource(item_name) > 0)
                
                if has_incompatible:
                    no_items_text = self.small_font.render("No compatible items for this tower", True, self.NEGATIVE_COLOR)
                else:
                    no_items_text = self.small_font.render("No items available", True, self.NEGATIVE_COLOR)
                    
                no_items_rect = no_items_text.get_rect(center=self.item_submenu_rect.center)
                self.screen.blit(no_items_text, no_items_rect)
            else:
                # Draw each item button
                for button in self.item_buttons:
                    button.draw(self.screen)
                    
                    # Get item info if available
                    if hasattr(button, 'item_info'):
                        item_info = button.item_info
                        effect_y = button.rect.bottom + 5
                        
                        # Draw item icon if available
                        if icon_manager:
                            icon_id = icon_manager.get_resource_icon_id(item_info['name'])
                            icon_size = (24, 24)
                            icon = icon_manager.get_icon(icon_id, icon_size)
                            
                            # Position icon to the left of the button
                            icon_rect = icon.get_rect(midright=(button.rect.left - 5, button.rect.centery))
                            self.screen.blit(icon, icon_rect)
                        
                        # Draw item effect description
                        effect_text = self.small_font.render(item_info['effect'], True, self.SUBTEXT_COLOR)
                        # Make sure the text fits within the submenu by wrapping if necessary
                        max_width = button.rect.width
                        if effect_text.get_width() > max_width:
                            # Simple text wrapping - split at a space if too long
                            words = item_info['effect'].split()
                            line1 = ""
                            line2 = ""
                            for word in words:
                                test_line = line1 + " " + word if line1 else word
                                test_width = self.small_font.size(test_line)[0]
                                if test_width <= max_width:
                                    line1 = test_line
                                else:
                                    line2 = line2 + " " + word if line2 else word
                            
                            # Draw the wrapped text
                            if line1:
                                line1_surf = self.small_font.render(line1, True, self.SUBTEXT_COLOR)
                                self.screen.blit(line1_surf, (button.rect.left, effect_y))
                                effect_y += 15
                            if line2:
                                line2_surf = self.small_font.render(line2, True, self.SUBTEXT_COLOR)
                                self.screen.blit(line2_surf, (button.rect.left, effect_y))
                        else:
                            # Draw single line if it fits
                            self.screen.blit(effect_text, (button.rect.left, effect_y))
