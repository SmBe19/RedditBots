"""
A bot to post on a schedule but posts on a given user so it can be edited later
Written by /u/SmBe19
"""

import praw
import time
from getpass import getpass
import ScheduledPost

# ### USER CONFIGURATION ### #

# The bot's username.
USERNAME = ""

# The bot's password.
PASSWORD = ""

# The bot's useragent. It should contain a short description of what it does and your username. e.g. "RSS Bot by /u/SmBe19"
USERAGENT = ""

# The name of the subreddit to post to. e.g. "funny"
SUBREDDIT = ""

# The time in seconds the bot should sleep until it checks again.
SLEEP = 60*60

# ### END USER CONFIGURATION ### #

try:
	# A file containing credentials used for testing. So my credentials don't get commited.
	import bot
	USERNAME = bot.username
	PASSWORD = bot.password
	USERAGENT = bot.useragent
	SUBREDDIT = bot.subreddit
except ImportError:
	pass
	
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
	
	ScheduledPost.read_config(sub)
	
	while True:
		try:
			pass
		# Allows the bot to exit on ^C, all other exceptions are ignored
		except KeyboardInterrupt:
			break
		except Exception as e:
			print("Exception", e)
			
		print("sleep for", SLEEP, "s")
		time.sleep(SLEEP)
		
	
	
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