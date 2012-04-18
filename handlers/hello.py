from bottle import get

@get('/hello')
def hello():
	return {"status": "Everything good, boss!"}