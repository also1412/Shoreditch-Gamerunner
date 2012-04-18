##############
### Shoreditch Gamerunner
##############

from bottle import run
from handlers import *

run(host='localhost', port=8080)