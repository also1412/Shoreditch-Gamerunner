##############
### Shoreditch Gamerunner
##############

from bottle import run
from handlers import *
from config import PORT

from storage import get_db
from preload_ais import AI
from util import add_player

db = get_db()

for ai in AI:
	add_player(db, ai, AI[ai])

run(host='localhost', port=PORT, reloader=True)