import sys
import types


def class_from_str(module_name, class_name):
    """
    Covert a module_name and class_name into a Class object
    original source is http://stackoverflow.com/a/1176225/448016
    """
    try:
        identifier = getattr(sys.modules[module_name], class_name)
    except AttributeError:
        raise NameError("%s doesn't exist." % class_name)
    if isinstance(identifier, (types.ClassType, types.TypeType)):
        return identifier
    raise TypeError("%s is not a class." % class_name)