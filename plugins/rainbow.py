from .util.decorators import command, initializer

colors = ['\x034', '\x037', '\x038', '\x039', '\x032', '\x036']
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
    item = ('%s' % (colors[count]))+'\u200b'+item
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


@command('rainbow')
def rainbowify(bot, nick, target, chan, arg):
    bot.msg(chan, '%s: %s' % (nick, rainbow(arg)))
