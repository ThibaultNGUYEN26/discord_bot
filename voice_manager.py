import discord

async def join_voice_channel(message):
	if message.author.voice:
		channel = message.author.voice.channel
		if message.guild.voice_client:
			await message.guild.voice_client.disconnect()
		try:
			if isinstance(channel, discord.VoiceChannel):
				if channel.permissions_for(message.guild.me).connect:
					await channel.connect()
					await message.channel.send(f"Joined **{channel.name}** voice channel!")
				else:
					await message.channel.send("I don't have permission to join this voice channel.")
			else:
				await message.channel.send("Error: The channel is not a voice channel.")
		except discord.errors.ClientException:
			await message.channel.send("It seems I'm already in a voice channel.")
		except discord.errors.Forbidden:
			await message.channel.send("I don't have permission to join this voice channel.")
		except discord.errors.HTTPException:
			await message.channel.send("Failed to join the voice channel due to an internal error.")
		except Exception:
			await message.channel.send("Failed to join the voice channel.")
	else:
		await message.channel.send("You are not in a voice channel!")

async def leave_voice_channel(message):
	if message.guild.voice_client:
		try:
			await message.guild.voice_client.disconnect()
			await message.channel.send(f"I have left the voice channel.")
		except Exception:
			await message.channel.send("Failed to leave the voice channel.")
	else:
		await message.channel.send("I am not connected to any voice channel.")
