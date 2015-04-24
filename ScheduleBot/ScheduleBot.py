"""
A bot to post on a schedule but posts on a given user so it can be edited later
Written by /u/SmBe19
"""

import praw
import time
from getpass import getpass
import threading
import ScheduledPost

# ### USER CONFIGURATION ### #

# The bot's username.
USERNAME = ""

# The bot's password.
PASSWORD = ""

# The bot's useragent. It should contain a short description of what it does and your username. e.g. "RSS Bot by /u/SmBe19"
USERAGENT = ""

# The name of the subreddit to post to. e.g. "funny"
SUBREDDIT = ""

# The time in seconds the bot should sleep until it checks the inbox again.
SLEEP_INBOX = 60

# ### END USER CONFIGURATION ### #

try:
	# A file containing credentials used for testing. So my credentials don't get commited.
	import bot
	USERNAME = bot.username
	PASSWORD = bot.password
	USERAGENT = bot.useragent
	SUBREDDIT = bot.subreddit
except ImportError:
	pass
	
def check_inbox(r, reschedule):
	Poster.lock.acquire()
	for mail in r.get_unread():
		if not mail.was_comment:
			if mail.body.strip().lower() == "schedule":
				mail.mark_as_read()
				reschedule.set()
				print("reschedule")
	Poster.lock.release()
				

class Poster (threading.Thread):
	lock = threading.Lock()
	
	def __init__(self, sub, reschedule, weredone):
		threading.Thread.__init__(self)
		self.sub = sub
		self.reschedule = reschedule
		self.weredone = weredone
	
	def run(self):
		while True:
			scheduled_posts = ScheduledPost.read_config(self.sub)
			
			while True:
				try:
					sleep_time = float("inf")
					nextPost = None
					for p in scheduled_posts:
						if p.get_time_until_next_post() < sleep_time:
							sleep_time = p.get_time_until_next_post()
							nextPost = p
					print("sleep submission for", sleep_time, "s")
					if not self.reschedule.wait(sleep_time):
						Poster.lock.acquire()
						submission = self.sub.submit(nextPost.title, text=nextPost.text)
						if nextPost.distinguish:
							submission.distinguish()
						if nextPost.sticky:
							submission.sticky()
						if nextPost.contest_mode:
							submission.set_contest_mode(nextPost.contest_mode)
						print("submitted")
						Poster.lock.release()
					
					if self.reschedule.is_set():
						self.reschedule.clear()
						break
						
				# Allows the bot to exit on ^C, all other exceptions are ignored
				except KeyboardInterrupt:
					print("We're almost done")
					break
				except Exception as e:
					print("Exception", e)
					import traceback
					traceback.print_exc()
			
			if self.weredone.is_set():
				break
	
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
	
	reschedule = threading.Event()
	weredone = threading.Event()
	
	thread = Poster(sub, reschedule, weredone)
	thread.deamon = True
	thread.start()
	
	while True:
		try:
			check_inbox(r, reschedule)
		
			print("sleep inbox for", SLEEP_INBOX, "s")
			time.sleep(SLEEP_INBOX)
		# Allows the bot to exit on ^C, all other exceptions are ignored
		except KeyboardInterrupt:
			print("We're almost done")
			break
		except Exception as e:
			print("Exception", e)
			import traceback
			traceback.print_exc()
		
	weredone.set()
	reschedule.set()
	print("We're done")
	
	
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