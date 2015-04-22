import praw
import time
import re

# ### BOT CONFIGURATION ### #
CONFIG_WIKIPAGE = "schedulebot-config"
# ### END BOT CONFIGURATION ### #

class ScheduledPost:
	def __init__(self, first, title="Scheduled Post", text="Scheduled Post", repeat=-1, sticky=False):
		self.first = first
		self.repeat = repeat
		self.sticky = sticky
		self.title = title
		self.text = text
		
	def get_time_until_next_post(self):
		diff = time.time() - self.first
		used = diff % self.repeat
		return self.repeat - used
	
	def get_next_post_time(self):
		return time.time() + get_time_until_next_post(self)
		
def read_config(sub):
	scheduled_posts = []
	config = sub.get_wiki_page(CONFIG_WIKIPAGE).content_md
	config = config.replace("\r\n", "\n")
	rules = list(filter(len, config.split("---\n")))
	if len(rules) < 1:
		return scheduled_posts
	match = re.match("^\s+", rules[0])
	if not match:
		print("Error: Could not define indentation")
		return scheduled_posts
	indentation = match.group(0)
	rules = [re.sub("^(?:{0})+".format(indentation), "\r", rule) for rule in rules]
	for rule in rules:
		lines = rule.split("\n")
		properties = {}
		last_property = ""
		for line in lines:
			level = line.count("\r")
			if level == 1:
				last_property = line.replace("\r", "").split(": ")[0].lower()
				properties[last_property] = line.replace("\r" + last_property + ": ", "")
			else
				properties[last_property] += "\n" + line.replace("\r", "")
				