# -*- coding: utf-8 -*-

"""
A bot that posts comments / posts received by PM
Written by /u/SmBe19
"""

import praw
import praw.errors
import time
import logging
import logging.handlers
import OAuth2Util

# ### USER CONFIGURATION ### #

# The bot's useragent. It should contain a short description of what it does and your username. e.g. "RSS Bot by /u/SmBe19"
USERAGENT = ""

# The time in seconds the bot should sleep until it checks again.
SLEEP = 60*10

# text that has to appear at the start of the message for a new self post
COMMAND_SELF = "proxy#self"

# text that has to appear at the start of the message for a new link post
COMMAND_LINK = "proxy#link"

# text that has to appear at the start of the message for a new toplevel comment
COMMAND_TOP_COMMENT = "proxy#topcomment"

# text that has to appear at the start of the message for a new comment
COMMAND_COMMENT = "proxy#comment"

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
	done = set()
	try:
		with open(DONE_CONFIGFILE, "r") as f:
			for line in f:
				if line.strip():
					done.add(line.strip())
	except OSError:
		log.info("%s not found.", DONE_CONFIGFILE)
	return done

def write_config_done(done):
	with open(DONE_CONFIGFILE, "w") as f:
		for d in done:
			if d:
				f.write(d + "\n")
# ### END DONE CONFIG FILE ### #

# ### MAIN PROCEDURE ### #
def extract_body(r, pm, command, with_title=False):
	lines = [s.replace("\r", "") for s in pm.body.split("\n")]
	assert lines[0].lower().startswith(command), lines[0]
	destination = lines[0][len(command):].strip()

	start = 1
	title = None
	while start < len(lines) and len(lines[start]) < 1:
		start += 1
		if title is None and with_title and start < len(lines) and len(lines[start]) > 0:
			title = lines[start]
			start += 1

	if start >= len(lines):
		log.info("Command without body")
		return None

	lines = lines[start:]

	if with_title:
		return (destination, title, lines)
	else:
		return (destination, lines)

def add_toplevel_comment(r, pm):
	body = extract_body(r, pm, COMMAND_TOP_COMMENT)
	if body is None:
		return

	url, lines = body
	sub = r.get_submission(url)
	sub.add_comment("\n".join(lines))

	log.info("post new topcomment in %s", sub.subreddit.display_name)

def add_comment(r, pm):
	body = extract_body(r, pm, COMMAND_COMMENT)
	if body is None:
		return

	url, lines = body
	sub = r.get_submission(url)
	if len(sub.comments) < 1:
		log.info("invalid comment url")
		return
	com = sub.comments[0]
	com.reply("\n".join(lines))

	log.info("post new comment in %s", sub.subreddit.display_name)

def add_self(r, pm):
	body = extract_body(r, pm, COMMAND_SELF, with_title=True)
	if body is None:
		return

	subreddit, title, lines = body
	sub = r.get_subreddit(subreddit)
	sub.submit(title=title, text="\n".join(lines))

	log.info("post new self post in %s", subreddit)

def add_link(r, pm):
	body = extract_body(r, pm, COMMAND_LINK, with_title=True)
	if body is None:
		return

	subreddit, title, lines = body
	sub = r.get_subreddit(subreddit)
	sub.submit(title=title, url=lines[0], resubmit=True)

	log.info("post new link post in %s", subreddit)

def handle_pm(r, pm):
	bodylower = pm.body.strip().lower()
	if bodylower.startswith(COMMAND_SELF):
		add_self(r, pm)
	elif bodylower.startswith(COMMAND_LINK):
		add_link(r, pm)
	elif bodylower.startswith(COMMAND_COMMENT):
		add_comment(r, pm)
	elif bodylower.startswith(COMMAND_TOP_COMMENT):
		add_toplevel_comment(r, pm)
	else:
		return False
	return True

def check_inbox(r, done):
	log.info("check inbox")
	for pm in r.get_unread():
		if pm.name in done:
			continue
		try:
			if handle_pm(r, pm):
				pm.mark_as_read()
			done.add(pm.name)
		except praw.errors.RateLimitExceeded as e:
			log.info("Hit rate limit: %s", e.message)

def run_bot():
	r = praw.Reddit(USERAGENT)
	o = OAuth2Util.OAuth2Util(r)
	o.refresh()

	log.info("Start bot")

	done = read_config_done()

	while True:
		try:
			o.refresh()
			check_inbox(r, done)

		# Allows the bot to exit on ^C, all other exceptions are ignored
		except KeyboardInterrupt:
			break
		except Exception as e:
			log.error("Exception %s", e, exc_info=True)

		write_config_done(done)
		log.info("sleep for %s s", SLEEP)
		time.sleep(SLEEP)

	write_config_done(done)
# ### END MAIN PROCEDURE ### #

# ### START BOT ### #
if __name__ == "__main__":
	if not USERAGENT:
		log.error("missing useragent")
	else:
		run_bot()
# ### END START BOT ### #
