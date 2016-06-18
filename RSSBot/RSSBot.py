"""
A bot to post from rss feeds to a given subreddit
Written by /u/SmBe19
"""

import praw
import time
import logging
import logging.handlers
import OAuth2Util
import RSSReader

# ### USER CONFIGURATION ### #

# The bot's useragent. It should contain a short description of what it does and your username. e.g. "RSS Bot by /u/SmBe19"
USERAGENT = ""

# The name of the subreddit to post to. e.g. "funny"
SUBREDDIT = ""

# The time in seconds the bot should sleep until it checks again.
SLEEP = 60*60

# If True, the bot will submit a link even if reddit says it was already submitted. This can be the case if it was submitted in an other subreddit or by an other user, or if the bot failed with keeping track of already submitted articles (shouldn't be the case).
RESUBMIT_ANYWAYS = True

# If True, the bot will post a comment with the description of the article.
POST_DESCRIPTION = True

# The text the bot should post with the description, {0} will be replaced by the description
DESCRIPTION_FORMAT = "Link description:\n\n{0}"

# ### END USER CONFIGURATION ### #

# ### BOT CONFIGURATION ### #
SOURCES_CONFIGFILE = "sources.txt"
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

def read_config_sources():
	sources = []
	try:
		with open(SOURCES_CONFIGFILE, "r") as f:
			for line in f:
				sources.append(line)
	except OSError:
		log.error("%s not found.", SOURCES_CONFIGFILE)
	return sources

def read_config_done():
	done = []
	try:
		with open(DONE_CONFIGFILE, "r") as f:
			for line in f:
				if line.strip():
					done.append(line.strip())
	except OSError:
		log.info("%s not found.", DONE_CONFIGFILE)
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

	log.info("Start bot for subreddit %s", SUBREDDIT)

	done = read_config_done()

	while True:
		try:
			o.refresh()
			sources = read_config_sources()

			log.info("check sources")
			newArticles = []
			for source in sources:
				newArticles.extend(RSSReader.get_new_articles(source))

			for article in newArticles:
				if article[3] not in done:
					done.append(article[3])
					try:
						submission = sub.submit(article[0], url=article[1], resubmit=RESUBMIT_ANYWAYS)
						if POST_DESCRIPTION and article[2] is not None:
							submission.add_comment(DESCRIPTION_FORMAT.format(article[2]))
					except praw.errors.AlreadySubmitted:
						log.info("already submitted")
					else:
						log.info("submit article")

		# Allows the bot to exit on ^C, all other exceptions are ignored
		except KeyboardInterrupt:
			break
		except Exception as e:
			log.error("Exception %s", e, exc_info=True)

		write_config_done(done)
		log.info("sleep for %s s", SLEEP)
		time.sleep(SLEEP)

	write_config_done(done)


if __name__ == "__main__":
	if not USERAGENT:
		log.error("missing useragent")
	elif not SUBREDDIT:
		log.error("missing subreddit")
	else:
		run_bot()
