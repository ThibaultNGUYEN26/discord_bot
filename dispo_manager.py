import datetime

async def handle_dispo_command(message, command):
	if command == "dispo":
		await show_dispo(message)
	elif command.startswith("dispo "):
		await update_dispo(message, command[6:])

async def show_dispo(message):
	today = datetime.datetime.now()
	valid_entries = []
	with open("dispo.txt", "r") as f:
		lines = f.readlines()
	for line in lines:
		line_date_str, _ = line.split(": ", 1)
		try:
			line_date = datetime.datetime.strptime(line_date_str, "%d/%m").replace(year=today.year)
		except ValueError:
			continue
		if line_date.date() >= today.date():
			valid_entries.append((line_date, line))
	valid_entries.sort(key=lambda x: x[0])
	sorted_lines = [entry[1] for entry in valid_entries]
	with open("dispo.txt", "w") as f:
		f.writelines(sorted_lines)
	with open("dispo.txt", 'r') as f:
		dispo = f.read()
	if dispo.strip():
		await message.channel.send(f"**{dispo}**")
	else:
		await message.channel.send("There are **no availabilities** at the moment.")

async def update_dispo(message, command):
	if command.startswith("remove"):
		await remove_dispo(message, command[7:].strip())
	else:
		await add_or_update_dispo(message, command)

async def remove_dispo(message, date_str):
	with open("dispo.txt", "r") as f:
		lines = f.readlines()
	updated = False
	for i, line in enumerate(lines):
		line_date, rest = line.split(": ", 1)
		if line_date == date_str:
			username = message.author.name
			updated_lines = [entry for entry in rest.split(", ") if not entry.startswith(f"{username}(")]
			if updated_lines:
				lines[i] = f"{date_str}: {', '.join(updated_lines)}\n"
			else:
				lines.pop(i)
			updated = True
			break
	if updated:
		with open("dispo.txt", "w") as f:
			f.writelines(lines)
		await message.channel.send(f"Status for **{message.author.name}** on **{date_str}** has been removed.")
	else:
		await message.channel.send(f"No status found for **{message.author.name}** on **{date_str}**.")

async def add_or_update_dispo(message, command):
	try:
		date_str, status = command.split(' ', 1)
		date = datetime.datetime.strptime(date_str, "%d/%m").replace(year=datetime.datetime.now().year)
	except ValueError:
		await message.channel.send("Invalid **date format**. Please use **dd/mm** format.")
		return

	today = datetime.datetime.now()
	if date.date() < today.date():
		await message.channel.send("The date has **already passed**. Please provide a future date.")
		return

	max_date = today + datetime.timedelta(days=31)
	if date > max_date:
		await message.channel.send("The date **exceeds one month** from today. Please provide a date **within the next month**.")
		return

	username = message.author.name
	new_entry = f"{username}({status})"
	with open("dispo.txt", "r") as f:
		lines = f.readlines()
	updated = False
	for i, line in enumerate(lines):
		line_date, rest = line.split(": ", 1)
		if line_date == date_str:
			if username in rest:
				updated_lines = [new_entry if entry.startswith(f"{username}(") else entry for entry in rest.split(", ")]
				lines[i] = f"{date_str}: {', '.join(updated_lines)}\n"
			else:
				lines[i] = f"{date_str}: {rest.strip()}, {new_entry}\n"
			updated = True
			break
	if not updated:
		lines.append(f"{date_str}: {new_entry}\n")
	with open("dispo.txt", "w") as f:
		f.writelines(lines)
	await message.channel.send(f"Status for **{username}** on **{date_str}** has been updated to **{status}**.")
