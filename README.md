# RedditBots
Reddit Bots by [/u/SmBe19](http://www.reddit.com/u/SmBe19)

To run any of those bots you need:
 - Python
 - PRAW (`pip install praw`)
 - OAuth2Util (`pip install praw-oauth2util`)

If the bot uses OAuth2, you have to copy the file `OAuth2Util.py` in the same folder as the script. You have to [register an app on Reddit](https://www.reddit.com/prefs/apps/), using `script` as app type and `http://127.0.0.1:65010/authorize_callback` as redirect uri. You then have to create a file called `oauthappinfo.txt` in the folder and paste the app id on the first line and the app secret on the second line.

In the source code of the bots you will find at the top the `USER CONFIGURATION` and sometimes the `BOT CONFIGURATION`. In the `USER CONFIGURATION` section you should fill out every variable as they describe detailed what and where the bot should do (e.g. User Name, Subreddit to operate in, duration of sleep). The `BOT CONFIGURATION` section defines variables that you don't really have to change, but if you really have to, they are there. They are mostly constants for the bot (e.g. Name of config files).

You can set the variables set in the `USER CONFIGURATION` / `BOT CONFIGURATION` also in a separate file called `bot.py`, just use `key = value` (e.g. `username = "SmBe19"`). This way you don't have to edit the source directly (so it's easier to update) and you can exclude this file from git. Btw. it's a normal Python file, that get's executed, so you can use code as for example `password = getpass.getpass()`.
