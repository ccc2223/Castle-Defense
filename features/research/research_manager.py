"""
Research manager for Castle Defense - Handles research data, progress, and effects
"""

class ResearchManager:
    """Manages research progress and applies research effects"""
    
    def __init__(self, registry=None):
        """
        Initialize research manager
        
        Args:
            registry: Component registry for accessing game systems
        """
        self.registry = registry
        
        # Research tree structure with alternating node count per column
        self.research_tree = {
            # Column 1 - 1 node
            1: {
                "double_loot": {
                    "name": "Double Loot",
                    "description": "1% chance for monsters to drop double loot when killed.",
                    "current_level": 0,
                    "max_level": 10,
                    "base_chance": 0.01,  # 1% per level
                    "time_cost": self._calculate_time_cost(1, 1),  # column 1, level 1
                    "resource_cost": {},  # Placeholder for future resource costs
                    "unlocked": True,
                    "prerequisites": []
                }
            },
            # Column 2 - 2 nodes
            2: {
                "castle_healer": {
                    "name": "Castle Healer",
                    "description": "Restore 50 HP to the castle when a boss is killed. Cannot exceed current max health.",
                    "current_level": 0,
                    "max_level": 10,
                    "heal_amount": 50,  # 50 HP per level
                    "time_cost": self._calculate_time_cost(2, 1),  # column 2, level 1
                    "resource_cost": {},  # Placeholder for future resource costs
                    "unlocked": False,
                    "prerequisites": ["double_loot"]
                },
                "free_upgrades": {
                    "name": "Free Upgrades",
                    "description": "1% chance to upgrade random upgrade option (damage, attack speed, range) of a placed tower.",
                    "current_level": 0,
                    "max_level": 10,
                    "base_chance": 0.01,  # 1% per level
                    "time_cost": self._calculate_time_cost(2, 1),  # column 2, level 1
                    "resource_cost": {},  # Placeholder for future resource costs
                    "unlocked": False,
                    "prerequisites": ["double_loot"]
                }
            },
            # Column 3 - 1 node
            3: {
                "clockwork_speed": {
                    "name": "Clockwork Speed",
                    "description": "Increase game speed by 0.2. This is reflected on the speed slider.",
                    "current_level": 0,
                    "max_level": 10,
                    "speed_increase": 0.2,  # 0.2 per level
                    "time_cost": self._calculate_time_cost(3, 1),  # column 3, level 1
                    "resource_cost": {},  # Placeholder for future resource costs
                    "unlocked": False,
                    "prerequisites": ["castle_healer", "free_upgrades"]
                }
            },
            # Column 4 - 2 nodes
            4: {
                "monster_weakness": {
                    "name": "Monster Weakness",
                    "description": "All towers deal 2% more damage to monsters.",
                    "current_level": 0,
                    "max_level": 10,
                    "damage_multiplier": 0.02,  # 2% per level
                    "time_cost": self._calculate_time_cost(4, 1),  # column 4, level 1
                    "resource_cost": {},  # Placeholder for future resource costs
                    "unlocked": False,
                    "prerequisites": ["clockwork_speed"]
                },
                "resource_efficiency": {
                    "name": "Resource Efficiency",
                    "description": "Reduce tower and building costs by 1%.",
                    "current_level": 0,
                    "max_level": 10,
                    "cost_reduction": 0.01,  # 1% per level
                    "time_cost": self._calculate_time_cost(4, 1),  # column 4, level 1
                    "resource_cost": {},  # Placeholder for future resource costs
                    "unlocked": False,
                    "prerequisites": ["clockwork_speed"]
                }
            },
            # Column 5 - 1 node
            5: {
                "advanced_engineering": {
                    "name": "Advanced Engineering",
                    "description": "Towers gain 1% attack speed.",
                    "current_level": 0,
                    "max_level": 10,
                    "attack_speed_multiplier": 0.01,  # 1% per level
                    "time_cost": self._calculate_time_cost(5, 1),  # column 5, level 1
                    "resource_cost": {},  # Placeholder for future resource costs
                    "unlocked": False,
                    "prerequisites": ["monster_weakness", "resource_efficiency"]
                }
            }
        }
        
        # Active research and progress
        self.active_research = None
        self.active_research_id = None
        self.active_column = None
        self.research_progress = 0.0
        self.research_complete = False
        
        # Track unlocked columns
        self.unlocked_columns = [1]  # Start with column 1 unlocked
        
        # Apply initial research effects (none active yet)
        self.apply_research_effects()
        
        # Initialize research unlocks to make first nodes clickable
        self.initialize_unlocks()
    
    def _calculate_time_cost(self, column, level):
        """
        Calculate research time based on column and level
        
        Args:
            column: Research tree column (1-indexed)
            level: Research level (1-indexed)
            
        Returns:
            Time cost in seconds
        """
        # Base time is 15 seconds
        base_time = 15
        
        # Column modifier: +5 seconds per column (starting from column 1)
        column_modifier = (column - 1) * 5
        
        # Level modifier: +5 seconds per level (starting from level 1)
        level_modifier = (level - 1) * 5
        
        # Total time
        total_time = base_time + column_modifier + level_modifier
        
        return total_time
    
    def get_available_research(self):
        """
        Get all available research options
        
        Returns:
            Dictionary of available research nodes
        """
        available = {}
        
        # Check each column that's unlocked
        for column in self.unlocked_columns:
            if column in self.research_tree:
                for research_id, research in self.research_tree[column].items():
                    # Add if unlocked and not at max level
                    if research["unlocked"] and research["current_level"] < research["max_level"]:
                        available[research_id] = research
        
        return available
    
    def get_research_by_id(self, research_id):
        """
        Get research data by ID
        
        Args:
            research_id: Research identifier
            
        Returns:
            Research data or None if not found
        """
        # Search all columns for this research ID
        for column, researches in self.research_tree.items():
            if research_id in researches:
                return researches[research_id]
        
        return None
    
    def get_column_for_research(self, research_id):
        """
        Get the column number for a research ID
        
        Args:
            research_id: Research identifier
            
        Returns:
            Column number or None if not found
        """
        for column, researches in self.research_tree.items():
            if research_id in researches:
                return column
        
        return None
    
    def start_research(self, research_id):
        """
        Start researching a technology
        
        Args:
            research_id: ID of research to start
            
        Returns:
            True if research started, False otherwise
        """
        # Get research data
        research = self.get_research_by_id(research_id)
        if not research:
            return False
            
        # Check if already at max level
        if research["current_level"] >= research["max_level"]:
            return False
            
        # Check if already researching something
        if self.active_research:
            return False
            
        # Check if unlocked
        if not research["unlocked"]:
            return False
        
        # Calculate research time for next level
        next_level = research["current_level"] + 1
        column = self.get_column_for_research(research_id)
        
        # Set as active research
        self.active_research = research
        self.active_research_id = research_id
        self.active_column = column
        self.research_progress = 0.0
        self.research_complete = False
        
        # Calculate time cost for the next level
        research["time_cost"] = self._calculate_time_cost(column, next_level)
        
        return True
    
    def cancel_research(self):
        """
        Cancel current research
        
        Returns:
            True if research was canceled, False if no active research
        """
        if not self.active_research:
            return False
            
        # Reset research state
        self.active_research = None
        self.active_research_id = None
        self.active_column = None
        self.research_progress = 0.0
        self.research_complete = False
        
        return True
    
    def update(self, dt):
        """
        Update research progress
        
        Args:
            dt: Time delta in seconds
            
        Returns:
            True if research completed this update, False otherwise
        """
        if not self.active_research or self.research_complete:
            return False
            
        # Progress the research
        self.research_progress += dt
        
        # Check if research is complete
        if self.research_progress >= self.active_research["time_cost"]:
            self.complete_research()
            return True
            
        return False
    
    def complete_research(self):
        """
        Complete current research and apply effects
        
        Returns:
            True if research completed, False if no active research
        """
        if not self.active_research or self.research_complete:
            return False
            
        # Increment research level
        self.active_research["current_level"] += 1
        
        # Mark as complete
        self.research_complete = True
        
        # Check if this unlocks new research options
        self.check_unlocks()
        
        # Apply research effects
        self.apply_research_effects()
        
        return True
    
    def finish_research(self):
        """
        Finish the current research and reset for the next one
        
        Returns:
            True if successful, False if no completed research to finish
        """
        if not self.active_research or not self.research_complete:
            return False
            
        # Store completed research ID for return
        completed_id = self.active_research_id
        
        # Reset research state
        self.active_research = None
        self.active_research_id = None
        self.active_column = None
        self.research_progress = 0.0
        self.research_complete = False
        
        return True
    
    def initialize_unlocks(self):
        """
        Initialize unlocked research nodes based on initial state
        """
        # Make sure all columns are checked for initial unlocks
        for column in range(1, 6):  # Assuming max 5 columns
            if column in self.research_tree:
                # For each research in this column
                for research_id, research in self.research_tree[column].items():
                    # Check prerequisites
                    if self.check_prerequisites(research):
                        research["unlocked"] = True
                    else:
                        research["unlocked"] = False
    
    def check_unlocks(self):
        """
        Check and update unlocked research nodes and columns
        based on current research progress
        """
        if not self.active_research_id or not self.active_column:
            return
            
        # First, add this research to the prerequisites list
        completed_research = self.active_research_id
        
        # Check if we need to unlock the next column
        next_column = self.active_column + 1
        if next_column not in self.unlocked_columns and next_column in self.research_tree:
            
            # Check if at least one prerequisite in the current column is completed
            column_has_completed = False
            for research_id, research in self.research_tree[self.active_column].items():
                if research["current_level"] > 0:
                    column_has_completed = True
                    break
            
            # If we have at least one completed research in this column, unlock the next
            if column_has_completed:
                self.unlocked_columns.append(next_column)
        
        # Update unlocks for ALL research nodes (not just the next column)
        # This ensures that all nodes with completed prerequisites are unlocked
        for column in self.research_tree:
            for research_id, research in self.research_tree[column].items():
                # Check prerequisites for each research
                if self.check_prerequisites(research):
                    research["unlocked"] = True
    
    def check_prerequisites(self, research):
        """
        Check if all prerequisites for a research are completed
        
        Args:
            research: Research data to check
            
        Returns:
            True if all prerequisites are met, False otherwise
        """
        # Always return True if no prerequisites
        if not research["prerequisites"]:
            return True
            
        # Check each prerequisite
        for prerequisite_id in research["prerequisites"]:
            prerequisite = self.get_research_by_id(prerequisite_id)
            
            # If prerequisite doesn't exist or isn't completed, return False
            if not prerequisite or prerequisite["current_level"] == 0:
                return False
                
        return True
    
    def apply_research_effects(self):
        """
        Apply the effects of all completed research nodes
        """
        # Check if we have a registry to apply effects
        if not self.registry:
            return
            
        # Apply Double Loot effect
        self.apply_double_loot_effect()
        
        # Apply Castle Healer effect
        self.apply_castle_healer_effect()
        
        # Apply Free Upgrades effect
        self.apply_free_upgrades_effect()
        
        # Apply Clockwork Speed effect
        self.apply_clockwork_speed_effect()
        
        # Apply Monster Weakness effect
        self.apply_monster_weakness_effect()
        
        # Apply Resource Efficiency effect
        self.apply_resource_efficiency_effect()
        
        # Apply Advanced Engineering effect
        self.apply_advanced_engineering_effect()
    
    def apply_double_loot_effect(self):
        """Apply Double Loot research effect"""
        double_loot = self.get_research_by_id("double_loot")
        if not double_loot or double_loot["current_level"] == 0:
            return
            
        # Get the wave manager to apply the effect
        if self.registry and self.registry.has("wave_manager"):
            wave_manager = self.registry.get("wave_manager")
            
            # Calculate chance based on level
            double_loot_chance = double_loot["base_chance"] * double_loot["current_level"]
            
            # Set the double loot chance in wave manager
            if hasattr(wave_manager, "set_double_loot_chance"):
                wave_manager.set_double_loot_chance(double_loot_chance)
            # If the method doesn't exist, we'll need to add it to the wave manager
    
    def apply_castle_healer_effect(self):
        """Apply Castle Healer research effect"""
        castle_healer = self.get_research_by_id("castle_healer")
        if not castle_healer or castle_healer["current_level"] == 0:
            return
            
        # Calculate heal amount based on level
        heal_amount = castle_healer["heal_amount"] * castle_healer["current_level"]
        
        # This will be applied when a boss is killed - need to add hook to wave manager
        if self.registry and self.registry.has("wave_manager"):
            wave_manager = self.registry.get("wave_manager")
            
            # Set the castle heal amount in wave manager
            if hasattr(wave_manager, "set_castle_heal_on_boss"):
                wave_manager.set_castle_heal_on_boss(heal_amount)
            # If the method doesn't exist, we'll need to add it to the wave manager
    
    def apply_free_upgrades_effect(self):
        """Apply Free Upgrades research effect"""
        free_upgrades = self.get_research_by_id("free_upgrades")
        if not free_upgrades or free_upgrades["current_level"] == 0:
            return
            
        # Calculate chance based on level
        free_upgrade_chance = free_upgrades["base_chance"] * free_upgrades["current_level"]
        
        # This will be applied when a tower is upgraded
        # We'll need to add a hook to the tower classes
    
    def apply_clockwork_speed_effect(self):
        """Apply Clockwork Speed research effect"""
        clockwork_speed = self.get_research_by_id("clockwork_speed")
        if not clockwork_speed or clockwork_speed["current_level"] == 0:
            return
            
        # Calculate speed increase based on level
        speed_increase = clockwork_speed["speed_increase"] * clockwork_speed["current_level"]
        
        # Apply to game speed
        if self.registry and self.registry.has("game"):
            game = self.registry.get("game")
            
            # Set the base time scale in game
            if hasattr(game, "set_base_time_scale"):
                game.set_base_time_scale(1.0 + speed_increase)
            # If the method doesn't exist, we'll need to add it to the game class
    
    def apply_monster_weakness_effect(self):
        """Apply Monster Weakness research effect"""
        monster_weakness = self.get_research_by_id("monster_weakness")
        if not monster_weakness or monster_weakness["current_level"] == 0:
            return
            
        # Calculate damage multiplier based on level
        damage_multiplier = 1.0 + (monster_weakness["damage_multiplier"] * monster_weakness["current_level"])
        
        # Apply to all towers
        if self.registry and self.registry.has("towers"):
            towers = self.registry.get("towers")
            
            for tower in towers:
                if hasattr(tower, "set_research_damage_multiplier"):
                    tower.set_research_damage_multiplier(damage_multiplier)
                # If the method doesn't exist, we'll need to add it to the tower class
    
    def apply_resource_efficiency_effect(self):
        """Apply Resource Efficiency research effect"""
        resource_efficiency = self.get_research_by_id("resource_efficiency")
        if not resource_efficiency or resource_efficiency["current_level"] == 0:
            return
            
        # Calculate cost reduction based on level
        cost_reduction = resource_efficiency["cost_reduction"] * resource_efficiency["current_level"]
        
        # This will be applied when calculating costs for buildings and towers
        # We'll need to add hooks to the cost calculation methods
    
    def apply_advanced_engineering_effect(self):
        """Apply Advanced Engineering research effect"""
        advanced_engineering = self.get_research_by_id("advanced_engineering")
        if not advanced_engineering or advanced_engineering["current_level"] == 0:
            return
            
        # Calculate attack speed multiplier based on level
        attack_speed_multiplier = 1.0 + (advanced_engineering["attack_speed_multiplier"] * advanced_engineering["current_level"])
        
        # Apply to all towers
        if self.registry and self.registry.has("towers"):
            towers = self.registry.get("towers")
            
            for tower in towers:
                if hasattr(tower, "set_research_attack_speed_multiplier"):
                    tower.set_research_attack_speed_multiplier(attack_speed_multiplier)
                # If the method doesn't exist, we'll need to add it to the tower class
