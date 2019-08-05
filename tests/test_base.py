from materials_io.base import BaseParser, BaseSingleFileParser
from glob import glob
import pytest
import os


class FakeParser(BaseParser):

    def parse(self, group, context=None):
        return {'group': list(group)}

    def implementors(self):
        return ['Logan Ward']

    def version(self):
        return '0.0.0'


class FakeSingleParser(BaseSingleFileParser):

    def _parse_file(self, path, context=None):
        return {'dirname': os.path.dirname(path)}

    def implementors(self):
        return ['Logan Ward']

    def version(self):
        return '0.0.0'


@pytest.fixture
def directory():
    return os.path.dirname(__file__)


@pytest.fixture
def parser():
    return FakeParser()


@pytest.fixture
def my_files(directory):
    return [p for p in glob(os.path.join(directory, '**', '*'), recursive=True)
            if os.path.isfile(p)]


def test_group(parser, directory, my_files):
    groups = set(parser.group(my_files))
    assert groups == set(zip(my_files))  # Each file own group


def test_parse_dir(caplog, parser, directory, my_files):
    assert len(list(parser.parse_directory(directory))) == len(my_files)


def test_citations(parser):
    assert parser.citations() == []


def test_single_file(directory):
    parser = FakeSingleParser()
    assert parser.parse(__file__) == {'dirname': directory}  # Handle sensibly incorrect inputs
    assert parser.parse([__file__]) == {'dirname': directory}
    with pytest.raises(ValueError):
        parser.parse(['/fake/file.in', '/fake/file.out'])
