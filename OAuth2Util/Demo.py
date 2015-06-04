import praw
import OAuth2Util

r = praw.Reddit("OAuth2Util Demo by /u/SmBe19")
o = OAuth2Util.OAuth2Util(r)

o.refresh()

print("Hi, {0}, you have {1} comment karma!".format(r.get_me().name, r.get_me().comment_karma))