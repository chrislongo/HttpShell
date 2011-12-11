class Color(object):
    GREY = 30
    RED = 31
    GREEN = 32
    YELLOW = 33
    BLUE = 34
    MAGENTA = 35
    CYAN = 36
    WHITE = 37


class Attribute(object):
    NORMAL = 0
    BRIGHT = 1


def colorize(text, color, attribute=Attribute.NORMAL):
    escape = "\033["
    reset = escape + "0m"

    return "{0}{1};{2}m{3}{4}".format(
        escape,
        attribute,
        color,
        text,
        reset)
