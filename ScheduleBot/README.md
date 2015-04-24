# Schedule Bot
A Bot that can post on a schedule. It will, other than AutoMod, post under a specified account such that the comment can be edited.

##Usage
Create a wiki page named "schedulebot-config". Here you can add rules, very similar to the ones AutoMod uses.
To update the schedule, edit the wiki page and then send the bot a PM with only "Schedule" as content.

For each scheduled post create a rule. Rules are separated by exactly three hypens on a single line (---). For each variable, write variableName: Value. Indent the lines with spaces, always the same number of spaces per level.

There are four variables you should define:

 * **First**: The date and time you want the post to be submitted for the first time. The format is "dd.mm.yyyy hh:mm". If you like you can also specify your timezone eg. as +0200 (difference to UTC). For example: "First: 24.04.2015 22:10" or "First: 24.04.2015 22:10 +0800"
 * **repeat**: How long the timespan is between two posts. Specify a number and a unit of time(seconds, minutes, hours, days, weeks, months, years). If repeat is not specified or there is no unit of time, the post will only posted once. E.g. "repeat: 2 hours". Note: 1 months = 30 days, 1 years = 365 days.
 * *title*: The title of the post.
 * **text**: The text of the post. If you would like to specify a multiline comment, write on the first line "text: |" and then write the text on the following lines, one level more indented than the rest of the variables.
 
Optionally you can define the following variables:
 * **distinguish**: Whether the post should be distinguished (true or false). Defaults to false
 * **sticky**: Whether the post should be made sticky (true or false). Defaults to false
 * **contest_mode**: Whether to turn contest mode on for the post (true or false). Defaults to false
 
##Example

	---
		First: 24.4.2015 21:10
		Repeat: 5 months
		Sticky: false
		Distinguish: true
		Contest_mode: false
		Title: TestPost
		Text: |
			This is a test post
			
			It is multiline
	---
		First: 24.4.2015 21:12
		Repeat: 5 weeks
		Sticky: false
		Distinguish: true
		Contest_mode: false
		Title: TestPost
		Text: |
			This is a second test post
			
			It is also *multiline*
			
