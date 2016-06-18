"""
A bot to change the header of a subreddit according a schedule
Written by /u/SmBe19
"""

import praw
import time
import OAuth2Util

# ### USER CONFIGURATION ### #

# The bot's useragent. It should contain a short description of what it does and your username. e.g. "RSS Bot by /u/SmBe19"
USERAGENT = ""

# The name of the subreddit to operate on. The bot has to be a mod there.
SUBREDDIT = ""

# ### END USER CONFIGURATION ### #

# ### BOT CONFIGURATION ### #
HEADERS_CONFIGFILE = "headers.txt"
# ### END BOT CONFIGURATION ### #


try:
	# A file containing data for global constants.
	import bot
	for k in dir(bot):
		if k.upper() in globals():
			globals()[k.upper()] = getattr(bot, k)
except ImportError:
	pass

def read_headers_config():
	headers = []
	with open(HEADERS_CONFIGFILE, "r") as f:
		for line in f:
			parts = line.split("\t")
			headers.append((int(parts[0]), parts[1].strip()))
	headers.sort()
	return headers

# main procedure
def run_bot():
	r = praw.Reddit(USERAGENT)
	o = OAuth2Util.OAuth2Util(r)
	o.refresh()
	sub = r.get_subreddit(SUBREDDIT)

	print("Start bot for subreddit", SUBREDDIT)

	while True:
		try:
			o.refresh()
			headers = read_headers_config()
			if len(headers) < 1:
				return

			next_header = headers[0]
			atime = time.localtime().tm_hour * 100 + time.localtime().tm_min
			for header in headers:
				if header[0] > atime:
					next_header = header
					break

			sleeptime = (next_header[0] % 100 - atime % 100) * 60 + (next_header[0] // 100 - atime // 100) * 3600
			if sleeptime < 0:
				sleeptime += 24*3600
			print("Now:", atime, "/ Sleep for", sleeptime, "s until", next_header[0])
			time.sleep(sleeptime)

			sub.upload_image(next_header[1], header=True)
			print("Change header")

		except KeyboardInterrupt:
			break
		except Exception as e:
			print("Exception", e)


if __name__ == "__main__":
	if not USERAGENT:
		print("missing useragent")
	elif not SUBREDDIT:
		print("missing subreddit")
	else:
		run_bot()
