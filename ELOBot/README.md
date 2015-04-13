# ELO Bot
A bot to keep track of users elo in game subreddits.

Usage:

 * Two user play against each other a game
 * Once they finished, one of them makes somewhere in the subreddit a comment with "!elo game /u/winner_name /u/loser_name"
 * The bot will answer with a message, asking the other player for confirmation
 * The other user replies to the original message with "!elo confirm"
 * The bot will calculate the new elo and change the flair accordingly