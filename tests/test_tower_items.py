# test_tower_items.py
"""
Test script for tower item slot functionality
"""
import sys
import os

# Add parent directory to path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from features.towers.factory import TowerFactory

def test_tower_items():
    """Test tower item slot functionality"""
    print("\n===== TOWER ITEM SLOT TEST =====")
    
    # Create test tower
    tower = TowerFactory.create_tower("Archer", (100, 100))
    
    # Test initial state
    print("Initial state:")
    print(f"  item_slots: {tower.item_slots}")
    
    # Test add_item for both slots
    print("\nTesting add_item:")
    tower.add_item("Test Item 1", 0, None)
    print(f"  After adding to slot 0: {tower.item_slots}")
    
    tower.add_item("Test Item 2", 1, None)
    print(f"  After adding to slot 1: {tower.item_slots}")
    
    # Test get_item_in_slot
    print("\nTesting get_item_in_slot:")
    item0 = tower.get_item_in_slot(0)
    item1 = tower.get_item_in_slot(1)
    print(f"  Item in slot 0: {item0}")
    print(f"  Item in slot 1: {item1}")
    
    # Test type conversion with string indices
    print("\nTesting string indices:")
    tower.add_item("String Item 1", "0", None)
    print(f"  After adding to slot '0': {tower.item_slots}")
    tower.add_item("String Item 2", "1", None)
    print(f"  After adding to slot '1': {tower.item_slots}")
    
    # Test remove_item
    print("\nTesting remove_item:")
    tower.remove_item(0, None)
    print(f"  After removing from slot 0: {tower.item_slots}")
    
    tower.remove_item(1, None)
    print(f"  After removing from slot 1: {tower.item_slots}")
    
    # Test mixed operations
    print("\nTesting mixed operations:")
    tower.add_item("Mixed Item 1", 0, None)
    print(f"  After adding to slot 0: {tower.item_slots}")
    tower.add_item("Mixed Item 2", "1", None)
    print(f"  After adding to slot '1': {tower.item_slots}")
    item0 = tower.get_item_in_slot("0")
    item1 = tower.get_item_in_slot(1)
    print(f"  Get item with string index '0': {item0}")
    print(f"  Get item with int index 1: {item1}")
    
    print("\n===== TEST COMPLETE =====")
    
    # Verify final state
    return tower.item_slots[0] == "Mixed Item 1" and tower.item_slots[1] == "Mixed Item 2"

if __name__ == "__main__":
    success = test_tower_items()
    print(f"\nTest Result: {'PASSED' if success else 'FAILED'}")
