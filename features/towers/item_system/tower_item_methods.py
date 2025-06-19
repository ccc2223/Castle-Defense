"""
Compatibility layer for tower item methods

This file provides methods that can be monkey-patched onto the Tower class
for backward compatibility with existing code that calls methods directly.
"""
from registry import RESOURCE_MANAGER

def add_item(tower, item, slot_index, resource_manager=None):
    """
    Add item to tower slot - redirects to item_manager
    
    Args:
        tower: Tower instance
        item: Item to add
        slot_index: Slot index (0 or 1)
        resource_manager: Optional ResourceManager
        
    Returns:
        True if successful
    """
    if hasattr(tower, 'item_manager'):
        result = tower.item_manager.add_item(item, slot_index, resource_manager)
        
        # Sync with legacy item_slots
        if hasattr(tower, '_sync_item_slots'):
            tower._sync_item_slots()
        
        # Apply effects
        if hasattr(tower, 'apply_item_effects'):
            tower.apply_item_effects()
        
        return result
    else:
        # Fall back to legacy implementation
        try:
            slot_index = int(slot_index)
        except (ValueError, TypeError):
            slot_index = 1 if str(slot_index) == "1" else 0
        
        # Validate slot range
        if slot_index not in [0, 1]:
            slot_index = 0
        
        # Ensure item_slots is properly initialized
        if not isinstance(tower.item_slots, list) or len(tower.item_slots) != 2:
            tower.item_slots = [None, None]
            
        # Get resource_manager from parameter or registry
        res_mgr = resource_manager
        if not res_mgr and hasattr(tower, 'registry') and tower.registry and tower.registry.has(RESOURCE_MANAGER):
            res_mgr = tower.registry.get(RESOURCE_MANAGER)
        
        # Handle current item if present
        current_item = tower.item_slots[slot_index]
        if current_item and res_mgr:
            res_mgr.add_resource(current_item, 1)
            
        # Set the new item
        tower.item_slots[slot_index] = item
        
        # Spend the item from inventory if resource_manager provided
        if res_mgr and item:
            res_mgr.spend_resource(item, 1)
            
        # Apply effects
        if hasattr(tower, 'apply_item_effects'):
            tower.apply_item_effects()
        
        return True

def remove_item(tower, slot_index, resource_manager=None):
    """
    Remove item from tower slot - redirects to item_manager
    
    Args:
        tower: Tower instance
        slot_index: Slot index (0 or 1)
        resource_manager: Optional ResourceManager
        
    Returns:
        Removed item or None
    """
    if hasattr(tower, 'item_manager'):
        result = tower.item_manager.remove_item(slot_index, resource_manager)
        
        # Sync with legacy item_slots
        if hasattr(tower, '_sync_item_slots'):
            tower._sync_item_slots()
        
        # Apply effects
        if hasattr(tower, 'apply_item_effects'):
            tower.apply_item_effects()
        
        return result
    else:
        # Fall back to legacy implementation
        try:
            slot_index = int(slot_index)
        except (ValueError, TypeError):
            slot_index = 1 if str(slot_index) == "1" else 0
        
        # Validate slot range
        if slot_index not in [0, 1]:
            slot_index = 0
            
        # Ensure item_slots is properly initialized
        if not isinstance(tower.item_slots, list) or len(tower.item_slots) != 2:
            tower.item_slots = [None, None]
            return None
            
        # Get resource_manager from parameter or registry
        res_mgr = resource_manager
        if not res_mgr and hasattr(tower, 'registry') and tower.registry and tower.registry.has(RESOURCE_MANAGER):
            res_mgr = tower.registry.get(RESOURCE_MANAGER)
            
        # Get the item
        removed_item = tower.item_slots[slot_index]
        if removed_item is None:
            return None
            
        # Clear slot
        tower.item_slots[slot_index] = None
        
        # Apply effects
        if hasattr(tower, 'apply_item_effects'):
            tower.apply_item_effects()
        
        # Return to inventory
        if res_mgr and removed_item:
            res_mgr.add_resource(removed_item, 1)
            
        return removed_item

def get_item_in_slot(tower, slot_index):
    """
    Get item from specified slot - redirects to item_manager
    
    Args:
        tower: Tower instance
        slot_index: Slot index (0 or 1)
        
    Returns:
        Item or None
    """
    if hasattr(tower, 'item_manager'):
        return tower.item_manager.get_item(slot_index)
    else:
        # Fall back to legacy implementation
        try:
            slot_index = int(slot_index)
        except (ValueError, TypeError):
            slot_index = 1 if str(slot_index) == "1" else 0
        
        # Validate slot range
        if slot_index not in [0, 1]:
            slot_index = 0
        
        # Ensure item_slots is properly initialized
        if not isinstance(tower.item_slots, list) or len(tower.item_slots) != 2:
            tower.item_slots = [None, None]
            return None
            
        return tower.item_slots[slot_index]
