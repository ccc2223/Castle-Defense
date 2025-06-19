"""
Comprehensive tests for the new tower item system
"""
import sys
import os
import pygame

# Add the parent directory to the path to allow importing game modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Initialize pygame for tests (needed for some components)
pygame.init()

def test_tower_item_system():
    """
    Test the new tower item system implementation
    """
    from features.towers.factory import TowerFactory
    
    print("\n===== TOWER ITEM SYSTEM TESTS =====")
    
    # Create test tower
    tower = TowerFactory.create_tower("Archer", (100, 100))
    
    # Test initialization
    print("\nTesting initialization:")
    has_item_manager = hasattr(tower, 'item_manager')
    has_item_effects = hasattr(tower, 'item_effects')
    has_item_slots = hasattr(tower, 'item_slots')
    
    print(f"Has item_manager: {has_item_manager}")
    print(f"Has item_effects: {has_item_effects}")
    print(f"Has item_slots: {has_item_slots}")
    print(f"item_slots length: {len(tower.item_slots) if has_item_slots and hasattr(tower.item_slots, '__len__') else 'N/A'}")
    
    # Test basic item operations (first slot)
    print("\nTesting adding item to slot 0:")
    tower.add_item("Unstoppable Force", 0, None)
    slot0_item = tower.get_item_in_slot(0)
    print(f"Item in slot 0: {slot0_item}")
    assert slot0_item == "Unstoppable Force", "Failed to add item to slot 0"
    
    # Test item operations (second slot)
    print("\nTesting adding item to slot 1:")
    tower.add_item("Serene Spirit", 1, None)
    slot1_item = tower.get_item_in_slot(1)
    print(f"Item in slot 1: {slot1_item}")
    assert slot1_item == "Serene Spirit", "Failed to add item to slot 1"
    
    # Verify both slots are working
    print("\nVerifying both slots:")
    item_slots = tower.item_slots
    manager_slots = tower.item_manager.get_all_items()
    print(f"item_slots: {item_slots}")
    print(f"item_manager slots: {manager_slots}")
    assert item_slots[0] == "Unstoppable Force" and item_slots[1] == "Serene Spirit", "Item slots not synced properly"
    
    # Test string index handling
    print("\nTesting string index handling:")
    tower.remove_item(0, None)
    tower.add_item("Multitudation Vortex", "0", None)  # Using string index
    slot0_item = tower.get_item_in_slot(0)
    print(f"Item in slot 0 after string index: {slot0_item}")
    assert slot0_item == "Multitudation Vortex", "String index failed"
    
    # Test invalid indices
    print("\nTesting invalid index handling:")
    tower.add_item("Unstoppable Force", 99, None)  # Invalid index should default to 0
    slot0_item = tower.get_item_in_slot(0)
    print(f"Item in slot 0 after invalid index: {slot0_item}")
    assert slot0_item == "Unstoppable Force", "Invalid index not properly handled"
    
    # Test item effects are applied
    print("\nTesting item effects:")
    print(f"has_item_effects: {tower.has_item_effects}")
    print(f"glow_color: {tower.item_glow_color}")
    
    if tower.tower_type in ["Archer", "Sniper"] and slot0_item == "Unstoppable Force":
        print(f"splash_damage_enabled: {tower.splash_damage_enabled}")
        print(f"splash_damage_radius: {tower.splash_damage_radius}")
    
    # Test removing items
    print("\nTesting item removal:")
    removed_item = tower.remove_item(0, None)
    print(f"Removed from slot 0: {removed_item}")
    slot0_item = tower.get_item_in_slot(0)
    print(f"Item in slot 0 after removal: {slot0_item}")
    assert slot0_item is None, "Failed to remove item from slot 0"
    
    # Test item sync after multiple operations
    print("\nTesting item sync after multiple operations:")
    tower.add_item("Unstoppable Force", 0, None)
    tower.remove_item(1, None)
    tower.add_item("Multitudation Vortex", 1, None)
    
    item_slots = tower.item_slots
    manager_slots = tower.item_manager.get_all_items()
    print(f"item_slots: {item_slots}")
    print(f"item_manager slots: {manager_slots}")
    
    assert item_slots[0] == "Unstoppable Force", "Sync failed for slot 0"
    assert item_slots[1] == "Multitudation Vortex", "Sync failed for slot 1"
    
    print("\nAll tower item system tests passed!")

if __name__ == "__main__":
    test_tower_item_system()
