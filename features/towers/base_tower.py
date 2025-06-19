# towers/base_tower.py
"""
Base Tower class for Castle Defense
"""
import pygame
import math
from config import (
    TOWER_TYPES,
    TOWER_UPGRADE_COST_MULTIPLIER,
    TOWER_MONSTER_COIN_COSTS,
    TOWER_MONSTER_COIN_UPGRADE_MULTIPLIER,
    TOWER_DAMAGE_UPGRADE_MULTIPLIER,
    TOWER_ATTACK_SPEED_UPGRADE_MULTIPLIER,
    TOWER_RANGE_UPGRADE_MULTIPLIER,
    TOWER_AOE_UPGRADE_MULTIPLIER,
    ITEM_EFFECTS
)

from utils import distance, calculate_angle, scale_position, scale_size, scale_value
from registry import RESOURCE_MANAGER, ANIMATION_MANAGER, WAVE_MANAGER

class Tower:
    """Base class for all towers"""
    def __init__(self, position, tower_type, registry=None):
        """
        Initialize tower with position and type
        
        Args:
            position: Tuple of (x, y) coordinates
            tower_type: String indicating tower type
            registry: Optional ComponentRegistry for tower dependencies
        """
        self.position = position
        self.tower_type = tower_type
        self.level = 1
        self.registry = registry  # Store registry for later use
        
        # Individual upgrade path levels
        self.damage_level = 1
        self.attack_speed_level = 1
        self.range_level = 1
        
        # Set stats from config - scale range based on screen size
        tower_config = TOWER_TYPES.get(tower_type, {})
        self.damage = tower_config.get("damage", 10)
        self.attack_speed = tower_config.get("attack_speed", 1.0)
        
        # Store both reference and scaled range
        self.ref_range = tower_config.get("range", 150)
        self.range = scale_value(self.ref_range)
        
        # Store base stats for item effect calculations
        self.base_damage = self.damage
        self.base_attack_speed = self.attack_speed
        self.base_range = self.range
        self.base_ref_range = self.ref_range
        
        # Attack tracking
        self.attack_timer = 0
        self.targets = []
        self.current_target = None  # Track current target for animations
        
        # Animation flags
        self.is_attacking = False
        self.attack_animation_time = 0
        
        # Initialize new item system
        from features.towers.item_system import TowerItemManager, TowerItemEffects
        self.item_manager = TowerItemManager(self)
        self.item_effects = TowerItemEffects(self)
        
        # For backwards compatibility
        self.item_slots = [None, None]
        self.has_item_effects = False
        
        # Multitudation Vortex effect
        self.bounce_enabled = False
        self.bounce_chance = 0
        
        # Talent effect multipliers
        self.talent_damage_multiplier = 1.0
        self.talent_range_multiplier = 1.0
        self.talent_critical_hit_chance = 0.0
        
        # Splash damage from Unstoppable Force (for single-target towers)
        self.splash_damage_enabled = False
        self.splash_damage_radius = 0
        
        # Item visual effects
        self.item_glow_color = None
        self.item_glow_intensity = 0
        
        # Visual properties
        self.ref_size = (40, 40)
        self.size = scale_size(self.ref_size)
        self.rect = pygame.Rect(
            position[0] - self.size[0] // 2,
            position[1] - self.size[1] // 2,
            self.size[0],
            self.size[1]
        )
        self.color = self.get_color_from_type(tower_type)
        
        # For selection and highlight
        self.selected = False
        
        # Tower-specific properties
        self.initialize_specific_properties()
    
    def get_color_from_type(self, tower_type):
        """
        Get color based on tower type
        
        Args:
            tower_type: String indicating tower type
            
        Returns:
            RGB color tuple
        """
        colors = {
            "Archer": (100, 150, 100),  # Green
            "Sniper": (150, 100, 100),  # Red
            "Splash": (150, 150, 100),  # Yellow
            "Frozen": (100, 150, 150)   # Cyan
        }
        return colors.get(tower_type, (100, 100, 100))
    
    def initialize_specific_properties(self):
        """Initialize tower-specific properties"""
        tower_config = TOWER_TYPES.get(self.tower_type, {})
        
        # Initialize AoE properties for Splash tower
        if self.tower_type == "Splash":
            self.ref_aoe_radius = tower_config.get("aoe_radius", 50)
            self.aoe_radius = scale_value(self.ref_aoe_radius)
            # Store base AoE for item effects
            self.base_ref_aoe_radius = self.ref_aoe_radius
            self.base_aoe_radius = self.aoe_radius
            # Add AoE upgrade level
            self.aoe_radius_level = 1
        
        # Initialize slow properties for Frozen tower
        elif self.tower_type == "Frozen":
            self.slow_effect = tower_config.get("slow_effect", 0.5)
            self.slow_duration = tower_config.get("slow_duration", 3.0)
            # Store base slow effect for item effects
            self.base_slow_effect = self.slow_effect
            self.base_slow_duration = self.slow_duration
            # Add slow upgrade levels
            self.slow_effect_level = 1
            self.slow_duration_level = 1
    
    def update(self, dt, monsters, animation_manager=None):
        """
        Update tower state and attack monsters
        
        Args:
            dt: Time delta in seconds
            monsters: List of monsters to target
            animation_manager: Optional AnimationManager for visual effects
        """
        # Update attack animation flag if needed
        if self.is_attacking:
            self.attack_animation_time -= dt
            if self.attack_animation_time <= 0:
                self.is_attacking = False
        
        # Update item glow effect
        if self.item_glow_color:
            # Pulsing glow effect
            self.item_glow_intensity = 0.5 + 0.5 * math.sin(pygame.time.get_ticks() * 0.005)
        
        # Find targets
        self.find_targets(monsters)
        
        # Update attack timer
        self.attack_timer += dt
        if self.attack_timer >= 1.0 / self.attack_speed and self.targets:
            self.attack_timer = 0
            
            # Use animation_manager from parameter, or get from registry if available
            anim_mgr = animation_manager
            if not anim_mgr and self.registry and self.registry.has(ANIMATION_MANAGER):
                anim_mgr = self.registry.get(ANIMATION_MANAGER)
                
            self.attack(anim_mgr)
    
    def find_targets(self, monsters):
        """
        Find valid targets within range
        
        Args:
            monsters: List of monsters to check
        """
        self.targets = []
        
        for monster in monsters:
            # Skip dead monsters
            if monster.is_dead:
                continue
                
            # Skip flying monsters unless we're an Archer or Sniper tower
            if monster.flying and self.tower_type not in ["Archer", "Sniper"]:
                continue
            
            # Check if monster is in range
            if distance(self.position, monster.position) <= self.range:
                self.targets.append(monster)
        
        # Sort targets by distance (closest first)
        self.targets.sort(key=lambda m: distance(self.position, m.position))
    
    def attack(self, animation_manager=None):
        """
        Attack targets
        
        Args:
            animation_manager: Optional AnimationManager for visual effects
        """
        # Set attacking flag and animation time
        self.is_attacking = True
        self.attack_animation_time = 0.5  # Animation duration in seconds
        
        # Store current target for animation
        if self.targets:
            self.current_target = self.targets[0]
            
            # Check for critical hit from talent effect
            is_critical = False
            if self.talent_critical_hit_chance > 0:
                # Roll for critical hit
                import random
                if random.random() < self.talent_critical_hit_chance:
                    is_critical = True
            
            # Apply damage with critical hit if applicable
            damage_to_apply = self.damage
            if is_critical:
                damage_to_apply *= 2  # Critical hits do double damage
            
            # Create attack animation if animation manager is provided
            if animation_manager and self.current_target:
                # Need to update animation_manager to support critical hits
                if hasattr(animation_manager, 'create_tower_attack_animation'):
                    # Try to pass critical hit info if the method supports it
                    try:
                        animation_manager.create_tower_attack_animation(self, self.current_target, is_critical)
                    except TypeError:
                        # Fall back to original method if it doesn't accept critical hit parameter
                        animation_manager.create_tower_attack_animation(self, self.current_target)
    
    def calculate_damage_upgrade_cost(self):
        """
        Calculate upgrade cost for damage based on damage level
        
        Returns:
            Dictionary of resource costs
        """
        base_cost = TOWER_TYPES.get(self.tower_type, {}).get("cost", {"Stone": 20})
        
        # Scale cost with damage level
        return {
            resource_type: int(amount * (TOWER_UPGRADE_COST_MULTIPLIER ** (self.damage_level - 1)))
            for resource_type, amount in base_cost.items()
        }
    
    def calculate_damage_upgrade_monster_coin_cost(self):
        """
        Calculate Monster Coin cost for damage upgrade based on damage level
        
        Returns:
            Integer Monster Coin cost
        """
        base_cost = TOWER_MONSTER_COIN_COSTS.get(self.tower_type, 5)
        return int(base_cost * (TOWER_MONSTER_COIN_UPGRADE_MULTIPLIER ** (self.damage_level - 1)))
    
    def calculate_attack_speed_upgrade_cost(self):
        """
        Calculate upgrade cost for attack speed based on attack speed level
        
        Returns:
            Dictionary of resource costs
        """
        base_cost = TOWER_TYPES.get(self.tower_type, {}).get("cost", {"Stone": 20})
        
        # Scale cost with attack speed level
        return {
            resource_type: int(amount * (TOWER_UPGRADE_COST_MULTIPLIER ** (self.attack_speed_level - 1)))
            for resource_type, amount in base_cost.items()
        }
    
    def calculate_attack_speed_upgrade_monster_coin_cost(self):
        """
        Calculate Monster Coin cost for attack speed upgrade based on attack speed level
        
        Returns:
            Integer Monster Coin cost
        """
        base_cost = TOWER_MONSTER_COIN_COSTS.get(self.tower_type, 5)
        return int(base_cost * (TOWER_MONSTER_COIN_UPGRADE_MULTIPLIER ** (self.attack_speed_level - 1)))
    
    def calculate_range_upgrade_cost(self):
        """
        Calculate upgrade cost for range based on range level
        
        Returns:
            Dictionary of resource costs
        """
        base_cost = TOWER_TYPES.get(self.tower_type, {}).get("cost", {"Stone": 20})
        
        # Scale cost with range level
        return {
            resource_type: int(amount * (TOWER_UPGRADE_COST_MULTIPLIER ** (self.range_level - 1)))
            for resource_type, amount in base_cost.items()
        }
    
    def calculate_range_upgrade_monster_coin_cost(self):
        """
        Calculate Monster Coin cost for range upgrade based on range level
        
        Returns:
            Integer Monster Coin cost
        """
        base_cost = TOWER_MONSTER_COIN_COSTS.get(self.tower_type, 5)
        return int(base_cost * (TOWER_MONSTER_COIN_UPGRADE_MULTIPLIER ** (self.range_level - 1)))
    
    def upgrade_damage(self, resource_manager):
        """
        Upgrade tower damage
        
        Args:
            resource_manager: ResourceManager to spend resources
            
        Returns:
            True if upgrade successful, False if insufficient resources
        """
        # Get resource_manager from parameter or registry
        res_mgr = resource_manager
        if not res_mgr and self.registry and self.registry.has(RESOURCE_MANAGER):
            res_mgr = self.registry.get(RESOURCE_MANAGER)
            
        if not res_mgr:
            return False
            
        cost = self.calculate_damage_upgrade_cost()
        monster_coin_cost = self.calculate_damage_upgrade_monster_coin_cost()
        
        # Check if we have enough resources and Monster Coins
        if not res_mgr.has_resources(cost) or res_mgr.get_resource("Monster Coins") < monster_coin_cost:
            return False
            
        # Spend resources and Monster Coins
        if res_mgr.spend_resources(cost):
            # Spend the Monster Coins separately
            res_mgr.spend_resource("Monster Coins", monster_coin_cost)
            
            self.base_damage *= TOWER_DAMAGE_UPGRADE_MULTIPLIER
            self.damage_level += 1
            self.level += 1  # Keep overall level for compatibility
            self.apply_item_effects()  # Re-apply item effects after upgrade
            return True
        return False
    
    def upgrade_attack_speed(self, resource_manager):
        """
        Upgrade tower attack speed
        
        Args:
            resource_manager: ResourceManager to spend resources
            
        Returns:
            True if upgrade successful, False if insufficient resources
        """
        # Get resource_manager from parameter or registry
        res_mgr = resource_manager
        if not res_mgr and self.registry and self.registry.has(RESOURCE_MANAGER):
            res_mgr = self.registry.get(RESOURCE_MANAGER)
            
        if not res_mgr:
            return False
            
        cost = self.calculate_attack_speed_upgrade_cost()
        monster_coin_cost = self.calculate_attack_speed_upgrade_monster_coin_cost()
        
        # Check if we have enough resources and Monster Coins
        if not res_mgr.has_resources(cost) or res_mgr.get_resource("Monster Coins") < monster_coin_cost:
            return False
            
        # Spend resources and Monster Coins
        if res_mgr.spend_resources(cost):
            # Spend the Monster Coins separately
            res_mgr.spend_resource("Monster Coins", monster_coin_cost)
            
            self.base_attack_speed *= TOWER_ATTACK_SPEED_UPGRADE_MULTIPLIER
            self.attack_speed_level += 1
            self.level += 1  # Keep overall level for compatibility
            self.apply_item_effects()  # Re-apply item effects after upgrade
            return True
        return False
    
    def upgrade_range(self, resource_manager):
        """
        Upgrade tower range
        
        Args:
            resource_manager: ResourceManager to spend resources
            
        Returns:
            True if upgrade successful, False if insufficient resources
        """
        # Get resource_manager from parameter or registry
        res_mgr = resource_manager
        if not res_mgr and self.registry and self.registry.has(RESOURCE_MANAGER):
            res_mgr = self.registry.get(RESOURCE_MANAGER)
            
        if not res_mgr:
            return False
            
        cost = self.calculate_range_upgrade_cost()
        monster_coin_cost = self.calculate_range_upgrade_monster_coin_cost()
        
        # Check if we have enough resources and Monster Coins
        if not res_mgr.has_resources(cost) or res_mgr.get_resource("Monster Coins") < monster_coin_cost:
            return False
            
        # Spend resources and Monster Coins
        if res_mgr.spend_resources(cost):
            # Spend the Monster Coins separately
            res_mgr.spend_resource("Monster Coins", monster_coin_cost)
            
            # Upgrade both reference and scaled range
            self.base_ref_range *= TOWER_RANGE_UPGRADE_MULTIPLIER
            self.base_range = scale_value(self.base_ref_range)
            self.range_level += 1
            self.level += 1  # Keep overall level for compatibility
            self.apply_item_effects()  # Re-apply item effects after upgrade
            return True
        return False
    
    def calculate_upgrade_cost(self):
        """
        Calculate general upgrade cost (for compatibility)
        
        Returns:
            Dictionary of resource costs
        """
        # This is kept for backward compatibility
        base_cost = TOWER_TYPES.get(self.tower_type, {}).get("cost", {"Stone": 20})
        
        # Scale cost with tower level
        return {
            resource_type: int(amount * (TOWER_UPGRADE_COST_MULTIPLIER ** (self.level - 1)))
            for resource_type, amount in base_cost.items()
        }

    def add_item(self, item, slot_index, resource_manager=None):
        """Add item to tower slot"""
        # Use the new item manager system
        result = self.item_manager.add_item(item, slot_index, resource_manager)
        
        # Sync with legacy item_slots for backward compatibility
        self._sync_item_slots()
        
        # Apply effects
        self.apply_item_effects()
        return result
    
    def remove_item(self, slot_index, resource_manager=None):
        """Remove item from tower slot"""
        # Use the new item manager system
        result = self.item_manager.remove_item(slot_index, resource_manager)
        
        # Sync with legacy item_slots for backward compatibility
        self._sync_item_slots()
        
        # Apply effects
        self.apply_item_effects()
        return result
    
    def get_item_in_slot(self, slot_index):
        """Get item in the specified slot"""
        # Use the new item manager system
        return self.item_manager.get_item(slot_index)
    
    def _sync_item_slots(self):
        """Sync item_slots with item_manager for backwards compatibility"""
        items = self.item_manager.get_all_items()
        for i in range(min(len(items), len(self.item_slots))):
            self.item_slots[i] = items[i]
    
    def debug_items(self):
        """Debug method to diagnose item slot issues"""
        print("\n--- Tower Item Slot Diagnostics ---")
        print(f"Tower type: {self.tower_type}")
        
        # Debug the new item system
        print("\n=== New Item System ===")
        print(f"item_manager: {hasattr(self, 'item_manager')}")
        print(f"item_effects: {hasattr(self, 'item_effects')}")
        if hasattr(self, 'item_manager'):
            print(f"item_manager slots: {self.item_manager.get_all_items()}")
        
        # Debug the legacy compatibility
        print("\n=== Legacy System (for compatibility) ===")
        print(f"item_slots type: {type(self.item_slots)}")
        if hasattr(self, 'item_slots'):
            print(f"item_slots: {self.item_slots}")
            print(f"item_slots length: {len(self.item_slots) if isinstance(self.item_slots, list) else 'N/A'}")
        else:
            print("No item_slots attribute found!")
        
        print("\nTesting add_item:")
        old_slots = self.item_slots.copy() if isinstance(self.item_slots, list) else None
        old_items = self.item_manager.get_all_items() if hasattr(self, 'item_manager') else None
        
        result0 = self.add_item("Debug Item 0", 0, None)
        print(f"Adding to slot 0: result={result0}")
        print(f"  - Legacy slots: {self.item_slots}")
        print(f"  - New system:   {self.item_manager.get_all_items() if hasattr(self, 'item_manager') else None}")
        
        result1 = self.add_item("Debug Item 1", "1", None)  # Test string index
        print(f"Adding to slot 1 (string index): result={result1}")
        print(f"  - Legacy slots: {self.item_slots}")
        print(f"  - New system:   {self.item_manager.get_all_items() if hasattr(self, 'item_manager') else None}")
        
        print("\nTesting get_item_in_slot:")
        item0 = self.get_item_in_slot(0)
        item1 = self.get_item_in_slot(1)
        print(f"Item in slot 0: {item0}")
        print(f"Item in slot 1: {item1}")
        
        print("\nTesting remove_item:")
        removed0 = self.remove_item(0, None)
        print(f"Removing from slot 0: removed={removed0}")
        print(f"  - Legacy slots: {self.item_slots}")
        print(f"  - New system:   {self.item_manager.get_all_items() if hasattr(self, 'item_manager') else None}")
        
        removed1 = self.remove_item(1, None)
        print(f"Removing from slot 1: removed={removed1}")
        print(f"  - Legacy slots: {self.item_slots}")
        print(f"  - New system:   {self.item_manager.get_all_items() if hasattr(self, 'item_manager') else None}")
        
        # Restore original state
        if hasattr(self, 'item_manager') and old_items:
            for i, item in enumerate(old_items):
                if item:
                    self.item_manager.add_item(item, i, None)
        self.item_slots = old_slots if old_slots else [None, None]
        self._sync_item_slots()  # Sync for consistency
        print("\n--- End Diagnostics ---")
    
    def apply_item_effects(self):
        """Apply effects from equipped items"""
        # Use the new item effects system
        self.item_effects.apply_effects(self.item_manager.get_all_items())
        
        # Update for backward compatibility
        self._sync_item_slots()
    
    def draw(self, screen):
        """
        Draw tower to screen
        
        Args:
            screen: Pygame surface to draw on
        """
        # Draw tower base
        pygame.draw.rect(screen, self.color, self.rect)
        
        # Draw item glow effect if tower has items
        if self.item_glow_color and self.item_glow_intensity > 0:
            # Create the glow as a transparent surface
            glow_size = int(self.size[0] * (1.2 + 0.1 * self.item_glow_intensity))
            glow_surface = pygame.Surface((glow_size, glow_size), pygame.SRCALPHA)
            
            # Calculate glow color with alpha based on intensity
            glow_alpha = int(100 * self.item_glow_intensity)
            glow_color = (*self.item_glow_color, glow_alpha)
            
            # Draw the glow
            pygame.draw.rect(glow_surface, glow_color, 
                           (0, 0, glow_size, glow_size), 
                           int(self.size[0] * 0.2))
            
            # Position the glow centered on the tower
            glow_pos = (
                self.position[0] - glow_size // 2,
                self.position[1] - glow_size // 2
            )
            
            # Draw the glow
            screen.blit(glow_surface, glow_pos)
        
        # Draw tower
        pygame.draw.rect(screen, self.color, self.rect)
        
        # Draw tower type indicator
        font_size = scale_value(16)
        font = pygame.font.Font(None, font_size)
        text = font.render(self.tower_type, True, (255, 255, 255))
        text_rect = text.get_rect(center=(self.rect.centerx, self.rect.top - scale_value(10)))
        screen.blit(text, text_rect)
        
        # Tower level and talent effects
        if self.selected:
            font_size = scale_value(20)
            font = pygame.font.Font(None, font_size)
            text = font.render(f"Lv {self.level}", True, (255, 255, 255))
            text_rect = text.get_rect(center=(self.rect.centerx, self.rect.centery))
            screen.blit(text, text_rect)
            
            # Show active talent effects if any
            small_font = pygame.font.Font(None, scale_value(14))
            effect_y = self.rect.bottom + scale_value(15)
            
            # Show damage boost
            if self.talent_damage_multiplier > 1.0:
                damage_text = f"+{int((self.talent_damage_multiplier-1)*100)}% DMG"
                damage_surface = small_font.render(damage_text, True, (220, 150, 150))
                damage_rect = damage_surface.get_rect(centerx=self.rect.centerx, top=effect_y)
                screen.blit(damage_surface, damage_rect)
                effect_y += damage_rect.height + scale_value(2)
            
            # Show range boost
            if self.talent_range_multiplier > 1.0:
                range_text = f"+{int((self.talent_range_multiplier-1)*100)}% Range"
                range_surface = small_font.render(range_text, True, (150, 150, 220))
                range_rect = range_surface.get_rect(centerx=self.rect.centerx, top=effect_y)
                screen.blit(range_surface, range_rect)
                effect_y += range_rect.height + scale_value(2)
            
            # Show critical hit chance
            if self.talent_critical_hit_chance > 0:
                crit_text = f"{int(self.talent_critical_hit_chance*100)}% Crit"
                crit_surface = small_font.render(crit_text, True, (220, 180, 100))
                crit_rect = crit_surface.get_rect(centerx=self.rect.centerx, top=effect_y)
                screen.blit(crit_surface, crit_rect)
        
        # Draw item indicators if tower has items
        if isinstance(self.item_slots, list) and len(self.item_slots) == 2 and any(self.item_slots):
            small_font = pygame.font.Font(None, scale_value(14))
            for i, item in enumerate(self.item_slots):
                if item:
                    # Calculate position for item indicator (top-left and top-right corners)
                    x_offset = -self.size[0]//2 + scale_value(8) if i == 0 else self.size[0]//2 - scale_value(8)
                    item_pos = (self.rect.centerx + x_offset, self.rect.top - scale_value(25))
                    
                    # Get first letter of item for indicator
                    item_letter = item[0]
                    
                    # Draw background circle
                    if item == "Unstoppable Force":
                        bg_color = (255, 100, 50)  # Orange for Unstoppable Force
                    elif item == "Serene Spirit":
                        bg_color = (100, 200, 100)  # Green for Serene Spirit
                    elif item == "Multitudation Vortex":
                        bg_color = (150, 100, 255)  # Purple for Multitudation Vortex
                    else:
                        bg_color = (150, 150, 150)  # Gray for other items
                        
                    pygame.draw.circle(screen, bg_color, item_pos, scale_value(8))
                    
                    # Draw item letter
                    text = small_font.render(item_letter, True, (255, 255, 255))
                    text_rect = text.get_rect(center=item_pos)
                    screen.blit(text, text_rect)
        
        # Draw attack animation (flash or highlight when attacking)
        if self.is_attacking:
            # Calculate highlight intensity based on animation time
            intensity = self.attack_animation_time * 2  # 0.0 to 1.0
            highlight_color = (
                min(255, self.color[0] + 50 * intensity),
                min(255, self.color[1] + 50 * intensity),
                min(255, self.color[2] + 50 * intensity)
            )
            highlight_rect = self.rect.inflate(scale_value(4), scale_value(4))
            pygame.draw.rect(screen, highlight_color, highlight_rect, scale_value(2))
        
        # Draw range indicator (only when selected)
        if self.selected:
            # Draw main range circle
            pygame.draw.circle(screen, (255, 255, 255), 
                              (int(self.position[0]), int(self.position[1])), 
                              int(self.range), scale_value(1))
            
            # Draw special range indicators based on tower type and items
            if self.tower_type == "Splash":
                # Draw AoE radius indicator for Splash Tower
                pygame.draw.circle(screen, (255, 200, 0), 
                                  (int(self.position[0]), int(self.position[1])), 
                                  int(self.aoe_radius), scale_value(1))
                
            elif self.tower_type in ["Archer", "Sniper"] and self.splash_damage_enabled:
                # Draw splash damage radius for single-target towers with Unstoppable Force
                pygame.draw.circle(screen, (255, 150, 50), 
                                  (int(self.position[0]), int(self.position[1])), 
                                  int(self.splash_damage_radius), scale_value(1))
