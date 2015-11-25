"""
A bot to post on a schedule but posts on a given user so it can be edited later
Written by /u/SmBe19
"""

import praw
import time
import re
import threading
import OAuth2Util
import ScheduledPost

# ### USER CONFIGURATION ### #

# The bot's useragent. It should contain a short description of what it does and your username. e.g. "RSS Bot by /u/SmBe19"
USERAGENT = ""

# The name of the subreddits to post to. e.g. "funny"
SUBREDDITS = ["", ""]

# The time in seconds the bot should sleep until it checks the inbox again.
SLEEP_INBOX = 60

# ### END USER CONFIGURATION ### #

# ### BOT CONFIGURATION ### #
DATE_RE = re.compile("\{\{date (.+?)\}\}")
# ### END BOT CONFIGURATION ### #

try:
	# A file containing infos for testing.
	import bot
	USERAGENT = bot.useragent
	SUBREDDITS = bot.subreddits
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

def repl_date(matchobj):
	return time.strftime(matchobj.group(1))

class Poster (threading.Thread):
	lock = threading.Lock()

	def __init__(self, o, subs, reschedule, weredone):
		threading.Thread.__init__(self)
		self.o = o
		self.subs = subs
		self.reschedule = reschedule
		self.weredone = weredone

	def run(self):
		while True:
			Poster.lock.acquire()
			scheduled_posts = []
			for sub in self.subs:
				scheduled_posts.extend(ScheduledPost.read_config(sub))
			Poster.lock.release()

			while True:
				try:
					Poster.lock.acquire()
					self.o.refresh()
					Poster.lock.release()

					sleep_time = float("inf")
					nextPost = None
					for p in scheduled_posts:
						if p.get_time_until_next_post() < sleep_time:
							sleep_time = p.get_time_until_next_post()
							nextPost = p
					nextPostNumber = p.get_next_post_number()
					assert nextPostNumber >= 0 or sleep_time == float("inf")
					print("sleep submission for", sleep_time, "s (", time.strftime("%d.%m.%Y %H:%M", time.localtime(nextPost.get_next_post_time())), ")")

					if sleep_time == float("inf"):
						self.reschedule.wait()
					elif not self.reschedule.wait(sleep_time):
						Poster.lock.acquire()
						titles = nextPost.title.split("\n")
						titleFormatted = titles[nextPostNumber % len(titles)]
						titleFormatted = DATE_RE.sub(repl_date, titleFormatted)
						textFormatted = nextPost.text
						if textFormatted is not None:
							textFormatted = DATE_RE.sub(repl_date, textFormatted)
						if nextPost.link is not None:
							links = nextPost.link.split("\n")
							link = links[nextPostNumber % len(links)]
							submission = nextPost.sub.submit(titleFormatted, url=link, resubmit=True)
							if textFormatted is not None and len(textFormatted) > 0:
								submission.add_comment(textFormatted)
						else:
							if textFormatted is None:
								textFormatted = "..."
							submission = nextPost.sub.submit(titleFormatted, textFormatted)
						submission.set_flair(flair_text=nextPost.flair_text, flair_css_class=nextPost.flair_css)
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
					Poster.lock.acquire(False)
					Poster.lock.release()

			if self.weredone.is_set():
				break

# main procedure
def run_bot():
	r = praw.Reddit(USERAGENT)
	o = OAuth2Util.OAuth2Util(r)
	o.refresh()
	subs = [r.get_subreddit(x) for x in SUBREDDITS]

	print("Start bot for subreddits", SUBREDDITS)

	reschedule = threading.Event()
	weredone = threading.Event()

	thread = Poster(o, subs, reschedule, weredone)
	thread.deamon = True
	thread.start()

	while True:
		try:
			o.refresh()
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
	if not USERAGENT:
		print("missing useragent")
	elif not SUBREDDITS:
		print("missing subreddits")
	else:
		run_bot()
