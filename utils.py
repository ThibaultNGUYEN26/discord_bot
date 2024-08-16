def get_user_id(target):
	usernames = {
		"michael": "yellowman",
		"thibault": "drakehunthor",
		"martin": "martinng",
		"oceane": "oceane9149",
		"lena": "lena1007",
		"mathias": "barbuga",
		"karine": ".karine.__46565"
	}

	user_ids = {
		"yellowman": 241148202315808769,
		"drakehunthor": 339089181164830731,
		"martinng": 490073469099180032,
		"oceane9149": 878725584778330112,
		"lena1007": 943211763636260965,
		"barbuga": 943932125256777788,
		".karine.__46565": 1200175453458149482
	}

	username = usernames.get(target.lower(), None)
	if username:
		return user_ids.get(username, None)
	return None
