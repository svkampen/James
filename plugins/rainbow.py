from .util.decorators import command, initializer
from .util.data import get_doc

colors = ["%s%.2d" % (k, v) for k,v in zip(["\x03" for i in range(0,12)], map(int, "5 4 7 8 9 3 10 11 2 12 6 13".split()))]
count = 0
even = False

bad_chars = ["\n", "\t", "\r", " "]

penisbird = r"""
                    _..._
                 .-"     "-.
                /     _    _\
               /":.  (o)  /__)
              /":. .,_    |  |
             |": ; /  \   /_/
             /  ;  `"`"    }
            ; ":.,         {
           /      ;        }
          ; "::.   ;\/\ /\ {
         |.      ":. ;``"``\
        / "::"::"    /      ;
       |":::" "::"  /       |
       \   "::" _.-`;       ;
       /`-..--;` ;  |       |
      ;  ;  ;  ;  ; |       |
      ; ;  ;  ; ;  ;        /        ,--.........,
      |; ;  ;  ;  ;/       ;       ."           -=".
      | ;  ;  ; ; /       /       .\               "
      |  ;   ;  /`      .\   _,=="  \             ."
      \;  ; ; .". _  ,_"\.\~"   //`. \          ."
      |  ;  .___~" \ \- | |    /,\ `  \      .."
    ~ ; ; ;/  ==''' |`| | |       =='''\.==''
    ~ /; ;/=""      |`| |`|   ==="`
    ~..==`     \\   |`| / /=="`
     ~` ~      /,\ / /= )")
    ~ ~~         _")")  
    ~ ~   _,=~";`
    ~  =~"|;  ;|       Penisbird
     ~  ~ | ;  |       =========
  ~ ~     |;|\ |
          |/  \|
"""

@initializer
def init_plugin(bot):
    global penisbird
    bot.state.data["penisbird"] = penisbird

def rainbow_char(item):
    global count
    global colors
    global bad_chars
    global even
    if count == len(colors):
        count = 0
    if item in bad_chars:
        if even:
            count += 1
        even = not even
        return item
    item = ("%s" % (colors[count]))+item
    if even:
      count += 1
    even = not even
    return item


def rainbow(arg):
    global count
    output = []
    for i in arg:
        output.append(rainbow_char(i))
    output = "".join(output)
    count = 0
    return output


@command("rainbow", category="misc")
def rainbowify(bot, nick, chan, arg):
    """ rainbow *args -> Rainbowify *args. """
    if not arg:
      return bot.msg(chan, get_doc())
    bot.msg(chan, "%s" % (rainbow(arg)))
