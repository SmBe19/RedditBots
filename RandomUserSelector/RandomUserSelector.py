# -*- coding: utf-8 -*-

"""
A script that selects random users and add them as approved submitters
Written by /u/SmBe19
"""

import praw
import random
import time
import OAuth2Util

# ### USER CONFIGURATION ### #

# The bot's useragent. It should contain a short description of what it does and your username. e.g. "RSS Bot by /u/SmBe19"
USERAGENT = ""

# The name of the subreddit to post to. e.g. "funny"
SUBREDDIT = ""

# Number of users to select
USERS_COUNT = 10

# Number of comments from which the users are selected (max is 1000)
SAMPLE_SIZE = 1000

# Whether to check whether the selected user is already a contributor (does not work atm)
CHECK_CONTRIBUTOR = False

# Whether to add the selected users as approved submitters.
# Note that that running the script with this flag set to True is considered spam.
ADD_CONTRIBUTOR = False

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
	if CHECK_CONTRIBUTOR or ADD_CONTRIBUTOR:
		o = OAuth2Util.OAuth2Util(r)
		o.refresh()
	sub = r.get_subreddit(SUBREDDIT)

	print("Start bot for subreddit", SUBREDDIT)
	print("Select", USERS_COUNT, "users from", SAMPLE_SIZE, "comments")

	sub = r.get_subreddit(SUBREDDIT)
	if CHECK_CONTRIBUTOR:
		contributors = list(sub.get_contributors())
	comments = list(r.get_comments("all", limit=SAMPLE_SIZE))
	added_users = []

	for i in range(USERS_COUNT):
		user = random.choice(comments).author
		while (CHECK_CONTRIBUTOR and user in contributors) or user in added_users:
			user = random.choice(comments).author
		added_users.append(user)

		print(user.name)

		if ADD_CONTRIBUTOR:
			sub.add_contributor(user)

if __name__ == "__main__":
	if not USERAGENT:
		print("missing useragent")
	elif not SUBREDDIT:
		print("missing subreddit")
	else:
		run_bot()
