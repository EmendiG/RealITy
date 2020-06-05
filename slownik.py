class Slownik(object):
    reguly = {
        u'ę': u'e',
        u'ó': u'o',
        u'ą': u'a',
        u'ś': u's',
        u'ł': u'l',
        u'ż': u'z',
        u'ź': u'z',
        u'ć': u'c',
        u'ń': u'n',
        u'Ę': u'E',
        u'Ó': u'O',
        u'Ą': u'A',
        u'Ś': u'S',
        u'Ł': u'L',
        u'Ż': u'Z',
        u'Ź': u'Z',
        u'Ć': u'C',
        u'Ń': u'N',
    }

    def kodowanie(self, do_zmiany):
        wynik = []

        for znak in do_zmiany:
            wynik.append(self.reguly.get(znak, znak))

        return ''.join(wynik)

