__module_name__ = 'RUINScripts - RUINBot'
__module_version__ = '1.01' 
__module_description__ = 'RUIN Scripts for xChat =)'

#All Message Scripts (w00t?)

def message_scripts(word, word_eol, userdata):
    message=word[1]
    user=word[0]
    cmdmsg = re.compile("@cmds")
    statusmsg = re.compile("@status")
    soupmsg = re.compile("@soup")
    vibrmsg = re.compile("@vibrate")
    ticklemsg = re.compile("@tickle")
    aboutmsg = re.compile("@about")
    suicidemsg = re.compile("@suicide")
    noodlemsg = re.compile("@noodles")
    guestmsg = re.compile("@guest")
    resurrectmsg = re.compile("@resurrect")
    stayinmsg = re.compile("@haha")
    sayhimsg = re.compile("@hi")
    vipmsg = re.compile("@site")

    #COMMANDS!

    
    if vipmsg.search(message) != None:
        xchat.command("say Site: http://ruincommunity.net!")
    
    if cmdmsg.search(message) != None:
        xchat.command("say Commands: [@status], [@soup], [@vibrate], [@suicide], [@about], [@tickle], [@noodles], [@guest], [@resurrect], [@haha], [@site]")
    
    if statusmsg.search(message) != None:
        xchat.command("say Status: Online")
    
    if noodlemsg.search(message) != None:
        xchat.command("me gives " + user + " ramen noodles.")
    
    if soupmsg.search(message) != None:
        xchat.command("me gives " + user + " some chicken soup. Hmm, tasty!")
    
    if vibrmsg.search(message) != None:
        xchat.command("me vibrates heavily!")
    
    if ticklemsg.search(message) != None:
        xchat.command("me tickles " + user + " until they cum =P")
    
    if aboutmsg.search(message) != None:
        xchat.command("say Most of the commands stolen from Caboodle. by svkampen. Free to look at code but it sucks, LOL.")
    
    if suicidemsg.search(message) != None:
        xchat.command("me jumps off a cliff and grabs " + user + " whilst falling. They both die =3")
        xchat.command("nick RUINBot[DEAD]")
    
    if resurrectmsg.search(message) != None:
        xchat.command("me resurrects himself...")
        xchat.command("nick RUINBot")
    
    if guestmsg.search(message) != None:
        xchat.command("say Welcome to RUIN! Please read the signs at spawn to be promoted!")
    
    if stayinmsg.search(message) != None:
        xchat.command("say Ha. Ha. Ha. Ha. Stayin' Alive!")
    
    if sayhimsg.search(message) != None:
        xchat.command("say Hi!")

import xchat
import re

xchat.hook_print("Channel Message", message_scripts)
xchat.prnt("Script Loaded!")
