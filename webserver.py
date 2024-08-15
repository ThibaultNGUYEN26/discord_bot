from flask import Flask, request
from threading import Thread

app = Flask('')
@app.route('/')
def home():
	return "Discord bot ok"

@app.route('/shutdown', methods=['POST'])
def shutdown():
    shutdown_server = request.environ.get('werkzeug.server.shutdown')
    if shutdown_server:
        shutdown_server()
    return "Server shutting down..."

def run():
	app.run(host="0.0.0.0", port=8080)

def keep_alive():
	t = Thread(target=run)
	t.start()