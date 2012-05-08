import json

from bottle import get, post
from bottle import view, redirect, abort
from bottle import request

from storage import use_db

from admin import list_players, add_player
from game import start_game


@get('/')
def i():
	return redirect('/ui/')

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

	game_id = start_game(json={"name": request.POST['name'], "players": players})['game_id']
	redirect('/ui/game/' + game_id)

@get('/ui/game/:game_id')
@use_db
@view('game.html')
def view_game(db, game_id):
	game = db.get(game_id)
	if not game:
		abort(404, "Invalid game id")
	return {"game_id": game_id, "game_name": game['name'], "pushes": json.dumps(game['pushes'])}