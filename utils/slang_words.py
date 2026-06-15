SLANG_WORDS = [
    "fuck", "shit", "bitch", "asshole", "bastard", "damn", "crap",
    "dick", "pussy", "cock", "cunt", "motherfucker", "fucker",
    "whore", "slut", "faggot", "nigger", "nigga", "retard", "idiot",
    "moron", "stupid", "dumbass", "ass", "bullshit", "hell",
    "piss", "jackass", "wanker", "tosser", "twat", "prick",
    "bloody", "bugger", "sod", "shag", "slag",

    "madarchod", "behenchod", "bhosdike", "chutiya", "gandu", "lauda",
    "lund", "gaand", "randi", "harami", "saala", "saali", "kamina",
    "haramkhor", "bhosdi", "bakrichod", "bakarchod", "bsdk",
    "mc", "bc", "lodu", "chut", "jhant", "gaandu", "madar",
    "bhenchod", "bhench", "maa ki aankh", "tere maa ki",
    "teri maa ki", "teri behen ki", "bhen ke lode", "teri bhen",
    "sala", "sali", "gadha", "gadhi", "ullu", "ullu ka pattha",
    "kutte", "kutta", "kuttiya", "harami", "haramzada", "haramzadi",

    "chodo", "chodna", "chodne", "chodna", "randi",
    "maa chod", "baap chod", "behen chod",

    "kanjoos", "gaddaar", "gandu",

    "puta", "coño", "polla", "joder", "mierda",
    "putain", "merde", "connard", "salope",
    "vaffanculo", "cazzo", "minchia",
    "ficken", "scheiße", "hurensohn",
    "ублюдок", "сука", "блядь", "хуй", "пиздец",
    "خنزير", "كلب", "عاهرة", "لعنة",

    "kill yourself", "kys", "go die", "hang yourself",
    "rape", "rapist", "pedo", "pedophile",
    "terrorist", "bomb threat", "death threat",
]

ILLEGAL_KEYWORDS = [
    "drug", "cocaine", "heroin", "methamphetamine", "meth", "weed sell",
    "buy gun", "illegal weapon", "child porn", "cp link", "onion link",
    "darkweb", "dark web", "hitman", "assassination",
    "money laundering", "fraud link", "phishing",
]

ALL_BANNED_WORDS = list(set(
    [w.lower() for w in SLANG_WORDS + ILLEGAL_KEYWORDS]
))


def contains_banned_word(text: str) -> bool:
    if not text:
        return False
    text_lower = text.lower()
    for word in ALL_BANNED_WORDS:
        if word in text_lower:
            return True
    return False
