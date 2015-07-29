# EMailNotification
Writes an email if some rule is satisfied.

You can specify as many rules as you want in the file `rules.txt`, one rule per line. For each rule, specify the parameters, separated by one tab. The following rules are available:

 - `recipient VotesInTime subreddit age score` This rule will trigger when a post in `/r/subreddit` gets `score` upvotes within `age` seconds
 - `recipient UserNewPost user` This rule will trigger when the user `/u/user` submits a new post
 - `recipient SubNewPost subreddit` This rule will trigger when a new post is submitted to `/r/subreddit`
 - `recipient UserInSubNewPost user subreddit` This rule will trigger when the user `/u/user` submits a new post to `/r/subreddit`
 - `recipient UserNewComment user` This rule will trigger when user `/u/user` submits a new comment
 - `recipient SubNewComment subreddit` This rule will trigger when a new comment is submitted to `/r/subreddit`
 - `recipient UserInSubNewComment user subreddit` This rule will trigger when the user `/u/user` submits a new post to `/r/subreddit`

As a `recipient` you can use either a reddit user in the format `/u/user` or an email address.

The rules are read after every cycle, so no need to restart the bot if you want to add / remove a rule.

To prevent your inbox from overflowing you will want to run the bot with the flag `BUILD_DONE_LIST = True` set and then after he built his list restart the bot with the flag unset.
