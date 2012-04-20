######
## Shoreditch configuration
######

PORT = 8080

# THEME SETTINGS

GENERATORS = {
	"lumber_mill": "lumber",
	"ore_refinery": "ore",
	"grain_field": "grain",
	"sheep": "wool",
	"building_yard": "brick"
}

# RULE SETTINGS
GENERATOR_COST = {
	"brick": 1,
	"lumber": 1,
	"wool": 1,
	"grain": 1
}

GENERATOR_IMPROVEMENT_COST = {
	"ore": 3,
	"grain": 2
}

ROAD_COST = {
	"brick": 1,
	"lumber": 1
}

BANK_TRADE_RATE = 4

RESOURCES = GENERATORS.values()
GENERATOR_REWARD = 1
GENERATOR_IMPROVEMENT_REWARD = 1
LONGEST_ROAD_BONUS = 2

MAX_RESOURCE_GENERATORS = 5
MAX_IMPROVED_RESOURCE_GENERATORS = 4

MIN_PLAYERS = 2
MAX_PLAYERS = 6
MAX_ROUNDS = 100



####### DEFAULT SETUP


DEFAULT_GENERATORS = {}
for generator in GENERATORS.keys():
	DEFAULT_GENERATORS[generator] = 0

DEFAULT_RESOURCES = {}
for resource in GENERATORS.values():
	DEFAULT_RESOURCES[resource] = 0