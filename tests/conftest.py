import tarfile
import pathlib

tar_f = pathlib.Path(__file__).parent / 'data' / 'electron_microscopy' / \
        'test_files.tar.gz'


def pytest_sessionstart(session):
    """
    Called after the Session object has been created and
    before performing collection and entering the run test loop.

    Unpack the compressed electron_microscopy est files.
    """
    with tarfile.open(tar_f, 'r:gz') as tar:
        tar.extractall(path=pathlib.Path(tar_f).parent)


def pytest_sessionfinish(session, exitstatus):
    """
    Called after whole test run finished, right before
    returning the exit status to the system.

    Remove the unpacked test files.
    """
    with tarfile.open(tar_f, 'r:gz') as tar:
        fn_list = tar.getnames()

    fn_list = [pathlib.Path(__file__).parent / 'data' /
               'electron_microscopy' / f for f in fn_list]
    for path in fn_list:
        if path.is_file():
            path.unlink()
