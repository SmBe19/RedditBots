# Forward Organgered
A bot to forward orangereds from one account to another account.

To configure the accounts to check, use the file accounts.txt, one account per line. The file is read after every cycle, so no need to restart the bot.

For every account: username password forward_to_account reset_orangered active (with one tab between values)

 * username: the username of the account to check
 * password: the password to this account
 * forward_to_account: the account to send a message with a summary
 * reset_orangered: If reset_orangered is set, all forwarded messages will be marked as read.
 * active: If active is set to False, the account is ignored