"""
A bot to forward orangereds from one account to another account.
Written by /u/SmBe19
"""

import praw
import time

# ### USER CONFIGURATION ### #

# The bot's username.
USERNAME = ""

# The bot's password.
PASSWORD = ""

# The bot's useragent. It should contain a short description of what it does and your username. e.g. "RSS Bot by /u/SmBe19"
USERAGENT = ""

# The time in seconds the bot should sleep until it checks again.
SLEEP = 60*60

# ### END USER CONFIGURATION ### #

# ### BOT CONFIGURATION ### #
ACCOUNTS_CONFIGFILE = "accounts.txt"
DONE_CONFIGFILE = "done.{0}.txt"
# ### END BOT CONFIGURATION ### #

try:
	# A file containing credentials used for testing. So my credentials don't get commited.
	import bot
	USERNAME = bot.username
	PASSWORD = bot.password
	USERAGENT = bot.useragent
except ImportError:
	pass
	
def read_accounts_config():
	accounts = []
	try:
		with open(ACCOUNTS_CONFIGFILE) as f:
			for line in f:
				# username password forward_to reset_orangered active
				acc = line.split("\t")
				if len(acc) < 5:
					print("not enough info for account", acc[0], ". Format is: username password forward_to reset_orangered active (with one tab between values)")
				
				if acc[4].strip().lower() == "true":
					r = praw.Reddit(USERAGENT)
					try:
						r.login(acc[0].strip(), acc[1].strip())
					except praw.errors.InvalidUserPass:
						print("Wrong password for account", acc[0])
					else:
						accounts.append((r, acc[2].strip(), acc[3].strip().lower() == "true"))
					
	except OSError:
		print(ACCOUNTS_CONFIGFILE, "not found.")
	return accounts
	
def read_config_done(account):
	done = []
	try:
		with open(DONE_CONFIGFILE.format(account), "r") as f:
			for line in f:
				if line.strip():
					done.append(line.strip())
	except OSError:
		print(DONE_CONFIGFILE.format(account), "not found.")
		with open(DONE_CONFIGFILE.format(account), "w") as f:
			pass
	return done
	
def write_config_done(done, account):
	with open(DONE_CONFIGFILE.format(account), "w") as f:
		for d in done:
			if d:
				f.write(d + "\n")
	
	
# main procedure
def run_bot():
	r = praw.Reddit(USERAGENT)
	try:
		r.login(USERNAME, PASSWORD)
	except praw.errors.InvalidUserPass:
		print("Wrong password")
		return
	
	print("Start bot")
	
	while True:
		try:
			accounts = read_accounts_config()
			for account in accounts:
				print("check", account[0].user.name)
				message = ""
				message_count = 0
				done = read_config_done(account[0].user.name)
				for msg in account[0].get_unread():
					if msg.name in done:
						continue
					if msg.context:
						this_message = "Comment from /u/{0}. [Link](http://reddit.com{1})\n\n".format(msg.author.name, msg.context)
					else:
						this_message = "Message from /u/{0} ({1}).\n\n".format(msg.author.name, msg.subject)
					for line in msg.body.split("\n"):
						this_message += "> " + line + "\n"
					if account[2]:
						msg.mark_as_read()
					message += "\n\n" + this_message
					message_count += 1
					done.append(msg.name)
				
				if message:
					message = "Summary for account /u/{0} ({1}):{2}".format(account[0].user.name, message_count, message)
					r.send_message(account[1], "Summary for account {0}: {1}".format(account[0].user.name, message_count), message)
					print("Message sent")
					
				write_config_done(done, account[0].user.name)
			
		except KeyboardInterrupt:
			break
		except Exception as e:
			print("Exception", e)
			raise e
		
		print("sleep for", SLEEP, "s")
		time.sleep(SLEEP)
	
	
if __name__ == "__main__":
	if not USERNAME:
		print("missing username")
	elif not PASSWORD:
		print("missing password")
	elif not USERAGENT:
		print("missing useragent")
	else:
		run_bot()
