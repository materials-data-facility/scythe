import tarfile
import os

tar_f = os.path.join(os.path.dirname(__file__), 'data',
                     'electron_microscopy', 'test_files.tar.gz')


def pytest_sessionstart(session):
    """
    Called after the Session object has been created and
    before performing collection and entering the run test loop.

    Unpack the compressed electron_microscopy est files.
    """
    with tarfile.open(tar_f, 'r:gz') as tar:
        tar.extractall(path=os.path.dirname(tar_f))


def pytest_sessionfinish(session, exitstatus):
    """
    Called after whole test run finished, right before
    returning the exit status to the system.

    Remove the unpacked test files.
    """
    with tarfile.open(tar_f, 'r:gz') as tar:
        fn_list = tar.getnames()

    fn_list = [os.path.join(os.path.dirname(__file__), 'data',
                            'electron_microscopy', f) for f in fn_list]
    for fn in fn_list:
        if os.path.isfile(fn):
            os.remove(fn)
