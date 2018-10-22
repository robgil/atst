import re


def first_or_none(predicate, lst):
    return next((x for x in lst if predicate(x)), None)


def deep_merge(source, destination: dict):
    """
    Merge source dict into destination dict recursively.
    """

    def _deep_merge(a, b):
        for key, value in a.items():
            if isinstance(value, dict):
                node = b.setdefault(key, {})
                _deep_merge(value, node)
            else:
                b[key] = value

        return b

    return _deep_merge(source, dict(destination))


def getattr_path(obj, path, default=None):
    _obj = obj
    for item in path.split("."):
        _obj = getattr(_obj, item, default)
    return _obj


def camel_to_snake(camel_cased):
    s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", camel_cased)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()