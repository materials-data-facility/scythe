from materials_io.base import BaseParser
from glob import glob
import logging
import pytest
import os


class FakeParser(BaseParser):

    def parse(self, group, context=None):
        return [{}] * len(group)

    def implementors(self):
        return ['Logan Ward']

    def version(self):
        return '0.0.0'


class FakeParserWithIsValid(FakeParser):

    def is_valid(self, group, context=None):
        return True


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
    groups = set(parser.group(directory))
    assert set(groups) == set(zip(my_files))  # Each file own group


def test_parse_dir(caplog, parser, directory, my_files):
    with caplog.at_level(logging.DEBUG):
        # Testing with the default is_valid
        assert len(list(parser.parse_directory(directory))) == len(my_files)
        assert 'Attempting to parse every file' in caplog.records[-1].msg

        assert len(list(FakeParserWithIsValid().parse_directory(directory))) == len(my_files)
        assert 'Using is_valid' in caplog.records[-1].msg


def test_is_valid(parser, my_files):
    assert parser.is_valid(my_files)  # By default


def test_citations(parser):
    assert parser.citations() == []
