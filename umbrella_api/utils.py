def get_url(options, use_case, path) -> str:
    return "{}/{}/{}/{}".format(options["server"], use_case, options["version"], path)


def create_dict_from_kwargs(**kwargs):
    new_dict = {}
    for key, value in kwargs.items():
        if value is not None:
            new_dict[key] = value
    return new_dict
