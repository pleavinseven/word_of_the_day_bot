# WWOTD
Reddit bot posting a **Welsh Word of the Day** with English translation, a short description and word class/lexical category, daily at 10.30am UTC to [r/learnwelsh.](https://www.reddit.com/r/learnwelsh/) 

The idea of this bot is to help people learn the Welsh language one word at a time.

## Usage
The bot is written entirely in python3 and ran through the Heroku server.

To use the bot for other subreddits you will need to create a new reddit account and change a few small details:

On the [reddit apps page](https://www.reddit.com/prefs/apps) at the bottom click create app and fill in the details under 'script' to obtain a client id (underneath 'personal use script') and a secret to be written into the script under 'client_id' and 'client_secret' respectively.

All passwords and client variables are stored as `config` (environmental) variables in Heroku.

## Issues
If you have found any bugs make sure to first check if they haven't already been reported and, if not, feel free to note them down in [issues](https://github.com/pleavinseven/WWOTD/issues).

## Contribute
If you have any ideas for new features or improvements feel free to note them down in [pull requests](https://github.com/pleavinseven/WWOTD/pulls).

##Contact
Contact me with any questions via email at `pleavinseven@gmail.com`.