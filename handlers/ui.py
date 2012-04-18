from bottle import get, post
from bottle import view, redirect, abort
from bottle import request

from storage import use_db

from admin import list_players, add_player
from game import start_game

@get('/ui/')
@view('index.html')
def index():
	return list_players()

@post('/ui/player')
def ui_add_player():
	add_player(json={"name": request.POST.get('name'), "endpoint": request.POST.get('endpoint')})
	redirect('/ui/')

@post('/ui/game')
def ui_start_game():
	players = []
	for k in request.POST:
		if k.startswith("player_"):
			for i in range(int(request.POST[k])):
				players.append(k[7:])

	start_game(json={"name": request.POST['name'], "players": players})