# -*- coding: utf-8 -*-

"""
A bot that posts a link to a wiki (for /r/evocreo)
Written by /u/SmBe19
"""

import praw
import re
import time
import OAuth2Util

# ### USER CONFIGURATION ### #

# The bot's useragent. It should contain a short description of what it does and your username. e.g. "RSS Bot by /u/SmBe19"
USERAGENT = ""

# The name of the subreddit to post to. e.g. "funny"
SUBREDDIT = ""

# The time in seconds the bot should sleep until it checks again.
SLEEP = 60

# The regex used to find comments to reply
COMMENT_REGEX = re.compile(r"\{(.*?)\} is my favorite Creo\.")

ANSWER = "More information about [{0}](http://evocreo.wikia.com/wiki/{0})."

# ### END USER CONFIGURATION ### #

# ### BOT CONFIGURATION ### #
DONE_CONFIGFILE = "done.txt"
# ### END BOT CONFIGURATION ### #

try:
	# A file containing data for global constants.
	import bot
	for k in dir(bot):
		if k.upper() in globals():
			globals()[k.upper()] = getattr(bot, k)
except ImportError:
	pass

def read_config_done():
	done = set()
	try:
		with open(DONE_CONFIGFILE, "r") as f:
			for line in f:
				if line.strip():
					done.add(line.strip())
	except OSError:
		print(DONE_CONFIGFILE, "not found.")
	return done

def write_config_done(done):
	with open(DONE_CONFIGFILE, "w") as f:
		for d in done:
			if d:
				f.write(d + "\n")

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
			o.refresh()
			sub.refresh()

			for comment in sub.get_comments():
				if comment.name not in done:
					answer = ""
					for match in COMMENT_REGEX.finditer(comment.body):
						answer += ANSWER.format(match.group(1)) + "\n"

					if len(answer) > 0:
						print("reply")
						comment.reply(answer)
						done.add(comment.name)

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
