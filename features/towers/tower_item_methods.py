# tower_item_methods.py
"""
This file contains the item handling methods to be added to the Tower class.
These methods provide robust handling of tower item slots.
"""
from registry import RESOURCE_MANAGER

def add_item(self, item, slot_index, resource_manager=None):
    """
    Add item to tower
    
    Args:
        item: Item to add
        slot_index: Slot index to place item (0 or 1)
        resource_manager: Optional ResourceManager to handle resource changes
        
    Returns:
        True if item added successfully
    """
    # Convert slot_index to integer
    try:
        slot_index = int(slot_index)
    except (ValueError, TypeError):
        # Default to 0 if not convertible
        slot_index = 1 if str(slot_index) == "1" else 0
    
    # Validate slot_index range
    if slot_index not in [0, 1]:
        slot_index = 0
    
    # Ensure item_slots is a properly initialized list
    if not isinstance(self.item_slots, list) or len(self.item_slots) != 2:
        self.item_slots = [None, None]
    
    # Get resource_manager from parameter or registry
    res_mgr = resource_manager
    if not res_mgr and self.registry and self.registry.has(RESOURCE_MANAGER):
        res_mgr = self.registry.get(RESOURCE_MANAGER)
    
    # Handle current item if present
    current_item = self.item_slots[slot_index]
    if current_item and res_mgr:
        # Return old item to inventory
        res_mgr.add_resource(current_item, 1)
    
    # Set the new item
    self.item_slots[slot_index] = item
    
    # Spend the item from inventory if resource_manager provided
    if res_mgr and item:
        res_mgr.spend_resource(item, 1)
    
    # Apply effects of all equipped items
    self.apply_item_effects()
    
    return True

def remove_item(self, slot_index, resource_manager=None):
    """
    Remove item from tower
    
    Args:
        slot_index: Slot index to remove item from (0 or 1)
        resource_manager: Optional ResourceManager to handle resource changes
        
    Returns:
        Name of removed item or None
    """
    # Convert slot_index to integer
    try:
        slot_index = int(slot_index)
    except (ValueError, TypeError):
        # Default to 0 if not convertible
        slot_index = 1 if str(slot_index) == "1" else 0
    
    # Validate slot_index range
    if slot_index not in [0, 1]:
        slot_index = 0
    
    # Ensure item_slots is a properly initialized list
    if not isinstance(self.item_slots, list) or len(self.item_slots) != 2:
        self.item_slots = [None, None]
        return None
    
    # Get resource_manager from parameter or registry
    res_mgr = resource_manager
    if not res_mgr and self.registry and self.registry.has(RESOURCE_MANAGER):
        res_mgr = self.registry.get(RESOURCE_MANAGER)
    
    # Get the item to remove
    removed_item = self.item_slots[slot_index]
    if removed_item is None:
        return None
    
    # Clear the slot
    self.item_slots[slot_index] = None
    
    # Apply updated item effects
    self.apply_item_effects()
    
    # Add the item back to inventory if resource_manager provided
    if res_mgr and removed_item:
        res_mgr.add_resource(removed_item, 1)
    
    return removed_item

def get_item_in_slot(self, slot_index):
    """
    Get item in specified slot
    
    Args:
        slot_index: Slot index to check (0 or 1)
        
    Returns:
        Item name or None if slot is empty or invalid
    """
    # Convert slot_index to integer
    try:
        slot_index = int(slot_index)
    except (ValueError, TypeError):
        # Default to 0 if not convertible
        slot_index = 1 if str(slot_index) == "1" else 0
    
    # Validate slot_index range
    if slot_index not in [0, 1]:
        slot_index = 0
    
    # Ensure item_slots is a properly initialized list
    if not isinstance(self.item_slots, list) or len(self.item_slots) != 2:
        self.item_slots = [None, None]
        return None
    
    # Return the item in the slot
    return self.item_slots[slot_index]

def apply_item_effects(self):
    """Apply effects from equipped items"""
    # Reset stats to base values
    self.damage = self.base_damage
    self.attack_speed = self.base_attack_speed
    self.ref_range = self.base_ref_range
    self.range = self.base_range
    
    # Reset tower-specific properties
    if self.tower_type == "Splash":
        self.ref_aoe_radius = self.base_ref_aoe_radius
        self.aoe_radius = self.base_aoe_radius
    elif self.tower_type == "Frozen":
        self.slow_effect = self.base_slow_effect
        self.slow_duration = self.base_slow_duration
    
    # Reset splash damage (for single-target towers)
    self.splash_damage_enabled = False
    self.splash_damage_radius = 0
    
    # Reset item visual effects
    self.item_glow_color = None
    
    # Reset Multitudation Vortex effects
    self.bounce_enabled = False
    self.bounce_chance = 0
    
    # Ensure item_slots is properly initialized
    if not isinstance(self.item_slots, list) or len(self.item_slots) != 2:
        self.item_slots = [None, None]
        self.has_item_effects = False
        return
    
    # No item effects to apply if both slots are empty
    if not any(self.item_slots):
        self.has_item_effects = False
        return
    
    self.has_item_effects = True
    
    # Apply effects from each equipped item
    from config import ITEM_EFFECTS
    
    for item in self.item_slots:
        if not item:
            continue
        
        # Get item effect information
        item_effect = ITEM_EFFECTS.get(item, {})
        
        # Apply Unstoppable Force effects
        if item == "Unstoppable Force":
            # Update visual effect
            self.item_glow_color = item_effect.get("glow_color", (255, 100, 50))
            
            # Apply AoE increase to AoE towers
            if self.tower_type in ["Splash", "Frozen"]:
                aoe_multiplier = item_effect.get("aoe_radius_multiplier", 1.3)
                
                if self.tower_type == "Splash":
                    self.ref_aoe_radius *= aoe_multiplier
                    self.aoe_radius = scale_value(self.ref_aoe_radius)
                elif self.tower_type == "Frozen":
                    # For Frozen Tower, increase slow effect area (which is the range)
                    self.ref_range *= aoe_multiplier
                    self.range = scale_value(self.ref_range)
            
            # Apply splash damage for single-target towers
            elif self.tower_type in ["Archer", "Sniper"]:
                self.splash_damage_enabled = True
                # Scale splash radius with tower range
                base_splash = item_effect.get("splash_damage_radius", 30)
                self.splash_damage_radius = scale_value(base_splash)
                
        # Apply Serene Spirit effects (not implemented yet)
        elif item == "Serene Spirit":
            # Update visual effect
            self.item_glow_color = item_effect.get("glow_color", (100, 200, 100))
            # Implementation for healing effect will be added later
            
        # Apply Multitudation Vortex effects
        elif item == "Multitudation Vortex":
            # Only apply to compatible towers (Archer and Sniper)
            compatible_towers = item_effect.get("compatible_towers", [])
            if self.tower_type in compatible_towers:
                self.bounce_enabled = True
                self.bounce_chance = item_effect.get("bounce_chance", 0.10)
                self.item_glow_color = item_effect.get("glow_color", (150, 100, 255))
