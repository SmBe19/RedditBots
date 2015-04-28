# Header Change Bot
A Bot to change the header of a subreddit according a schedule.

The schedule is located in the file `headers.txt`, one image per line. For each line specify the time in the format `hhmm` (e.g. `1642` would be 16:42) and the name of the image (e.g. `header1.jpg`), seperated by one tab.

The schedule file is reread after every header change, so no need to restart the bot if the schedule changes (only if there is a scheduled change before the one the bot is at the moment waiting for).