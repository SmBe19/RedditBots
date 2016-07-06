"""
A bot to forward orangereds from one account to another account.
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

# The time in seconds the bot should sleep until it checks again.
SLEEP = 60*60

# ### END USER CONFIGURATION ### #

# ### BOT CONFIGURATION ### #
ACCOUNTS_CONFIGFILE = "accounts.txt"
DONE_CONFIGFILE = "done.{0}.txt"
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

def read_accounts_config():
	accounts = []
	try:
		with open(ACCOUNTS_CONFIGFILE) as f:
			for line in f:
				# username password forward_to reset_orangered active
				acc = line.split("\t")
				if len(acc) < 5:
					log.error("not enough info for account %s. Format is: username password forward_to reset_orangered active (with one tab between values)", acc[0])

				if acc[4].strip().lower() == "true":
					r = praw.Reddit(USERAGENT)
					try:
						r.login(acc[0].strip(), acc[1].strip(), disable_warning=True)
					except praw.errors.InvalidUserPass:
						log.error("Wrong password for account %s", acc[0])
					else:
						accounts.append((r, acc[2].strip(), acc[3].strip().lower() == "true"))

	except OSError:
		log.error("%s not found.", ACCOUNTS_CONFIGFILE)
	return accounts

def read_config_done(account):
	done = set()
	try:
		with open(DONE_CONFIGFILE.format(account), "r") as f:
			for line in f:
				if line.strip():
					done.add(line.strip())
	except OSError:
		log.info("%s not found.", DONE_CONFIGFILE.format(account))
	return done

def write_config_done(done, account):
	with open(DONE_CONFIGFILE.format(account), "w") as f:
		for d in done:
			if d:
				f.write(d + "\n")


# main procedure
def run_bot():
	r = praw.Reddit(USERAGENT)
	o = OAuth2Util.OAuth2Util(r)

	log.info("Start bot")

	while True:
		try:
			o.refresh()
			accounts = read_accounts_config()
			for account in accounts:
				try:
					log.info("check %s", account[0].user.name)
					message = ""
					message_count = 0
					done = read_config_done(account[0].user.name)
					for msg in account[0].get_unread():
						if msg.name in done:
							continue
						if msg.context and msg.author:
							this_message = "Comment from /u/{0}. [Link]({1}?context=10000)\n\n".format(msg.author.name, msg.permalink)
						elif msg.author:
							this_message = "Message from /u/{0} ({1}).\n\n".format(msg.author.name, msg.subject)
						else:
							this_message = "Something from Someone.\n\n"
						for line in msg.body.split("\n"):
							this_message += "> " + line + "\n"
						if account[2]:
							msg.mark_as_read()
						message += "\n\n" + this_message
						message_count += 1
						done.add(msg.name)

					if message:
						message = "Summary for account /u/{0} ({1}):{2}".format(account[0].user.name, message_count, message)
						r.send_message(account[1], "Summary for account {0}: {1}".format(account[0].user.name, message_count), message)
						log.info("Message sent")

					write_config_done(done, account[0].user.name)
				except KeyboardInterrupt:
					raise
				except Exception as e:
					log.error("Exception %s", e, exc_info=True)

		except KeyboardInterrupt:
			break
		except Exception as e:
			log.error("Exception %s", e, exc_info=True)

		log.info("sleep for %s s", SLEEP)
		time.sleep(SLEEP)


if __name__ == "__main__":
	if not USERAGENT:
		log.error("missing useragent")
	else:
		run_bot()
