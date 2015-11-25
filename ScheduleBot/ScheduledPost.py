import praw
import time
import re

# ### BOT CONFIGURATION ### #
CONFIG_WIKIPAGE = "schedulebot-config"
# ### END BOT CONFIGURATION ### #

class ScheduledPost:
	def __init__(self, sub, first, title="Scheduled Post", text=None, link=None, repeat="-1", times="-1", flair_text="", flair_css="", distinguish="False", sticky="False", contest_mode="False"):
		self.sub = sub
		self.first = first
		self.title = title
		self.text = text
		self.link = link
		self.repeat = repeat
		self.times = int(times)
		self.flair_text = flair_text
		self.flair_css = flair_css
		self.distinguish = distinguish.lower() == "true"
		self.sticky = sticky.lower() == "true"
		self.contest_mode = contest_mode.lower() == "true"

		try:
			self.first = time.mktime(time.strptime(self.first, "%d.%m.%Y %H:%M %z"))
		except ValueError:
			self.first = time.mktime(time.strptime(self.first, "%d.%m.%Y %H:%M"))

		num = int(repeat.split(" ")[0])
		unit = repeat.split(" ")[-1].lower()
		if unit == "years":
			num *= 365*24*60*60
		elif unit == "months":
			num *= 30*24*60*60
		elif unit == "weeks":
			num *= 7*24*60*60
		elif unit == "days":
			num *= 24*60*60
		elif unit == "hours":
			num *= 60*60
		elif unit == "minutes":
			num *= 60
		elif unit == "seconds":
			num *= 1
		else:
			num = -1

		if num == 0:
			num = 1

		self.repeat = num

	def get_time_until_next_post(self):
		diff = time.time() - self.first
		if diff < 0:
			return -diff
		if self.repeat < 0:
			return float("inf")
		if self.times > 0:
			if diff // self.repeat >= self.times:
				return float("inf")
		used = diff % self.repeat
		return self.repeat - used

	def get_next_post_number(self):
		diff = time.time() - self.first
		if diff < 0:
			return 0
		if self.repeat < 0:
			return -1
		return int(diff // self.repeat) + 1

	def get_next_post_time(self):
		return time.time() + self.get_time_until_next_post()

def repl_indentation(matchobj):
	return "\r" * matchobj.group(0).count(matchobj.group(1))

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
	for rule in rules:
		lines = [re.sub("^({0})+".format(indentation), repl_indentation, line) for line in rule.split("\n")]
		properties = {}
		last_property = ""
		for line in lines:
			level = line.count("\r")
			if level == 1:
				last_property = line.replace("\r", "").split(": ")[0].strip().lower()
				properties[last_property] = line.replace("\r", "")[len(last_property) + 2:].strip()
			else:
				properties[last_property] += "\n" + line.replace("\r", "").strip()

		for key in properties:
			if properties[key].startswith("|\n"):
				properties[key] = properties[key][2:]
			# print(key, ":", properties[key])
		try:
			scheduled_posts.append(ScheduledPost(sub, **properties))
		except TypeError:
			print("Rule for post with title", properties["title"], "is not correct!")

	return scheduled_posts
