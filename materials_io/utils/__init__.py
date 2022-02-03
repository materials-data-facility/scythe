from typing import Dict, Union, Tuple, Any, Callable, Optional, List
from typing_extensions import TypedDict


def get_nested_dict_value_by_path(nest_dict: Dict,
                                  path: Union[Tuple, str],
                                  cast: Optional[Callable] = None) -> Any:
    """
    Get the value from within a nested dictionary structure by traversing into
    the dictionary as deep as that path found and returning that value

    Parameters
    ----------
    nest_dict
        A dictionary of dictionaries that is to be queried
    path
        A string or tuple that specifies the subsequent keys
        needed to get to a value within `nest_dict`. If a string, the value will
        return just from the first level (mostly for convenience)
    cast
        A function that (if provided) will be applied to the value. This
        helps with serialization.

    Returns
    -------
    value
        The value at the path within the nested dictionary; if there's no
        value there, return ``None``
    """
    sub_dict = nest_dict

    if isinstance(path, str):
        path = (path, )

    for key in path:
        try:
            sub_dict = sub_dict[key]
        except KeyError:
            return None

    # coerce empty values to None
    if sub_dict in [{}, dict(), [], '']:
        return None

    if cast is not None:
        return cast(sub_dict)
    else:
        return sub_dict


def set_nested_dict_value(nest_dict: Dict, path: Tuple,
                          value: Any, override: Optional[bool] = False,):
    """
    Set a value within a nested dictionary structure by traversing into
    the dictionary as deep as that path found and changing it to ``value``.
    If ``value`` is ``None``, immediately return without performing an action
    Cribbed from https://stackoverflow.com/a/13688108/1435788

    Parameters
    ----------
    nest_dict
        A dictionary of dictionaries that is to be queried
    path
        A tuple (or other iterable type) that specifies the subsequent keys
        needed to get to a a value within `nest_dict`
    value
        The value which will be given to the path in the nested dictionary
    override
        If the value is already present, this flag controls whether to override
        its existing value
    """
    if value is None:
        return
    orig_value = get_nested_dict_value_by_path(nest_dict, path)
    for key in path[:-1]:
        nest_dict = nest_dict.setdefault(key, {})
    if orig_value is None or \
            orig_value is not None and override:
        # only set the value if it was None, or we chose to override
        nest_dict[path[-1]] = value


def set_nested_dict_value_with_units(nest_dict: Dict, path: Tuple,
                                     value: Any, units: Optional[str] = None,
                                     override: bool = False,
                                     fn: Optional[Callable] = None):
    """
    Same as :func:`~materials_io.utils.set_nested_dict_value`, but sets the
    value in the format of a dictionary with keys ``'value'`` and ``'units'``
    according to the specified units. If ``fn`` is supplied, it will be
    applied to the value prior to setting it.
    """
    if value is not None:
        if fn is not None:
            value = fn(value)
        to_set = {'value': value}
        if units is not None:
            to_set['units'] = units
        set_nested_dict_value(nest_dict, path, to_set, override)


MappingElements = TypedDict('MappingElements',
                            {'source_dict': Dict,
                             'source_path': Union[str, Tuple[str, ...]],
                             'dest_dict': Dict,
                             'dest_path': Union[str, Tuple[str, ...]],
                             'cast_fn': Optional[Callable],
                             'units': Optional[Union[None, str]],
                             'conv_fn': Optional[Union[None, Callable]]})


def map_dict_values(mapping: List[MappingElements]):
    """
    Helper method to apply map values from one dictionary into another.
    Inspired by the implementation in :func:`hyperspy.io.dict2signal`

    For each mapping we need a source dict and destination dict, then for
    eaqch term, the source path, the destination path, the cast function,
    the units to set, and potentially a conversion function

    So, ``mapping`` should be a list of dicts:
    [
        {'source_path': ('source', 'path',),
         'dest_path': ('dest', 'path',),
         'cast_fn': float,
         'units': str,
         'conv_fn': lambda x: x}
    ]
    """
    for m in mapping:
        m.setdefault('cast_fn', None)
        m.setdefault('units', None)
        m.setdefault('conv_fn', None)

        value = get_nested_dict_value_by_path(
            nest_dict=m['source_dict'],
            path=m['source_path'],
            cast=m['cast_fn'])
        set_nested_dict_value_with_units(
            nest_dict=m['dest_dict'], path=m['dest_path'], value=value,
            units=m['units'], fn=m['conv_fn'])
