from bottle import get, post
from bottle import view, redirect
from bottle import request

from storage import use_db

from admin import list_players, add_player

@get('/ui/')
@use_db
@view('index.html')
def index(db):
	return list_players()

@post('/ui/player')
def ui_add_player():
	add_player(json={"name": request.POST.get('name'), "endpoint": request.POST.get('endpoint')})
	redirect('/ui/')