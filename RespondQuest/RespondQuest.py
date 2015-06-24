"""
A bot to post from rss feeds to a given subreddit
Written by /u/SmBe19
"""

import praw
import time
import OAuth2Util

# ### USER CONFIGURATION ### #

# The bot's useragent. It should contain a short description of what it does and your username. e.g. "RespondQuest Bot by /u/SmBe19"
USERAGENT = ""

# The name of the subreddit to check. e.g. "funny"
SUBREDDIT = ""

# The time in seconds the bot should sleep until it checks again.
SLEEP = 60*60

# The reason the bot should give for reporting the post
REPORT_MESSAGE = "Potential Rule E violation, please check!"

# The time in seconds, within OP has to respond
RESPOND_QUEST_TIME = 3*60*60

# The minimum number of comments a post should have before it is reported
MIN_COMMENTS = 15

# ### END USER CONFIGURATION ### #

# ### BOT CONFIGURATION ### #
DONE_CONFIGFILE = "done.txt"
# ### END BOT CONFIGURATION ### #

try:
	# A file containing infos for testing.
	import bot
	USERAGENT = bot.useragent
	SUBREDDIT = bot.subreddit
except ImportError:
	pass
	
def read_config_done():
	done = []
	try:
		with open(DONE_CONFIGFILE, "r") as f:
			for line in f:
				if line.strip():
					done.append(line.strip())
	except OSError:
		print(DONE_CONFIGFILE, "not found.")
	return done
	
def write_config_done(done):
	with open(DONE_CONFIGFILE, "w") as f:
		for d in done:
			if d:
				f.write(d + "\n")
	
def op_responded(post):
	try:
		post.replace_more_comments()
	except:
		pass
		
	for comment in praw.helpers.flatten_tree(post.comments):
		if comment.author == post.author:
			return True
	return False
	
# main procedure
def run_bot():
	r = praw.Reddit(USERAGENT)
	o = OAuth2Util.OAuth2Util(r)
	o.refresh()
	sub = r.get_subreddit(SUBREDDIT)
	
	print("Start bot for subreddit", SUBREDDIT)
	
	done = read_config_done()
	
	while True:
		try:
			print("check subreddit")
			o.refresh()
			
			for post in sub.get_new(limit=100):
				if post.name in done:
					continue
				if time.time() - post.created_utc > RESPOND_QUEST_TIME:
					if len(post.comments) >= MIN_COMMENTS:
						if not op_responded(post):
							post.report(REPORT_MESSAGE)
							print("reported")
					
						done.append(post.name)
			
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
	if not USERAGENT:
		print("missing useragent")
	elif not SUBREDDIT:
		print("missing subreddit")
	else:
		run_bot()