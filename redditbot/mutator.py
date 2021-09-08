def soft(word):
    soft_dict = {
        "B": "F", "Ch": "Ch", "C": "G", "Dd": "Dd", "D": "Dd", "G": "",
        "Ll": "L", "Ph": "Ph", "P": "B", "M": "F", "Rh": "R", "Th": "Th", "T": "D"}
    for mutation in soft_dict:
        if word.startswith(mutation):
            if mutation != "G":
                mutated_word = soft_dict[mutation] + word[(len(mutation)):]
                return mutated_word
            elif mutation == "G":
                if word in ["Golff", "Gêm"]:
                    return word
                else:
                    mutated_word = word[1:]
                    return mutated_word
    return word


def nasal(word):
    nasal_dict = {"B": "M", "Ch": "Ch", "C": "Ngh", "Dd": "Dd", "D": "N", "G": "Ng",
                  "P": "Mh", "Th": "Th", "T": "Nh"
                  }
    for mutation in nasal_dict:
        if word.startswith(mutation):
            mutated_word = nasal_dict[mutation] + word[(len(mutation)):]
            return mutated_word
    return word


def aspirate(word):
    aspirate_dict = {"Ch": "Ch", "C": "Ch", "Ph": "Ph", "P": "Ph", "Th": "Th", "T": "Th"}
    for mutation in aspirate_dict:
        if word.startswith(mutation):
            mutated_word = aspirate_dict[mutation] + word[(len(mutation)):]
            return mutated_word
    return word


def h_proth(word):
    mutable_letters = {"A", "E", "I", "O", "W", "Y"}
    do_not_mutate_list = {"A", "Ar", "I", "O", "W", "Y", "Yn"}
    if len(word.split()) == 1:
        if word not in do_not_mutate_list:
            if word[0] in mutable_letters:
                mutated_word = "H" + word
                return mutated_word
    return word
