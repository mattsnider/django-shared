def diff(a, b, asymetric=False, asymetric_left=True):
    """
    Returns the difference between the two lists.
        If asymetric is True, then it will only it will only return the items from `b` that are not in `a`, instead of both
        If asymetric_left is False, then it will only it will only return the items from `a` that are not in `b`
    """
    if asymetric:
        l = []

        list_to_eval = a if asymetric_left else b
        list_to_diff = b if asymetric_left else a

        # if no list_to_diff, then there is no possible difference in that list
        if not list_to_diff:
            return []
        # if no list_to_eval, then the whole list_to_diff is different
        elif not list_to_eval:
            return list_to_diff

        for o in list_to_diff:
            if o not in list_to_eval:
                l.append(o)

        return l
    else:
        # simple set intersection or if one set is empty, then return the set with a value
        return list(set(a) ^ set(b)) if a and b else a or b or []


def find(f, seq, first=True):
    """
    Return item(s) in sequence where f(item) == True.
        Default stops and returns the first value, set first=False if you want a list of values.
    """
    if first:
        for item in seq:
            if f(item):
                return item
    else:
        return filter(f, seq)


def first(list, default=None):
    """Returns the first item in the list or `default` if it doesn't exists"""
    if list:
        return list[0]
    else:
        return default


def intersect(a, b):
    """ return the intersection of two lists """
    if b is None or a is None:
        return []
    return list(set(a) & set(b))


def last(list, default=None):
    """Returns the last item in the list or `default` if it doesn't exists"""
    if list:
        return list[-1]
    else:
        return default


def pluck(dicts, keys, aliases=None):
    """
    Given a list of dictionaries,
      return a list of smaller dicts (w/ just the requested keys)
        optionally aliasing those properties to new names.
      If a requested key doesn't exist, the resulting dicts
         will also not have it (no error raised, None not inserted.)

    >>> pluck([{'a':1, 'b':2}, {'a':3}, {'b':9}], ['a','y'], ['x','y'])
    [{'x': 1}, {'x': 3}, {}]
    """
    ret = []
    if not aliases:
        aliases = keys
    else:
        if len(aliases) != len(keys):
            raise ValueError("len of aliases and props must match.")

    for d in dicts:
        d_ret = {}
        for (key, alias) in zip(keys, aliases):
            if key in d:
                d_ret[alias] = d[key]
        ret.append(d_ret)
    return ret


def union(a, b):
    """ return the union of two lists """
    if b is None or a is None:
        return a or b or []
    return list(set(a) | set(b))


def unique_ordered(seq, idfun=None):
    """Makes the list unique, while preserving order"""
    if idfun is None:
        def idfun(x):
            return x
    seen = {}
    result = []
    for item in seq:
        marker = idfun(item)
        # in old Python versions:
        # if seen.has_key(marker)
        # but in new ones:
        if marker in seen:
            continue
        seen[marker] = 1
        result.append(item)
    return result


def unique_unordered(seq):
    """Makes the list unique, but is not order preserving; much faster"""
    return list(set(seq))
