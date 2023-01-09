"""Utilities for implementing grouping operations"""
from typing import Union, List, Iterable, Tuple
from operator import itemgetter
from pathlib import Path
import itertools
import os


def preprocess_paths(paths: Union[str, Path, List[str], List[Path]]) -> List[str]:
    """Transform paths to absolute paths

    Designed to be used to simplify grouping logic

    Args:
        paths (Union[str, List[str]): Files and directories to be parsed
    Returns:
        (List[str]): List of paths in standardized form
    """

    # Make sure paths are strings or Path-like objects
    if isinstance(paths, (str, Path)):
        paths = [paths]

    # Make paths absolute
    return [os.path.abspath(os.path.expanduser(f)) for f in paths]


def group_by_postfix(files: Iterable[str], vocabulary: List[str]) -> Iterable[Tuple[str, ...]]:
    """Group files that have a common ending

    Finds all filenames that begin with a prefixes from a
    user-provided vocabulary and end with the same post-fix.

    For example, consider a directory that contains files A.1, B.1, A.2, B.2, and C.1.
    If a user provides a vocabulary of ['A', 'B'], the parser will return
    groups (A.1, B.1) and (A.2, B.2).
    If a user provides a vocabulary of ['A', 'B', 'C'], the parser will
    return groups (A.1, B.1), (A.2, B.2), and (C.1)

    See :class:`scythe.dft.DFTParser` for an example usage.

    Args:
        files ([str]): List of files to be grouped
        vocabulary ([str]): List of known starts for the file
    Yields:
        ([str]): Groups of files to be parsed together
    """

    # TODO (lw): This function could be more flexible, but let's add features on demand

    # Get the files with similar post-fixes and are from the user-defined vocabulary
    matchable_files = []  # List of (path, type, (dir, postfix))
    for filename in files:
        # Find if the filename matches a known type
        name = os.path.basename(filename)
        name_lower = name.lower()
        matches = [name_lower.startswith(n) for n in vocabulary]
        if not any(matches):
            continue

        # Get the extension of the file
        match_id = matches.index(True)
        vtype = vocabulary[match_id]
        ext = name[len(vtype):]
        d = os.path.dirname(filename)

        # Add to the list
        matchable_files.append((filename, vtype, (d, ext)))

    # Group files by postfix type and directory
    sort_key = itemgetter(2)
    for k, group in itertools.groupby(sorted(matchable_files, key=sort_key),
                                      key=sort_key):
        yield [x[0] for x in group]
