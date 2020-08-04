#!/usr/bin/env python
#
# @file __init__.py
#
# MLPerf HPC benchmarking utilities
#   - command line options
#   - decorators
#   - context-managers
#   - timers
#

from __future__ import absolute_import
import os
import six
import sys
import inspect
import argparse
from functools import wraps

__author__ = "Jonathan Madsen"
__copyright__ = "Copyright 2020, The Regents of the University of California"
__credits__ = ["Jonathan Madsen"]
__license__ = "MIT"
__version__ = "0.0.1"
__maintainer__ = "Jonathan Madsen"
__email__ = "jrmadsen@lbl.gov"
__status__ = "Development"
__all__ = ['get_results',
           'finalize',
           'parse_args',
           'marker',
           'profile',
           'trace']


PY3 = sys.version_info[0] == 3
if PY3:
    import builtins
else:
    import __builtin__ as builtins

_Metrics = ['wall_clock']

try:
    # benchmarking toolkit
    import timemory
    from timemory.component import WallClock, CpuClock, CudaEvent, UserClock, SysClock
    import timemory.profiler
    import timemory.line_profiler
    import json

    def get_results(report=False):
        # Get the results as dictionary
        data = timemory.get()
        if report is True:
            print("\n{}".format(json.dumps(data, indent=4, sort_keys=True)))
        return data

    def finalize():
        timemory.finalize()

    class marker(timemory.util.marker):
        '''Decorator/context-manager for all stages of an ML-Perf Benchmark

        Usage:
            @mlperf_prof.profile
            def myfunc():
                # ...
                using mlperf_prof.profile:
                    # ...
        '''

        def __init__(self, components=[], **kwargs):
            super(marker, self).__init__(_Metrics + components, **kwargs)

        def __call__(self, func):
            return super(marker, self).__call__(func)

        def __enter__(self, *args, **kwargs):
            return super(marker, self).__enter__(*args, **kwargs)

        def __exit__(self, exc_type, exc_value, exc_traceback):
            return super(marker, self).__exit__(exc_type, exc_value, exc_traceback)

    class profile(timemory.profiler.profile):
        '''Implements full profiling for every Python function call

        Usage:
            @mlperf_prof.profile
            def myfunc():
                # ...
                using mlperf_prof.profile:
                    # ...
        '''

        def __init__(self, *args, **kwargs):
            super(profile, self).__init__(*args, **kwargs)

        def __call__(self, func):
            return super(profile, self).__call__(func)

        def __enter__(self, *args, **kwargs):
            return super(profile, self).__enter__(*args, **kwargs)

        # def __exit__(self, exc_type, exc_value, exc_traceback):
        #    return super(profile, self).__exit__(exc_type, exc_value, exc_traceback)

    class trace(timemory.line_profiler.LineProfiler):
        '''Implements full line-by-line profiling for every line in function

        Usage:
            @mlperf_prof.trace
            def myfunc():
                # ...
        '''

        def __init__(self, *args, **kwargs):
            super(trace, self).__init__(*args, **kwargs)

        def __call__(self, func):
            return super(trace, self).__call__(func)

        def __enter__(self, *args, **kwargs):
            return super(trace, self).__enter__(*args, **kwargs)

        def __exit__(self, exc_type, exc_value, exc_traceback):
            return super(trace, self).__exit__(exc_type, exc_value, exc_traceback)

    class timer(object):
        '''Implements a timer of the selected type'''

        def __init__(self, dtype='wall', label=''):
            '''Initialize a timer
            '''
            if dtype.lower().startswith('wall'):
                self._obj = WallClock(label)
                self._unit = WallClock.unit()
                self._disp = WallClock.display_unit()
            elif dtype.lower().startswith('cpu'):
                self._obj = CpuClock(label)
                self._unit = CpuClock.unit()
                self._disp = CpuClock.display_unit()
            elif dtype.lower().startswith('cuda_event'):
                self._obj = CudaEvent(label)
                self._unit = CudaEvent.unit()
                self._disp = CudaEvent.display_unit()
            elif dtype.lower().startswith('user'):
                self._obj = UserClock(label)
                self._unit = UserClock.unit()
                self._disp = UserClock.display_unit()
            elif dtype.lower().startswith('system'):
                self._obj = SysClock(label)
                self._unit = SysClock.unit()
                self._disp = SysClock.display_unit()
            else:
                raise RuntimeError('invalid type')

        def get(self):
            return self._obj.get()

        def start(self):
            return self._obj.start()

        def stop(self):
            return self._obj.stop()

        def laps(self):
            return self._obj.laps()

        def units(self):
            return self._unit

        def display_units(self):
            return self._disp

    def parse_args(parser):
        '''Adds command line options

        Usage:
            parser = argparse.ArgumentParser()
            parser.add_argument('--user', help='User app option')
            # ...
            # adds mlperf_prof options
            args = mlperf_prof.parse_args(parser)
        '''
        global _Metrics

        timemory.init()

        parser.add_argument('--disable-prof', action='store_true',
                            help='Disable performance analysis')
        parser.add_argument('-c', '--metrics', default=_Metrics, nargs='+',
                            type=str, help='Select metrics to collect')
        parser.add_argument('-P', '--profile', action='store_true',
                            help='Enable full Python profiling')
        parser.add_argument('-T', '--trace', action='store_true',
                            help='Enable full Python tracing (line-by-line)')
        parser.add_argument('--perf-output-dir', default=None, type=str,
                            help='Output directory')
        parser.add_argument('--perf-output-mode', default=['cout', 'text'], type=str,
                            choices=('text', 'json', 'cout',
                                     'flamegraph', 'plot'),  nargs='+',
                            help='Output types')

        args = parser.parse_args()
        # handle known settings
        timemory.settings.enabled = not args.disable_prof
        if not args.disable_prof:
            _Metrics = args.metrics
            timemory.settings.global_components = ','.join(args.metrics)
            timemory.settings.profiler_components = ','.join(args.metrics)
            if args.perf_output_dir is not None:
                timemory.settings.output_path = args.perf_output_dir

            timemory.settings.text_output = True if 'text' in args.perf_output_mode else False
            timemory.settings.json_output = True if 'json' in args.perf_output_mode else False
            timemory.settings.cout_output = True if 'cout' in args.perf_output_mode else False
            timemory.settings.plot_output = True if 'plot' in args.perf_output_mode else False
            timemory.settings.flamegraph_output = True if 'flamegraph' in args.perf_output_mode else False

            # create a built-in @mlperf_prof_record decorator
            if args.profile:
                _Prof = profile()
            elif args.trace:
                _Prof = trace()
            else:
                _Prof = marker()

            builtins.__dict__['mlperf_prof.record'] = _Prof
        else:
            _Metrics = []

        return args

except Exception as e:
    print(e)

    def get_results(report=False):
        return {}

    def finalize():
        pass

    def parse_args(parser):
        return parser.parse_args()

    class marker(object):
        '''Dummy decorator/context-manager for all stages of an ML-Perf Benchmark

        Usage:
            @mlperf_prof.marker
            def myfunc():
                # ...
                using mlperf_prof.marker:
                    # ...
        '''

        def __init__(self):
            pass

        def __call__(self, func):

            @wraps(func)
            def function_wrapper(*args, **kwargs):
                _ret = func(*args, **kwargs)
                return _ret
            return function_wrapper

        def __enter__(self, *args, **kwargs):
            pass

        def __exit__(self, exc_type, exc_value, exc_traceback):
            if exc_type is not None and exc_value is not None and exc_traceback is not None:
                import traceback
                traceback.print_exception(
                    exc_type, exc_value, exc_traceback, limit=5)

    class profile(timemory.profiler.profile):
        '''
        Implements full profiling for every Python function call

        Usage:
            @mlperf_prof.profile
            def myfunc():
                # ...
                using mlperf_prof.profile:
                    # ...
        '''

        def __init__(self, *args, **kwargs):
            super(profile, self).__init__(*args, **kwargs)

    class trace(timemory.line_profiler.LineProfiler):
        '''
        Implements full line-by-line profiling for every Python

        Usage:
            @mlperf_prof.trace
            def myfunc():
                # ...
        '''

        def __init__(self, *args, **kwargs):
            super(trace, self).__init__(*args, **kwargs)

    class timer(object):
        '''Implements a timer of the selected type
        '''

        def __init__(self, dtype):
            self._obj = None

        def get(self):
            return 0.0

        def start(self):
            pass

        def stop(self):
            pass

        def laps(self):
            return 0

        def units(self):
            return 0

        def display_units(self):
            return ''

_Prof = marker()
builtins.__dict__['mlperf_prof_record'] = _Prof
