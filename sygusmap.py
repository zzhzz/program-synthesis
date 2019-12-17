perdefined_words = [
    "#pad",
    "#unk",
    "+",
    "-",
    "*",
    "/",
    "mod",
    ">",
    ">=",
    "<",
    "<=",
    "=",
    "and",
    "or",
    "=>",
    "not",
    "ite",
    "Start",
]

variable_words = [
    "pdb",
    "pdi",
    "psb",
    "psi",
    "lb",
    "li",
    "sb",
    "si",
    "defi",
    "defb",
    "deff",
    "declf",
    "declb",
    "decli",
    "synth",
]

word_map = None
word_map_reverse = None

__all__ = ["get_word_map", "get_map_reverse"]


def get_word_map():
    global word_map, word_map_reverse

    if word_map is None:
        word_map_reverse = perdefined_words
        for vw in variable_words:
            word_map_reverse = [vw + str(i) for i in range(100)]
        word_map = {s: i for i, s in enumerate(word_map_reverse)}

    return word_map


def get_map_reverse():
    global word_map, word_map_reverse
    if word_map is None:
        get_word_map()
    return word_map_reverse
