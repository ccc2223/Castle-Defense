# features/towers/factory.py
"""
Factory for tower creation in Castle Defense
"""
from .archer_tower import ArcherTower
from .sniper_tower import SniperTower
from .splash_tower import SplashTower
from .frozen_tower import FrozenTower

class TowerFactory:
    """Factory class for creating tower instances"""
    
    @staticmethod
    def create_tower(tower_type, position, registry=None):
        """
        Create a tower of the specified type at the given position
        
        Args:
            tower_type: String indicating tower type
            position: Tuple of (x, y) coordinates
            registry: Optional ComponentRegistry for tower dependencies
            
        Returns:
            Tower instance
            
        Raises:
            ValueError: If tower_type is invalid
        """
        # Create tower based on type, passing registry if provided
        tower = None
        if tower_type == "Archer":
            tower = ArcherTower(position, registry)
        elif tower_type == "Sniper":
            tower = SniperTower(position, registry)
        elif tower_type == "Splash":
            tower = SplashTower(position, registry)
        elif tower_type == "Frozen":
            tower = FrozenTower(position, registry)
        else:
            raise ValueError(f"Unknown tower type: {tower_type}")
        
        # Ensure the tower has the new item system initialized
        if tower and not hasattr(tower, 'item_manager'):
            try:
                from features.towers.item_system import TowerItemManager, TowerItemEffects
                tower.item_manager = TowerItemManager(tower)
                tower.item_effects = TowerItemEffects(tower)
                
                # For backward compatibility
                if not hasattr(tower, 'item_slots') or not isinstance(tower.item_slots, list) or len(tower.item_slots) != 2:
                    tower.item_slots = [None, None]
            except ImportError:
                # If for some reason the import fails, we'll use the old system
                if not hasattr(tower, 'item_slots'):
                    tower.item_slots = [None, None]
        
        return tower
