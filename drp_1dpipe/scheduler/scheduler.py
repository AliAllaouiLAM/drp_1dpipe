"""
File: drp_1dpipe/scheduler/scheduler.py

Created on: 01/11/18
Author: CeSAM
"""

import uuid
from drp_1dpipe.io.utils import init_logger, get_args_from_file, normpath, \
    init_argparse
from drp_1dpipe.scheduler import pbs, local


def main():
    """Pipeline entry point.

    Initialize a logger, parse command line arguments, and call the run()
    function.
    """

    parser = init_argparse()
    parser.add_argument('--scheduler', metavar='SCHEDULER',
                        help='The scheduler to use. Whether "local" or "pbs".')
    parser.add_argument('--pre_commands', metavar='COMMAND',
                        help='Commands to run before before process_spectra.')
    parser.add_argument('--spectra_path', metavar='DIR',
                        help='Base path where to find spectra. '
                        'Relative to workdir.')
    parser.add_argument('--bunch_size', metavar='SIZE',
                        help='Maximum number of spectra per bunch.')

    args = parser.parse_args()
    get_args_from_file("scheduler.conf", args)

    return run(args)


def run(args):
    """Run the 1D Data Reduction Pipeline.

    :return: 0 on success
    """

    # initialize logger
    init_logger("scheduler", args.logdir, args.loglevel)

    if args.scheduler.lower() == 'pbs':
        scheduler = pbs
    elif args.scheduler.lower() == 'local':
        scheduler = local
    else:
        raise "Unknown scheduler {}".format(args.scheduler)

    bunch_list = normpath(args.workdir,
                          'list_{}.json'.format(uuid.uuid4().hex))

    # prepare workdir
    scheduler.single('pre_process', args={'workdir': normpath(args.workdir),
                                          'logdir': normpath(args.logdir),
                                          'loglevel': args.loglevel,
                                          'bunch_size': args.bunch_size,
                                          'pre_commands': args.pre_commands,
                                          'spectra_path': args.spectra_path,
                                          'bunch_list': bunch_list})

    # process spectra
    scheduler.parallel('process_spectra', bunch_list,
                       'spectra_listfile', 'output_dir',
                       args={'workdir': normpath(args.workdir),
                             'logdir': normpath(args.logdir),
                             'loglevel': args.loglevel,
                             'spectra_path': args.spectra_path,
                             'pre_commands': args.pre_commands,
                             'output_dir': 'output-'})

    # merge results
    #scheduler.single('merge_results', args={'workdir': normpath(args.workdir),
    #                                        'logdir': normpath(args.logdir),
    #                                        'spectra_path': args.spectra_path,
    #                                        'result_dirs': 'output-*'})

    return 0
