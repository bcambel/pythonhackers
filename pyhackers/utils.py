
thousand = 10**3
million = 10**6


def nice_number(n):
    ident = n
    abbr = ""
    if n > million:
        abbr = "M"
        ident = (n*10/million)/10.0

    elif n > thousand:
        abbr = "K"
        ident = (n*10/thousand)/10.0


    ident_int = int(ident)
    if ident - ident_int == 0:
        ident = ident_int

    return u"{ident}{abbr}".format(**vars())