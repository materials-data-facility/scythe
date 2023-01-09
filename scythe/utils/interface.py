"""Utilities for working with parsers from other applications"""

from stevedore.extension import ExtensionManager
from stevedore.driver import DriverManager
from typing import Iterator, Union, Dict, List
from collections import namedtuple
from copy import deepcopy

from scythe.adapters.base import BaseAdapter
from scythe.base import BaseParser
import logging

logger = logging.getLogger(__name__)

ParseResult = namedtuple('ParseResult', ['group', 'parser', 'metadata'])


def _output_plugin_info(mgr: ExtensionManager) -> dict:
    """Gets information about all plugins attached to a particular manager

    Args:
        mgr (ExtensionManager): Plugin manager
    Returns:
        (dict): Dictionary where keys are plugin ids and values are descriptions
    """

    output = {}
    for name, ext in mgr.items():
        plugin = ext.plugin()
        output[name] = {
            'description': plugin.__doc__.split("\n")[0],
            'version': plugin.version(),
            'class': ext.entry_point_target
        }
    return output


def get_available_parsers():
    """Get information about the available parsers

    Returns:
        [dict]: Descriptions of available parsers
    """
    mgr = ExtensionManager(
        namespace='scythe.parser',
    )

    # Get information about each parser
    return _output_plugin_info(mgr)


def get_available_adapters() -> dict:
    """Get information on all available adapters

    Returns:
        (dict) Where keys are adapter names and values are descriptions
    """

    return _output_plugin_info(ExtensionManager(namespace='scythe.adapter'))


def _get_adapter_map(adapter_map: str, parsers: list) -> dict:
    """ Helper function to generate 'adapter map'
            (so different run_all_parsers functions can call it)

    Adapter map is a list of parsers and names of the appropriate adapters
    to use to format their output.

    Args:
        adapter_map (str): string argument for adapters.
            - 'match' means just find adapters with same names as corresponding parsers.
        parsers ([str]): list of parsers
    Returns:
        (dict) where keys are adapter names parser/adapter names and values are adapter objects.
        """
    if adapter_map is None:
        adapter_map = {}
    elif adapter_map == 'match':
        adapters = get_available_adapters()
        adapter_map = dict((x, x) for x in parsers if x in adapters)
    elif not isinstance(adapter_map, dict):
        raise ValueError('Adapter map must be a dict, None, or `matching`')

    # Give it to the user
    return adapter_map


def _get_parser_and_adapter_contexts(name, global_context, parser_context, adapter_context):
    """
    Helper function to update the helper and adapter contexts and the 'name'
        of a parser/adapter pair
    Args:
        name (str): adapter/parser name.
        global_context (dict): Context of the files, used for every parser and adapter
        adapter_context (dict): Context used for adapters. Key is the name of the adapter,
            value is the context.  The key ``@all`` is used to for context used for every adapter
        parser_context (dict): Context used for adapters. Key is the name of the parser,
            value is the context. The key ``@all`` is used to for context used for every parser
    Returns:
         (dict, dict): parser_context, my_adapter context tuple
    """

    # Get the context information for the parser and adapter
    my_parser_context = deepcopy(global_context)
    my_parser_context.update(parser_context.get('@all', {}))
    my_parser_context.update(parser_context.get(name, {}))

    my_adapter_context = deepcopy(global_context)
    my_adapter_context.update(adapter_context.get('@all', {}))
    my_adapter_context.update(adapter_context.get(name, {}))

    return my_parser_context, my_adapter_context


def _get_parser_list(include_parsers: list, exclude_parsers: list) -> list:
    """ Helper function to get a list of parsers given lists of parsers to include/exclude

    Args:
        include_parsers ([str]): Predefined list of parsers to run. Only these will be used.
            Mutually exclusive with `exclude_parsers`.
        exclude_parsers ([str]): List of parsers to exclude.
            Mutually exclusive with `include_parsers`.
    Returns:
        parsers (list): list of all applicable parsers.

    """

    parsers = get_available_parsers()
    if include_parsers is not None and exclude_parsers is not None:
        raise ValueError('Including and excluding parsers are mutually exclusive')
    elif include_parsers is not None:
        missing_parsers = set(include_parsers).difference(parsers.keys())
        if len(missing_parsers) > 0:
            raise ValueError('Some parsers are missing: ' + ' '.join(missing_parsers))
        parsers = include_parsers
    elif exclude_parsers is not None:
        parsers = list(set(parsers.keys()).difference(exclude_parsers))

    return parsers


def get_parser(name: str) -> BaseParser:
    """Load a parser object

    Args:
        name (str): Name of parser
    Returns:
        (BaseParser) Requested parser
    """
    return DriverManager(
        namespace='scythe.parser',
        name=name,
        invoke_on_load=True
    ).driver


def get_adapter(name: str) -> BaseAdapter:
    """Load an adapter

    Args:
        name (str): Name of adapter
    Returns:
        (BaseAdapter) Requested adapter
    """

    # Load the adapter
    mgr = DriverManager(
        namespace='scythe.adapter',
        name=name,
        invoke_on_load=True
    )

    # Give it to the user
    return mgr.driver


def execute_parser(name, group, context=None,
                   adapter=None):
    """Invoke a parser on a certain group of data
    Args:
        name (str): Name of the parser
        group ([str]): Paths to group of files to be parsed
        context (dict): Context of the files, used in adapter and parser
        adapter (str): Name of adapter to use to transform metadata
    Returns:
        ([dict]): Metadata generated by the parser
    """
    metadata = get_parser(name).parse(group, context)
    if adapter is not None:
        adapter = get_adapter(adapter)
        return adapter.transform(metadata, context=context)
    return metadata


def run_all_parsers_on_directory(directory: str, global_context=None,
                                 adapter_context: Union[None, dict] = None,
                                 parser_context: Union[None, dict] = None,
                                 include_parsers: Union[None, List[str]] = None,
                                 exclude_parsers: Union[None, List] = None,
                                 adapter_map: Union[None, str, Dict[str, str]] = None,
                                 default_adapter: Union[None, str] = None) \
        -> Iterator[ParseResult]:
    """Run all known files on a directory of files

    Args:
        directory (str): Path to directory to be parsed
        global_context (dict): Context of the files, used for every parser and adapter
        adapter_context (dict): Context used for adapters. Key is the name of the adapter,
            value is the context.  The key ``@all`` is used to for context used for every adapter
        parser_context (dict): Context used for adapters. Key is the name of the parser,
            value is the context. The key ``@all`` is used to for context used for every parser
        include_parsers ([str]): Predefined list of parsers to run. Only these will be used.
            Mutually exclusive with `exclude_parsers`.
        exclude_parsers ([str]): List of parsers to exclude.
            Mutually exclusive with `include_parsers`.
        adapter_map (str, dict): Map of parser name to the desired adapter.
            Use 'match' to find adapters with the same names
        default_adapter (str): Adapter to use if no other adapter is defined
    Yields
        ((str), str, dict) Tuple of (1) group of files, (2) name of parser, (3) metadata
    """

    # Load in default arguments
    if global_context is None:
        global_context = dict()
    if adapter_context is None:
        adapter_context = dict()
    if parser_context is None:
        parser_context = dict()

    # Get the list of parsers
    parsers = _get_parser_list(include_parsers, exclude_parsers)

    # Make the adapter map
    adapter_map = _get_adapter_map(adapter_map=adapter_map, parsers=parsers)

    # Get the list of known parsers
    for name in parsers:
        # Get the parser and adapter
        parser = get_parser(name)
        adapter_name = adapter_map.get(name, default_adapter)
        if adapter_name is not None:
            adapter = get_adapter(adapter_name)
        else:
            adapter = None

        my_parser_context, my_adapter_context = _get_parser_and_adapter_contexts(name,
                                                                                 global_context,
                                                                                 parser_context,
                                                                                 adapter_context)

        for group, metadata in parser.parse_directory(directory, context=my_parser_context):
            # Run the adapter, if defined
            if adapter is not None:
                try:
                    metadata = adapter.transform(metadata, my_adapter_context)
                except Exception as e:
                    logger.warning(f'Adapter for {parser} failed with caught exception: {e}')
                    continue
                if metadata is None:
                    continue

            yield ParseResult(group, name, metadata)


def run_all_parsers_on_group(group,
                             adapter_map=None,
                             global_context=None,
                             adapter_context: Union[None, dict] = None,
                             parser_context: Union[None, dict] = None,
                             include_parsers: Union[None, List[str]] = None,
                             exclude_parsers: Union[None, List] = None,
                             default_adapter: Union[None, str] = None):
    """
    Parse metadata from a file-group and adapt its metadata per a user-supplied adapter_map.

    This function is effectively a wrapper to execute_parser() that enables us to output metadata
    in the same format as run_all_parsers_on_directory(), but just on a single file group.

    Args:
        group ([str]): Paths to group of files to be parsed
        global_context (dict): Context of the files, used for every parser and adapter
        adapter_context (dict): Context used for adapters. Key is the name of the adapter,
            value is the context.  The key ``@all`` is used to for context used for every adapter
        parser_context (dict): Context used for adapters. Key is the name of the parser,
            value is the context. The key ``@all`` is used to for context used for every parser
        include_parsers ([str]): Predefined list of parsers to run. Only these will be used.
            Mutually exclusive with `exclude_parsers`.
        exclude_parsers ([str]): List of parsers to exclude.
            Mutually exclusive with `include_parsers`.
        adapter_map (str, dict): Map of parser name to the desired adapter.
            Use 'match' to find adapters with the same names:
        default_adapter:
    Yields:
        ParseResult(group, name, metadata)
    """

    # Load in default arguments
    if global_context is None:
        global_context = dict()
    if adapter_context is None:
        adapter_context = dict()
    if parser_context is None:
        parser_context = dict()

    # Get the list of parsers
    parsers = _get_parser_list(include_parsers, exclude_parsers)

    # Make the adapter map
    adapter_map = _get_adapter_map(adapter_map=adapter_map, parsers=parsers)

    for name in parsers:
        # Get the parser and adapter
        adapter_name = adapter_map.get(name, default_adapter)

        my_parser_context, my_adapter_context = _get_parser_and_adapter_contexts(name,
                                                                                 global_context,
                                                                                 parser_context,
                                                                                 adapter_context)

        metadata = execute_parser(name, group, context=my_parser_context, adapter=adapter_name)

        yield ParseResult(group, name, metadata)
