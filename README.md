## James, a simple IRC bot.

**Ohai.** James is an IRC bot I originally made just for fun.
Well, it's still just for fun, but also used to get to know
more about python.

### How it works

To make James work, you need a couple of libraries.

* Tweepy (optional, only if you want to enable tweeting.)
* Oyoyo
* Standard Python 2.7 libraries (also tested on 2.6.5, works perfectly)
* BeautifulSoup
* PyYAML

**You should be** able to do without PyYAML using my modified version using a simpler config file in Python.
This will be coming shortly, if anyone wants it. (not using it myself)

#### Tweepy

**Tweepy** is the library I use for twittering with my bot. You will probably not need this, so you can disable tweeting
in the configuration file.

#### Oyoyo

Oyoyo is the IRC library for Python I use. It might not have been the right choice,
seeing as Twisted has a great library for doing this, but oh well.
Im not going to convert it, because that would take a lot of time that I do not have.
And it still does everything I want, so..

#### BeautifulSoup

A HTML parser used for getting titles of websites and such.

#### PyYAML

The parser for my configuration files, this is a very important library that you **will** have to get.
Unless you ask me to make a simpleConfig file using dicts.

### Why you should use this and not Eggdrop/Any other IRC bot

It is simple to install, yet will be able to use much of the functions you will actually use. 
<br>(botnets? telnet configs? old! insecure! I don't need them **and** don't want them!)

You can simply add in functions in Python (it's really not that hard.) instead of having to learn TCL or C and modifying (in this case) Eggdrop. The simplicity is endless!

You won't have to set 999 options in the config file, but it will work just as well for simple things like reacting on sentences, remembering factoids, saving quotes and more!

**-- Sam**
