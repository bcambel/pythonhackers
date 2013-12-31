from os import listdir
from os.path import join, isfile

rules = [(10 ** 9, 'B'), (10 ** 6, 'M'), (10 ** 3, 'K')]


def nice_number(n):
    numeric = n
    abbreviation = ""

    for number, abbr in rules:
        if n > number:
            abbreviation = abbr
            ident = (n * 10 / number) / 10.0
            break

    ident_int = int(numeric)
    if numeric - ident_int == 0:
        numeric = ident_int

    return u"{}{}".format(numeric, abbreviation)


def files_in(directory):
    for f in listdir(directory):
        if isfile(join(directory, f)):
            yield join(directory, f)
    return

if __name__ == "__main__":

    def tests():
        assert "10K" == nice_number(10020)
        assert "102" == nice_number(102)
        assert "1M" == nice_number(1002000)
        assert "1.1B" == nice_number(1102000000)

    tests()