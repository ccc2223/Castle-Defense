# config.py
"""
Game configuration and constants
"""

# Window settings
WINDOW_WIDTH = 1920
WINDOW_HEIGHT = 1080

# Reference dimensions (original design size)
REF_WIDTH = 800
REF_HEIGHT = 600

# Scale factors
SCALE_X = WINDOW_WIDTH / REF_WIDTH
SCALE_Y = WINDOW_HEIGHT / REF_HEIGHT

# General game settings
FPS = 60
BACKGROUND_COLOR = (0, 0, 0)

# Resource settings
RESOURCE_TYPES = ["Stone", "Iron", "Copper", "Thorium"]
SPECIAL_RESOURCES = ["Monster Coins", "Force Core", "Spirit Core", "Magic Core", "Void Core", 
                     "Unstoppable Force", "Serene Spirit", "Multitudation Vortex"]
FOOD_RESOURCES = ["Grain", "Fruit", "Meat", "Dairy"]
INITIAL_RESOURCES = {"Stone": 100, "Iron": 0, "Copper": 0, "Thorium": 0, "Monster Coins": 50,
                     "Force Core": 0, "Spirit Core": 0, "Magic Core": 0, "Void Core": 0,
                     "Unstoppable Force": 0, "Serene Spirit": 0, "Multitudation Vortex": 0,
                     "Grain": 0, "Fruit": 0, "Meat": 0, "Dairy": 0}

# Castle settings
CASTLE_INITIAL_HEALTH = 1000
CASTLE_INITIAL_DAMAGE_REDUCTION = 0.1
CASTLE_INITIAL_HEALTH_REGEN = 1  # Health per second
CASTLE_HEALTH_UPGRADE_MULTIPLIER = 1.5
CASTLE_DAMAGE_REDUCTION_UPGRADE_MULTIPLIER = 1.2
CASTLE_HEALTH_REGEN_UPGRADE_MULTIPLIER = 1.3

# Castle upgrade costs (differentiated by upgrade path)
CASTLE_HEALTH_UPGRADE_COST = {"Stone": 75, "Monster Coins": 1}
CASTLE_DAMAGE_REDUCTION_UPGRADE_COST = {"Stone": 40, "Iron": 15, "Monster Coins": 2}
CASTLE_HEALTH_REGEN_UPGRADE_COST = {"Stone": 30, "Iron": 10, "Copper": 5, "Monster Coins": 3}

# Mine settings
MINE_INITIAL_PRODUCTION = 3
MINE_PRODUCTION_INTERVAL = 10  # Seconds
MINE_PRODUCTION_MULTIPLIER = 1.2
MINE_UPGRADE_TIME_MULTIPLIER = 2.2
MINE_INITIAL_UPGRADE_TIME = 10  # Seconds
MINE_UPGRADE_COST = {"Monster Coins": 100}

# Coresmith settings
CORESMITH_CRAFTING_TIME = 30  # Seconds

# Item settings
ITEM_COSTS = {
    "Unstoppable Force": {"Stone": 1, "Force Core": 1},
    "Serene Spirit": {"Stone": 1, "Spirit Core": 1},
    "Multitudation Vortex": {"Stone": 1, "Magic Core": 1}
}

# Item effects
ITEM_EFFECTS = {
    "Unstoppable Force": {
        "description": "Increases tower AoE radius by 30%",
        "aoe_radius_multiplier": 1.3,  # 30% increase
        "splash_damage_radius": 30,     # Radius for single-target towers
        "glow_color": (255, 100, 50)    # Orange-ish glow for visual effect
    },
    "Serene Spirit": {
        "description": "Converts 5% of tower damage into healing for castle walls",
        "healing_percentage": 0.05,
        "glow_color": (100, 200, 100)   # Green glow for visual effect
    },
    "Multitudation Vortex": {
        "description": "10% chance for projectiles to bounce to a second target",
        "bounce_chance": 0.10,          # 10% chance to bounce
        "compatible_towers": ["Archer", "Sniper"],
        "glow_color": (150, 100, 255)   # Purple glow for visual effect
    }
}

# Tower settings
TOWER_TYPES = {
    "Archer": {
        "damage": 10,
        "attack_speed": 1.5,  # Attacks per second
        "range": 150,
        "cost": {"Stone": 20}
    },
    "Sniper": {
        "damage": 50,
        "attack_speed": 0.5,  # Attacks per second
        "range": 300,
        "cost": {"Stone": 40}
    },
    "Splash": {
        "damage": 20,
        "attack_speed": 0.8,  # Attacks per second
        "range": 200,
        "aoe_radius": 50,
        "cost": {"Stone": 30, "Iron": 5, "Copper": 2}
    },
    "Frozen": {
        "damage": 5,
        "attack_speed": 1.0,  # Attacks per second
        "range": 180,
        "slow_effect": 0.5,  # 50% slowdown
        "slow_duration": 3.0,  # Seconds
        "cost": {"Stone": 25, "Iron": 5, "Copper": 3}
    }
}

# Tower Monster Coin costs
TOWER_MONSTER_COIN_COSTS = {
    "Archer": 15,
    "Sniper": 75,
    "Splash": 65,
    "Frozen": 65
}

# Tower upgrade costs (multiplier per level)
TOWER_UPGRADE_COST_MULTIPLIER = 1.5
TOWER_MONSTER_COIN_UPGRADE_MULTIPLIER = 1.3
TOWER_DAMAGE_UPGRADE_MULTIPLIER = 1.3
TOWER_ATTACK_SPEED_UPGRADE_MULTIPLIER = 1.2
TOWER_RANGE_UPGRADE_MULTIPLIER = 1.2
TOWER_AOE_UPGRADE_MULTIPLIER = 1.2

# Monster settings
MONSTER_STATS = {
    "Grunt": {
        "health": 40,
        "speed": 50,  # Pixels per second
        "damage": 8
    },
    "Runner": {
        "health": 15,
        "speed": 100,  # Pixels per second
        "damage": 3
    },
    "Tank": {
        "health": 190,
        "speed": 30,  # Pixels per second
        "damage": 18
    },
    "Flyer": {
        "health": 30,
        "speed": 70,  # Pixels per second
        "damage": 13,
        "flying": True
    }
}

# Boss settings
BOSS_STATS = {
    "Force": {
        "health": 500,
        "speed": 40,
        "damage": 50,
        "ability": "knockback"
    },
    "Spirit": {
        "health": 400,
        "speed": 50,
        "damage": 40,
        "ability": "heal"
    },
    "Magic": {
        "health": 450,
        "speed": 45,
        "damage": 45,
        "ability": "teleport"
    },
    "Void": {
        "health": 600,
        "speed": 35,
        "damage": 60,
        "ability": "spawn"
    }
}

# Wave settings
MONSTER_SPAWN_INTERVAL = 1.5  # Seconds between spawns
WAVE_DIFFICULTY_MULTIPLIER = 1.2  # Health/damage increase per wave
WAVE_MONSTER_COUNT_BASE = 5  # Base number of monsters per wave
WAVE_MONSTER_COUNT_MULTIPLIER = 1.5  # Increase in monster count per 10 waves

# Loot settings
LOOT_MONSTER_BASE_COIN_DROP = 1  # Base number of monster coins from regular monsters
LOOT_BOSS_BASE_COIN_DROP = 10  # Base number of monster coins from boss monsters
LOOT_WAVE_SCALING = 0.05  # How much loot quantity increases per wave

# Backward compatibility constants
BOSS_COIN_DROP = LOOT_BOSS_BASE_COIN_DROP  # Keep old name for backward compatibility

# Village settings
VILLAGE_BUILDING_COSTS = {
    "TownHall": {"Stone": 200, "Iron": 50},
    "ResearchLab": {"Stone": 150, "Iron": 30, "Copper": 10},
    "MonsterCodex": {"Stone": 100, "Monster Coins": 20},
    "CropFarm": {"Stone": 50},
    "LivestockFarm": {"Stone": 75, "Iron": 10},
    "StorageBarn": {},  # Free building
    "Mine": {},  # Free building
    "Coresmith": {}  # Free building
}

# Food resource production
CROP_FARM_PRODUCTION = {"Grain": 2, "Fruit": 1}
LIVESTOCK_FARM_PRODUCTION = {"Meat": 1, "Dairy": 1}

# Talent point rewards
TALENT_POINTS_PER_WAVE = 1  # Base talent points per wave
TALENT_POINT_MILESTONE_WAVES = [5, 10, 25, 50, 100]  # Special milestones
TALENT_POINT_MILESTONE_REWARDS = [2, 3, 5, 10, 20]  # Rewards for milestones