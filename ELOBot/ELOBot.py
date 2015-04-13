"""
A bot to track elo ratings.
Written by /u/SmBe19
"""

import praw
import time
from getpass import getpass
import re

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
SLEEP = 60

# The string the bot looks for
BOTCALLSTRING = "!elo"

# The commands the bot understands. 0: report game result; 1: confirm game result
BOTACTIONS = ["game", "confirm"]

# The text that should be used to ask for confirmation. {0} will be replaced by the users name
PLEASE_CONFIRM_TEXT = "/u/{0}, please confirm that this result is correct by replying \"" + BOTCALLSTRING + " " + BOTACTIONS[1] + "\" to the original comment."

# The text that should be used to confirm the elo change. {0} will be the name of the winner, {1} his new elo. {2} will be the name of the loser, {3} his new elo.
CONFIRMATION_TEXT = "ELO ranking changed.\n\n/u/{0}: {1}\n\n/u/{2}: {3}"

# The text the bot should post if a user wants to play with itself
BOT_ERROR_SAME_USER = "You can't play with yourself. Well yeah, not here."

# The signature the bot adds to every comment he makes
BOT_SIGNATURE = "\n\n---\n\n^I'm ^a ^bot. ^Use ^\"" + BOTCALLSTRING + " ^" + BOTACTIONS[0] + " ^winner_name ^loser_name\" ^to ^report ^a ^finished ^game."

#The flair the users get. {0} is replaced by the actual elo rating
FLAIR_TEXT = "rating: {0}"

# ### END USER CONFIGURATION ### #

# ### ELO CONFIGURATION ### #
# based on http://en.wikipedia.org/wiki/Elo_rating_system#Theory

ELO_INITIAL_SCORE = 1000
ELO_MAX_DIFFERENCE = 400
ELO_MAX_ADJUSTMENT = 20

# ### END ELO CONFIGURATION ### #

# ### BOT CONFIGURATION ### #
ELO_CONFIGFILE = "elo.txt"
PROGRESS_CONFIGFILE = "progress.txt"
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
	
BOTCALLRE = re.compile(re.escape(BOTCALLSTRING.lower()) + " (" + "|".join([re.escape(a.lower()) for a in BOTACTIONS]) + ")(?: (?:\/u\/)?(\S*) (?:\/u\/)?(\S*))?")
	
def read_config_elo():
	elo = {}
	try:
		with open(ELO_CONFIGFILE, "r") as f:
			for line in f:
				parts = line.split("\t")
				elo[parts[0].strip()] = int(parts[1])
	except OSError:
		print(ELO_CONFIGFILE, "not found.")
	return elo
	
def write_config_elo(elo):
	with open(ELO_CONFIGFILE, "w") as f:
		for key in elo:
			f.write("{0}\t{1}\n".format(key, str(elo[key])))

def read_config_progress():
	progress = {}
	try:
		with open(PROGRESS_CONFIGFILE, "r") as f:
			for line in f:
				parts = line.strip().split("\t")
				progress[parts[0]] = [[parts[1], parts[2].lower() == "true"], [parts[3], parts[4].lower() == "true"]]
	except OSError:
		print(PROGRESS_CONFIGFILE, "not found.")
	return progress
	
def write_config_progress(progress):
	with open(PROGRESS_CONFIGFILE, "w") as f:
		for key in progress:
			f.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(key, progress[key][0][0], str(progress[key][0][1]), progress[key][1][0], str(progress[key][1][1])))
				
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
				
def write_all_config(elo, progress, done):
	write_config_done(done)
	write_config_elo(elo)
	write_config_progress(progress)
				
def get_new_elo(winner_elo, loser_elo):
	diff = (loser_elo - winner_elo)
	if abs(diff) > ELO_MAX_DIFFERENCE:
		diff = ELO_MAX_DIFFERENCE * (1 if diff > 0 else -1)
	e_a = 1/(1+10**(diff/ELO_MAX_DIFFERENCE))
	e_b = 1/(1+10**(-diff/ELO_MAX_DIFFERENCE))
	new_winner_elo = winner_elo + ELO_MAX_ADJUSTMENT * (1 - e_a)
	new_loser_elo = loser_elo + ELO_MAX_ADJUSTMENT * (0 - e_b)
	return (int(new_winner_elo), int(new_loser_elo))
				
def set_new_elo(winner, loser, elo, sub):
	if winner == loser:
		return
	if winner not in elo:
		elo[winner] = ELO_INITIAL_SCORE
	if loser not in elo:
		elo[loser] = ELO_INITIAL_SCORE
	elo[winner], elo[loser] = get_new_elo(elo[winner], elo[loser])
	try:
		sub.set_flair(winner, FLAIR_TEXT.format(str(elo[winner])))
		sub.set_flair(loser, FLAIR_TEXT.format(str(elo[loser])))
	except praw.errors.ModeratorRequired:
		print("You have to be mod to set flair")
	
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
	
	done = read_config_done()
	elo = read_config_elo()
	progress = read_config_progress()
	
	while True:
		try:
			sub.refresh()
			print("check comments")
			for comment in sub.get_comments():
				if comment.author.name == r.user.name:
					continue
				match = BOTCALLRE.search(comment.body.lower())
				if match:
					# game finished
					if match.group(1).lower() == BOTACTIONS[0]:
						if comment.name not in progress and comment.name not in done:
							print("register new game:", match.group(0))
							if match.group(2).lower() == match.group(3).lower():
								comment.reply(BOT_ERROR_SAME_USER + BOT_SIGNATURE)
								done.append(comment.name)
								print("Same user!")
								continue
								
							progress[comment.name] = [[match.group(2).lower(), match.group(2).lower() == comment.author.name.lower()], [match.group(3).lower(), match.group(3).lower() == comment.author.name.lower()]]
							
							for i in range(2):
								if not progress[comment.name][i][1]:
									comment.reply(PLEASE_CONFIRM_TEXT.format(progress[comment.name][i][0]) + BOT_SIGNATURE)
									print(progress[comment.name][i][0], "has to confirm")
					
					# confirmation
					if match.group(1).lower() == BOTACTIONS[1]:
						if comment.parent_id in progress:
							for i in range(2):
								if comment.author.name.lower() == progress[comment.parent_id][i][0]:
									progress[comment.parent_id][i][1] = True
									print("found confirmation for", comment.author.name)
							
							if progress[comment.parent_id][0][1] and progress[comment.parent_id][1][1]:
								set_new_elo(progress[comment.parent_id][0][0], progress[comment.parent_id][1][0], elo, sub)
								conf = CONFIRMATION_TEXT.format(progress[comment.parent_id][0][0], elo[progress[comment.parent_id][0][0]], progress[comment.parent_id][1][0], elo[progress[comment.parent_id][1][0]])
								done.append(comment.parent_id)
								del progress[comment.parent_id]
								parent = r.get_info(thing_id=comment.parent_id)
								parent.reply(conf + BOT_SIGNATURE)
								
								print("updated elo")

								write_all_config(elo, progress, done)
			
		# Allows the bot to exit on ^C, all other exceptions are ignored
		except KeyboardInterrupt:
			break
		except Exception as e:
			print("Exception", e)
			
		write_all_config(elo, progress, done)
		print("sleep for", SLEEP, "s")
		time.sleep(SLEEP)
		
	write_all_config(elo, progress, done)
	
	
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