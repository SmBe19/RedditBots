"""
A bot to change the header of a subreddit according a schedule
Written by /u/SmBe19
"""

import praw
import time
from getpass import getpass

# ### USER CONFIGURATION ### #

# The bot's username.
USERNAME = ""

# The bot's password.
PASSWORD = ""

# The bot's useragent. It should contain a short description of what it does and your username. e.g. "RSS Bot by /u/SmBe19"
USERAGENT = ""

# The name of the subreddit to operate on. The bot has to be a mod there.
SUBREDDIT = ""

# ### END USER CONFIGURATION ### #

# ### BOT CONFIGURATION ### #
HEADERS_CONFIGFILE = "headers.txt"
# ### END BOT CONFIGURATION ### #


try:
	# A file containing credentials used for testing. So my credentials don't get commited.
	import bot
	USERNAME = bot.username
	PASSWORD = bot.password
	USERAGENT = bot.useragent
	SUBREDDIT = bot.subreddit
except ImportError:
	pass
	
def read_headers_config():
	headers = []
	with open(HEADERS_CONFIGFILE, "r") as f:
		for line in f:
			parts = line.split("\t")
			headers.append((int(parts[0]), parts[1].strip()))
	headers.sort()
	return headers
	
# main procedure
def run_bot():
	r = praw.Reddit(USERAGENT)
	try:
		r.login(USERNAME, PASSWORD)
	except praw.errors.InvalidUserPass:
		print("Wrong password")
		return
	sub = r.get_subreddit(SUBREDDIT)
	
	print("Start bot for subreddit", SUBREDDIT)
	
	while True:
		try:
			headers = read_headers_config()
			if len(headers) < 1:
				return
			
			next_header = headers[0]
			atime = time.localtime().tm_hour * 100 + time.localtime().tm_min
			for header in headers:
				if header[0] > atime:
					next_header = header
					break
			
			sleeptime = (next_header[0] % 100 - atime % 100) * 60 + (next_header[0] // 100 - atime // 100) * 3600
			if sleeptime < 0:
				sleeptime += 24*3600
			print("Now:", atime, "/ Sleep for", sleeptime, "s until", next_header[0])
			time.sleep(sleeptime)
			
			sub.upload_image(next_header[1], header=True)
			print("Change header")
			
		except KeyboardInterrupt:
			break
		except Exception as e:
			print("Exception", e)
	
	
if __name__ == "__main__":
	if not USERNAME:
		print("missing username")
	elif not USERAGENT:
		print("missing useragent")
	elif not SUBREDDIT:
		print("missing subreddit")
	else:
		if not PASSWORD:
			PASSWORD = getpass()
		run_bot()