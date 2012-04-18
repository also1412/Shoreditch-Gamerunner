from bottle import post

from storage import use_db

@post('/test/clear')
@use_db
def clear_db(db):
	db.empty()