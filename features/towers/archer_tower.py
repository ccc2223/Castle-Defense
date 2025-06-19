# towers/archer_tower.py
"""
Archer Tower implementation for Castle Defense
"""
from .base_tower import Tower

class ArcherTower(Tower):
    """Tower with fast attack speed, low damage"""
    def __init__(self, position, registry=None):
        super().__init__(position, "Archer", registry)
    
    def attack(self, animation_manager=None):
        """
        Attack closest target with single-target damage
        
        Args:
            animation_manager: Optional AnimationManager for visual effects
        """
        super().attack(animation_manager)
        
        if not self.targets:
            return
            
        target = self.targets[0]  # Attack closest target
        
        if target.is_dead:
            return
        
        # Create attack animation before potentially killing the monster
        if animation_manager:
            animation_manager.create_tower_attack_animation(self, target)
        
        # Apply damage to primary target
        primary_target_killed = not target.take_damage(self.damage)
        
        # Handle Multitudation Vortex bounce effect
        bounce_target = None
        bounce_target_killed = False
        
        if self.bounce_enabled and len(self.targets) > 1:
            # Determine if bounce occurs based on chance
            import random
            if random.random() < self.bounce_chance:
                # Find another target (not the primary target)
                other_targets = [m for m in self.targets if m != target and not m.is_dead]
                if other_targets:
                    # Select closest target for the bounce
                    bounce_target = min(other_targets, key=lambda m: distance(target.position, m.position))
                    if bounce_target:
                        # Create bounce animation if animation manager is available
                        if animation_manager:
                            animation_manager.create_tower_attack_animation(self, bounce_target, is_bounce=True)
                        # Apply same damage to bounce target
                        bounce_target_killed = not bounce_target.take_damage(self.damage)
        
        # Apply splash damage if enabled (from Unstoppable Force item)
        splash_targets = []
        if self.splash_damage_enabled and self.splash_damage_radius > 0:
            for monster in self.targets:
                if monster != target and not monster.is_dead:
                    # Check if monster is within splash radius of primary target
                    if distance(monster.position, target.position) <= self.splash_damage_radius:
                        # Apply 50% damage to splash targets
                        splash_damage = self.damage * 0.5
                        if not monster.take_damage(splash_damage, "splash"):
                            # Monster was killed by splash damage
                            splash_targets.append(monster)
                        elif animation_manager:
                            # Monster was hit but not killed by splash
                            animation_manager.create_monster_hit_animation(monster, "splash")
        
        # Handle deaths and resource drops
        killed_monsters = []
        
        # Add primary target if killed
        if primary_target_killed:
            killed_monsters.append(target)
            
        # Add bounce target if killed
        if bounce_target and bounce_target_killed:
            killed_monsters.append(bounce_target)
            
        # Add splash targets that were killed
        killed_monsters.extend(splash_targets)
        
        # Handle all killed monsters
        if killed_monsters:
            # Get reference to wave_manager and resource_manager from the game instance
            from game import Game
            for game_instance in [obj for obj in globals().values() if isinstance(obj, Game)]:
                for monster in killed_monsters:
                    if animation_manager:
                        animation_manager.create_monster_death_animation(monster)
                    game_instance.wave_manager.handle_monster_death(monster, game_instance.resource_manager, animation_manager)
        elif animation_manager:
            # Create hit animations for non-killed targets
            if not primary_target_killed:
                animation_manager.create_monster_hit_animation(target)
                
            # Create hit animation for bounce target if it wasn't killed
            if bounce_target and not bounce_target_killed:
                animation_manager.create_monster_hit_animation(bounce_target)

# Import this at the module level to avoid circular import in attack()
from utils import distance