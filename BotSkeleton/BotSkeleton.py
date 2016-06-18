# -*- coding: utf-8 -*-

"""
An empty bot to be able to start a new bot fast.
Written by /u/SmBe19
"""

import praw
import time
import logging
import logging.handlers
import OAuth2Util

# ### USER CONFIGURATION ### #

# The bot's useragent. It should contain a short description of what it does and your username. e.g. "RSS Bot by /u/SmBe19"
USERAGENT = ""

# The name of the subreddit to post to. e.g. "funny"
SUBREDDIT = ""

# The time in seconds the bot should sleep until it checks again.
SLEEP = 60*60

# ### END USER CONFIGURATION ### #

# ### BOT CONFIGURATION ### #
DONE_CONFIGFILE = "done.txt"
# ### END BOT CONFIGURATION ### #

# ### LOGGING CONFIGURATION ### #
LOG_LEVEL = logging.INFO
LOG_FILENAME = "bot.log"
LOG_FILE_BACKUPCOUNT = 5
LOG_FILE_MAXSIZE = 1024 * 256
# ### END LOGGING CONFIGURATION ### #

# ### EXTERNAL CONFIG FILE ### #
try:
	# A file containing data for global constants.
	import bot
	for k in dir(bot):
		if k.upper() in globals():
			globals()[k.upper()] = getattr(bot, k)
except ImportError:
	pass
# ### END EXTERNAL CONFIG FILE ### #

# ### LOGGING SETUP ### #
log = logging.getLogger("bot")
log.setLevel(LOG_LEVEL)
log_formatter = logging.Formatter('%(levelname)s: %(message)s')
log_formatter_file = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
log_stderrHandler = logging.StreamHandler()
log_stderrHandler.setFormatter(log_formatter)
log.addHandler(log_stderrHandler)
if LOG_FILENAME is not None:
	log_fileHandler = logging.handlers.RotatingFileHandler(LOG_FILENAME, maxBytes=LOG_FILE_MAXSIZE, backupCount=LOG_FILE_BACKUPCOUNT)
	log_fileHandler.setFormatter(log_formatter_file)
	log.addHandler(log_fileHandler)
# ### END LOGGING SETUP ### #

# ### DONE CONFIG FILE ### #
def read_config_done():
	done = []
	try:
		with open(DONE_CONFIGFILE, "r") as f:
			for line in f:
				if line.strip():
					done.append(line.strip())
	except OSError:
		log.error("%s not found.", DONE_CONFIGFILE)
	return done

def write_config_done(done):
	with open(DONE_CONFIGFILE, "w") as f:
		for d in done:
			if d:
				f.write(d + "\n")
# ### END DONE CONFIG FILE ### #

# ### MAIN PROCEDURE ### #
def run_bot():
	r = praw.Reddit(USERAGENT)
	o = OAuth2Util.OAuth2Util(r)
	o.refresh()
	sub = r.get_subreddit(SUBREDDIT)

	log.info("Start bot for subreddit %s", SUBREDDIT)

	done = read_config_done()

	while True:
		try:
			pass

		# Allows the bot to exit on ^C, all other exceptions are ignored
		except KeyboardInterrupt:
			break
		except Exception as e:
			log.error("Exception %s", e)

		write_config_done(done)
		log.info("sleep for %s s", SLEEP)
		time.sleep(SLEEP)

	write_config_done(done)
# ### END MAIN PROCEDURE ### #

# ### START BOT ### #
if __name__ == "__main__":
	if not USERAGENT:
		log.error("missing useragent")
	elif not SUBREDDIT:
		log.error("missing subreddit")
	else:
		run_bot()
# ### END START BOT ### #
