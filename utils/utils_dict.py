# Retourne un dictionnaire flattened à partir d'un nested dictionnaire
def flattened_dict(dict_to_traverse, prechain="", delimiter="."):
    res = {}
    pc = [prechain] if len(prechain) else []
    for k, v in dict_to_traverse.items():
        if isinstance(v, dict):
            res = {**res, **flattened_dict(v, prechain=delimiter.join(pc + [k]))}
        else:
            res[delimiter.join(pc + [k])] = v
    return res


# Retourne un nested dictionnaireà partir d'un dictionnaire flattened
def unflattened_dict(dict_to_traverse, delimiter="."):
    res = {}
    for k, v in dict_to_traverse.items():
        chemin = k.split(delimiter)
        cur = res
        for i in chemin[:-1]:
            if i not in cur:
                cur[i] = {}
            cur = cur[i]
        cur[chemin[-1]] = v
    return res


def translate_dict(dict_to_translate, table_transcription, leave_not_found=True):
    flattened_dict_pretranslation = flattened_dict(dict_to_translate)
    flattened_dict_posttranslation = {}
    for k, v in flattened_dict_pretranslation.items():
        new_key = None
        if k in table_transcription:
            new_key = table_transcription[k]
        else:
            if leave_not_found:
                new_key = k
        if new_key is not None:
            flattened_dict_posttranslation[new_key] = v
    return unflattened_dict(flattened_dict_posttranslation)
