# features/village/building_factory.py
"""
Factory for creating village buildings
"""
from .buildings import TownHall, ResearchLab, MonsterCodex, Farm
from .storage_barn import StorageBarn
from .production_buildings import Mine, Coresmith

class VillageBuildingFactory:
    """Factory for creating village buildings"""
    
    @staticmethod
    def create_building(building_type, position, registry, **kwargs):
        """
        Create a building of the specified type
        
        Args:
            building_type: Type of building to create
            position: Tuple of (x, y) coordinates
            registry: Component registry for accessing game components
            **kwargs: Additional keyword arguments specific to building type
            
        Returns:
            Instance of the building
            
        Raises:
            ValueError: If building type is not recognized
        """
        if building_type == "TownHall":
            return TownHall(position, registry)
        
        elif building_type == "ResearchLab":
            return ResearchLab(position, registry)
        
        elif building_type == "MonsterCodex":
            return MonsterCodex(position, registry)
        
        elif building_type == "CropFarm":
            return Farm(position, registry, farm_type="crop")
        
        elif building_type == "LivestockFarm":
            return Farm(position, registry, farm_type="livestock")
        
        elif building_type == "Mine":
            return Mine(position, registry)
        
        elif building_type == "Coresmith":
            return Coresmith(position, registry)
        
        elif building_type == "StorageBarn":
            return StorageBarn(position, registry)
        
        else:
            raise ValueError(f"Unknown village building type: {building_type}")
