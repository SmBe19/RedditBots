"""
A bot to post from rss feeds to a given subreddit
Written by /u/SmBe19
"""

import praw
import time
import RSSReader

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

# ### BOT CONFIGURATION ### #
SOURCES_CONFIGFILE = "sources.txt"
DONE_CONFIGFILE = "done.txt"
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
	
def read_config_sources():
	sources = []
	try:
		with open(SOURCES_CONFIGFILE, "r") as f:
			for line in f:
				sources.append(line)
	except OSError:
		print(SOURCES_CONFIGFILE, "not found.")
	return sources

def read_config_done():
	done = []
	try:
		with open(DONE_CONFIGFILE, "r") as f:
			for line in f:
				if line.strip():
					done.append(line.strip())
	except OSError:
		print(DONE_CONFIGFILE, "not found.")
		with open(DONE_CONFIGFILE, "w") as f:
			pass
	return done
	
def write_config_done(done):
	with open(DONE_CONFIGFILE, "w") as f:
		for d in done:
			if d:
				f.write(d + "\n")
	
# main procedure
def run_bot():
	r = praw.Reddit(USERAGENT)
	r.login(USERNAME, PASSWORD)
	sub = r.get_subreddit(SUBREDDIT)
	
	print("Start bot for subreddit", SUBREDDIT)
	
	done = read_config_done()
	
	while True:
		try:
			sources = read_config_sources()
			
			print("check sources")
			newArticles = []
			for source in sources:
				newArticles.extend(RSSReader.get_new_articles(source))
			
			for article in newArticles:
				if article[2] not in done:
					try:
						sub.submit(article[0], url=article[1])
					except praw.errors.AlreadySubmitted:
						print("already submitted")
					else:
						print("submit article")
					done.append(article[2])
			
		# Allows the bot to exit on ^C, all other exceptions are ignored
		except KeyboardInterrupt:
			break
		except Exception as e:
			print("Exception", e)
			
		write_config_done(done)
		print("sleep for", SLEEP, "s")
		time.sleep(SLEEP)
		
	write_config_done(done)
	
	
if __name__ == "__main__":
	if not USERNAME:
		print("missing username")
	elif not PASSWORD:
		print("missing password")
	elif not USERAGENT:
		print("missing useragent")
	elif not SUBREDDIT:
		print("missing subreddit")
	else:
		run_bot()