#!/usr/bin/env python

import sys
import argparse
import traceback
import mlperf_prof


def parse_args():
    parser = argparse.ArgumentParser('example')
    parser.add_argument('--test', action='store_true',
                        help='Test adding user options')

    '''add the mlperf command-line options'''
    args = mlperf_prof.parse_args(parser)
    if args.test:
        print('Testing...')


def fibonacci(n):
    return n if n < 2 else fibonacci(n-1) + fibonacci(n-2)


@mlperf_prof.marker(['wall_clock', 'cpu_clock'], mode='full')
def main():
    '''Use decorator with wall-clock and cpu-clock components
    Set the mode to full which writes the function name, line number
    and file instead of just the function
    '''
    import time

    '''Use a manual wall-clock timer'''
    t = mlperf_prof.timer('wall')
    t.start()
    '''Use the full function profiler as a context-manager'''
    with mlperf_prof.profile():
        fibonacci(10)
    t.stop()
    print('\nmanual timer: {} {}\n'.format(t.get(), t.display_units()))


if __name__ == '__main__':
    try:
        parse_args()
        main()
        '''Finalize the results before exiting'''
        mlperf_prof.finalize()
    except Exception as e:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback.print_exception(exc_type, exc_value, exc_traceback)
