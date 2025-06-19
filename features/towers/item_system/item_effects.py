"""
Tower item effects application
"""
from config import ITEM_EFFECTS
from utils import scale_value

class TowerItemEffects:
    """Handles application of item effects to towers"""
    def __init__(self, tower):
        """
        Initialize with tower instance
        
        Args:
            tower: Tower instance
        """
        self.tower = tower
        
        # Store original values for resetting
        self.base_stats = {
            'damage': tower.base_damage,
            'attack_speed': tower.base_attack_speed,
            'range': tower.base_range,
            'ref_range': tower.base_ref_range
        }
        
        # Store tower-specific base values
        if tower.tower_type == "Splash" and hasattr(tower, 'base_aoe_radius'):
            self.base_stats['aoe_radius'] = tower.base_aoe_radius
            self.base_stats['ref_aoe_radius'] = tower.base_ref_aoe_radius
        elif tower.tower_type == "Frozen" and hasattr(tower, 'base_slow_effect'):
            self.base_stats['slow_effect'] = tower.base_slow_effect
            self.base_stats['slow_duration'] = tower.base_slow_duration
    
    def apply_effects(self, items):
        """
        Apply effects from a list of items
        
        Args:
            items: List of items (can include None)
        """
        # Reset to base values first
        self._reset_stats()
        
        # Apply each item's effect
        for item in items:
            if item:
                self._apply_item_effect(item)
        
        # Update has_item_effects flag
        self.tower.has_item_effects = any(item is not None for item in items)
    
    def _reset_stats(self):
        """Reset tower stats to base values"""
        # Reset basic stats
        self.tower.damage = self.base_stats['damage']
        self.tower.attack_speed = self.base_stats['attack_speed']
        self.tower.ref_range = self.base_stats['ref_range']
        self.tower.range = scale_value(self.tower.ref_range)
        
        # Reset tower-specific properties
        if self.tower.tower_type == "Splash" and 'aoe_radius' in self.base_stats:
            self.tower.ref_aoe_radius = self.base_stats['ref_aoe_radius']
            self.tower.aoe_radius = scale_value(self.tower.ref_aoe_radius)
        elif self.tower.tower_type == "Frozen" and 'slow_effect' in self.base_stats:
            self.tower.slow_effect = self.base_stats['slow_effect']
            self.tower.slow_duration = self.base_stats['slow_duration']
        
        # Reset special effect flags
        self.tower.splash_damage_enabled = False
        self.tower.splash_damage_radius = 0
        self.tower.bounce_enabled = False
        self.tower.bounce_chance = 0
        self.tower.healing_percentage = 0
        self.tower.item_glow_color = None
    
    def _apply_item_effect(self, item):
        """
        Apply effect for a specific item
        
        Args:
            item: Item name
        """
        # Get item effect information
        item_effect = ITEM_EFFECTS.get(item, {})
        
        # Apply based on item type
        if item == "Unstoppable Force":
            self._apply_unstoppable_force(item_effect)
        elif item == "Serene Spirit":
            self._apply_serene_spirit(item_effect)
        elif item == "Multitudation Vortex":
            self._apply_multitudation_vortex(item_effect)
    
    def _apply_unstoppable_force(self, effect):
        """
        Apply Unstoppable Force effect
        
        Args:
            effect: Effect data dictionary
        """
        # Set visual effect
        self.tower.item_glow_color = effect.get("glow_color", (255, 100, 50))
        
        # Apply AoE increase for AoE towers
        if self.tower.tower_type in ["Splash", "Frozen"]:
            aoe_multiplier = effect.get("aoe_radius_multiplier", 1.3)
            
            if self.tower.tower_type == "Splash":
                self.tower.ref_aoe_radius *= aoe_multiplier
                self.tower.aoe_radius = scale_value(self.tower.ref_aoe_radius)
            elif self.tower.tower_type == "Frozen":
                # For Frozen Tower, increase slow effect area
                self.tower.ref_range *= aoe_multiplier
                self.tower.range = scale_value(self.tower.ref_range)
        
        # Add splash damage to single-target towers
        elif self.tower.tower_type in ["Archer", "Sniper"]:
            self.tower.splash_damage_enabled = True
            base_splash = effect.get("splash_damage_radius", 30)
            self.tower.splash_damage_radius = scale_value(base_splash)
    
    def _apply_serene_spirit(self, effect):
        """
        Apply Serene Spirit effect
        
        Args:
            effect: Effect data dictionary
        """
        # Set visual effect
        self.tower.item_glow_color = effect.get("glow_color", (100, 200, 100))
        # Set healing percentage
        self.tower.healing_percentage = effect.get("healing_percentage", 0.05)
    
    def _apply_multitudation_vortex(self, effect):
        """
        Apply Multitudation Vortex effect
        
        Args:
            effect: Effect data dictionary
        """
        # Check if tower is compatible
        compatible_towers = effect.get("compatible_towers", [])
        if self.tower.tower_type in compatible_towers:
            self.tower.bounce_enabled = True
            self.tower.bounce_chance = effect.get("bounce_chance", 0.10)
            self.tower.item_glow_color = effect.get("glow_color", (150, 100, 255))
