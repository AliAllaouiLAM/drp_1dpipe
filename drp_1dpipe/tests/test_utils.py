"""
File: drp_1dpipe/tests/test_utils.py

Created on: 31/10/18
Author: PSF DRP1D developers
"""

import pytest
import os.path
import tempfile
import threading
import time
from drp_1dpipe.io.utils import get_auxiliary_path, get_conf_path, normpath, wait_semaphores


def test_auxdir():
    """
    The "test_auxdir" function.

    This function tests features concerning auxiliary directory.
    """
    assert os.path.exists(get_auxiliary_path("."))
    assert not(os.path.exists(get_auxiliary_path("foo.txt")))


def test_confdir():
    """
    The "test_confdir" function.

    This function tests features concerning configuration directory.
    """
    assert os.path.exists(get_conf_path("."))
    assert not(os.path.exists(get_conf_path("foo.txt")))


def test_args_from_file():
    """
    The "test_args_from_file" function.

    This function tests feature of retrieving argument value from
    configuration file
    """
    from drp_1dpipe.io.utils import get_args_from_file
    import tempfile
    fp1 = tempfile.NamedTemporaryFile()
    conf_file = fp1.name
    with open(conf_file, 'w') as cf:
        cf.write('arg1 = 4\n')
        cf.write('arg2 = foo2 foo2\n')
        cf.write('arg3 = foo3 # test\n')
        cf.write('arg4 = # foo4\n')
        cf.write('arg5 # = foo5\n')
        cf.write('#arg6 = foo6')
        cf.write('arg7 arg7 = foo7\n')

    class MyCls():
        arg1 = "2"

    args = MyCls()
    get_args_from_file(conf_file, args)
    assert args.arg1 == "2"
    assert args.arg2 == "foo2 foo2"
    assert args.arg3 == "foo3"
    assert args.arg4 == ""
    with pytest.raises(AttributeError):
        getattr(args, "arg5")
    with pytest.raises(AttributeError):
        getattr(args, "arg6")
    with pytest.raises(AttributeError):
        getattr(args, "arg7")
    fp1.close()

def test_normpath():
    assert normpath('~/foo//bar/baz/~') == os.path.expanduser('~/foo/bar/baz/~')
    assert normpath('~/foo/.././bar/./baz/') == os.path.expanduser('~/bar/baz')
    assert normpath('////foo/baz////') == os.path.expanduser('/foo/baz')


def _create_semaphores(semaphores):
    """Create all files in semaphores, one per second"""
    for f in semaphores:
        fd = open(f, 'w')
        time.sleep(1)
        fd.close()

def test_wait_semaphores():

    # wait a never creater file
    try:
        wait_semaphores(['/tmp/foo'], 5)
    except TimeoutError:
        pass
    except:
        raise

    # create files before waiting
    semaphores = [tempfile.NamedTemporaryFile(prefix='pytest_') for i in range(5)]
    wait_semaphores([s.name for s in semaphores], 10)

    # create files after waiting
    with tempfile.TemporaryDirectory(prefix='pytest_') as tmpdir:
        semaphores = [os.path.join(tmpdir, str(i)) for i in range(8)]
        t = threading.Thread(target=_create_semaphores, args=(semaphores,))
        t.start()
        wait_semaphores(semaphores, 20)
        t.join(timeout=2)
