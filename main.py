import os
import discord
import asyncio
from dotenv import load_dotenv
import webserver
from ping_server import start_pinging
from event_handler import handle_message, on_ready

load_dotenv()
TOKEN = os.environ['DISCORD_TOKEN']

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
	await on_ready(client)

@client.event
async def on_message(message):
	await handle_message(client, message)

async def run_bot():
	try:
		await client.start(TOKEN)
	except KeyboardInterrupt:
		print("Disconnecting the bot...")
		await client.close()
		print("Bot disconnected.")

if __name__ == "__main__":
	ping_url = "https://discord-bot-78qc.onrender.com"
	ping_interval = 840  # Interval in seconds

	start_pinging(ping_url, ping_interval)

	webserver.keep_alive()
	asyncio.run(run_bot())
