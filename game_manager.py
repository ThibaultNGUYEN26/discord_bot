import random

async def list_games(message):
	with open('game_list.txt') as f:
		game_list = f.read().title()
	await message.channel.send(f'Game list: \n**{game_list}**')

async def add_game(message, games_to_add):
	games = [game.strip().lower() for game in games_to_add.split(',')]
	with open("game_list.txt", "r") as f:
		existing_games = [game.strip().lower() for game in f.readlines()]
	new_games = [game for game in games if game not in existing_games]
	with open("game_list.txt", "a") as f:
		for game in new_games:
			f.write(game + '\n')
	if new_games:
		await message.channel.send(f"The games **{', '.join([game.title() for game in new_games])}** were added to the game list")
	else:
		await message.channel.send("All the games you tried to add are already in the game list.")

async def remove_game(message, game_to_remove):
	with open("game_list.txt", 'r') as f:
		lines = f.readlines()
	with open("game_list.txt", 'w') as f:
		for line in lines:
			if line.strip().lower() != game_to_remove.lower():
				f.write(line)
	await message.channel.send(f"The game **{game_to_remove.title()}** was removed from the game list")

async def choose_random_game(message):
	with open("game_list.txt", 'r') as f:
		game_list = [game.strip() for game in f.readlines()]
	await message.channel.send(f"I chose the game **{random.choice(game_list).title()}** for you!")
