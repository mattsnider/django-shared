def get_and_cast_or_default(dictionary, key, casting_fn, default_value):
    """
    Gets the value and casts it, or returns the default_value.
    """
    try:
        return casting_fn(dictionary.get(key)) or default_value
    except KeyError:
        return default_value