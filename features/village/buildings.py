# features/village/buildings.py
"""
Village building implementations for Castle Defense
"""
import pygame
from utils import scale_value, scale_position, scale_size
from config import VILLAGE_BUILDING_COSTS, CROP_FARM_PRODUCTION, LIVESTOCK_FARM_PRODUCTION

class VillageBuilding:
    """Base class for all village buildings"""
    def __init__(self, position, registry):
        """
        Initialize building with position
        
        Args:
            position: Tuple of (x, y) coordinates
            registry: Component registry for accessing game components
        """
        self.position = position
        self.registry = registry
        self.level = 1
        self.ref_size = (80, 80)  # Default size in reference coordinates
        self.size = scale_size(self.ref_size)
        self.rect = pygame.Rect(
            position[0] - self.size[0] // 2,
            position[1] - self.size[1] // 2,
            self.size[0],
            self.size[1]
        )
        self.color = (100, 100, 100)  # Default color
        self.name = "Building"
        self.description = "A village building"
        self.is_selected = False
        
        # Building type determines functionality
        self.building_type = "basic"
        
        # Default upgrade costs and requirements
        self.upgrade_cost = {"Stone": 50}
        self.upgrade_requirements = {"village_level": 1}
    
    def update(self, dt):
        """
        Update building state
        
        Args:
            dt: Time delta in seconds
        """
        pass
    
    def draw(self, screen):
        """
        Draw building to screen
        
        Args:
            screen: Pygame surface to draw on
        """
        # Fix for buildings that might be missing their rect
        if not hasattr(self, 'rect') or not self.rect:
            print(f"Recreating rect for {self.name} at position {self.position}")
            # Make sure we have the size attribute
            if not hasattr(self, 'size') or not self.size:
                if hasattr(self, 'ref_size'):
                    from utils import scale_size
                    self.size = scale_size(self.ref_size)
                else:
                    self.size = (80, 80)  # Default fallback
            
            # Recreate the rect
            self.rect = pygame.Rect(
                self.position[0] - self.size[0] // 2,
                self.position[1] - self.size[1] // 2,
                self.size[0],
                self.size[1]
            )
            
        # Draw building with slightly different color if selected
        border_width = 3 if self.is_selected else 1
        border_color = (200, 200, 50) if self.is_selected else (200, 200, 200)
        
        pygame.draw.rect(screen, self.color, self.rect)
        pygame.draw.rect(screen, border_color, self.rect, border_width)
        
        # Draw building name and level
        font_size = scale_value(18)
        font = pygame.font.Font(None, font_size)
        text = font.render(f"{self.name} (Lv {self.level})", True, (255, 255, 255))
        text_rect = text.get_rect(center=(self.rect.centerx, self.rect.top - scale_value(10)))
        screen.blit(text, text_rect)
    
    def handle_click(self, position):
        """
        Handle click on building
        
        Args:
            position: Tuple of (x, y) coordinates of click
            
        Returns:
            True if building was clicked, False otherwise
        """
        if self.rect.collidepoint(position):
            self.is_selected = not self.is_selected
            return True
        elif self.is_selected and hasattr(self, 'view_talents_button_rect') and self.view_talents_button_rect.collidepoint(position):
            # Handle talent tree button click
            # Tell the village state to open the talent tree UI
            if self.registry and self.registry.has("game"):
                game = self.registry.get("game")
                if hasattr(game, 'state_manager') and hasattr(game.state_manager, 'current_state'):
                    current_state = game.state_manager.current_state
                    if hasattr(current_state, 'open_talent_tree'):
                        current_state.open_talent_tree(self)
                        return True
            return True
        else:
            # Deselect if clicked elsewhere
            self.is_selected = False
            return False
    
    def can_upgrade(self):
        """
        Check if building can be upgraded
        
        Returns:
            True if can upgrade, False otherwise
        """
        # Check resource requirements
        resource_manager = self.registry.get("resource_manager")
        if not resource_manager.has_resources(self.upgrade_cost):
            return False
        
        # Check village level requirement
        village = self.registry.get("game").village
        if village.development_level < self.upgrade_requirements["village_level"]:
            return False
        
        return True
    
    def upgrade(self):
        """
        Upgrade the building
        
        Returns:
            True if upgrade successful, False otherwise
        """
        if not self.can_upgrade():
            return False
        
        # Spend resources
        resource_manager = self.registry.get("resource_manager")
        if not resource_manager.spend_resources(self.upgrade_cost):
            return False
        
        # Increase level
        self.level += 1
        
        # Update upgrade costs (increase with each level)
        for resource, amount in self.upgrade_cost.items():
            self.upgrade_cost[resource] = int(amount * 1.5)
        
        return True
    
    def get_info_text(self):
        """
        Get building information text
        
        Returns:
            List of text lines with building information
        """
        info = [
            f"{self.name} (Level {self.level})",
            f"{self.description}",
            f"Upgrade cost: {', '.join([f'{amount} {resource}' for resource, amount in self.upgrade_cost.items()])}"
        ]
        return info

class TownHall(VillageBuilding):
    """Central management building and talent progression hub"""
    def __init__(self, position, registry):
        """
        Initialize town hall
        
        Args:
            position: Tuple of (x, y) coordinates
            registry: Component registry
        """
        super().__init__(position, registry)
        self.name = "Town Hall"
        self.description = "Central management building and talent progression hub"
        self.color = (150, 120, 80)  # Brown color for town hall
        self.building_type = "town_hall"
        
        # Talent points
        self.talent_points = 0
        
        # Enhanced talent trees with detailed structure
        self.talent_trees = {
            "defense": {
                "name": "Defense",
                "description": "Improve castle and tower defenses",
                "talents": {
                    "castle_fortification": {
                        "name": "Castle Fortification",
                        "description": "Increases castle max health",
                        "levels": 5,
                        "current_level": 0,
                        "effects_per_level": {"castle_health_multiplier": 0.05},  # +5% per level
                        "requires": {},
                        "cost": 1,  # Cost in talent points
                        "icon_color": (150, 150, 200),
                        "position": (0, 0)  # Relative position in tree display
                    },
                    "tower_damage": {
                        "name": "Superior Weaponry",
                        "description": "Increases all tower damage",
                        "levels": 5,
                        "current_level": 0,
                        "effects_per_level": {"tower_damage_multiplier": 0.03},  # +3% per level
                        "requires": {"castle_fortification": 2},  # Requires level 2 in castle_fortification
                        "cost": 1,
                        "icon_color": (200, 100, 100),
                        "position": (0, 1)
                    },
                    "improved_walls": {
                        "name": "Improved Walls",
                        "description": "Increases castle damage reduction",
                        "levels": 3,
                        "current_level": 0,
                        "effects_per_level": {"castle_damage_reduction": 0.05},  # +5% per level
                        "requires": {"castle_fortification": 1},
                        "cost": 1,
                        "icon_color": (100, 120, 170),
                        "position": (-1, 1)
                    },
                    "tower_range": {
                        "name": "Extended Range",
                        "description": "Increases tower attack range",
                        "levels": 3,
                        "current_level": 0,
                        "effects_per_level": {"tower_range_multiplier": 0.05},  # +5% per level
                        "requires": {"tower_damage": 1},
                        "cost": 1,
                        "icon_color": (150, 150, 100),
                        "position": (1, 2)
                    },
                    "castle_regeneration": {
                        "name": "Self-Repair Systems",
                        "description": "Increases castle health regeneration",
                        "levels": 3,
                        "current_level": 0,
                        "effects_per_level": {"castle_regen_multiplier": 0.15},  # +15% per level
                        "requires": {"improved_walls": 1},
                        "cost": 2,
                        "icon_color": (100, 170, 170),
                        "position": (-1, 2)
                    }
                }
            },
            
            "economy": {
                "name": "Economy",
                "description": "Improve resource generation and management",
                "talents": {
                    "resource_gathering": {
                        "name": "Efficient Gathering",
                        "description": "Increases resource production from all sources",
                        "levels": 5,
                        "current_level": 0,
                        "effects_per_level": {"resource_production_multiplier": 0.05},  # +5% per level
                        "requires": {},
                        "cost": 1,
                        "icon_color": (100, 180, 100),
                        "position": (0, 0)
                    },
                    "storage_capacity": {
                        "name": "Expanded Storage",
                        "description": "Increases maximum resource storage capacity",
                        "levels": 3,
                        "current_level": 0,
                        "effects_per_level": {"resource_capacity_multiplier": 0.1},  # +10% per level
                        "requires": {"resource_gathering": 1},
                        "cost": 1,
                        "icon_color": (130, 160, 100),
                        "position": (-1, 1)
                    },
                    "mining_efficiency": {
                        "name": "Mining Efficiency",
                        "description": "Increases stone and ore production",
                        "levels": 4,
                        "current_level": 0,
                        "effects_per_level": {"mining_multiplier": 0.08},  # +8% per level
                        "requires": {"resource_gathering": 2},
                        "cost": 1,
                        "icon_color": (150, 150, 150),
                        "position": (0, 1)
                    },
                    "monster_loot": {
                        "name": "Improved Salvaging",
                        "description": "Increases Monster Coin drops from monsters",
                        "levels": 5,
                        "current_level": 0,
                        "effects_per_level": {"monster_coin_drop_multiplier": 0.06},  # +6% per level
                        "requires": {"resource_gathering": 1},
                        "cost": 1,
                        "icon_color": (180, 130, 180),
                        "position": (1, 1)
                    },
                    "farm_yield": {
                        "name": "Advanced Farming",
                        "description": "Increases food production from farms",
                        "levels": 3,
                        "current_level": 0,
                        "effects_per_level": {"farm_production_multiplier": 0.1},  # +10% per level
                        "requires": {"mining_efficiency": 1},
                        "cost": 1,
                        "icon_color": (150, 200, 100),
                        "position": (0, 2)
                    }
                }
            },
            
            "technology": {
                "name": "Technology",
                "description": "Unlock new abilities and special upgrades",
                "talents": {
                    "research_speed": {
                        "name": "Advanced Research",
                        "description": "Increases research speed in Research Lab",
                        "levels": 3,
                        "current_level": 0,
                        "effects_per_level": {"research_speed_multiplier": 0.1},  # +10% per level
                        "requires": {},
                        "cost": 1,
                        "icon_color": (100, 160, 220),
                        "position": (0, 0)
                    },
                    "tower_specialization": {
                        "name": "Tower Specialization",
                        "description": "Unlocks additional tower upgrade paths",
                        "levels": 3,
                        "current_level": 0,
                        "effects_per_level": {"tower_upgrade_paths": 1},  # +1 upgrade path per level
                        "requires": {"research_speed": 1},
                        "cost": 2,
                        "icon_color": (200, 160, 100),
                        "position": (1, 1)
                    },
                    "monster_analysis": {
                        "name": "Monster Analysis",
                        "description": "Improves Monster Codex efficacy",
                        "levels": 2,
                        "current_level": 0,
                        "effects_per_level": {"monster_weakness_multiplier": 0.07},  # +7% per level
                        "requires": {"research_speed": 2},
                        "cost": 1,
                        "icon_color": (200, 100, 100),
                        "position": (-1, 1)
                    },
                    "special_ammunition": {
                        "name": "Special Ammunition",
                        "description": "Towers have a chance to deal critical damage",
                        "levels": 3,
                        "current_level": 0,
                        "effects_per_level": {"critical_hit_chance": 0.03},  # +3% chance per level
                        "requires": {"tower_specialization": 1},
                        "cost": 2,
                        "icon_color": (220, 180, 80),
                        "position": (1, 2)
                    },
                    "auto_repair": {
                        "name": "Automated Repairs",
                        "description": "Castle periodically repairs itself when damaged",
                        "levels": 1,
                        "current_level": 0,
                        "effects_per_level": {"auto_repair_trigger": 1},  # Boolean trigger
                        "requires": {"monster_analysis": 1},
                        "cost": 3,
                        "icon_color": (100, 200, 200),
                        "position": (-1, 2)
                    }
                }
            }
        }
    
    def update(self, dt):
        """
        Update town hall
        
        Args:
            dt: Time delta in seconds
        """
        # Town hall specific updates
        pass
    
    def draw(self, screen):
        """
        Draw town hall
        
        Args:
            screen: Pygame surface to draw on
        """
        # Fix for town hall disappearing - make sure to draw the base building properly
        if not hasattr(self, 'rect') or not self.rect:
            print(f"Recreating rect for {self.name} at position {self.position}")
            self.rect = pygame.Rect(
                self.position[0] - self.size[0] // 2,
                self.position[1] - self.size[1] // 2,
                self.size[0],
                self.size[1]
            )
            
        super().draw(screen)
        
        # Draw more details for town hall when selected
        if self.is_selected:
            # Draw talent information panel
            info_rect = pygame.Rect(
                self.rect.left - 100,
                self.rect.bottom + 10,
                self.rect.width + 200,
                180  # Increased height to fit the button
            )
            pygame.draw.rect(screen, (30, 30, 50), info_rect)
            pygame.draw.rect(screen, (100, 100, 150), info_rect, 2)
            
            # Draw talent tree info
            font = pygame.font.Font(None, scale_value(20))
            title = font.render("Talent Trees:", True, (220, 220, 180))
            screen.blit(title, (info_rect.left + 10, info_rect.top + 10))
            
            # Draw each talent tree summary
            y_offset = 35
            for tree_name, tree_data in self.talent_trees.items():
                # Count invested talent points in this tree
                tree_level = sum(talent["current_level"] for talent in tree_data["talents"].values())
                max_level = sum(talent["levels"] for talent in tree_data["talents"].values())
                
                # Format tree info
                tree_text = f"{tree_data['name']}: {tree_level}/{max_level} Points"
                tree_surface = font.render(tree_text, True, (200, 200, 200))
                screen.blit(tree_surface, (info_rect.left + 20, info_rect.top + y_offset))
                y_offset += 25
            
            # Draw available talent points
            points_text = f"Available Talent Points: {self.talent_points}"
            points_surface = font.render(points_text, True, (220, 220, 100))
            screen.blit(points_surface, (info_rect.left + 10, info_rect.top + y_offset + 10))
            y_offset += 40
            
            # Draw "View Talent Tree" button
            button_rect = pygame.Rect(
                info_rect.centerx - scale_value(90),
                info_rect.top + y_offset,
                scale_value(180),
                scale_value(30)
            )
            
            # Store button rect for click detection
            self.view_talents_button_rect = button_rect
            
            # Check if mouse is hovering over button
            mouse_pos = pygame.mouse.get_pos()
            button_hovered = button_rect.collidepoint(mouse_pos)
            
            # Draw button with hover effect
            button_color = (100, 140, 200) if button_hovered else (80, 100, 170)
            pygame.draw.rect(screen, button_color, button_rect)
            pygame.draw.rect(screen, (150, 180, 255), button_rect, 2)
            
            # Draw button text
            button_text = font.render("View Talent Tree", True, (230, 230, 250))
            button_text_rect = button_text.get_rect(center=button_rect.center)
            screen.blit(button_text, button_text_rect)
    
    def get_info_text(self):
        """
        Get town hall information text
        
        Returns:
            List of text lines with town hall information
        """
        info = super().get_info_text()
        info.extend([
            f"Talent Points: {self.talent_points}",
            "Talent Trees:",
            f"  Defense: Level {self.talent_trees['defense']['level']}/{self.talent_trees['defense']['max_level']}",
            f"  Economy: Level {self.talent_trees['economy']['level']}/{self.talent_trees['economy']['max_level']}",
            f"  Technology: Level {self.talent_trees['technology']['level']}/{self.talent_trees['technology']['max_level']}"
        ])
        return info
    
    def add_talent_points(self, amount=1):
        """
        Add talent points
        
        Args:
            amount: Amount to add
        """
        self.talent_points += amount
    
    def spend_talent_points(self, tree_name, talent_id, amount=1):
        """
        Spend talent points on a specific talent
        
        Args:
            tree_name: Name of talent tree
            talent_id: ID of the talent to upgrade
            amount: Amount of points to spend
            
        Returns:
            True if points were spent, False if insufficient or max level
        """
        if tree_name not in self.talent_trees:
            return False
        
        # Get tree and talent
        tree = self.talent_trees[tree_name]
        if talent_id not in tree["talents"]:
            return False
            
        talent = tree["talents"][talent_id]
        
        # Check if talent is already at max level
        if talent["current_level"] >= talent["levels"]:
            return False
            
        # Check requirements
        for req_talent_id, req_level in talent["requires"].items():
            if req_talent_id not in tree["talents"]:
                return False
                
            if tree["talents"][req_talent_id]["current_level"] < req_level:
                return False
        
        # Check if enough points
        if self.talent_points < talent["cost"]:
            return False
        
        # Spend points and upgrade talent
        self.talent_points -= talent["cost"]
        talent["current_level"] += 1
        
        # Apply the effects of this talent
        self.apply_talent_effects()
        
        return True
        
    def apply_talent_effects(self):
        """
        Apply all talent effects to game components
        This method should be called when talents change or when loading a saved game
        """
        # Apply effects to appropriate game components
        self.apply_castle_effects()
        self.apply_tower_effects()
        self.apply_economy_effects()
        
    def apply_castle_effects(self):
        """
        Apply talent effects to the castle
        """
        # Get castle from registry
        if not self.registry or not self.registry.has("castle"):
            return
            
        castle = self.registry.get("castle")
        
        # Apply health multiplier
        health_multiplier = 1.0
        if "castle_fortification" in self.talent_trees["defense"]["talents"]:
            talent = self.talent_trees["defense"]["talents"]["castle_fortification"]
            if talent["current_level"] > 0:
                effect = talent["effects_per_level"]["castle_health_multiplier"] * talent["current_level"]
                health_multiplier += effect
        
        # Update castle max health (but maintain health percentage)
        health_percent = castle.health / castle.max_health if castle.max_health > 0 else 1.0
        base_max_health = castle.max_health / health_multiplier
        castle.max_health = base_max_health * health_multiplier
        castle.health = castle.max_health * health_percent
        
        # Apply damage reduction
        if "improved_walls" in self.talent_trees["defense"]["talents"]:
            talent = self.talent_trees["defense"]["talents"]["improved_walls"]
            if talent["current_level"] > 0:
                effect = talent["effects_per_level"]["castle_damage_reduction"] * talent["current_level"]
                castle.damage_reduction = min(0.9, castle.damage_reduction + effect)  # Cap at 90%
        
        # Apply health regeneration
        if "castle_regeneration" in self.talent_trees["defense"]["talents"]:
            talent = self.talent_trees["defense"]["talents"]["castle_regeneration"]
            if talent["current_level"] > 0:
                effect = talent["effects_per_level"]["castle_regen_multiplier"] * talent["current_level"]
                # Modified the existing regeneration rate
                castle.health_regen *= (1 + effect)
        
        # Apply auto-repair if unlocked
        if "auto_repair" in self.talent_trees["technology"]["talents"]:
            talent = self.talent_trees["technology"]["talents"]["auto_repair"]
            if talent["current_level"] > 0:
                # This would trigger auto-repair logic in the castle class
                # Actual implementation would need to be added to the Castle class
                pass
    
    def apply_tower_effects(self):
        """
        Apply talent effects to all towers
        """
        # Get towers from registry
        if not self.registry or not self.registry.has("towers"):
            return
            
        towers = self.registry.get("towers")
        
        # Calculate effect multipliers
        damage_multiplier = 1.0
        range_multiplier = 1.0
        critical_hit_chance = 0.0
        
        # Superior Weaponry talent (damage)
        if "tower_damage" in self.talent_trees["defense"]["talents"]:
            talent = self.talent_trees["defense"]["talents"]["tower_damage"]
            if talent["current_level"] > 0:
                effect = talent["effects_per_level"]["tower_damage_multiplier"] * talent["current_level"]
                damage_multiplier += effect
        
        # Extended Range talent (range)
        if "tower_range" in self.talent_trees["defense"]["talents"]:
            talent = self.talent_trees["defense"]["talents"]["tower_range"]
            if talent["current_level"] > 0:
                effect = talent["effects_per_level"]["tower_range_multiplier"] * talent["current_level"]
                range_multiplier += effect
        
        # Special Ammunition talent (critical hits)
        if "special_ammunition" in self.talent_trees["technology"]["talents"]:
            talent = self.talent_trees["technology"]["talents"]["special_ammunition"]
            if talent["current_level"] > 0:
                critical_hit_chance = talent["effects_per_level"]["critical_hit_chance"] * talent["current_level"]
        
        # Apply effects to all towers
        for tower in towers:
            # Store talent-based multipliers for the tower to use
            tower.talent_damage_multiplier = damage_multiplier
            tower.talent_range_multiplier = range_multiplier
            tower.talent_critical_hit_chance = critical_hit_chance
            
            # Apply the effects directly if the tower class doesn't handle them
            # For demonstration, we'll apply them directly here
            if hasattr(tower, 'base_damage'):
                tower.damage = tower.base_damage * damage_multiplier
            
            if hasattr(tower, 'base_range'):
                tower.range = tower.base_range * range_multiplier
    
    def apply_economy_effects(self):
        """
        Apply talent effects to economy components (resource production, etc.)
        """
        # Get resource manager and other economy components
        if not self.registry or not self.registry.has("resource_manager"):
            return
            
        resource_manager = self.registry.get("resource_manager")
        
        # Calculate production multipliers
        resource_multiplier = 1.0
        mining_multiplier = 1.0
        farm_multiplier = 1.0
        monster_loot_multiplier = 1.0
        
        # Resource Gathering talent
        if "resource_gathering" in self.talent_trees["economy"]["talents"]:
            talent = self.talent_trees["economy"]["talents"]["resource_gathering"]
            if talent["current_level"] > 0:
                effect = talent["effects_per_level"]["resource_production_multiplier"] * talent["current_level"]
                resource_multiplier += effect
        
        # Mining Efficiency talent
        if "mining_efficiency" in self.talent_trees["economy"]["talents"]:
            talent = self.talent_trees["economy"]["talents"]["mining_efficiency"]
            if talent["current_level"] > 0:
                effect = talent["effects_per_level"]["mining_multiplier"] * talent["current_level"]
                mining_multiplier += effect
        
        # Farm Yield talent
        if "farm_yield" in self.talent_trees["economy"]["talents"]:
            talent = self.talent_trees["economy"]["talents"]["farm_yield"]
            if talent["current_level"] > 0:
                effect = talent["effects_per_level"]["farm_production_multiplier"] * talent["current_level"]
                farm_multiplier += effect
        
        # Monster Loot talent
        if "monster_loot" in self.talent_trees["economy"]["talents"]:
            talent = self.talent_trees["economy"]["talents"]["monster_loot"]
            if talent["current_level"] > 0:
                effect = talent["effects_per_level"]["monster_coin_drop_multiplier"] * talent["current_level"]
                monster_loot_multiplier += effect
        
        # Store these multipliers in the resource manager for it to use
        resource_manager.talent_resource_multiplier = resource_multiplier
        resource_manager.talent_mining_multiplier = mining_multiplier
        resource_manager.talent_farm_multiplier = farm_multiplier
        resource_manager.talent_monster_loot_multiplier = monster_loot_multiplier
        
        # Get buildings from registry to apply to farms and mines
        if self.registry.has("buildings"):
            buildings = self.registry.get("buildings")
            
            # Apply to all buildings
            for building in buildings:
                # Apply mining multiplier to mines
                if building.__class__.__name__ == "Mine":
                    building.talent_multiplier = mining_multiplier * resource_multiplier
                
                # Apply farm multiplier to farms
                elif building.__class__.__name__ == "Farm":
                    building.talent_multiplier = farm_multiplier * resource_multiplier
        
        # Get wave manager to apply monster loot multiplier
        if self.registry.has("wave_manager"):
            wave_manager = self.registry.get("wave_manager")
            wave_manager.talent_loot_multiplier = monster_loot_multiplier
    
    def can_upgrade_talent(self, tree_name, talent_id):
        """
        Check if a talent can be upgraded
        
        Args:
            tree_name: Name of the talent tree
            talent_id: ID of the talent
            
        Returns:
            Tuple of (can_upgrade, reason)
            where reason is None if can_upgrade is True, or a string explanation otherwise
        """
        if tree_name not in self.talent_trees:
            return False, "Unknown talent tree"
        
        tree = self.talent_trees[tree_name]
        if talent_id not in tree["talents"]:
            return False, "Unknown talent"
            
        talent = tree["talents"][talent_id]
        
        # Check if talent is already at max level
        if talent["current_level"] >= talent["levels"]:
            return False, "Already at maximum level"
            
        # Check requirements
        for req_talent_id, req_level in talent["requires"].items():
            if req_talent_id not in tree["talents"]:
                return False, f"Missing required talent: {req_talent_id}"
                
            req_talent = tree["talents"][req_talent_id]
            if req_talent["current_level"] < req_level:
                return False, f"Requires {req_talent['name']} level {req_level}"
        
        # Check if enough points
        if self.talent_points < talent["cost"]:
            return False, f"Not enough talent points (need {talent['cost']})"
        
        return True, None
    
    def upgrade(self):
        """
        Upgrade the town hall
        
        Returns:
            True if upgrade successful, False otherwise
        """
        success = super().upgrade()
        
        if success:
            # Increase village capacity when town hall is upgraded
            village = self.registry.get("game").village
            village.increase_capacity(1)
            village.increase_development_level()
        
        return success

class ResearchLab(VillageBuilding):
    """Building for researching technologies"""
    def __init__(self, position, registry):
        """
        Initialize research lab
        
        Args:
            position: Tuple of (x, y) coordinates
            registry: Component registry
        """
        super().__init__(position, registry)
        self.name = "Research Lab"
        self.description = "Discovers and develops technological improvements"
        self.color = (50, 100, 150)  # Blue color for research lab
        self.building_type = "research_lab"
        
        # Research data
        self.current_research = None
        self.research_progress = 0
        self.research_time = 60  # Base research time in seconds
        
        # Available research (initially all locked)
        self.available_research = {
            "materials_efficiency": {"level": 0, "max_level": 5, "unlocked": True, "cost": {"Stone": 100}},
            "weapon_damage": {"level": 0, "max_level": 5, "unlocked": True, "cost": {"Stone": 80, "Iron": 20}},
            "construction_speed": {"level": 0, "max_level": 3, "unlocked": True, "cost": {"Stone": 120, "Iron": 40}},
            "energy_systems": {"level": 0, "max_level": 3, "unlocked": False, "cost": {"Stone": 100, "Iron": 30, "Copper": 10}}
        }
        
        # Research requirements (dependencies)
        self.research_requirements = {
            "energy_systems": {"materials_efficiency": 2, "construction_speed": 1}
        }
    
    def update(self, dt):
        """
        Update research lab
        
        Args:
            dt: Time delta in seconds
        """
        # Progress research if active
        if self.current_research:
            self.research_progress += dt
            
            # Complete research if time is up
            if self.research_progress >= self.research_time:
                self.complete_research()
    
    def draw(self, screen):
        """
        Draw research lab
        
        Args:
            screen: Pygame surface to draw on
        """
        super().draw(screen)
        
        # Draw research progress if active
        if self.current_research:
            # Draw progress bar
            progress_width = int((self.research_progress / self.research_time) * self.rect.width)
            progress_rect = pygame.Rect(
                self.rect.left,
                self.rect.bottom + 5,
                progress_width,
                8
            )
            
            # Background bar
            pygame.draw.rect(screen, (70, 70, 70), 
                            (self.rect.left, self.rect.bottom + 5, self.rect.width, 8))
            
            # Progress bar
            pygame.draw.rect(screen, (50, 150, 200), progress_rect)
            
            # Progress text
            font = pygame.font.Font(None, scale_value(16))
            progress_text = f"Researching: {self.current_research} ({int(self.research_progress)}/{int(self.research_time)}s)"
            text_surface = font.render(progress_text, True, (200, 200, 250))
            text_rect = text_surface.get_rect(center=(self.rect.centerx, self.rect.bottom + 20))
            screen.blit(text_surface, text_rect)
        
        # Draw more details when selected
        if self.is_selected:
            # Draw research information
            info_rect = pygame.Rect(
                self.rect.right + 10,
                self.rect.top,
                300,
                200
            )
            pygame.draw.rect(screen, (30, 30, 50), info_rect)
            pygame.draw.rect(screen, (100, 100, 150), info_rect, 2)
            
            # Draw research tree info
            font = pygame.font.Font(None, scale_value(20))
            title = font.render("Available Research:", True, (220, 220, 180))
            screen.blit(title, (info_rect.left + 10, info_rect.top + 10))
            
            # Draw each research option
            y_offset = 35
            for research_name, research_data in self.available_research.items():
                if research_data["unlocked"]:
                    color = (200, 200, 200)
                    status = "Available"
                else:
                    color = (150, 150, 150)
                    status = "Locked"
                
                # Show completed if at max level
                if research_data["level"] >= research_data["max_level"]:
                    status = "Completed"
                    color = (100, 200, 100)
                
                research_text = f"{research_name.replace('_', ' ').title()}: {status}"
                level_text = f"Level {research_data['level']}/{research_data['max_level']}"
                
                research_surface = font.render(research_text, True, color)
                level_surface = font.render(level_text, True, color)
                
                screen.blit(research_surface, (info_rect.left + 15, info_rect.top + y_offset))
                screen.blit(level_surface, (info_rect.left + 200, info_rect.top + y_offset))
                
                y_offset += 25
    
    def start_research(self, research_name):
        """
        Start researching a technology
        
        Args:
            research_name: Name of research to start
            
        Returns:
            True if research started, False otherwise
        """
        # Check if already researching
        if self.current_research:
            return False
        
        # Check if research exists and is unlocked
        if research_name not in self.available_research:
            return False
        
        research = self.available_research[research_name]
        if not research["unlocked"]:
            return False
        
        # Check if already at max level
        if research["level"] >= research["max_level"]:
            return False
        
        # Check dependencies
        if research_name in self.research_requirements:
            for req_name, req_level in self.research_requirements[research_name].items():
                if self.available_research[req_name]["level"] < req_level:
                    return False
        
        # Check resources
        resource_manager = self.registry.get("resource_manager")
        if not resource_manager.has_resources(research["cost"]):
            return False
        
        # Spend resources
        if not resource_manager.spend_resources(research["cost"]):
            return False
        
        # Start research
        self.current_research = research_name
        self.research_progress = 0
        
        # Scale research time based on lab level
        self.research_time = 60 / (1 + (self.level - 1) * 0.2)  # 20% faster per level
        
        return True
    
    def complete_research(self):
        """
        Complete current research
        
        Returns:
            True if research completed, False if no research active
        """
        if not self.current_research:
            return False
        
        # Increase research level
        research = self.available_research[self.current_research]
        research["level"] += 1
        
        # Apply research effects
        self.apply_research_effects(self.current_research, research["level"])
        
        # Reset research state
        current = self.current_research
        self.current_research = None
        self.research_progress = 0
        
        # Check for newly unlockable research
        self.check_unlock_research()
        
        return True
    
    def apply_research_effects(self, research_name, level):
        """
        Apply effects of completed research
        
        Args:
            research_name: Name of completed research
            level: New level of the research
        """
        # Apply different effects based on research type
        if research_name == "materials_efficiency":
            # Increase resource storage capacity or gathering efficiency
            pass
        
        elif research_name == "weapon_damage":
            # Increase tower damage
            pass
        
        elif research_name == "construction_speed":
            # Reduce building and upgrade times
            pass
        
        elif research_name == "energy_systems":
            # Unlock special buildings or abilities
            pass
    
    def check_unlock_research(self):
        """Check and unlock research options based on prerequisites"""
        for research_name, requirements in self.research_requirements.items():
            if not self.available_research[research_name]["unlocked"]:
                # Check if all requirements are met
                requirements_met = True
                for req_name, req_level in requirements.items():
                    if self.available_research[req_name]["level"] < req_level:
                        requirements_met = False
                        break
                
                # Unlock if all requirements met
                if requirements_met:
                    self.available_research[research_name]["unlocked"] = True
    
    def get_info_text(self):
        """
        Get research lab information text
        
        Returns:
            List of text lines with research lab information
        """
        info = super().get_info_text()
        
        if self.current_research:
            progress_percent = int((self.research_progress / self.research_time) * 100)
            info.append(f"Researching: {self.current_research} ({progress_percent}%)")
        else:
            info.append("No active research")
        
        info.append("Available Research:")
        for name, data in self.available_research.items():
            if data["unlocked"]:
                status = f"Level {data['level']}/{data['max_level']}"
            else:
                status = "Locked"
            info.append(f"  {name}: {status}")
        
        return info

class MonsterCodex(VillageBuilding):
    """Building for monster research, tracking, and challenges"""
    def __init__(self, position, registry):
        """
        Initialize monster codex
        
        Args:
            position: Tuple of (x, y) coordinates
            registry: Component registry
        """
        super().__init__(position, registry)
        self.name = "Monster Codex"
        self.description = "Catalogues monsters and provides monster-specific challenges"
        self.color = (150, 50, 50)  # Reddish color for monster database
        self.building_type = "monster_codex"
        
        # Monster data storage
        self.monster_data = {}
        
        # Last selected monster
        self.selected_monster = None
        
        # Knowledge tiers and thresholds
        self.knowledge_tiers = {
            1: 10,    # Basic info
            2: 50,    # Combat data
            3: 100,   # Placeholder - will be defined
            4: 250,   # Placeholder - will be defined
            5: 500    # Master knowledge
        }
        
        # Challenge tiers and thresholds
        self.challenge_tiers = {
            "bronze": 250,
            "silver": 1000,
            "gold": 2500,
            "platinum": 10000
        }
        
        # Track challenge completions
        self.challenge_completions = {}
        
        # Challenge reward cups
        self.monster_cups = {}
    
    def update(self, dt):
        """
        Update monster codex
        
        Args:
            dt: Time delta in seconds
        """
        # Monster codex specific updates - currently none needed
        pass
    
    def draw(self, screen):
        """
        Draw monster codex
        
        Args:
            screen: Pygame surface to draw on
        """
        super().draw(screen)
        
        # Draw more details when selected
        if self.is_selected:
            # Draw monster information
            info_rect = pygame.Rect(
                self.rect.left - 50,
                self.rect.bottom + 10,
                self.rect.width + 100,
                200
            )
            pygame.draw.rect(screen, (50, 30, 30), info_rect)
            pygame.draw.rect(screen, (150, 100, 100), info_rect, 2)
            
            # Draw monster codex info
            font = pygame.font.Font(None, scale_value(20))
            title = font.render("Monster Codex:", True, (220, 180, 180))
            screen.blit(title, (info_rect.left + 10, info_rect.top + 10))
            
            # Draw monster data or empty message
            if not self.monster_data:
                empty_text = "No monster data collected yet."
                empty_surface = font.render(empty_text, True, (180, 150, 150))
                screen.blit(empty_surface, (info_rect.left + 10, info_rect.top + 70))
            else:
                # List some monsters in the database
                monsters_text = "Monsters recorded:"
                monsters_surface = font.render(monsters_text, True, (200, 180, 180))
                screen.blit(monsters_surface, (info_rect.left + 10, info_rect.top + 70))
                
                y_offset = 95
                for i, (monster_type, monster_info) in enumerate(list(self.monster_data.items())[:5]):
                    # Determine knowledge tier
                    tier = self.get_knowledge_tier(monster_type)
                    
                    # Show monster info with tier and kill count
                    monster_text = f"{monster_type}: Tier {tier} - {monster_info['kills']} kills"
                    monster_surface = font.render(monster_text, True, (180, 160, 160))
                    screen.blit(monster_surface, (info_rect.left + 20, info_rect.top + y_offset))
                    y_offset += 20
                
                # If there are more monsters, show a message
                if len(self.monster_data) > 5:
                    more_text = f"... and {len(self.monster_data) - 5} more"
                    more_surface = font.render(more_text, True, (180, 160, 160))
                    screen.blit(more_surface, (info_rect.left + 20, info_rect.top + y_offset))
            
            # Show instructions to open full monster codex interface
            y_offset = info_rect.height - 30
            hint_text = "Click to view Monster Codex details"
            hint_surface = font.render(hint_text, True, (200, 200, 200))
            hint_rect = hint_surface.get_rect(center=(info_rect.centerx, info_rect.top + y_offset))
            screen.blit(hint_surface, hint_rect)
    
    def record_monster(self, monster_type):
        """
        Record a monster encounter
        
        Args:
            monster_type: Type of monster encountered
        """
        # Initialize monster data if not already recorded
        if monster_type not in self.monster_data:
            self.monster_data[monster_type] = {
                "kills": 0,
                "first_seen": None,  # Could add timestamp
                "knowledge_tier": 0,  # No knowledge yet
                "challenge_progress": {
                    "bronze": False,
                    "silver": False,
                    "gold": False,
                    "platinum": False
                }
            }
    
    def record_kill(self, monster_type):
        """
        Record a monster kill
        
        Args:
            monster_type: Type of monster killed
        """
        # Ensure monster is in the database
        self.record_monster(monster_type)
        
        # Ensure monster_stats dictionary exists
        if not hasattr(self, 'monster_stats'):
            self.monster_stats = {}
            print("Initializing monster_stats dictionary in Monster Codex")
        
        # Make sure monster type exists in monster_stats
        if monster_type not in self.monster_stats:
            self.monster_stats[monster_type] = {
                "kills": 0,
                "challenges": {
                    "bronze": False,
                    "silver": False,
                    "gold": False,
                    "platinum": False
                }
            }
            print(f"Added new monster type to monster_stats: {monster_type}")
        
        # Increment kill count in monster_data
        self.monster_data[monster_type]["kills"] += 1
        
        # Increment kill count in monster_stats
        self.monster_stats[monster_type]["kills"] += 1
        
        kills_data = self.monster_data[monster_type]["kills"]
        kills_stats = self.monster_stats[monster_type]["kills"]
        print(f"Monster kill recorded for {monster_type}. Data: {kills_data}, Stats: {kills_stats}")
        
        # Check for knowledge tier upgrades
        self.check_knowledge_tier(monster_type)
        
        # Check for challenge availability
        self.check_challenge_availability(monster_type)
    
    def get_knowledge_tier(self, monster_type):
        """
        Get current knowledge tier for a monster
        
        Args:
            monster_type: Type of monster to check
            
        Returns:
            Current knowledge tier (0-5)
        """
        if monster_type not in self.monster_data:
            return 0
            
        kills = self.monster_data[monster_type]["kills"]
        
        # Determine tier based on kill count
        tier = 0
        for t, threshold in self.knowledge_tiers.items():
            if kills >= threshold:
                tier = t
        
        return tier
    
    def check_knowledge_tier(self, monster_type):
        """
        Check and update knowledge tier based on kills
        
        Args:
            monster_type: Type of monster to check
            
        Returns:
            True if tier increased, False otherwise
        """
        if monster_type not in self.monster_data:
            return False
            
        old_tier = self.monster_data[monster_type].get("knowledge_tier", 0)
        new_tier = self.get_knowledge_tier(monster_type)
        
        # Update if increased
        if new_tier > old_tier:
            self.monster_data[monster_type]["knowledge_tier"] = new_tier
            
            # Notify about new knowledge tier
            print(f"Monster knowledge tier increased for {monster_type}: Tier {new_tier}!")
            
            # Show notification to player
            from game import game_instance
            if game_instance and hasattr(game_instance, 'notification_manager'):
                # Choose color based on tier
                tier_colors = {
                    1: (180, 180, 150),  # Basic tier
                    2: (180, 200, 150),  # Combat data tier
                    3: (150, 200, 180),  # Tier 3
                    4: (180, 150, 200),  # Tier 4
                    5: (220, 180, 100)   # Master tier (gold)
                }
                color = tier_colors.get(new_tier, (200, 200, 200))
                
                # Create notification message
                message = f"Knowledge Increased! {monster_type} - Tier {new_tier}"
                game_instance.notification_manager.add_notification(message, 4.0, color)
            
            return True
        
        return False
    
    def check_challenge_availability(self, monster_type):
        """
        Check if new challenge tiers are available based on kill count
        
        Args:
            monster_type: Type of monster to check
        """
        if monster_type not in self.monster_data:
            return
            
        kills = self.monster_data[monster_type]["kills"]
        
        # Check each challenge tier
        for tier, threshold in self.challenge_tiers.items():
            if kills >= threshold:
                # Add notification or indication that this challenge is available
                challenge_key = f"{monster_type}_{tier}"
                if challenge_key not in self.challenge_completions:
                    print(f"{tier.capitalize()} challenge now available for {monster_type}! ({kills}/{threshold} kills)")
                    
                    # Notifications are disabled for challenges
                    # The code to show notifications has been removed
    
    def start_challenge(self, monster_type, tier):
        """
        Start a monster challenge
        
        Args:
            monster_type: Type of monster for challenge
            tier: Challenge tier (bronze, silver, gold, platinum)
            
        Returns:
            True if challenge started, False otherwise
        """
        # Verify monster and tier
        if monster_type not in self.monster_data or tier not in self.challenge_tiers:
            return False
        
        # Check if player has enough kills for this challenge
        kills = self.monster_data[monster_type]["kills"]
        threshold = self.challenge_tiers[tier]
        
        if kills < threshold:
            return False
        
        # Check if challenge already completed
        challenge_key = f"{monster_type}_{tier}"
        if challenge_key in self.challenge_completions and self.challenge_completions[challenge_key]:
            return False
        
        # Get the game instance to start the challenge
        if self.registry and self.registry.has("game"):
            game = self.registry.get("game")
            
            # Start a special wave with only this monster type
            # This would configure the wave manager for challenge mode
            if hasattr(game, "start_monster_challenge"):
                return game.start_monster_challenge(monster_type, tier)
        
        return False
    
    def complete_challenge(self, monster_type, tier):
        """
        Complete a monster challenge and award rewards
        
        Args:
            monster_type: Type of monster for challenge
            tier: Challenge tier (bronze, silver, gold, platinum)
            
        Returns:
            True if challenge completed, False otherwise
        """
        # Verify monster and tier
        if monster_type not in self.monster_data or tier not in self.challenge_tiers:
            return False
        
        # Mark challenge as completed
        challenge_key = f"{monster_type}_{tier}"
        self.challenge_completions[challenge_key] = True
        
        # Add cup to inventory
        cup_name = f"{monster_type} {tier.capitalize()} Cup"
        
        # Add cup to player inventory
        if self.registry and self.registry.has("resource_manager"):
            resource_manager = self.registry.get("resource_manager")
            resource_manager.add_resource(cup_name, 1)
            
            # Add to our tracking
            if monster_type not in self.monster_cups:
                self.monster_cups[monster_type] = []
            
            self.monster_cups[monster_type].append(tier)
            
            # Notify player
            print(f"Challenge completed! {cup_name} awarded.")
            
            # Notifications for challenge completion are disabled
            # The code to show notifications has been removed
            
            return True
        
        return False
    
    def get_info_text(self):
        """
        Get monster codex information text
        
        Returns:
            List of text lines with monster codex information
        """
        info = super().get_info_text()
        info.extend([
            f"Monster Types Recorded: {len(self.monster_data)}",
            f"Challenge Cups Earned: {sum(len(cups) for cups in self.monster_cups.values()) if self.monster_cups else 0}"
        ])
        
        # Add information about selected monster if any
        if self.selected_monster and self.selected_monster in self.monster_data:
            monster_info = self.monster_data[self.selected_monster]
            info.extend([
                f"Selected Monster: {self.selected_monster}",
                f"Kills: {monster_info['kills']}",
                f"Knowledge Tier: {monster_info['knowledge_tier']}"
            ])
            
            # Add challenge information
            if self.selected_monster in self.monster_cups:
                info.append("Earned Cups:")
                for tier in self.monster_cups[self.selected_monster]:
                    info.append(f"  {tier.capitalize()}")
        
        return info
    
    def get_challenge_status(self, monster_type):
        """
        Get the status of challenges for a monster type
        
        Args:
            monster_type: Monster type to check
            
        Returns:
            Dictionary of challenge tiers and their status
        """
        if monster_type not in self.monster_data:
            return {}
            
        kills = self.monster_data[monster_type]["kills"]
        result = {}
        
        for tier, threshold in self.challenge_tiers.items():
            challenge_key = f"{monster_type}_{tier}"
            completed = challenge_key in self.challenge_completions and self.challenge_completions[challenge_key]
            available = kills >= threshold
            
            result[tier] = {
                "completed": completed,
                "available": available,
                "threshold": threshold,
                "kills": kills
            }
        
        return result

class Farm(VillageBuilding):
    """Building for producing food resources"""
    def __init__(self, position, registry, farm_type="crop"):
        """
        Initialize farm
        
        Args:
            position: Tuple of (x, y) coordinates
            registry: Component registry
            farm_type: Type of farm ("crop" or "livestock")
        """
        super().__init__(position, registry)
        
        self.farm_type = farm_type
        
        if farm_type == "crop":
            self.name = "Crop Field"
            self.description = "Produces grain and fruit"
            self.color = (100, 150, 50)  # Green for crops
            self.production = CROP_FARM_PRODUCTION.copy()
            self.building_type = "crop_farm"
            # Use proper key from VILLAGE_BUILDING_COSTS
            self.upgrade_cost = VILLAGE_BUILDING_COSTS["CropFarm"].copy() if "CropFarm" in VILLAGE_BUILDING_COSTS else {"Stone": 50}
        else:  # livestock
            self.name = "Livestock Pen"
            self.description = "Produces meat and dairy"
            self.color = (150, 120, 80)  # Brown for livestock
            self.production = LIVESTOCK_FARM_PRODUCTION.copy()
            self.building_type = "livestock_farm"
            # Use proper key from VILLAGE_BUILDING_COSTS
            self.upgrade_cost = VILLAGE_BUILDING_COSTS["LivestockFarm"].copy() if "LivestockFarm" in VILLAGE_BUILDING_COSTS else {"Stone": 75, "Iron": 10}
        
        # Production timer
        self.production_timer = 0
        self.production_interval = 30  # Seconds between harvests
    
    def update(self, dt):
        """
        Update farm
        
        Args:
            dt: Time delta in seconds
        """
        # Make sure production_timer is initialized
        if not hasattr(self, 'production_timer'):
            self.production_timer = 0
            print(f"Initialized production_timer for {self.name}")
            
        if not hasattr(self, 'production_interval'):
            self.production_interval = 30  # Seconds between harvests
            print(f"Initialized production_interval for {self.name}")
            
        # Update production timer
        self.production_timer += dt
        if self.production_timer >= self.production_interval:
            self.harvest()
    
    def draw(self, screen):
        """
        Draw farm
        
        Args:
            screen: Pygame surface to draw on
        """
        # Fix for buildings disappearing - make sure to draw the base building properly
        if not hasattr(self, 'rect') or not self.rect:
            print(f"Recreating rect for {self.name} at position {self.position}")
            self.rect = pygame.Rect(
                self.position[0] - self.size[0] // 2,
                self.position[1] - self.size[1] // 2,
                self.size[0],
                self.size[1]
            )
            
        super().draw(screen)
        
        # Make sure production_timer and production_interval are initialized
        if not hasattr(self, 'production_timer'):
            self.production_timer = 0
        if not hasattr(self, 'production_interval'):
            self.production_interval = 30
            
        # Draw production progress
        progress_pct = self.production_timer / self.production_interval
        progress_width = int(self.rect.width * progress_pct)
        
        # Background bar
        pygame.draw.rect(screen, (50, 50, 50), 
                        (self.rect.left, self.rect.bottom + 5, self.rect.width, 8))
        
        # Progress bar - different color based on farm type
        if self.farm_type == "crop":
            progress_color = (100, 200, 50)  # Green for crops
        else:
            progress_color = (200, 150, 50)  # Orange-brown for livestock
            
        pygame.draw.rect(screen, progress_color, 
                        (self.rect.left, self.rect.bottom + 5, progress_width, 8))
        
        # Production text
        font = pygame.font.Font(None, scale_value(16))
        progress_text = f"Producing: {int(progress_pct * 100)}%"
        text_surface = font.render(progress_text, True, (200, 200, 200))
        text_rect = text_surface.get_rect(center=(self.rect.centerx, self.rect.bottom + 20))
        screen.blit(text_surface, text_rect)
    
    def harvest(self):
        """Harvest resources from the farm"""
        # Reset production timer
        self.production_timer = 0
        
        # Add resources based on farm type and level
        resource_manager = self.registry.get("resource_manager")
        
        if resource_manager:
            # Calculate production based on level
            production_multiplier = 1 + (self.level - 1) * 0.2  # 20% increase per level
            
            # Add each resource produced by this farm
            for resource_type, base_amount in self.production.items():
                amount = int(base_amount * production_multiplier)
                resource_manager.add_resource(resource_type, amount)
            
            # Debug output
            print(f"Farm harvested at level {self.level} with multiplier {production_multiplier}")
    
    def upgrade(self):
        """
        Upgrade the farm
        
        Returns:
            True if upgrade successful, False otherwise
        """
        success = super().upgrade()
        
        if success:
            # Increase production rate when farm is upgraded
            for resource_type in self.production:
                self.production[resource_type] = int(self.production[resource_type] * 1.2)
        
        return success
    
    def get_info_text(self):
        """
        Get farm information text
        
        Returns:
            List of text lines with farm information
        """
        info = super().get_info_text()
        
        # Production information
        production_pct = int((self.production_timer / self.production_interval) * 100)
        
        # Calculate production with level multiplier
        production_multiplier = 1 + (self.level - 1) * 0.2  # 20% increase per level
        
        info.append(f"Production Progress: {production_pct}%")
        info.append(f"Harvests every {self.production_interval} seconds")
        info.append("Produces:")
        
        for resource_type, base_amount in self.production.items():
            amount = int(base_amount * production_multiplier)
            info.append(f"  {amount} {resource_type}")
        
        return info