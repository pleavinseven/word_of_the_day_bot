def soft(word):
    soft_dict = {
        "b": "f", "ch": "ch", "c": "g", "dd": "dd", "d": "dd", "g": "",
        "ll": "l", "ph": "ph", "p": "b", "m": "f", "rh": "r", "th": "th","t": "d"}
    for mutation in soft_dict:
        if word.startswith(mutation):
            if mutation != "g":
                mutated_word = soft_dict[mutation] + word[(len(mutation)):]
                return mutated_word
            elif mutation == "g":
                if word in ["golff", "gêm"]:
                    return word
                else:
                    mutated_word = word[1:]
                    return mutated_word
    return word


def nasal(word):
    nasal_dict = {"b": "m", "ch": "ch", "c": "ngh", "dd": "dd", "d": "n", "g": "ng",
                  "p": "mh", "th": "th", "t": "nh"
                  }
    for mutation in nasal_dict:
        if word.startswith(mutation):
            mutated_word = nasal_dict[mutation] + word[(len(mutation)):]
            return mutated_word
    return word


def aspirate(word):
    aspirate_dict = {"ch": "ch", "c": "ch", "ph": "ph", "p": "ph", "th": "th", "t": "th"}
    for mutation in aspirate_dict:
        if word.startswith(mutation):
            mutated_word = aspirate_dict[mutation] + word[(len(mutation)):]
            return mutated_word
    return word


def h_proth(word):
    mutable_letters = {"a", "e", "i", "o", "w", "y"}
    do_not_mutate_list = {"a", "ar", "i", "o", "w", "y", "yn"}
    if word not in do_not_mutate_list:
        if word[0] in mutable_letters:
            mutated_word = "h" + word
            return mutated_word
    return word
