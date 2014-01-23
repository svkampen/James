## James, a modular IRC bot

**Hello**. James is a modular IRC bot created by **svkampen et aliī**.
It has been in development for roughly two years.

### Requirements
James requires the following libraries:

* Requests (`pip install requests`)
* BeautifulSoup 4 (`pip install beautifulsoup4`)

James also requires Python version 3.2 or higher.

### Starting and using James
Create a config file with `makeconfig.py`, then start the bot with `python3 bot.py`.

To get a list of commands, use the `help` command. If a command requires arguments,
and you do not supply them, the command will print its help. If you are an admin, you
are able to access James' internals by using either:

* the `eval` command, or
* using the `>>>` shortcut.
