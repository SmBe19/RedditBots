"""
Writes an email if some rule is satisfied
Written by /u/SmBe19
"""

import praw
import time
import smtplib
import OAuth2Util

# ### USER CONFIGURATION ### #

# The bot's useragent. It should contain a short description of what it does and your username. e.g. "RSS Bot by /u/SmBe19"
USERAGENT = ""

# The time in seconds the bot should sleep until it checks again.
SLEEP = 60

# The number of seconds the age of a post can be off and is still seen as within the timespan (e.g. if 20 ups in 20 minutes are searched, with a buffer of 5 minutes a post with 20 ups which is 25 minutes old will still be considered)
AGE_BUFFER = 10*60

# Hostname of the smtp server to use
SMTP_HOST = "smtp.gmail.com"

# Port of the smtp server to use
SMTP_PORT = 587

# EMail address to use as sender
SMTP_FROM = "me@example.com"

# Username to login on the smtp server
SMTP_USERNAME = "me@example.com"

# Password to login on the smtp server
SMTP_PASSWORD = "123"

# Subject line of the message for the SubNewPost rule. {0} will be replaced by the Subreddit name
SUBJECT_SUBNEWPOST_TEXT = "New Post in {0}"

# Subject line of the message for the UserNewPost rule. {0} will be replaced by the user name
SUBJECT_USERNEWPOST_TEXT = "New Post from {0}"

# Subject line of the message for the UserInSubNewPost rule. {0} will be replaced by the Subreddit name, {1} by the user name
SUBJECT_USERINSUBNEWPOST_TEXT = "New Post in {0} from {1}"

# Subject line of the message for the SubNewComment rule. {0} will be replaced by the Subreddit name
SUBJECT_SUBNEWCOMMENT_TEXT = "New Comment in {0}"

# Subject line of the message for the UserNewComment rule. {0} will be replaced by the user name
SUBJECT_USERNEWCOMMENT_TEXT = "New Comment from {0}"

# Subject line of the message for the UserInSubNewComment rule. {0} will be replaced by the Subreddit name, {1} by the user name
SUBJECT_USERINSUBNEWCOMMENT_TEXT = "New Comment in {0} from {1}"

# Subject line of the message for the VotesInTime rule. {0} will be replaced by the Subreddit name
SUBJECT_VOTESINTIME_TEXT = "New Post in {0} satisfying rule"

# Body of the message. {0} will be replaced by the permalink, {1} by the title, {2} will be replaced by the URL, {3} by selftext
BODY_TEXT = "Comments: {0}\n\nTitle: {1}\n\nURL: {2}\n\nSelftext: {3}"

# If true, no messages will be sent. Used to initialize a new Subreddit / User so you don't get a message for every post already existing.
BUILD_DONE_LIST = False
# ### END USER CONFIGURATION ### #

# ### BOT CONFIGURATION ### #
DONE_CONFIGFILE = "done.txt"
RULES_CONFIGFILE = "rules.txt"
# ### END BOT CONFIGURATION ### #

try:
	# A file containing data for global constants.
	import bot
	for k in dir(bot):
		if k.upper() in globals():
			globals()[k.upper()] = getattr(bot, k)
except ImportError:
	pass

def read_config_rules():
	rules = []
	try:
		with open(RULES_CONFIGFILE, "r") as f:
			for line in f:
				if line.startswith("#"):
					continue
				rules.append([w.strip().lower() for w in line.split("\t")])
	except OSError:
		print(RULES_CONFIGFILE, "not found.")
	return rules


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

def send_email(recipient, subject, message):
	smtp = smtplib.SMTP(host=SMTP_HOST, port=SMTP_PORT)
	smtp.starttls()
	if SMTP_USERNAME and SMTP_PASSWORD:
		try:
			smtp.login(SMTP_USERNAME, SMTP_PASSWORD)
		except smtplib.SMTPAuthenticationError:
			print("Wrong email password")

	try:
		smtp.sendmail(SMTP_FROM, recipient, "Subject: {0}\n\n{1}".format(subject, message))
	except Exception as e:
		print("Error while sending mail", e)
	smtp.quit()

def send_message(r, recipient, subject, message):
	if recipient.startswith("/u/"):
		if not r.is_oauth_session():
			print("Recipient is Reddit user, but you are not logged in. Rule ignored.")
			return
		r.send_message(r.get_redditor(recipient[3:]), subject, message)
	else:
		send_email(recipient, subject, message)

# main procedure
def run_bot():
	r = praw.Reddit(USERAGENT)
	o = OAuth2Util.OAuth2Util(r)
	o.refresh()

	print("Start bot")

	done = read_config_done()

	while True:
		try:
			o.refresh()
			rules = read_config_rules()
			old_done = done[:]
			for rule in rules:
				print("process rule", rule[1])
				if rule[0].startswith("/u/") and not r.is_oauth_session():
					print("Recipient is Reddit user, but you are not logged in. Rule ignored.")
					continue
				if rule[1] == "votesintime":
					sub = r.get_subreddit(rule[2])
					age = int(rule[3])
					ups = int(rule[4])

					for post in sub.get_new(limit=100):
						diff = abs((time.time() - post.created_utc) - age)
						if diff <= AGE_BUFFER and post.score >= ups:
							if post.name in old_done:
								continue
							if not BUILD_DONE_LIST:
								send_message(r, rule[0], SUBJECT_VOTESINTIME_TEXT.format(sub.display_name), BODY_TEXT.format(post.permalink, post.title, post.url, post.selftext))
							done.append(post.name)
							print("found new post for rule", rule[1])

				elif rule[1] == "usernewpost":
					redditor = r.get_redditor(rule[2])
					for post in redditor.get_submitted(limit=100):
						if post.name in old_done:
							continue
						if not BUILD_DONE_LIST:
							send_message(r, rule[0], SUBJECT_USERNEWPOST_TEXT.format(redditor.name), BODY_TEXT.format(post.permalink, post.title, post.url, post.selftext))
						done.append(post.name)
						print("found new post for rule", rule[1])

				elif rule[1] == "subnewpost":
					sub = r.get_subreddit(rule[2])
					for post in sub.get_new(limit=100):
						if post.name in old_done:
							continue
						if not BUILD_DONE_LIST:
							send_message(r, rule[0], SUBJECT_SUBNEWPOST_TEXT.format(sub.display_name), BODY_TEXT.format(post.permalink, post.title, post.url, post.selftext))
						done.append(post.name)
						print("found new post for rule", rule[1])

				elif rule[1] == "userinsubnewpost":
					redditor = r.get_redditor(rule[2])
					for post in redditor.get_submitted(limit=100):
						if post.subreddit.display_name.lower() != rule[3] or post.name in old_done:
							continue
						if not BUILD_DONE_LIST:
							send_message(r, rule[0], SUBJECT_USERINSUBNEWPOST_TEXT.format(post.subreddit.display_name, redditor.name), BODY_TEXT.format(post.permalink, post.title, post.url, post.selftext))
						done.append(post.name)
						print("found new post for rule", rule[1])

				elif rule[1] == "usernewcomment":
					redditor = r.get_redditor(rule[2])
					for comment in redditor.get_comments(limit=100):
						if comment.name in old_done:
							continue
						if not BUILD_DONE_LIST:
							send_message(r, rule[0], SUBJECT_USERNEWCOMMENT_TEXT.format(redditor.name), BODY_TEXT.format(comment.permalink, comment.link_title, comment.link_url, comment.body))
						done.append(comment.name)
						print("found new comment for rule", rule[1])

				elif rule[1] == "subnewcomment":
					sub = r.get_subreddit(rule[2])
					for comment in sub.get_comments(limit=100):
						if comment.name in old_done:
							continue
						if not BUILD_DONE_LIST:
							send_message(r, rule[0], SUBJECT_SUBNEWCOMMENT_TEXT.format(sub.display_name), BODY_TEXT.format(comment.permalink, comment.link_title, comment.link_url, comment.body))
						done.append(comment.name)
						print("found new comment for rule", rule[1])

				elif rule[1] == "userinsubnewcomment":
					redditor = r.get_redditor(rule[2])
					for comment in redditor.get_comments(limit=100):
						if comment.subreddit.display_name.lower() != rule[3] or comment.name in old_done:
							continue
						if not BUILD_DONE_LIST:
							send_message(r, rule[0], SUBJECT_USERINSUBNEWCOMMENT_TEXT.format(comment.subreddit.display_name, redditor.name), BODY_TEXT.format(comment.permalink, comment.link_title, comment.link_url, comment.body))
						done.append(comment.name)
						print("found new comment for rule", rule[1])

				write_config_done(done)

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
	else:
		run_bot()
