# tower_items.py
"""
Tower item slot functionality - clean implementation
"""

def validate_item_slots(item_slots):
    """
    Ensure item_slots is properly formatted as a two-element list
    
    Args:
        item_slots: The item_slots to validate
        
    Returns:
        A properly formatted item_slots list [None, None]
    """
    # Always ensure item_slots is a 2-element list
    if not isinstance(item_slots, list) or len(item_slots) != 2:
        item_slots = [None, None]
    return item_slots

def validate_slot_index(slot_index):
    """
    Convert and validate a slot index to ensure it's 0 or 1
    
    Args:
        slot_index: The slot index to validate (can be int, str, etc.)
        
    Returns:
        An integer 0 or 1
    """
    # First try to convert to int
    try:
        slot_index = int(slot_index)
    except (ValueError, TypeError):
        # If conversion fails, use string comparison
        slot_index = 1 if str(slot_index) == "1" else 0
    
    # Ensure the index is valid (0 or 1)
    if slot_index not in [0, 1]:
        slot_index = 0
    
    return slot_index

def add_item(tower, item, slot_index, resource_manager=None):
    """
    Add item to tower slot
    
    Args:
        tower: Tower instance
        item: Item to add
        slot_index: Slot index to place item (0 or 1)
        resource_manager: Optional ResourceManager to handle resource changes
        
    Returns:
        True if item added successfully
    """
    # Validate slot index
    slot_index = validate_slot_index(slot_index)
    
    # Ensure item_slots is properly initialized
    tower.item_slots = validate_item_slots(tower.item_slots)
    
    # Get resource_manager from parameter or registry
    res_mgr = resource_manager
    if not res_mgr and hasattr(tower, 'registry') and tower.registry and tower.registry.has('RESOURCE_MANAGER'):
        res_mgr = tower.registry.get('RESOURCE_MANAGER')
    
    # Handle current item if present
    current_item = tower.item_slots[slot_index]
    if current_item and res_mgr:
        # Return old item to inventory
        res_mgr.add_resource(current_item, 1)
    
    # Set the new item
    tower.item_slots[slot_index] = item
    
    # Spend the item from inventory if resource_manager provided
    if res_mgr and item:
        res_mgr.spend_resource(item, 1)
    
    # Apply effects of all equipped items
    if hasattr(tower, 'apply_item_effects'):
        tower.apply_item_effects()
    
    return True

def remove_item(tower, slot_index, resource_manager=None):
    """
    Remove item from tower slot
    
    Args:
        tower: Tower instance
        slot_index: Slot index to remove item from (0 or 1)
        resource_manager: Optional ResourceManager to handle resource changes
        
    Returns:
        Name of removed item or None
    """
    # Validate slot index
    slot_index = validate_slot_index(slot_index)
    
    # Ensure item_slots is properly initialized
    tower.item_slots = validate_item_slots(tower.item_slots)
    
    # Get resource_manager from parameter or registry
    res_mgr = resource_manager
    if not res_mgr and hasattr(tower, 'registry') and tower.registry and tower.registry.has('RESOURCE_MANAGER'):
        res_mgr = tower.registry.get('RESOURCE_MANAGER')
    
    # Get the item to remove
    removed_item = tower.item_slots[slot_index]
    if removed_item is None:
        return None
    
    # Clear the slot
    tower.item_slots[slot_index] = None
    
    # Apply updated item effects
    if hasattr(tower, 'apply_item_effects'):
        tower.apply_item_effects()
    
    # Add the item back to inventory if resource_manager provided
    if res_mgr and removed_item:
        res_mgr.add_resource(removed_item, 1)
    
    return removed_item

def get_item_in_slot(tower, slot_index):
    """
    Get item in specified slot
    
    Args:
        tower: Tower instance
        slot_index: Slot index to check (0 or 1)
        
    Returns:
        Item name or None if slot is empty or invalid
    """
    # Validate slot index
    slot_index = validate_slot_index(slot_index)
    
    # Ensure item_slots is properly initialized
    tower.item_slots = validate_item_slots(tower.item_slots)
    
    # Return the item in the slot
    return tower.item_slots[slot_index]
