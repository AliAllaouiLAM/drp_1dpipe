import os
import copy
import logging
import time
import argparse


def init_argparse():
    """Initialize command-line argument parser with common arguments.

    :return: An initialized ArgumentParsel object.
    """
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--workdir', default=os.getcwd(),
                        help='The root working directory where data is '
                        'located.')
    parser.add_argument('--logdir',
                        default=os.path.join(os.getcwd(), 'logdir'),
                        help='The logging directory.')
    parser.add_argument('--loglevel', default='WARNING',
                        help='The logging level. CRITICAL, ERROR, WARNING, '
                        'INFO or DEBUG.')
    return parser


def get_auxiliary_path(file_name):
    """Get the full path of file in auxiliary directory.

    :param file_name: Name of the file.
    :return: Full path of auxiliary directory.

    :Example:

    get_auxiliary_path("my_data.dat") # -> /python/package/path/my_data.dat
    """
    return os.path.join(os.path.dirname(__file__), 'auxdir', file_name)


def get_conf_path(file_name):
    """Get the full path of file in configuration directory.

    :param file_name: Name of the file.
    :return: Full path of configuration file.

    :Example:

    get_conf_path("my_conf.conf") # -> /python/package/path/my_conf.conf
    """
    return os.path.join(os.path.dirname(__file__), 'conf', file_name)


_loglevels = {
    'CRITICAL': logging.CRITICAL,
    'FATAL': logging.CRITICAL,
    'ERROR': logging.ERROR,
    'WARNING': logging.WARNING,
    'WARN': logging.WARNING,
    'INFO': logging.INFO,
    'DEBUG': logging.DEBUG,
    'NOTSET': logging.NOTSET,
}


def init_logger(process_name, logdir, loglevel):
    """Initializes a logger depending on which module calls it.

    :param process_name: name of the module calling it.

    :Example:

    In define_program_options() of process_spectra.py :

    init_logger("pre_process")
    """

    os.makedirs(logdir, exist_ok=True)
    _level = _loglevels[loglevel.upper()]

    logger = logging.getLogger(process_name)
    logger.setLevel(_level)
    formatter = logging.Formatter('%(asctime)s :: %(levelname)s :: %(message)s')

    # file handler
    file_handler = logging.FileHandler(os.path.join(logdir,
                                                    process_name + '.log'),
                                       'w')
    file_handler.setLevel(_level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # stream handler
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(_level)
    logger.addHandler(stream_handler)


def get_args_from_file(file_name):
    """Get arguments value from configuration file.

    :param file_name: name of the configuration file

    Get arguments value from configuration file. Value has to be formatted as
    ``option = string``. To comment use ``#``.

    Return a key, value pairs as a dictionnary.
    """
    args = {}
    with open(get_conf_path(file_name), 'r') as ff:
        lines = ff.readlines()
    for line in lines:
        try:
            key, value = line.replace('\n', '').split('#')[0].split("=")
        except ValueError:
            continue
        args[key.strip()] = value.strip()
    return args


def normpath(*args):
    return os.path.normpath(os.path.expanduser(os.path.join(*args)))


def wait_semaphores(semaphores, timeout=4.354e17, tick=60):
    """Wait all files are created.

    :param semaphores: List of files to watch for creation.
    :param timeout: Maximun wait time, in seconds.
    """
    start = time.time()
    # we have to copy the semaphore list as some other thread may use it
    _semaphores = copy.copy(semaphores)
    while _semaphores:
        if time.time() - start > timeout:
            raise TimeoutError(_semaphores)
        if os.path.exists(_semaphores[0]):
            del _semaphores[0]
            continue
        time.sleep(tick)
