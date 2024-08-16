from flask import Flask, request
from threading import Thread

app = Flask('')
@app.route('/')
def home():
	return "Discord bot ok"

def run():
	app.run(host="0.0.0.0", port=8080)

webserver_thread = None

def shutdown_webserver():
	global webserver_thread
	if request.environ.get('werkzeug.server.shutdown'):
		request.environ['werkzeug.server.shutdown']()
	if webserver_thread is not None:
		webserver_thread.join()

def keep_alive():
	t = Thread(target=run)
	t.start()