colors = ["grey", "red", "green", "yellow", "blue", "magenta", "cyan", "white"]
attribs = ["normal", "bright"]

escape = "\033["
reset = escape + "0m"


def colorize(text, color, attrib="normal"):
    result = None

    try:
        color_code = 30 + colors.index(color)
        attrib_code = attribs.index(attrib)

        result = "{0}{1};{2}m{3}{4}".format(
            escape,
            attrib_code,
            color_code,
            text,
            reset)
    except ValueError:
        result = text

    return result


def test():
    for color in colors:

        code = color.lower()

        print colorize(color + "\t", code),
        print colorize(color, code, "bright")
