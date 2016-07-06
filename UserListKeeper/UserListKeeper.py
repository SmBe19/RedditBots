# -*- coding: utf-8 -*-

"""
Keep a list of users that posted a "matching" post.
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

# The name of the subreddit to post to. e.g. "funny"
SUBREDDIT = ""

# The name of the subreddit to post the wiki page to
WIKI_SUBREDDIT = ""

# The name of the wiki page to post the list to
WIKI_PAGE = "UserListKeeper"

# The flair a post needs to have so it's added to the list
ADD_FLAIR = "offer to mod"

# Time in seconds until a user is removed from the list
LEAVE_TIME = 30 * 24 * 3600 # one month

# The time in seconds the bot should sleep until it checks again.
SLEEP = 60*60

# ### END USER CONFIGURATION ### #

# ### BOT CONFIGURATION ### #
DONE_CONFIGFILE = "done.txt"
USERLIST_CONFIGFILE = "userlist.txt"
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

def read_config_userlist():
	users = {}
	try:
		with open(USERLIST_CONFIGFILE, "r") as f:
			for line in f:
				sp = line.strip().split("\t")
				assert len(sp) == 7, sp
				users[sp[0]] = User(*sp)
	except OSError:
		log.info("%s not found.", USERLIST_CONFIGFILE)
	return users

def write_config_userlist(users):
	with open(USERLIST_CONFIGFILE, "w") as f:
		for user in users:
			print(users[user].get_for_file(), file=f)
# ### END DONE CONFIG FILE ### #

# ### MAIN PROCEDURE ### #
class User:

	def __init__(self, name, posting, added, link_karma, comment_karma, age, subs):
		self.name = name
		self.posting = posting
		self.added = float(added)
		self.link_karma = link_karma
		self.comment_karma = comment_karma
		self.age = float(age)
		self.subs = int(subs)

	def get_for_file(self):
		return "\t".join(map(str, [self.name, self.posting, self.added, self.link_karma, self.comment_karma, self.age, self.subs]))

	def get_for_table(self):
		return "| {} |".format(" | ".join(map(str, ["/u/{}".format(self.name), "[link]({})".format(self.posting), self.link_karma, self.comment_karma, self.age // (24*3600), self.subs])))


def add_user(users, submission):
	user = submission.author
	# deleted
	if user is None:
		return
	try:
		log.info("add user %s", user.name)
		nuser = User(user.name, submission.permalink, submission.created_utc, user.link_karma, user.comment_karma, time.time() - user.created_utc, 0)
		if nuser.name in users:
			if nuser.added < users[nuser.name].added:
				log.info("newer posting for %s already registered", user.name)
				return
		users[nuser.name] = nuser
	except AttributeError:
		log.info("user %s is suspended", user.name)
	except praw.errors.NotFound:
		log.info("user %s is banned", user.name)


def check_posts(r, users, done):
	log.info("look for new posts")
	sub = r.get_subreddit(SUBREDDIT)
	sub.refresh()
	for submission in sub.get_new(limit=1000):
		if submission.name in done:
			continue
		if submission.link_flair_text is not None and submission.link_flair_text.lower() == ADD_FLAIR:
			add_user(users, submission)
			done.add(submission.name)
		if time.time() - submission.created_utc > LEAVE_TIME:
			log.info("reached age limit")
			break


def remove_old_users(users):
	todel = []
	for user in users:
		if time.time() - users[user].added > LEAVE_TIME:
			todel.append(users[user])
	for user in todel:
		if user in users:
			del users[user]
			log.info("remove user %s", user)


def update_wiki_page(r, users):
	entry = ["| User | Link | Link Karma | Comment Karma | Age [d] | Subreddits |",
	         "| ---- | ---- | ---------- | ------------- | ------- | ---------- |"]
	usertable = []
	for username in users:
		usertable.append(users[username].get_for_table())
	entry.extend(sorted(usertable))
	r.edit_wiki_page(WIKI_SUBREDDIT, WIKI_PAGE, "\n".join(entry))
	log.info("update wiki page %s/%s", WIKI_SUBREDDIT, WIKI_PAGE)


def run_bot():
	r = praw.Reddit(USERAGENT)
	o = OAuth2Util.OAuth2Util(r)
	o.refresh()

	log.info("Start bot for subreddit %s", SUBREDDIT)

	done = read_config_done()
	users = read_config_userlist()

	while True:
		try:
			o.refresh()

			check_posts(r, users, done)
			remove_old_users(users)
			update_wiki_page(r, users)

		# Allows the bot to exit on ^C, all other exceptions are ignored
		except KeyboardInterrupt:
			break
		except Exception as e:
			log.error("Exception %s", e, exc_info=True)

		write_config_done(done)
		write_config_userlist(users)
		log.info("sleep for %s s", SLEEP)
		time.sleep(SLEEP)

	write_config_done(done)
	write_config_userlist(users)
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
