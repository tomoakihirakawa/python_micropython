_black_ =  "\u001b[30m"
_red_ = "\u001b[31m"
_green_="\u001b[32m"
_yellow_="\u001b[33m"
_blue_="\u001b[34m"
_magenta_="\u001b[35m"
_cyan_="\u001b[36m"
_white_="\u001b[37m"
_default_color_="\u001b[0m"


try:
    from display.SSD1315 import *
    print(_cyan_+"display is imported"+_default_color_)
    print(_cyan_+"You can use:"+_default_color_)
    print(_cyan_+" * display.SSD1315"+_default_color_)
except:
    print(_red_+" x display.SSD1315"+_default_color_)

