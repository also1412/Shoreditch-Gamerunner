##############
### Shoreditch Gamerunner
##############

from bottle import run
from handlers import *
from config import PORT

run(host='localhost', port=PORT)