def parse_URL(URL, host=None):
	if str(URL).isdigit():
		out = "http://localhost:" + str(URL)
	else:
		out = URL
	return out