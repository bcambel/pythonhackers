# coding=utf-8
import htmlentitydefs
import anyjson
import unicodedata as ud


def leaner_url(s):
    """
    Highly refactoring necessary!
    """
    if s is None or len(s) <= 0:
        return "_"
    s2 = s.replace('http://', '').replace("'", '').replace(u'’', '').replace(' ', '-').replace('www.', ''). \
        replace('?', '').replace('&amp;', '-').replace(';', ''). \
        replace('/', '-').replace('=', '-').replace("#", "").replace(",", '').replace('"', '').replace('&', '').replace(
        "%", '')
    if s2[-1] == '-':
        s2 = s2[0:-1]
    return s2.replace('--', '-')


def safe_str(my_str):
    if my_str is not None:
        if isinstance(my_str, basestring):
            try:
                return my_str.encode('ascii', errors='ignore')
            except:
                return my_str
        else:
            return "%s" % my_str
    else:
        return "None"


def safe_filename(filename):
    return "".join([c for c in filename if c.isalpha() or c.isdigit() or c == ' ']).rstrip()


def safe_obj_str(my_obj):
    return anyjson.serialize(my_obj)


def max_length_field(instance, name, length):
    if hasattr(instance, name):
        original_val = getattr(instance, name)
        if original_val is not None and len(original_val) > length:
            cut_val = original_val[:length]
            setattr(instance, name, cut_val)
            return cut_val
        else:
            return original_val
    return None


def max_length_field2(instance, name, length):
    if hasattr(instance, name):
        original_val = getattr(instance, name)

        if original_val is not None and len(original_val) > length:
            cut_val = original_val[:length]
            setattr(instance, name, cut_val)
            original_field = "original_%s" % name
            if hasattr(instance, original_field):
                setattr(instance, original_field, original_val)


def non_empty_str(str):
    return str is not None and len(str) > 0


def explain_string(str):
    for ch in str:
        charname = ud.name(ch)
        print "%d U%04x %s " % (ord(ch), ord(ch), charname )


def normalize_str(str):
    new_str = []
    for ch in str:

        ordinal = ord(ch)
        if ordinal < 128:
            new_str.append(ch)
        else:
            new_str.append(u'\\u%04x' % ordinal)

    return u''.join(new_str)


def uescape(text):
    escaped_chars = []
    for c in text:
        if (ord(c) < 32) or (ord(c) > 126):
            c = '&{};'.format(htmlentitydefs.codepoint2name[ord(c)])
        escaped_chars.append(c)
    return ''.join(escaped_chars)


if __name__ == '__main__':
    class Test:
        def __init__(self):
            self.name = ''
            self.__surname = ''

        @property
        def surname(self):
            return self.__surname

        @surname.setter
        def surname(self, val):
            self.__surname = val

    test = Test()

    test_name = "1000000000000"
    test.name = test_name
    test.surname = 'cambel'

    max_length_field2(test, 'name', 4)
    max_length_field2(test, 'surname', 2)

    assert hasattr(test, '_original_name')
    print "%s - %s" % (test_name, test._original_name)

    assert test._original_name == test_name
    assert test.name == "1000"

    assert hasattr(test, '_original_surname')
    assert test._original_surname == "cambel"
    assert test.surname == "ca"

    def printer(x):
        print x

    print "{0}{1}{0}".format(("=" * 10), "Keys")
    map(printer, test.__dict__.iterkeys())
    print "{0}{1}{0}".format(("=" * 10), "Keys Values")
    map(printer, test.__dict__.iteritems())