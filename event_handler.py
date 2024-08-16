import datetime
import random
import discord
from game_manager import list_games, add_game, remove_game, choose_random_game
from dispo_manager import handle_dispo_command
from voice_manager import join_voice_channel, leave_voice_channel
from utils import get_user_id

async def on_ready(client):
	print(f'{client.user} has connected to Discord!')

async def handle_message(client, message):
	if message.author == client.user:
		return

	msg = message.content.lower()

	if not msg.startswith('.'):
		return

	command = msg[1:]

	if "hello" in command:
		await greet_user(message)

	if "game list" in command:
		await list_games(message)

	if "add game " in command:
		await add_game(message, command[len("add game "):])

	if "remove game " in command:
		await remove_game(message, command[len("remove game "):])

	if "random game" in command:
		await choose_random_game(message)

	if "dispo" in command:
		await handle_dispo_command(message, command)

	if "dm" in command:
		await send_direct_message(client, message, command[len("dm "):])

	if "join" in command:
		await join_voice_channel(message)

	if "leave" in command:
		await leave_voice_channel(message)

	if "clear" in command:
		await clear_messages(message)

	if "help" in command:
		await send_help_message(message)

	if "disconnect" in command:
		await disconnect_bot(client, message)

async def greet_user(message):
	greetings = ["Hello", "Hi", "Yo"]
	hour = datetime.datetime.now().hour

	if hour < 12:
		greetings.append("Good morning")
	elif hour > 18:
		greetings.append("Good evening")

	await message.channel.send(f'**{random.choice(greetings)}, {message.author.name}!**')

async def send_direct_message(client, message, command):
	target, msg = command.split(' ', 1)
	target_user_id = get_user_id(target)
	target_user = message.guild.get_member(target_user_id)

	try:
		await target_user.send(msg)
	except discord.HTTPException as e:
		await message.channel.send(f"An error occurred while trying to send a DM: {e}")

async def clear_messages(message):
	async for msg in message.channel.history(limit=1000):
		await msg.delete()

async def send_help_message(message):
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
# ".join                         - The bot joins your voice channel.\n"
# ".leave                        - The bot leaves the voice channel.\n"

async def shutdown_webserver():
	global webserver_thread
	# Here, implement a shutdown mechanism for the webserver
	# e.g., if using Flask:
	# request.environ.get('werkzeug.server.shutdown')()
	# Then, wait for the thread to finish
	if webserver_thread is not None:
		webserver_thread.join()

async def disconnect_bot(client, message):
	if message.guild.voice_client:
		await message.guild.voice_client.disconnect()
	await message.channel.send(f"**Goodbye! I left the channel!**")
	
	shutdown_webserver()  # Stop the webserver
	await client.close()  # Close the bot connection
	
	loop = asyncio.get_event_loop()
	loop.stop()  # Stop the asyncio loop
	
	sys.exit()  # Exit the process