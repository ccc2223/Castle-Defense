# save_system.py
"""
Save system for Castle Defense game
"""
import os
import pickle
import datetime
from features.building_factory import BuildingFactory
from features.towers.factory import TowerFactory

class SaveManager:
    """Manages game saving and loading"""
    def __init__(self, game):
        """
        Initialize save manager
        
        Args:
            game: Game instance to save/load
        """
        self.game = game
        self.save_directory = "saves"
        self.max_saves = 10
        self.autosave_waves = 10
        
        # Create save directory if it doesn't exist
        if not os.path.exists(self.save_directory):
            os.makedirs(self.save_directory)
    
    def save_game(self, filename=None):
        """
        Save the current game state
        
        Args:
            filename: Optional filename, auto-generated if None
            
        Returns:
            Filename of saved game
        """
        # Generate filename if not provided
        if filename is None:
            now = datetime.datetime.now()
            date_str = now.strftime("%Y-%m-%d_%H-%M-%S")
            wave_str = str(self.game.wave_manager.current_wave).zfill(3)
            filename = f"{date_str}-Wave{wave_str}.save"
        
        # Create serializable game state
        game_state = {
            "wave": self.game.wave_manager.current_wave,
            "resources": self.game.resource_manager.resources,
            "wave_manager": {
                "challenge_mode": self.game.wave_manager.challenge_mode,
                "challenge_monster_type": self.game.wave_manager.challenge_monster_type,
                "challenge_tier": self.game.wave_manager.challenge_tier,
                "challenge_wave_count": self.game.wave_manager.challenge_wave_count,
                "continuous_wave": self.game.wave_manager.continuous_wave
            },
            "castle": {
                "health": self.game.castle.health,
                "max_health": self.game.castle.max_health,
                "damage_reduction": self.game.castle.damage_reduction,
                "health_regen": self.game.castle.health_regen,
                "level": self.game.castle.level
            },
            "buildings": [self.serialize_building(b) for b in self.game.buildings],
            "towers": [self.serialize_tower(t) for t in self.game.towers]
        }
        
        # Save village data if it exists
        if hasattr(self.game, 'village') and self.game.village is not None:
            game_state["village"] = self.serialize_village(self.game.village)
        
        # Save to file
        filepath = os.path.join(self.save_directory, filename)
        with open(filepath, "wb") as f:
            pickle.dump(game_state, f)
        
        # Clean up old saves
        self.clean_old_saves()
        
        return filename
    
    def load_game(self, filename):
        """
        Load a saved game
        
        Args:
            filename: Filename to load
            
        Returns:
            True if load successful, False otherwise
        """
        filepath = os.path.join(self.save_directory, filename)
        if not os.path.exists(filepath):
            return False
        
        try:
            # Load game state
            with open(filepath, "rb") as f:
                game_state = pickle.load(f)
            
            # Restore wave
            self.game.wave_manager.current_wave = game_state["wave"]
            self.game.wave_manager.active_monsters = []
            self.game.wave_manager.wave_active = False
            self.game.wave_manager.wave_completed = True
            
            # Restore wave manager challenge mode if present
            if "wave_manager" in game_state:
                wave_mgr_data = game_state["wave_manager"]
                self.game.wave_manager.challenge_mode = wave_mgr_data.get("challenge_mode", False)
                self.game.wave_manager.challenge_monster_type = wave_mgr_data.get("challenge_monster_type", None)
                self.game.wave_manager.challenge_tier = wave_mgr_data.get("challenge_tier", None)
                self.game.wave_manager.challenge_wave_count = wave_mgr_data.get("challenge_wave_count", 0)
                self.game.wave_manager.continuous_wave = wave_mgr_data.get("continuous_wave", True)
            
            # Restore resources
            self.game.resource_manager.resources = game_state["resources"]
            
            # Restore castle
            castle_state = game_state["castle"]
            self.game.castle.health = castle_state["health"]
            self.game.castle.max_health = castle_state["max_health"]
            self.game.castle.damage_reduction = castle_state["damage_reduction"]
            self.game.castle.health_regen = castle_state["health_regen"]
            self.game.castle.level = castle_state["level"]
            
            # Restore buildings
            self.game.buildings = [self.deserialize_building(b) for b in game_state["buildings"]]
            
            # Restore towers
            self.game.towers = [self.deserialize_tower(t) for t in game_state["towers"]]
            
            # Restore village if it exists in the save
            if "village" in game_state:
                self.deserialize_village(game_state["village"])
            
            return True
        
        except (pickle.PickleError, KeyError, AttributeError) as e:
            print(f"Error loading save: {e}")
            return False
    
    def check_autosave(self):
        """Check if we should autosave the game"""
        current_wave = self.game.wave_manager.current_wave
        if current_wave > 0 and current_wave % self.autosave_waves == 0 and self.game.wave_manager.wave_completed:
            self.save_game()
    
    def clean_old_saves(self):
        """Remove oldest save files if we have too many"""
        save_files = [f for f in os.listdir(self.save_directory) if f.endswith(".save")]
        save_files.sort()  # Sort by name, which includes date
        
        # Remove oldest files if we have too many
        if len(save_files) > self.max_saves:
            for i in range(0, len(save_files) - self.max_saves):
                os.remove(os.path.join(self.save_directory, save_files[i]))
    
    def serialize_building(self, building):
        """
        Create serializable representation of building
        
        Args:
            building: Building instance
            
        Returns:
            Dictionary of building data
        """
        building_data = {
            "type": building.__class__.__name__,
            "position": building.position,
            "level": building.level
        }
        
        # Add type-specific data
        if building.__class__.__name__ == "Mine":
            building_data.update({
                "resource_type": building.resource_type,
                "production_rate": building.production_rate,
                "production_timer": building.production_timer,
                "upgrade_timer": building.upgrade_timer,
                "upgrading": building.upgrading,
                "upgrade_time": building.upgrade_time
            })
        
        # Add Coresmith-specific data
        elif building.__class__.__name__ == "Coresmith":
            building_data.update({
                "crafting": building.crafting,
                "crafting_timer": building.crafting_timer,
                "crafting_time": building.crafting_time,
                "current_item": building.current_item
            })
        
        return building_data
    
    def deserialize_building(self, building_data):
        """
        Recreate building from serialized data
        
        Args:
            building_data: Dictionary of building data
            
        Returns:
            Building instance
        """
        building_type = building_data["type"]
        position = building_data["position"]
        
        try:
            building = BuildingFactory.create_building(building_type, position)
            
            # Set common properties
            building.level = building_data["level"]
            
            # Set building-specific properties
            if building_type == "Mine":
                building.resource_type = building_data["resource_type"]
                building.production_rate = building_data["production_rate"]
                building.production_timer = building_data["production_timer"]
                building.upgrade_timer = building_data["upgrade_timer"]
                building.upgrading = building_data["upgrading"]
                building.upgrade_time = building_data["upgrade_time"]
                building.update_resource_type()  # Update color based on resource type
            
            elif building_type == "Coresmith":
                building.crafting = building_data["crafting"]
                building.crafting_timer = building_data["crafting_timer"]
                building.crafting_time = building_data["crafting_time"]
                building.current_item = building_data["current_item"]
                
            return building
            
        except ValueError:
            # Fallback for unknown building types
            return BuildingFactory.create_building("Mine", position)
    
    def serialize_tower(self, tower):
        """Create serializable representation of tower"""
        # Get item slots from new item system if available, otherwise use legacy system
        item_slots = [None, None]
        if hasattr(tower, 'item_manager'):
            # Get items from the new system
            items = tower.item_manager.get_all_items()
            for i in range(min(len(items), 2)):
                if items[i] is not None:
                    item_slots[i] = str(items[i])
        elif isinstance(tower.item_slots, list) and len(tower.item_slots) >= 2:
            # Legacy system fallback
            for i in range(2):
                if tower.item_slots[i] is not None:
                    item_slots[i] = str(tower.item_slots[i])
        
        # Create tower data dictionary
        tower_data = {
            "type": tower.__class__.__name__,
            "position": tower.position,
            "level": tower.level,
            "damage": tower.damage,
            "attack_speed": tower.attack_speed,
            "range": tower.range,
            "item_slots": item_slots
        }
        
        # Add tower-specific data
        if tower.__class__.__name__ == "SplashTower":
            tower_data["aoe_radius"] = tower.aoe_radius
        
        elif tower.__class__.__name__ == "FrozenTower":
            tower_data["slow_effect"] = tower.slow_effect
            tower_data["slow_duration"] = tower.slow_duration
        
        return tower_data
    
    def deserialize_tower(self, tower_data):
        """Recreate tower from serialized data"""
        tower_type = tower_data["type"]
        position = tower_data["position"]
        
        try:
            tower = TowerFactory.create_tower(tower_type, position)
            
            # Set common properties
            tower.level = tower_data["level"]
            tower.damage = tower_data["damage"]
            tower.attack_speed = tower_data["attack_speed"]
            tower.range = tower_data["range"]
            
            # Handle item slots safely
            if "item_slots" in tower_data and isinstance(tower_data["item_slots"], list):
                saved_slots = tower_data["item_slots"]
                
                # Use new item system if available
                if hasattr(tower, 'item_manager'):
                    # First make sure slots are clear
                    for i in range(2):
                        tower.item_manager.remove_item(i, None)
                    
                    # Then add saved items
                    for i in range(min(len(saved_slots), 2)):
                        if i < len(saved_slots) and saved_slots[i] is not None:
                            tower.item_manager.add_item(str(saved_slots[i]), i, None)
                    
                    # Sync with legacy system
                    if hasattr(tower, '_sync_item_slots'):
                        tower._sync_item_slots()
                else:
                    # Legacy fallback
                    item_slots = [None, None]
                    for i in range(min(len(saved_slots), 2)):
                        if i < len(saved_slots) and saved_slots[i] is not None:
                            item_slots[i] = str(saved_slots[i])
                    
                    tower.item_slots = item_slots
                
                # Apply effects
                tower.apply_item_effects()
            
            # Set tower-specific properties
            if tower_type == "SplashTower" and hasattr(tower, 'aoe_radius'):
                tower.aoe_radius = tower_data["aoe_radius"]
            
            elif tower_type == "FrozenTower" and hasattr(tower, 'slow_effect'):
                tower.slow_effect = tower_data["slow_effect"]
                tower.slow_duration = tower_data["slow_duration"]
            
            return tower
            
        except ValueError:
            # Fallback for unknown tower types
            return TowerFactory.create_tower("Archer", position)
    
    def serialize_village(self, village):
        """
        Create serializable representation of village
        
        Args:
            village: Village instance
            
        Returns:
            Dictionary of village data
        """
        from features.village.building_factory import VillageBuildingFactory
        
        village_data = {
            "position": village.position,
            "development_level": village.development_level,
            "talent_points": village.talent_points,
            "capacity": village.capacity,
            "used_capacity": village.used_capacity,
            "buildings": []
        }
        
        # Serialize village buildings
        for building in village.buildings:
            building_data = {
                "type": building.__class__.__name__,
                "position": building.position,
                "level": building.level
            }
            
            # Add type-specific data
            if building.__class__.__name__ == "TownHall":
                building_data["talent_points"] = building.talent_points
                building_data["talent_trees"] = building.talent_trees
            
            elif building.__class__.__name__ == "ResearchLab":
                building_data["current_research"] = building.current_research
                building_data["research_progress"] = building.research_progress
                building_data["research_time"] = building.research_time
                building_data["available_research"] = building.available_research
            
            elif building.__class__.__name__ == "MonsterCodex":
                building_data["monster_data"] = building.monster_data
                building_data["selected_monster"] = building.selected_monster
                building_data["challenge_completions"] = building.challenge_completions
                building_data["monster_cups"] = building.monster_cups
            
            elif building.__class__.__name__ == "Farm":
                building_data["farm_type"] = building.farm_type
                building_data["production"] = building.production
                building_data["production_timer"] = building.production_timer
                building_data["production_interval"] = building.production_interval
            
            village_data["buildings"].append(building_data)
        
        return village_data
    
    def deserialize_village(self, village_data):
        """
        Recreate village from serialized data
        
        Args:
            village_data: Dictionary of village data
        """
        from features.village.village import Village
        from features.village.building_factory import VillageBuildingFactory
        
        # Create or update village
        if not hasattr(self.game, 'village') or self.game.village is None:
            self.game.village = Village(self.game.registry, village_data["position"])
        
        # Update village properties
        village = self.game.village
        village.development_level = village_data["development_level"]
        village.talent_points = village_data["talent_points"]
        village.capacity = village_data["capacity"]
        village.used_capacity = village_data["used_capacity"]
        
        # Clear existing buildings
        village.buildings = []
        
        # Restore buildings
        for building_data in village_data["buildings"]:
            building_type = building_data["type"]
            position = building_data["position"]
            
            try:
                # Create appropriate building type
                if building_type == "Farm":
                    farm_type = building_data.get("farm_type", "crop")
                    if farm_type == "crop":
                        building = VillageBuildingFactory.create_building("CropFarm", position, self.game.registry)
                    else:
                        building = VillageBuildingFactory.create_building("LivestockFarm", position, self.game.registry)
                else:
                    building = VillageBuildingFactory.create_building(building_type, position, self.game.registry)
                
                # Set common properties
                building.level = building_data["level"]
                
                # Set building-specific properties
                if building_type == "TownHall":
                    building.talent_points = building_data["talent_points"]
                    building.talent_trees = building_data["talent_trees"]
                
                elif building_type == "ResearchLab":
                    building.current_research = building_data["current_research"]
                    building.research_progress = building_data["research_progress"]
                    building.research_time = building_data["research_time"]
                    building.available_research = building_data["available_research"]
                
                elif building_type == "MonsterCodex":
                    building.monster_data = building_data["monster_data"]
                    building.selected_monster = building_data["selected_monster"]
                    # Handle both old and new save formats
                    if "challenge_completions" in building_data:
                        building.challenge_completions = building_data["challenge_completions"]
                    if "monster_cups" in building_data:
                        building.monster_cups = building_data["monster_cups"]
                    # For backwards compatibility with old saves
                    if "modification_points" in building_data:
                        # Ignore old modification points
                        pass
                
                elif building_type == "Farm":
                    building.farm_type = building_data["farm_type"]
                    building.production = building_data["production"]
                    building.production_timer = building_data["production_timer"]
                    building.production_interval = building_data["production_interval"]
                
                # Add building to village
                village.buildings.append(building)
                
            except ValueError as e:
                print(f"Error recreating village building: {e}")
        
        # Update used capacity
        village.used_capacity = len(village.buildings)
