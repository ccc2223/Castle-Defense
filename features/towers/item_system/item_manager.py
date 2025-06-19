"""
Tower item slot and manager implementation
"""
from registry import RESOURCE_MANAGER

class TowerItemSlot:
    """Single item slot with encapsulated functionality"""
    def __init__(self):
        self.item = None
    
    def set_item(self, item):
        """
        Set item, returning any previous item
        
        Args:
            item: Item to set
            
        Returns:
            Previous item or None
        """
        previous = self.item
        self.item = item
        return previous
    
    def get_item(self):
        """
        Get the current item without removing it
        
        Returns:
            Current item or None
        """
        return self.item
    
    def remove_item(self):
        """
        Remove and return the current item
        
        Returns:
            The removed item or None
        """
        item = self.item
        self.item = None
        return item
    
    def is_empty(self):
        """
        Check if the slot is empty
        
        Returns:
            True if empty, False otherwise
        """
        return self.item is None


class TowerItemManager:
    """Manages a collection of item slots for a tower"""
    def __init__(self, tower, num_slots=2):
        """
        Initialize the item manager
        
        Args:
            tower: Tower instance
            num_slots: Number of item slots
        """
        self.tower = tower
        self.slots = [TowerItemSlot() for _ in range(num_slots)]
        self.registry = tower.registry if hasattr(tower, 'registry') else None
    
    def add_item(self, item, slot_index, resource_manager=None):
        """
        Add item to specified slot, handling resource management
        
        Args:
            item: Item to add
            slot_index: Slot index (0 or 1)
            resource_manager: Optional ResourceManager
            
        Returns:
            True if successful
        """
        # Validate and normalize slot index
        slot_index = self._normalize_slot_index(slot_index)
        
        # Get resource manager if not provided
        res_mgr = self._get_resource_manager(resource_manager)
        
        # Get current item to return to inventory if needed
        current_item = self.slots[slot_index].get_item()
        
        # Set new item
        self.slots[slot_index].set_item(item)
        
        # Handle resource management
        if res_mgr:
            if current_item:
                res_mgr.add_resource(current_item, 1)
            if item:
                res_mgr.spend_resource(item, 1)
        
        return True
    
    def remove_item(self, slot_index, resource_manager=None):
        """
        Remove item from specified slot, handling resource return
        
        Args:
            slot_index: Slot index (0 or 1)
            resource_manager: Optional ResourceManager
            
        Returns:
            Removed item or None
        """
        # Validate and normalize slot index
        slot_index = self._normalize_slot_index(slot_index)
        
        # Get resource manager if not provided
        res_mgr = self._get_resource_manager(resource_manager)
        
        # Remove item from slot
        removed_item = self.slots[slot_index].remove_item()
        
        # Return to inventory if needed
        if res_mgr and removed_item:
            res_mgr.add_resource(removed_item, 1)
        
        return removed_item
    
    def get_item(self, slot_index):
        """
        Get item from specified slot without removing it
        
        Args:
            slot_index: Slot index (0 or 1)
            
        Returns:
            Item or None
        """
        # Validate and normalize slot index
        slot_index = self._normalize_slot_index(slot_index)
        
        return self.slots[slot_index].get_item()
    
    def get_all_items(self):
        """
        Get list of all items (including None for empty slots)
        
        Returns:
            List of items
        """
        return [slot.get_item() for slot in self.slots]
    
    def _normalize_slot_index(self, index):
        """
        Convert and validate slot index to ensure it's within bounds
        
        Args:
            index: Slot index (string or int)
            
        Returns:
            Normalized integer index
        """
        try:
            # Try to convert to integer
            slot_index = int(index)
        except (ValueError, TypeError):
            # If conversion fails, use string comparison for special cases
            slot_index = 1 if str(index) == "1" else 0
        
        # Ensure index is within bounds
        if slot_index < 0 or slot_index >= len(self.slots):
            slot_index = 0
        
        return slot_index
    
    def _get_resource_manager(self, resource_manager=None):
        """
        Get resource manager from parameter or registry
        
        Args:
            resource_manager: Optional ResourceManager
            
        Returns:
            ResourceManager instance or None
        """
        if resource_manager:
            return resource_manager
        elif self.registry and self.registry.has(RESOURCE_MANAGER):
            return self.registry.get(RESOURCE_MANAGER)
        return None
    
    def to_list(self):
        """
        Convert to simple list for backwards compatibility
        
        Returns:
            List of items
        """
        return self.get_all_items()
