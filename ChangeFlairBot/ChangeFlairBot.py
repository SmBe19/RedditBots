"""
A bot to change the flair of all posts in a subreddit
Written by /u/SmBe19
"""

import praw
import OAuth2Util

# ### USER CONFIGURATION ### #

# The bot's useragent. It should contain a short description of what it does and your username. e.g. "RSS Bot by /u/SmBe19"
USERAGENT = ""

# The name of the subreddit to operate on. The bot has to be a mod there.
SUBREDDIT = ""

# The old and new flair text and css class. Set to None to use a wildcard.
OLD_FLAIR_TEXT = "Question"
OLD_FLAIR_CSS = "question"
NEW_FLAIR_TEXT = "Question | Answered"
NEW_FLAIR_CSS = "questionan"

# Set to True if you only want to see how many posts would be altered
ONLY_TEST = False

# ### END USER CONFIGURATION ### #

try:
	# A file containing data for global constants.
	import bot
	for k in dir(bot):
		if k.upper() in globals():
			globals()[k.upper()] = getattr(bot, k)
except ImportError:
	pass

# main procedure
def run_bot():
	r = praw.Reddit(USERAGENT)
	o = OAuth2Util.OAuth2Util(r)
	o.refresh()

	sub = r.get_subreddit(SUBREDDIT)

	print("Start bot for subreddit", SUBREDDIT)
	print("Will replace flair \"{0}\" with \"{1}\"".format(OLD_FLAIR_TEXT, NEW_FLAIR_TEXT))

	try:
		last_element = None
		posts = sub.get_new(limit=100)
		found_new_post = True
		changed = 0
		active_page = 0
		while found_new_post:
			active_page += 1
			print("Search Page", active_page)
			found_new_post = False

			for post in posts:
				found_new_post = True

				if (post.link_flair_css_class == OLD_FLAIR_CSS or not OLD_FLAIR_CSS) and (post.link_flair_text == OLD_FLAIR_TEXT or not OLD_FLAIR_TEXT):
					if ONLY_TEST:
						print ("would change flair")
					else:
						print("change flair")
						post.set_flair(NEW_FLAIR_TEXT, NEW_FLAIR_CSS)

					changed += 1
				last_element = post.name
			posts = sub.get_new(limit=100, params={"after" : last_element})

		print("changed", changed, "posts")

	except KeyboardInterrupt:
		pass
	except Exception as e:
		print("Exception", e)


if __name__ == "__main__":
	if not USERAGENT:
		print("missing useragent")
	elif not SUBREDDIT:
		print("missing subreddit")
	elif not OLD_FLAIR_CSS and not OLD_FLAIR_TEXT:
		print("old flair not set")
	else:
		run_bot()
