######
## Shoreditch configuration
######

PORT = 8080

PUSHER_APP_ID = "19057"
PUSHER_KEY = "b91e1271dbcde8bb5b5d"
PUSHER_SECRET = "c41f60b9a51f3e061d62"


############################
###
### This is to stop us using all our Pusher bandwidth on everyone testing their AIs
### - All it does is make the gamerunner show information one round at a time rather than
###   one action at a time. If you'd like to disable this PLEASE sign up for your own
###   pusher account at http://pusher.com/ and update the Pusher settings above to your own settings
###
############################
LOW_BANDWIDTH_MODE = True

# THEME SETTINGS

GENERATORS = {
	"suggestion_box": "idea",
	"coder": "feature",
	"kettle": "coffee",
	"designer": "website",
	"angel_investor": "cash"
}

# RULE SETTINGS
GENERATOR_COST = {
	"cash": 1,
	"idea": 1,
	"website": 1,
	"coffee": 1
}

GENERATOR_IMPROVEMENT_COST = {
	"feature": 3,
	"coffee": 2
}

PR_COST = {
	"cash": 1,
	"idea": 1
}

RESOURCES = GENERATORS.values()

RESOURCE_NAMES = dict((v,v.replace('_', ' ').title()) for v in RESOURCES)

GENERATOR_NAMES = dict((k,k.replace('_', ' ').title()) for k in GENERATORS.keys())
IMPROVED_GENERATOR_NAMES = {
	"suggestion_box": "Idea Management System",
	"coder": "Rockstar Coder",
	"kettle": "Espresso Machine",
	"designer": "Hipster Designer",
	"angel_investor": "VC Fund"
}


BANK_TRADE_RATE = 4
GENERATOR_REWARD = 1
GENERATOR_IMPROVEMENT_REWARD = 1
LONGEST_ROAD_BONUS = 2

MAX_RESOURCE_GENERATORS = 5
MAX_IMPROVED_RESOURCE_GENERATORS = 4

MIN_PLAYERS = 2
MAX_PLAYERS = 6
MAX_ROUNDS = 100
MAX_POINTS = 10

TURN_TIMEOUT = 15.0



####### DEFAULT SETUP


DEFAULT_GENERATORS = {}
for generator in GENERATORS.keys():
	DEFAULT_GENERATORS[generator] = 0

DEFAULT_RESOURCES = {}
for resource in GENERATORS.values():
	DEFAULT_RESOURCES[resource] = 0