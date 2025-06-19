# features/monsters/wave_manager.py
"""
Wave management system for Castle Defense
"""
import pygame
import random
import math
from .factory import MonsterFactory
from .boss_monster import BossMonster
from config import (
    MONSTER_STATS,
    BOSS_STATS,
    MONSTER_SPAWN_INTERVAL,
    WAVE_DIFFICULTY_MULTIPLIER,
    WAVE_MONSTER_COUNT_BASE,
    WAVE_MONSTER_COUNT_MULTIPLIER,
    REF_WIDTH,
    REF_HEIGHT,
    TALENT_POINTS_PER_WAVE,
    TALENT_POINT_MILESTONE_WAVES,
    TALENT_POINT_MILESTONE_REWARDS
)
from utils import scale_position

class WaveManager:
    """Manages monster waves and spawning"""
    def __init__(self):
        """Initialize wave manager"""
        self.current_wave = 0
        self.active_monsters = []
        self.spawn_timer = 0
        self.monsters_to_spawn = 0
        self.wave_active = False
        self.wave_completed = True
        
        # Animation flags
        self.wave_start_animation_timer = 0
        self.wave_complete_animation_timer = 0
        
        # Spawn points will be generated dynamically across the top of the screen
        self.spawn_path = []  # No longer used with the direct movement system
        
        # Developer mode settings - Set continuous_wave to True by default
        self.continuous_wave = True  # Auto-start next wave when current wave ends
        
        # Wave timeout failsafe
        self.wave_timeout = 120.0  # 2 minutes max per wave
        self.wave_timer = 0
        
        # Challenge mode settings
        self.challenge_mode = False
        self.challenge_monster_type = None
        self.challenge_tier = None
        self.challenge_total_waves = 20  # Always 20 waves for a challenge
        self.challenge_wave_count = 0
    
    def start_next_wave(self):
        """
        Start the next wave of monsters
        
        Returns:
            True if wave was started, False if already active
        """
        if not self.wave_active:
            self.current_wave += 1
            self.wave_active = True
            self.wave_completed = False
            self.spawn_timer = 0
            self.wave_timer = 0  # Reset wave timer
            
            # Set wave start animation
            self.wave_start_animation_timer = 1.0  # 1 second animation
            
            # Calculate number of monsters to spawn
            if self.challenge_mode:
                # Update challenge wave count
                self.challenge_wave_count += 1
                
                # Calculate monsters based on challenge wave count and tier
                base_count = 5 + self.challenge_wave_count  # Increase with each wave
                self.monsters_to_spawn = int(base_count * self.challenge_monster_multiplier)
                
                # Add boss monster at specific intervals in challenge mode
                if self.challenge_wave_count % 5 == 0:
                    # Every 5th wave is a boss wave in challenge mode
                    self.monsters_to_spawn += 1  # Add boss to regular monsters
            else:
                # Normal mode wave calculation
                if self.current_wave % 10 == 0:
                    # Boss wave
                    self.monsters_to_spawn = 1
                else:
                    # Regular wave
                    base_count = WAVE_MONSTER_COUNT_BASE
                    multiplier = WAVE_DIFFICULTY_MULTIPLIER ** (self.current_wave // 10)
                    self.monsters_to_spawn = int(base_count + self.current_wave * 0.5 * multiplier)
            
            return True
        return False
    
    def update(self, dt, castle, animation_manager=None):
        """
        Update wave state and all active monsters
        
        Args:
            dt: Time delta in seconds
            castle: Castle instance for monster attacks
            animation_manager: Optional AnimationManager for visual effects
        """
        # Update animation timers
        if self.wave_start_animation_timer > 0:
            self.wave_start_animation_timer -= dt
        
        if self.wave_complete_animation_timer > 0:
            self.wave_complete_animation_timer -= dt
        
        if self.wave_active:
            # Update wave timer for timeout
            self.wave_timer += dt
            
            # Check for wave timeout - if active for too long, force completion
            if self.wave_timer > self.wave_timeout:
                print(f"Wave {self.current_wave} timed out after {self.wave_timer:.1f} seconds with {len(self.active_monsters)} monsters remaining")
                # Log all active monsters for debugging
                for i, monster in enumerate(self.active_monsters):
                    print(f"  Monster {i}: {monster.monster_type} at ({monster.position[0]:.1f}, {monster.position[1]:.1f}) with {monster.health:.1f} health")
                
                # Force-kill all remaining monsters
                for monster in self.active_monsters[:]:  # Use a copy of the list
                    monster.is_dead = True
                    # Get game_instance reference to access resource_manager
                    from game import game_instance
                    if game_instance:
                        self.handle_monster_death(monster, game_instance.resource_manager, animation_manager)
                    else:
                        # Fallback if game_instance not available
                        self.handle_monster_death(monster, None, animation_manager)
                    if monster in self.active_monsters:  # Check if it's still in the list
                        self.active_monsters.remove(monster)
                
                # End the wave
                self.monsters_to_spawn = 0
                self.wave_active = False
                self.wave_completed = True
                self.wave_complete_animation_timer = 2.0
                self.wave_timer = 0
                return
            # Spawn new monsters
            self.spawn_timer += dt
            if self.spawn_timer >= MONSTER_SPAWN_INTERVAL and self.monsters_to_spawn > 0:
                self.spawn_monster(castle.position, animation_manager)
                self.monsters_to_spawn -= 1
                self.spawn_timer = 0
            
            # Update all active monsters and handle dead monsters
            monsters_to_remove = []
            
            for monster in self.active_monsters:
                monster_still_active = monster.update(dt, castle, animation_manager)
                
                if not monster_still_active:
                    # Monster died
                    monsters_to_remove.append(monster)
            
            # Remove monsters
            for monster in monsters_to_remove:
                if monster in self.active_monsters:
                    # If monster died but wasn't handled by a tower, handle it here
                    if monster.is_dead and not monster.reached_castle:
                        # Get game_instance reference to access resource_manager
                        # This is a fallback - towers should normally handle this
                        from game import game_instance
                        if game_instance:
                            self.handle_monster_death(monster, game_instance.resource_manager, animation_manager)
                    
                    self.active_monsters.remove(monster)
            
            # Run sanity check on monster positions
            self.check_monster_positions()
            
            # Check if wave is complete
            if len(self.active_monsters) == 0 and self.monsters_to_spawn == 0:
                self.wave_active = False
                self.wave_completed = True
                self.wave_complete_animation_timer = 2.0  # 2 second animation
                self.wave_timer = 0  # Reset wave timer
                
                # Check if this was the last wave of a challenge
                if self.challenge_mode and self.challenge_wave_count >= self.challenge_total_waves:
                    # Challenge is complete!
                    from game import game_instance
                    if game_instance:
                        print(f"Challenge complete! {self.challenge_monster_type} {self.challenge_tier} challenge completed!")
                        game_instance.complete_monster_challenge(self.challenge_monster_type, self.challenge_tier, True)
                else:
                    # Award talent points for normal wave completion
                    self.award_talent_points()
    
    def spawn_monster(self, castle_position, animation_manager=None):
        """
        Spawn a monster based on current wave
        
        Args:
            castle_position: Position of castle to target
            animation_manager: Optional AnimationManager for visual effects
        """
        # Generate random spawn position along the top of the screen in reference coordinates
        ref_spawn_x = random.randint(50, REF_WIDTH - 50)
        ref_spawn_y = 50  # 50 pixels from the top
        
        # Scale to actual screen coordinates
        spawn_pos = scale_position((ref_spawn_x, ref_spawn_y))
        
        if self.challenge_mode:
            # Challenge mode - spawn only the selected monster type
            if self.challenge_wave_count % 5 == 0 and self.monsters_to_spawn == 1:
                # For challenge boss waves (every 5th wave), last monster is a boss
                # Use a boss version of the challenge monster type
                boss_type = "Force"  # Default boss type
                
                # Map monster type to appropriate boss type if possible
                if "Grunt" in self.challenge_monster_type:
                    boss_type = "Force"
                elif "Flyer" in self.challenge_monster_type:
                    boss_type = "Spirit"
                elif "Runner" in self.challenge_monster_type:
                    boss_type = "Magic"
                elif "Tank" in self.challenge_monster_type:
                    boss_type = "Void"
                
                monster = MonsterFactory.create_boss_monster(boss_type, spawn_pos, castle_position)
            else:
                # Regular challenge monster
                wave_difficulty = min(20, self.challenge_wave_count + 5)  # Increase difficulty with each wave
                monster = MonsterFactory.create_regular_monster(self.challenge_monster_type, spawn_pos, castle_position, wave_difficulty)
        else:
            # Normal wave mode
            if self.current_wave % 10 == 0:
                # Boss wave
                boss_type = self.get_boss_type()
                monster = MonsterFactory.create_boss_monster(boss_type, spawn_pos, castle_position)
            else:
                # Regular monster
                monster_type = self.get_random_monster_type()
                monster = MonsterFactory.create_regular_monster(monster_type, spawn_pos, castle_position, self.current_wave)
        
        self.active_monsters.append(monster)
        
        # Create spawn animation if animation manager is provided
        # This would be implemented in the animation_manager
    
    def get_boss_type(self):
        """
        Determine boss type based on wave number
        
        Returns:
            String boss type
        """
        boss_types = ["Force", "Spirit", "Magic", "Void"]
        return boss_types[(self.current_wave // 10 - 1) % len(boss_types)]
    
    def get_random_monster_type(self):
        """
        Get a random monster type weighted by wave number
        
        Returns:
            String monster type
        """
        available_types = []
        
        # Always include Grunt
        available_types.append("Grunt")
        
        # Add Runner after wave 3
        if self.current_wave >= 3:
            available_types.append("Runner")
        
        # Add Tank after wave 5
        if self.current_wave >= 5:
            available_types.append("Tank")
        
        # Add Flyer after wave 8
        if self.current_wave >= 8:
            available_types.append("Flyer")
        
        # Weight later monsters to be more common in later waves
        # Using int() to ensure all weights are integers
        weights = {
            "Grunt": int(100 - min(80, self.current_wave * 2)),
            "Runner": int(min(60, max(10, self.current_wave * 3))),
            "Tank": int(min(50, max(10, self.current_wave * 2))),
            "Flyer": int(min(40, max(10, self.current_wave * 1.5)))
        }
        
        # Filter weights to only include available types
        weights = {k: v for k, v in weights.items() if k in available_types}
        
        # Choose random type based on weights
        total_weight = sum(weights.values())
        
        # Ensure total_weight is at least 1
        if total_weight <= 0:
            return "Grunt"  # Default to Grunt if weights calculation went wrong
        
        r = random.randint(1, total_weight)
        cumulative_weight = 0
        
        for monster_type, weight in weights.items():
            cumulative_weight += weight
            if r <= cumulative_weight:
                return monster_type
        
        # Fallback
        return "Grunt"
    
    def handle_monster_death(self, monster, resource_manager, animation_manager=None):
        """
        Handle monster death and loot drops
        
        Args:
            monster: Monster that died
            resource_manager: ResourceManager to add loot
            animation_manager: Optional AnimationManager for visual effects
        """
        # Already dead or not in active monsters
        if not monster or not monster in self.active_monsters:
            return
            
        # Mark as dead to prevent duplicate handling
        monster.is_dead = True
            
        # Create death animation if animation manager is provided
        if animation_manager:
            animation_manager.create_monster_death_animation(monster)
        
        # Create loot dictionary to track drops
        loot_dict = {}
        
        # Add Monster Coins for all monsters
        if resource_manager is not None:
            resource_manager.add_resource("Monster Coins", 1)
            loot_dict["Monster Coins"] = 1
        
        # Record monster kill in Monster Codex if available
        from game import game_instance
        if game_instance:
            # Check if village exists
            if not hasattr(game_instance, 'village') or game_instance.village is None:
                # Create village if needed for monster tracking
                if hasattr(game_instance, 'state_manager') and hasattr(game_instance.state_manager, 'states') and 'village' in game_instance.state_manager.states:
                    # Initialize village through state to ensure proper setup
                    village_state = game_instance.state_manager.states['village']
                    if hasattr(village_state, 'game') and hasattr(village_state.game, 'village') and village_state.game.village is not None:
                        game_instance.village = village_state.game.village
            
            # Now check if village exists and has been initialized
            if hasattr(game_instance, 'village') and game_instance.village:
                village = game_instance.village
                
                # Find the Monster Codex building if it exists
                for building in village.buildings:
                    if building.__class__.__name__ == "MonsterCodex":
                        # Record monster kill
                        building.record_monster(monster.monster_type)
                        building.record_kill(monster.monster_type)
                        print(f"Monster kill recorded: {monster.monster_type}")
                        break
        
        # Handle boss loot
        if isinstance(monster, BossMonster) and resource_manager is not None:
            boss_loot = monster.drop_loot()
            for resource_type, amount in boss_loot.items():
                resource_manager.add_resource(resource_type, amount)
                # Add to loot dictionary for display
                loot_dict[resource_type] = amount
        
        # Create loot indicator if animation manager is provided and loot was dropped
        if animation_manager and loot_dict and hasattr(animation_manager, 'create_loot_indicator'):
            animation_manager.create_loot_indicator(monster.position, loot_dict)
    
    def award_talent_points(self):
        """
        Award talent points for completing a wave
        """
        # Get game_instance reference
        from game import game_instance
        if not game_instance or not hasattr(game_instance, 'village'):
            return
        
        # Base talent points for every wave
        talent_points = TALENT_POINTS_PER_WAVE
        
        # Check for milestone rewards
        if self.current_wave in TALENT_POINT_MILESTONE_WAVES:
            milestone_index = TALENT_POINT_MILESTONE_WAVES.index(self.current_wave)
            milestone_reward = TALENT_POINT_MILESTONE_REWARDS[milestone_index]
            talent_points += milestone_reward
            print(f"Milestone wave {self.current_wave} completed! +{milestone_reward} bonus talent points!")
        
        # Add talent points to village
        village = game_instance.village
        village.add_talent_points(talent_points)
        
        # Also add talent points to Town Hall if it exists
        for building in village.buildings:
            if building.__class__.__name__ == "TownHall":
                building.add_talent_points(talent_points)
                break
        
        print(f"Wave {self.current_wave} completed! +{talent_points} talent points!")
    
    def draw(self, screen):
        """
        Draw all monsters and wave animations
        
        Args:
            screen: Pygame surface to draw on
        """
        # Draw all monsters
        for monster in self.active_monsters:
            monster.draw(screen)
        
        # Draw wave start animation
        if self.wave_start_animation_timer > 0:
            alpha = int(255 * min(1, self.wave_start_animation_timer))
            font_size = 36
            font = pygame.font.Font(None, font_size)
            
            if self.current_wave % 10 == 0:
                # Boss wave announcement
                text = f"BOSS WAVE {self.current_wave}"
                color = (255, 100, 100)  # Red for boss waves
            else:
                # Regular wave announcement
                text = f"Wave {self.current_wave}"
                color = (255, 255, 255)
            
            text_surface = font.render(text, True, color)
            
            # Apply fading effect
            if alpha < 255:
                alpha_surface = pygame.Surface(text_surface.get_size(), pygame.SRCALPHA)
                alpha_surface.fill((255, 255, 255, alpha))
                text_surface.blit(alpha_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            
            text_rect = text_surface.get_rect(center=(screen.get_width() // 2, 100))
            screen.blit(text_surface, text_rect)
        
        # Draw wave complete animation
        if self.wave_complete_animation_timer > 0 and self.wave_completed:
            alpha = int(255 * min(1, self.wave_complete_animation_timer))
            font_size = 30
            font = pygame.font.Font(None, font_size)
            
            text = f"Wave {self.current_wave} Complete!"
            text_surface = font.render(text, True, (200, 255, 200))
            
            # Apply fading effect
            if alpha < 255:
                alpha_surface = pygame.Surface(text_surface.get_size(), pygame.SRCALPHA)
                alpha_surface.fill((255, 255, 255, alpha))
                text_surface.blit(alpha_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            
            text_rect = text_surface.get_rect(center=(screen.get_width() // 2, 150))
            screen.blit(text_surface, text_rect)
            
            # Draw continuous wave mode indicator if enabled
            if self.continuous_wave:
                font_size = 20
                font = pygame.font.Font(None, font_size)
                
                next_wave_text = f"Starting Wave {self.current_wave + 1} Soon..."
                next_wave_surface = font.render(next_wave_text, True, (200, 200, 255))
                
                # Apply fading effect
                if alpha < 255:
                    alpha_surface = pygame.Surface(next_wave_surface.get_size(), pygame.SRCALPHA)
                    alpha_surface.fill((255, 255, 255, alpha))
                    next_wave_surface.blit(alpha_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
                
                next_wave_rect = next_wave_surface.get_rect(center=(screen.get_width() // 2, 180))
                screen.blit(next_wave_surface, next_wave_rect)
            
    def check_monster_positions(self):
        """Check for monsters with invalid positions and correct or remove them"""
        import math
        from config import WINDOW_WIDTH, WINDOW_HEIGHT
        
        for monster in self.active_monsters[:]:  # Use a copy to allow safe removal
            # Check for NaN positions which can happen due to math errors
            if (math.isnan(monster.position[0]) or math.isnan(monster.position[1]) or
                math.isinf(monster.position[0]) or math.isinf(monster.position[1])):
                print(f"Found monster with invalid position: {monster.position}")
                monster.is_dead = True
                self.active_monsters.remove(monster)
                continue
                
            # Check for extremely out-of-bounds positions
            if (monster.position[0] < -100 or monster.position[0] > WINDOW_WIDTH + 100 or
                monster.position[1] < -100 or monster.position[1] > WINDOW_HEIGHT + 100):
                print(f"Found monster way out of bounds: {monster.position}")
                monster.is_dead = True
                self.active_monsters.remove(monster)
                continue
    
    def set_challenge_mode(self, monster_type, tier):
        """
        Set up challenge mode with specific monster type and tier
        
        Args:
            monster_type: Type of monster for the challenge
            tier: Challenge tier (bronze, silver, gold, platinum)
        """
        # Save current wave number to restore it later
        self.normal_wave_backup = self.current_wave
        
        self.challenge_mode = True
        self.challenge_monster_type = monster_type
        self.challenge_tier = tier
        self.challenge_wave_count = 0
        
        # Reset wave state
        self.current_wave = 0
        self.active_monsters = []
        self.wave_active = False
        self.wave_completed = True
        self.monsters_to_spawn = 0
        
        # Adjust wave difficulty based on tier
        if tier == "bronze":
            self.challenge_monster_multiplier = 1.0
        elif tier == "silver":
            self.challenge_monster_multiplier = 1.5
        elif tier == "gold":
            self.challenge_monster_multiplier = 2.0
        elif tier == "platinum":
            self.challenge_monster_multiplier = 3.0
        else:
            self.challenge_monster_multiplier = 1.0
            
        print(f"Challenge mode activated: {tier} challenge with {monster_type}")
    
    def reset_challenge_mode(self):
        """
        Reset back to normal wave mode
        """
        self.challenge_mode = False
        self.challenge_monster_type = None
        self.challenge_tier = None
        self.challenge_wave_count = 0
        
        # Restore the previous wave number if available
        if hasattr(self, 'normal_wave_backup'):
            self.current_wave = self.normal_wave_backup
            print(f"Restored normal wave progress: Wave {self.current_wave}")
        
        # Reset active wave state
        self.active_monsters = []
        self.wave_active = False
        self.wave_completed = True
        self.monsters_to_spawn = 0
        
        print("Challenge mode deactivated, returning to normal waves")
    
    def is_challenge_complete(self):
        """
        Check if the current challenge is complete
        
        Returns:
            True if challenge is complete, False otherwise
        """
        if not self.challenge_mode:
            return False
            
        return self.challenge_wave_count >= self.challenge_total_waves