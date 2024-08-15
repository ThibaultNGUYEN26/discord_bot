# bot.py
import os
import discord
import asyncio
import random
import datetime
import webserver
import requests
import time
from threading import Thread
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.environ['DISCORD_TOKEN']

print("Connection with the bot...")

# Create an instance of Intents and specify which events you want
intents = discord.Intents.default() # This enables the default intents
intents.message_content = True # This is required to receive message content events

client = discord.Client(intents=intents)

@client.event
async def on_ready():
	print(f'{client.user} has connected to Discord!')

@client.event
async def on_message(message):
	# Check if the message author is not the bot itself
	if message.author == client.user:
		return

	msg = message.content.lower()

	# Check if the message starts with the '!' prefix
	if not msg.startswith('.'):
		return

	# Remove the '!' prefix for easier command processing
	msg = msg[1:]

	# Check if the message contains the word "hello"
	if "hello" in msg:
		greetings = ["Hello", "Hi", "Yo"]
		hour = datetime.datetime.now().hour
		# Determine the appropriate greeting based on the time of day
		if hour < 12:
			greetings.append("Good morning")
		elif hour > 18:
			greetings.append("Good evening")
		await message.channel.send(f'**{random.choice(greetings)}, {message.author.name}!**')

	with open('game_list.txt') as f:
		game_list = f.read().title()
	if "game list" in msg:
		await message.channel.send(f'Game list: \n**{game_list}**')
	
	add_game = "add game "
	if add_game in msg:
		games_to_add = msg[len(add_game):]
		games = [game.strip().lower() for game in games_to_add.split(',')]

		# Read the existing games from the file
		with open("game_list.txt", "r") as f:
			existing_games = [game.strip().lower() for game in f.readlines()]

		# Filter out games that are already in the list
		new_games = [game for game in games if game not in existing_games]

		# Add the new games to the file
		with open("game_list.txt", "a") as f:
			for game in new_games:
				f.write(game + '\n')

		# Prepare the response message
		if new_games:
			await message.channel.send(f"The games **{', '.join([game.title() for game in new_games])}** were added to the game list")
		else:
			await message.channel.send("All the games you tried to add are already in the game list.")

	remove_game = "remove game "
	if remove_game in msg:
		msg = msg[len(remove_game):]
		with open("game_list.txt", 'r') as f:
			lines = f.readlines()
		with open("game_list.txt", 'w') as f:
			for line in lines:
				if line.strip().lower() != msg.lower():
					f.write(line)
		await message.channel.send(f"The game **{msg.title()}** was removed to the game list")
	
	random_game = "random game"
	if random_game in msg:
		msg = msg[len(random_game):]
		with open("game_list.txt", 'r') as f:
			game_list = list(f.readlines())
			game_list = [game[:-1] for game in game_list]
		await message.channel.send(f"I chose the game **{random.choice(game_list).title()}** for you !")

	if msg == "dispo":
		today = datetime.datetime.now()
		valid_entries = []

		# Open the file and read the lines
		with open("dispo.txt", "r") as f:
			lines = f.readlines()

		# Iterate through the lines to check if the date has passed
		for line in lines:
			line_date_str, rest = line.split(": ", 1)
			
			# Parse the date in the format `dd/mm`
			try:
				line_date = datetime.datetime.strptime(line_date_str, "%d/%m").replace(year=today.year)
			except ValueError:
				continue  # Skip lines with an invalid date format

			# If the date is in the future or today, add it to the valid_entries list
			if line_date.date() >= today.date():
				valid_entries.append((line_date, line))

		# Sort the valid entries by date
		valid_entries.sort(key=lambda x: x[0])

		# Extract the sorted lines
		sorted_lines = [entry[1] for entry in valid_entries]

		# Write the sorted lines back to the file
		with open("dispo.txt", "w") as f:
			f.writelines(sorted_lines)

		# Read the updated file content to send to the user
		with open("dispo.txt", 'r') as f:
			dispo = f.read()
		await message.channel.send(f"**{dispo}**")

	elif msg.startswith("dispo "):
		# Only enter this block if the message starts with "dispo " and has more content
		msg = msg[6:]

		if msg[:6] == "remove":
			# Extract the date from the message (e.g., "remove 15/08")
			date_str = msg[7:].strip()  # Get the date after "remove"

			# Open the file and read the lines
			with open("dispo.txt", "r") as f:
				lines = f.readlines()

			updated = False

			# Iterate through the lines to find the correct date
			for i, line in enumerate(lines):
				line_date, rest = line.split(": ", 1)

				if line_date == date_str:
					# Remove the user's entry for the specific date
					username = message.author.name
					updated_lines = []

					for entry in rest.split(", "):
						if not entry.startswith(f"{username}("):
							updated_lines.append(entry)

					# If there are still entries left after removal, update the line
					if updated_lines:
						lines[i] = f"{date_str}: {', '.join(updated_lines)}\n"
					else:
						# If no entries are left, remove the entire line
						lines.pop(i)
					updated = True
					break

			if updated:
				# Write the updated lines back to the file
				with open("dispo.txt", "w") as f:
					f.writelines(lines)
				await message.channel.send(f"Status for **{username}** on **{date_str}** has been removed.")
			else:
				await message.channel.send(f"No status found for **{username}** on **{date_str}**.")

		# Check if the status is valid
		elif any(status in msg for status in ["yes", "no", "maybe"]):
			date_str = msg[:5]
			status = msg[6:]
			username = message.author.name
			updated = False

			# Validate the date format
			try:
				# Parse the date with the current year
				date = datetime.datetime.strptime(date_str, "%d/%m").replace(year=datetime.datetime.now().year)
			except ValueError:
				await message.channel.send("Invalid **date format**. Please use **dd/mm** format.")
				return

			# Get today's date
			today = datetime.datetime.now()

			# Check if the date is in the past
			if date.date() < today.date():
				await message.channel.send("The date has **already passed**. Please provide a future date.")
				return

			# Calculate the maximum allowed date (one month from today)
			max_date = today + datetime.timedelta(days=31)
			max_date = max_date.replace(day=date.day, month=date.month)

			# Check if the date exceeds one month from today
			if date > max_date:
				await message.channel.send("The date **exceeds one month** from today. Please provide a date **within the next month**.")
				return

			# Open the file and read the lines
			with open("dispo.txt", "r") as f:
				lines = f.readlines()

			# Prepare the new line entry
			new_entry = f"{username}({status})"

			# Iterate through the lines to find the correct date
			for i, line in enumerate(lines):
				line_date, rest = line.split(": ", 1)

				if line_date == date_str:
					# Check if the user is already listed in that line
					if username in rest:
						# User is already listed, update their status
						updated_lines = []
						for entry in rest.split(", "):
							if entry.startswith(f"{username}("):
								updated_lines.append(new_entry)
							else:
								updated_lines.append(entry)
						lines[i] = f"{date_str}: {', '.join(updated_lines)}\n"
					else:
						# Add the new user entry
						lines[i] = f"{date_str}: {rest.strip()}, {new_entry}\n"
					updated = True
					break

			# If the date was not found, add a new line
			if not updated:
				lines.append(f"{date_str}: {new_entry}\n")

			# Write the updated lines back to the file
			with open("dispo.txt", "w") as f:
				f.writelines(lines)

			await message.channel.send(f"Status for **{username}** on **{date_str}** has been updated to **{status}**.")
		else:
			await message.channel.send("Invalid status. Please use **'yes'**, **'no'**, or **'maybe'**.")

	if msg == "disconnect":
		await message.channel.send(f"**Goodbye I left the channel!**")
		await client.close()
	
	if msg == "clear":
		async for message in message.channel.history(limit=1000):
			await message.delete()

	# List all available commands
	if msg == "help":
		help_message = (
			"**Here are the commands you can use:**\n"
			"```"
			".hello                        - The bot will greet you.\n"
			".game list                    - Lists all the games.\n"
			".add game <game_name>         - Adds a game to the list.\n"
			".remove game <game_name>      - Removes a game from the list.\n"
			".random game                  - The bot will choose a random game for you.\n"
			".dispo                        - Sees all the disponibilites up to 1 month\n"
			".dispo <dd/mm> <yes/no/maybe> - Puts a dispobility to the date with the status\n"
			".dispo remove <dd/mm>         - Removes the disponibility to the date\n"
			".help                         - Shows this help message."
			"```"
		)
		await message.channel.send(help_message)

async def run_bot():
	try:
		await client.start(TOKEN)
	except KeyboardInterrupt:
		print("Disconnecting the bot...")
		await client.close()
		print("Bot disconnected.")

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
	ping_thread.daemon = True  # This allows the thread to exit when the main program exits
	ping_thread.start()

if __name__ == "__main__":
	# URL of your server
	ping_url = "https://discord-bot-78qc.onrender.com"
	ping_interval = 900  # Interval in seconds (e.g., 3600 for 1 hour, 900 for 15 minutes)

	# Start the pinging in a separate thread
	start_pinging(ping_url, ping_interval)

	webserver.keep_alive()
	# Run the bot with graceful shutdown on Ctrl+C
	asyncio.run(run_bot())