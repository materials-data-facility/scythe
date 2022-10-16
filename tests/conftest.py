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
        
        import os
        
        def is_within_directory(directory, target):
            
            abs_directory = os.path.abspath(directory)
            abs_target = os.path.abspath(target)
        
            prefix = os.path.commonprefix([abs_directory, abs_target])
            
            return prefix == abs_directory
        
        def safe_extract(tar, path=".", members=None, *, numeric_owner=False):
        
            for member in tar.getmembers():
                member_path = os.path.join(path, member.name)
                if not is_within_directory(path, member_path):
                    raise Exception("Attempted Path Traversal in Tar File")
        
            tar.extractall(path, members, numeric_owner=numeric_owner) 
            
        
        safe_extract(tar, path=pathlib.Path(tar_f).parent)


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
