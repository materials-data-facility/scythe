"""Utilities for working with extractors from other applications"""

from stevedore.extension import ExtensionManager
from stevedore.driver import DriverManager
from typing import Iterator, Union, Dict, List
from collections import namedtuple
from copy import deepcopy

from scythe.adapters.base import BaseAdapter
from scythe.base import BaseExtractor
import logging

logger = logging.getLogger(__name__)

ExtractResult = namedtuple('ExtractResult', ['group', 'extractor', 'metadata'])


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


def get_available_extractors():
    """Get information about the available extractors

    Returns:
        [dict]: Descriptions of available extractors
    """
    mgr = ExtensionManager(
        namespace='scythe.extractor',
    )

    # Get information about each extractor
    return _output_plugin_info(mgr)


def get_available_adapters() -> dict:
    """Get information on all available adapters

    Returns:
        (dict) Where keys are adapter names and values are descriptions
    """

    return _output_plugin_info(ExtensionManager(namespace='scythe.adapter'))


def _get_adapter_map(adapter_map: str, extractors: list) -> dict:
    """Helper function to generate 'adapter map'

    Adapter map is a list of extractors and names of the appropriate adapters
    to use to format their output.

    Args:
        adapter_map (str): string argument for adapters.
            - 'match' means just find adapters with same names as corresponding extractors.
        extractors ([str]): list of extractors
    Returns:
        (dict) where keys are adapter names extractor/adapter names and values are adapter objects.
    """
    if adapter_map is None:
        adapter_map = {}
    elif adapter_map == 'match':
        adapters = get_available_adapters()
        adapter_map = dict((x, x) for x in extractors if x in adapters)
    elif not isinstance(adapter_map, dict):
        raise ValueError('Adapter map must be a dict, None, or `matching`')

    # Give it to the user
    return adapter_map


def get_extractor_and_adapter_contexts(name, global_context, extractor_context, adapter_context):
    """
    Helper function to update the helper and adapter contexts and the 'name'
        of a extractor/adapter pair
    Args:
        name (str): adapter/extractor name.
        global_context (dict): Context of the files, used for every extractor and adapter
        adapter_context (dict): Context used for adapters. Key is the name of the adapter,
            value is the context.  The key ``@all`` is used to for context used for every adapter
        extractor_context (dict): Context used for adapters. Key is the name of the extractor,
            value is the context. The key ``@all`` is used to for context used for every extractor
    Returns:
         (dict, dict): extractor_context, my_adapter context tuple
    """

    # Get the context information for the extractor and adapter
    my_extractor_context = deepcopy(global_context)
    my_extractor_context.update(extractor_context.get('@all', {}))
    my_extractor_context.update(extractor_context.get(name, {}))

    my_adapter_context = deepcopy(global_context)
    my_adapter_context.update(adapter_context.get('@all', {}))
    my_adapter_context.update(adapter_context.get(name, {}))

    return my_extractor_context, my_adapter_context


def _get_extractor_list(to_include: list, to_exclude: list) -> list:
    """ Helper function to get a list of extractors given lists of extractors to include/exclude

    Args:
        to_include ([str]): Predefined list of extractors to run. Only these will be used.
            Mutually exclusive with `exclude_extractors`.
        to_exclude ([str]): List of extractors to exclude.
            Mutually exclusive with `include_extractors`.
    Returns:
        List of all applicable extractors
    """

    extractors = get_available_extractors()
    if to_include is not None and to_exclude is not None:
        raise ValueError('Including and excluding extractors are mutually exclusive')
    elif to_include is not None:
        missing_extractors = set(to_include).difference(extractors.keys())
        if len(missing_extractors) > 0:
            raise ValueError('Some extractors are missing: ' + ' '.join(missing_extractors))
        extractors = to_include
    elif to_exclude is not None:
        extractors = list(set(extractors.keys()).difference(to_exclude))

    return extractors


def get_extractor(name: str) -> BaseExtractor:
    """Load an extractor object

    Args:
        name (str): Name of extractor
    Returns:
        Requested extractor
    """
    return DriverManager(
        namespace='scythe.extractor',
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


def run_extractor(name, group, context=None, adapter=None):
    """Invoke a extractor on a certain group of files

    Args:
        name (str): Name of the extractor
        group ([str]): Paths to group of files to be parsed
        context (dict): Context of the files, used in adapter and extractor
        adapter (str): Name of adapter to use to transform metadata
    Returns:
        ([dict]): Metadata generated by the extractor
    """
    metadata = get_extractor(name).extract(group, context)
    if adapter is not None:
        adapter = get_adapter(adapter)
        return adapter.transform(metadata, context=context)
    return metadata


def run_all_extractors_on_directory(directory: str, global_context=None,
                                    adapter_context: Union[None, dict] = None,
                                    extractor_context: Union[None, dict] = None,
                                    include_extractors: Union[None, List[str]] = None,
                                    exclude_extractors: Union[None, List] = None,
                                    adapter_map: Union[None, str, Dict[str, str]] = None,
                                    default_adapter: Union[None, str] = None) \
        -> Iterator[ExtractResult]:
    """Run all known files on a directory of files

    Args:
        directory (str): Path to directory to be parsed
        global_context (dict): Context of the files, used for every extractor and adapter
        adapter_context (dict): Context used for adapters. Key is the name of the adapter,
            value is the context.  The key ``@all`` is used to for context used for every adapter
        extractor_context (dict): Context used for adapters. Key is the name of the extractor,
            value is the context. The key ``@all`` is used to for context used for every extractor
        include_extractors ([str]): Predefined list of extractors to run. Only these will be used.
            Mutually exclusive with `exclude_extractors`.
        exclude_extractors ([str]): List of extractors to exclude.
            Mutually exclusive with `include_extractors`.
        adapter_map (str, dict): Map of extractor name to the desired adapter.
            Use 'match' to find adapters with the same names
        default_adapter (str): Adapter to use if no other adapter is defined
    Yields
        ((str), str, dict) Tuple of (1) group of files, (2) name of extractor, (3) metadata
    """

    # Load in default arguments
    if global_context is None:
        global_context = dict()
    if adapter_context is None:
        adapter_context = dict()
    if extractor_context is None:
        extractor_context = dict()

    # Get the list of extractors
    extractors = _get_extractor_list(include_extractors, exclude_extractors)

    # Make the adapter map
    adapter_map = _get_adapter_map(adapter_map=adapter_map, extractors=extractors)

    # Get the list of known extractors
    for name in extractors:
        # Get the extractor and adapter
        extractor = get_extractor(name)
        adapter_name = adapter_map.get(name, default_adapter)
        if adapter_name is not None:
            adapter = get_adapter(adapter_name)
        else:
            adapter = None

        my_extractor_context, my_adapter_context = get_extractor_and_adapter_contexts(name,
                                                                                      global_context,
                                                                                      extractor_context,
                                                                                      adapter_context)

        for group, metadata in extractor.extract_directory(directory, context=my_extractor_context):
            # Run the adapter, if defined
            if adapter is not None:
                try:
                    metadata = adapter.transform(metadata, my_adapter_context)
                except Exception as e:
                    logger.warning(f'Adapter for {extractor} failed with caught exception: {e}')
                    continue
                if metadata is None:
                    continue

            yield ExtractResult(group, name, metadata)


def run_all_extractors_on_group(group,
                                adapter_map=None,
                                global_context=None,
                                adapter_context: Union[None, dict] = None,
                                extractor_context: Union[None, dict] = None,
                                include_extractors: Union[None, List[str]] = None,
                                exclude_extractors: Union[None, List] = None,
                                default_adapter: Union[None, str] = None):
    """
    Parse metadata from a file-group and adapt its metadata per a user-supplied adapter_map.

    This function is effectively a wrapper to execute_extractor() that enables us to output metadata
    in the same format as run_all_extractors_on_directory(), but just on a single file group.

    Args:
        group ([str]): Paths to group of files to be parsed
        global_context (dict): Context of the files, used for every extractor and adapter
        adapter_context (dict): Context used for adapters. Key is the name of the adapter,
            value is the context.  The key ``@all`` is used to for context used for every adapter
        extractor_context (dict): Context used for adapters. Key is the name of the extractor,
            value is the context. The key ``@all`` is used to for context used for every extractor
        include_extractors ([str]): Predefined list of extractors to run. Only these will be used.
            Mutually exclusive with `exclude_extractors`.
        exclude_extractors ([str]): List of extractors to exclude.
            Mutually exclusive with `include_extractors`.
        adapter_map (str, dict): Map of extractor name to the desired adapter.
            Use 'match' to find adapters with the same names:
        default_adapter:
    Yields:
        Metadata for a certain
    """

    # Load in default arguments
    if global_context is None:
        global_context = dict()
    if adapter_context is None:
        adapter_context = dict()
    if extractor_context is None:
        extractor_context = dict()

    # Get the list of extractors
    extractors = _get_extractor_list(include_extractors, exclude_extractors)

    # Make the adapter map
    adapter_map = _get_adapter_map(adapter_map=adapter_map, extractors=extractors)

    for name in extractors:
        # Get the extractor and adapter
        adapter_name = adapter_map.get(name, default_adapter)

        my_extractor_context, my_adapter_context = get_extractor_and_adapter_contexts(name,
                                                                                      global_context,
                                                                                      extractor_context,
                                                                                      adapter_context)

        metadata = run_extractor(name, group, context=my_extractor_context, adapter=adapter_name)

        yield ExtractResult(group, name, metadata)
