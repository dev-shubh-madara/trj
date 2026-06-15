_RI = {
    'a':'🇦','b':'🇧','c':'🇨','d':'🇩','e':'🇪','f':'🇫','g':'🇬','h':'🇭',
    'i':'🇮','j':'🇯','k':'🇰','l':'🇱','m':'🇲','n':'🇳','o':'🇴','p':'🇵',
    'q':'🇶','r':'🇷','s':'🇸','t':'🇹','u':'🇺','v':'🇻','w':'🇼','x':'🇽',
    'y':'🇾','z':'🇿',
}
_ZW = '\u200c'


def frak(text: str) -> str:
    out = []
    prev_ri = False
    for ch in text:
        lo = ch.lower()
        if lo in _RI:
            if prev_ri:
                out.append(_ZW)
            out.append(_RI[lo])
            prev_ri = True
        else:
            prev_ri = False
            out.append(ch)
    return ''.join(out)


ri = frak
