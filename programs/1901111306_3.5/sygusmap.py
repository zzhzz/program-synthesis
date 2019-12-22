import numpy as np

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
    "true",
    "false",
    "(",
    ")"
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

__all__ = ["get_word_map", "get_map_reverse", "apply_to_list"]


def get_word_map():
    global word_map, word_map_reverse

    if word_map is None:
        word_map_reverse = perdefined_words
        word_map_reverse = (
            word_map_reverse
            + list(map(str, range(-20, 20, 1)))
            + list(map(str, range(-100, -20, 10)))
            + list(map(str, range(20, 110, 10)))
        )
        for vw in variable_words:
            word_map_reverse = word_map_reverse + [vw + str(i) for i in range(100)]
        word_map = {s: i for i, s in enumerate(word_map_reverse)}

    return word_map


def get_map_reverse():
    global word_map, word_map_reverse
    if word_map is None:
        get_word_map()
    return word_map_reverse


def apply_to_list(l):
    # print(l)
    result = np.empty([len(l)], dtype=np.int32)
    m = get_word_map()
    for i, a in enumerate(l):
        result[i] = m[a]
    return result

if __name__ == "__main__":
    print(len(get_word_map()))