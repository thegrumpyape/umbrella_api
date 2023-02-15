from typing import Dict


def kwargs2dict(**kwargs):
    new_dict = {}
    for key, value in kwargs.items():
        if value is not None:
            new_dict[key] = value
    return new_dict


def dict2obj(raw: Dict, top: object = None):
    if top is None:
        top = type("PropertyHolder", (object,), raw)

    seqs = tuple, list, set, frozenset
    for i, j in raw.items():
        if isinstance(j, dict):
            setattr(top, i, dict2obj(j))
        elif isinstance(j, seqs):
            seq_list = []
            for seq_elem in j:
                if isinstance(seq_elem, dict):
                    seq_list.append(dict2obj(seq_elem))
                else:
                    seq_list.append(seq_elem)
            setattr(top, i, seq_list)
        else:
            setattr(top, i, j)
    return top
