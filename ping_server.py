import time
import requests
from threading import Thread

def ping_server(url, interval):
	while True:
		try:
			response = requests.get(url)
			print(f"Pinged {url}, Status: {response.status_code}")
		except requests.exceptions.RequestException as e:
			print(f"Error pinging {url}: {e}")
		time.sleep(interval)

def start_pinging(url, interval):
	ping_thread = Thread(target=ping_server, args=(url, interval))
	ping_thread.daemon = True
	ping_thread.start()
