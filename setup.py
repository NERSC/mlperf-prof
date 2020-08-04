#!/usr/bin/env python

import os
import sys
import argparse
import warnings
import platform
from distutils.core import setup


def get_project_version():
    # open "VERSION"
    with open(os.path.join(os.getcwd(), 'VERSION'), 'r') as f:
        data = f.read().replace('\n', '')
    # make sure is string
    if isinstance(data, list) or isinstance(data, tuple):
        return data[0]
    else:
        return data


def get_long_description():
    long_descript = ''
    try:
        long_descript = open('README.md').read()
    except Exception:
        long_descript = ''
    return long_descript


def get_short_description():
    return "{} {} {}".format(
        "Lightweight cross-language instrumentation API for C, C++, Python,",
        "Fortran, and CUDA which allows arbitrarily bundling tools together",
        "into a single performance analysis handle")


def get_keywords():
    return ['profiling']


def get_classifiers():
    return [
        # no longer beta
        'Development Status :: 5 - Production/Stable',
        # performance monitoring
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        # can be used for all of below
        'Topic :: Software Development :: Testing',
        'Topic :: Software Development :: Quality Assurance',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities',
        # written in English
        'Natural Language :: English',
        # MIT license
        'License :: OSI Approved :: MIT License',
        # tested on these OSes
        'Operating System :: MacOS',
        'Operating System :: Microsoft :: Windows :: Windows 10',
        'Operating System :: POSIX :: Linux',
        'Operating System :: POSIX :: BSD',
        # written in C++, available to Python via PyBind11
        'Programming Language :: Python :: 3',
    ]


def get_name():
    return 'Jonathan R. Madsen'


def get_email():
    return 'jrmadsen@lbl.gov'


def get_entry_points():
    # not yet implemented
    # return {
    #    'console_scripts': [
    #        'mlperf-line-profiler=mlperf_prof.line_profiler.__main__:main',
    #        'mlperf-profiler=mlperf_prof.profiler.__main__:main'],
    # }
    return {}


def parse_requirements(fname='requirements.txt', with_version=False):
    """
    Parse the package dependencies listed in a requirements file but strips
    specific versioning information.

    Args:
        fname (str): path to requirements file
        with_version (bool, default=False): if true include version specs

    Returns:
        List[str]: list of requirements items

    CommandLine:
        python -c "import setup; print(setup.parse_requirements())"
        python -c "import setup; print(chr(10).join(
            setup.parse_requirements(with_version=True)))"
    """
    from os.path import exists
    import re
    require_fpath = fname

    def parse_line(line):
        """
        Parse information from a line in a requirements text file
        """
        if line.startswith('-r '):
            # Allow specifying requirements in other files
            target = line.split(' ')[1]
            for info in parse_require_file(target):
                yield info
        else:
            info = {'line': line}
            if line.startswith('-e '):
                info['package'] = line.split('#egg=')[1]
            else:
                # Remove versioning from the package
                pat = '(' + '|'.join(['>=', '==', '>']) + ')'
                parts = re.split(pat, line, maxsplit=1)
                parts = [p.strip() for p in parts]

                info['package'] = parts[0]
                if len(parts) > 1:
                    op, rest = parts[1:]
                    if ';' in rest:
                        # Handle platform specific dependencies
                        # http://setuptools.readthedocs.io/en/latest/setuptools.html#declaring-platform-specific-dependencies
                        version, platform_deps = map(
                            str.strip, rest.split(';'))
                        info['platform_deps'] = platform_deps
                    else:
                        version = rest  # NOQA
                    info['version'] = (op, version)
            yield info

    def parse_require_file(fpath):
        with open(fpath, 'r') as f:
            for line in f.readlines():
                line = line.strip()
                if line and not line.startswith('#'):
                    for info in parse_line(line):
                        yield info

    def gen_packages_items():
        if exists(require_fpath):
            for info in parse_require_file(require_fpath):
                parts = [info['package']]
                if with_version and 'version' in info:
                    parts.extend(info['version'])
                if not sys.version.startswith('3.4'):
                    # apparently package_deps are broken in 3.4
                    platform_deps = info.get('platform_deps')
                    if platform_deps is not None:
                        parts.append(';' + platform_deps)
                item = ''.join(parts)
                yield item

    packages = list(gen_packages_items())
    return packages


with warnings.catch_warnings():
    setup(
        name='mlperf-prof',
        packages=['mlperf_prof'],
        version=get_project_version(),
        include_package_data=False,
        author=get_name(),
        author_email=get_email(),
        maintainer=get_name(),
        maintainer_email=get_email(),
        contact=get_name(),
        contact_email=get_email(),
        description=get_short_description(),
        long_description=get_long_description(),
        long_description_content_type='text/markdown',
        license='MIT',
        url='https://github.com/NERSC/mlperf-prof',
        download_url='https://github.com/NERSC/mlperf-prof.git',
        zip_safe=False,
        setup_requires=[],
        install_requires=[],
        extras_require={
            'all': parse_requirements('requirements.txt'),
        },
        keywords=get_keywords(),
        classifiers=get_classifiers(),
        python_requires='>=3',
        entry_points=get_entry_points(),
    )
