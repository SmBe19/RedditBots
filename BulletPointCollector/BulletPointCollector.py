"""
A bot that collects all bullet points of a thread.
Written by /u/SmBe19
"""

import praw
import re
import sys
import time

# ### USER CONFIGURATION ### #

# The bot's useragent. It should contain a short description of what it does and your username. e.g. "RSS Bot by /u/SmBe19"
USERAGENT = ""

# The time in seconds the bot should sleep until it checks again.
SLEEP = 60*60

# ### END USER CONFIGURATION ### #

# ### BOT CONFIGURATION ### #
LIST_OUTPUTFILE = "list.txt"

LIST_RE = re.compile(r"^( *)[-+*] (.*?)$")
LIST_LINESTART_RE = re.compile(r"^( *)([-+*])( +)")
# ### END BOT CONFIGURATION ### #

try:
	# A file containing infos for testing.
	import bot
	USERAGENT = bot.useragent
except ImportError:
	pass
	
def collect_points(url):
	r = praw.Reddit(USERAGENT)
	
	thread = r.get_submission(url=url)
	
	if thread is None:
		print("Thread not found")
		return
	
	comments = praw.helpers.flatten_tree(thread.comments)
	
	result = []
	
	for comment in comments:
		isInList = False
		wasEmpty = True
		for line in comment.body.splitlines():
			if wasEmpty:
				isInList = LIST_RE.match(line)
			wasEmpty = line == ""
			if not wasEmpty and isInList:
				result.append(LIST_LINESTART_RE.sub(r"\1* ", line))
				
	with open(LIST_OUTPUTFILE, "w") as f:
		f.write("\n".join(result))
	
	
if __name__ == "__main__":
	if not USERAGENT:
		print("missing useragent")
	elif len(sys.argv) < 2:
		print("usage: python", sys.argv[0], "url [outputfile]")
	else:
		if len(sys.argv) > 2:
			LIST_OUTPUTFILE = sys.argv[2]
		collect_points(sys.argv[1])