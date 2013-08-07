from .util.decorators import command, initializer

colors = ['\x0304', '\x0307', '\x0308', '\x0309', '\x0302', '\x0306']
count = 0

bad_chars = ['\n', '\t', '\r', ' ']

penisbird = r"""
                    _..._
                 .-'     '-.
                /     _    _\
               /':.  (o)  /__)
              /':. .,_    |  |
             |': ; /  \   /_/
             /  ;  `"`"    }
            ; ':.,         {
           /      ;        }
          ; '::.   ;\/\ /\ {
         |.      ':. ;``"``\
        / '::'::'    /      ;
       |':::' '::'  /       |
       \   '::' _.-`;       ;
       /`-..--;` ;  |       |
      ;  ;  ;  ;  ; |       |
      ; ;  ;  ; ;  ;        /        ,--.........,
      |; ;  ;  ;  ;/       ;       .'           -='.
      | ;  ;  ; ; /       /       .\               '
      |  ;   ;  /`      .\   _,=="  \             .'
      \;  ; ; .'. _  ,_'\.\~"   //`. \          .'
      |  ;  .___~' \ \- | |    /,\ `  \      ..'
    ~ ; ; ;/  =="'' |`| | |       =="''\.==''
    ~ /; ;/=""      |`| |`|   ==="`
    ~..==`     \\   |`| / /=="`
     ~` ~      /,\ / /= )")
    ~ ~~         _')")  
    ~ ~   _,=~";`
    ~  =~"|;  ;|       Penisbird
     ~  ~ | ;  |       =========
  ~ ~     |;|\ |
          |/  \|
"""

@initializer
def init_plugin(bot):
    global penisbird
    bot.state.data['penisbird'] = penisbird

def rainbow_char(item):
    global count
    global colors
    global bad_chars
    if count == len(colors):
        count = 0
    if item in bad_chars:
        return item
    item = ('%s' % (colors[count]))+item
    count += 1
    return item


def rainbow(arg):
    global count
    output = []
    for i in arg:
        output.append(rainbow_char(i))
    output = ''.join(output)
    count = 0
    return output


@command('rainbow', category='misc')
def rainbowify(bot, nick, chan, arg):
    """ Rainbowify anything. """
    bot.msg(chan, '%s: %s' % (nick, rainbow(arg)))
