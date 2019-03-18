#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""
from __future__ import print_function
from setuptools import setup, find_packages

import os
import sys
import subprocess
import imp
if 'check_output' not in dir(subprocess):
 def check_output(cmd_args, *args, **kwargs):
     proc = subprocess.Popen(
	 cmd_args, *args,
	 stdout=subprocess.PIPE, stderr=subprocess.PIPE, **kwargs)
     out, err = proc.communicate()
     if proc.returncode != 0:
	 raise subprocess.CalledProcessError(args)
     return out
 subprocess.check_output = check_output

from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand
from distutils import spawn
from glob import glob

try:
 import colorama
 colorama.init()  # Initialize colorama on Windows
except ImportError:
 # Don't require colorama just for running paver tasks. This allows us to
 # run `paver install' without requiring the user to first have colorama
 # installed.
 pass

# Add the current directory to the module search path
sys.path.insert(0, os.path.abspath('.'))
#Constants
CODE_DIRECTORY = 'puticr'
DOCS_DIRECTORY = 'docs'
TESTS_DIRECTORY = 'tests'
PYTEST_FLAGS = ['--doctest-modules']

# Import metadata
metadata = imp.load_source(
        'metadata', os.path.join(CODE_DIRECTORY, 'metadata.py'))

## Miscellaneous helper functions

def get_project_files():
 """Retrieve a list of project files, ignoring hidden files.

 :return: sorted list of project files
 :rtype: :class:`list`
 """
 if is_git_project() and has_git():
     return get_git_project_files()

 project_files = []
 for top, subdirs, files in os.walk('.'):
     for subdir in subdirs:
	 if subdir.startswith('.'):
	     subdirs.remove(subdir)

     for f in files:
	 if f.startswith('.'):
	     continue
	 project_files.append(os.path.join(top, f))

 return project_files


def is_git_project():
  return os.path.isdir('.git')


def has_git():
  return bool(spawn.find_executable("git"))

def get_git_project_files():
 """Retrieve a list of all non-ignored files, including untracked files,
 excluding deleted files.

 :return: sorted list of git project files
 :rtype: :class:`list`
 """
 cached_and_untracked_files = git_ls_files(
     '--cached',  # All files cached in the index
     '--others',  # Untracked files
     # Exclude untracked files that would be excluded by .gitignore, etc.
     '--exclude-standard')
 uncommitted_deleted_files = git_ls_files('--deleted')

 # Since sorting of files in a set is arbitrary, return a sorted list to
 # provide a well-defined order to tools like flake8, etc.
 return sorted(cached_and_untracked_files - uncommitted_deleted_files)


def git_ls_files(*cmd_args):
 """Run ``git ls-files`` in the top-level project directory. Arguments go
 directly to execution call.

 :return: set of file names
 :rtype: :class:`set`
 """
 cmd = ['git', 'ls-files']
 cmd.extend(cmd_args)
 return set(subprocess.check_output(cmd).splitlines())


def print_success_message(message):
 """Print a message indicating success in green color to STDOUT.

 :param message: the message to print
 :type message: :class:`str`
 """
 try:
     import colorama
     print(colorama.Fore.GREEN + message + colorama.Fore.RESET)
 except ImportError:
     print(message)

def print_failure_message(message):
 """Print a message indicating failure in red color to STDERR.

 :param message: the message to print
 :type message: :class:`str`
 """
 try:
     import colorama
     print(colorama.Fore.RED + message + colorama.Fore.RESET,
	   file=sys.stderr)
 except ImportError:
     print(message, file=sys.stderr)


def read(filename):
 """Return the contents of a file.

 :param filename: file path
 :type filename: :class:`str`
 :return: the file's content
 :rtype: :class:`str`
 """
 with open(os.path.join(os.path.dirname(__file__), filename)) as f:
     return f.read()


def _lint():
 """Run lint and return an exit code."""
 # Flake8 doesn't have an easy way to run checks using a Python function, so
 # just fork off another process to do it.

 # Python 3 compat:
 # - The result of subprocess call outputs are byte strings, meaning we need
 #   to pass a byte string to endswith.
 project_python_files = [filename for filename in get_project_files()
			 if filename.endswith(b'.py')]
 retcode = subprocess.call(
     ['flake8', '--max-complexity=10'] + project_python_files)
 if retcode == 0:
     print_success_message('No style errors')
 return retcode

def _test():
 """Run the unit tests.

 :return: exit code
 """
 # Make sure to import pytest in this function. For the reason, see here:
 # <http://pytest.org/latest/goodpractises.html#integration-with-setuptools-test-commands>  # NOPEP8
 import pytest
 # This runs the unit tests.
 # It also runs doctest, but only on the modules in TESTS_DIRECTORY.
 return pytest.main(PYTEST_FLAGS + [TESTS_DIRECTORY])


def _test_all():
 """Run lint and tests.

 :return: exit code
 """
 return _lint() + _test()

class TestAllCommand(TestCommand):
     def finalize_options(self):
         TestCommand.finalize_options(self)
         # These are fake, and just set to appease distutils and setuptools.
         self.test_suite = True
         self.test_args = []

     def run_tests(self):
         raise SystemExit(_test_all())


 # define install_requires for specific Python versions
python_version_specific_requires = []

 # as of Python >= 2.7 and >= 3.2, the argparse module is maintained within
 # the Python standard library, otherwise we install it as a separate package
if sys.version_info < (2, 7) or (3, 0) <= sys.version_info < (3, 3):
    python_version_specific_requires.append('argparse')

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = ['Click>=6.0', ]

setup_requirements = ['pytest-runner', ]

test_requirements = ['pytest', ]
#GLOBDIR = glob('puticr/download/cgmaptools-0.1.2/bin/CG*')
setup_dict = dict(
    author="Dereje Jima",
    author_email='ddjima2014@gmail.com',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    description="Program to idenentify putative imprint control region (ICR) from Whole genome methylation data.",
    entry_points={
        'console_scripts': [
            'puticr_cli=puticr.main:main',
        ],
    },
    
    install_requires=requirements,
    license='MIT',
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='puticr',
    name='puticr',
    packages=find_packages(include=['puticr']),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/demis001/puticr',
    version='0.1.0',
    zip_safe=False,
    
    
    scripts = [
        'puticr/download/TrimGalore-0.5.0/trim_galore',
        'puticr/download/bowtie2-2.3.4.3-linux-x86_64/bowtie2',
        'puticr/download/bowtie2-2.3.4.3-linux-x86_64/bowtie2-align-l', 
        'puticr/download/bowtie2-2.3.4.3-linux-x86_64/bowtie2-align-l-debug', 
        'puticr/download/bowtie2-2.3.4.3-linux-x86_64/bowtie2-inspect-l-debug', 
        'puticr/download/bowtie2-2.3.4.3-linux-x86_64/bowtie2-align-s-debug', 
        'puticr/download/bowtie2-2.3.4.3-linux-x86_64/bowtie2-inspect-s-debug', 
        'puticr/download/bowtie2-2.3.4.3-linux-x86_64/bowtie2-build-l', 
        'puticr/download/bowtie2-2.3.4.3-linux-x86_64/bowtie2-build-l-debug', 
        'puticr/download/bowtie2-2.3.4.3-linux-x86_64/bowtie2-inspect-s', 
        'puticr/download/bowtie2-2.3.4.3-linux-x86_64/bowtie2-build-s-debug', 
        'puticr/download/bowtie2-2.3.4.3-linux-x86_64/bowtie2-align-s', 
        'puticr/download/bowtie2-2.3.4.3-linux-x86_64/bowtie2-build-s', 
        'puticr/download/bowtie2-2.3.4.3-linux-x86_64/bowtie2-inspect', 
        'puticr/download/bowtie2-2.3.4.3-linux-x86_64/bowtie2-inspect-l', 
        'puticr/download/bowtie2-2.3.4.3-linux-x86_64/bowtie2-build',
        'puticr/download/samtools/samtools',
        'puticr/download/cgmaptools-0.1.2/bin/ATCGbzFetchRegion',
        'puticr/download/cgmaptools-0.1.2/bin/ATCGbzToATCGmap',
        'puticr/download/cgmaptools-0.1.2/bin/ATCGmapMerge',
        'puticr/download/cgmaptools-0.1.2/bin/ATCGmapToATCGbz',
        'puticr/download/cgmaptools-0.1.2/bin/CGbzFetchRegion',
        'puticr/download/cgmaptools-0.1.2/bin/CGbzToCGmap',
        'puticr/download/cgmaptools-0.1.2/bin/CGmapFromBAM',
        'puticr/download/cgmaptools-0.1.2/bin/CGmapMethInBed',
        'puticr/download/cgmaptools-0.1.2/bin/CGmapMethInFragReg',
        'puticr/download/cgmaptools-0.1.2/bin/CGmapSelectByRegion',
        'puticr/download/cgmaptools-0.1.2/bin/CGmapToCGbz',
        'puticr/download/bedops24/bin/starchcluster_gnuParallel-float128', 
        'puticr/download/bedops24/bin/starchcluster_gnuParallel-megarow', 
        'puticr/download/bedops24/bin/starchcluster_gnuParallel-typical',
        'puticr/download/bedops24/bin/starchcluster_sge', 
        'puticr/download/bedops24/bin/starchcluster_sge-float128', 
        'puticr/download/bedops24/bin/starchcluster_sge-megarow', 
        'puticr/download/bedops24/bin/starchcluster_sge-typical', 
        'puticr/download/bedops24/bin/starchcluster_slurm', 
        'puticr/download/bedops24/bin/starchcluster_slurm-float128', 
        'puticr/download/bedops24/bin/starchcluster_slurm-megarow', 
        'puticr/download/bedops24/bin/starchcluster_slurm-typical', 
        'puticr/download/bedops24/bin/starch-diff', 
        'puticr/download/bedops24/bin/starch-diff-float128', 
        'puticr/download/bedops24/bin/starch-diff-megarow', 
        'puticr/download/bedops24/bin/starch-diff-typical', 
        'puticr/download/bedops24/bin/starch-float128', 
        'puticr/download/bedops24/bin/starch-megarow', 
        'puticr/download/bedops24/bin/starchstrip', 
        'puticr/download/bedops24/bin/starchstrip-float128', 
        'puticr/download/bedops24/bin/starchstrip-megarow', 
        'puticr/download/bedops24/bin/starchstrip-typical', 
        'puticr/download/bedops24/bin/starch-typical', 
        'puticr/download/bedops24/bin/switch-BEDOPS-binary-type', 
        'puticr/download/bedops24/bin/unstarch', 
        'puticr/download/bedops24/bin/unstarch-float128', 
        'puticr/download/bedops24/bin/unstarch-megarow', 
        'puticr/download/bedops24/bin/unstarch-typical', 
        'puticr/download/bedops24/bin/update-sort-bed-migrate-candidates', 
        'puticr/download/bedops24/bin/update-sort-bed-migrate-candidates-float128', 
        'puticr/download/bedops24/bin/update-sort-bed-migrate-candidates-megarow', 
        'puticr/download/bedops24/bin/update-sort-bed-migrate-candidates-typical', 
        'puticr/download/bedops24/bin/update-sort-bed-slurm', 
        'puticr/download/bedops24/bin/update-sort-bed-slurm-float128', 
        'puticr/download/bedops24/bin/update-sort-bed-slurm-megarow', 
        'puticr/download/bedops24/bin/update-sort-bed-slurm-typical', 
        'puticr/download/bedops24/bin/update-sort-bed-starch-slurm', 
        'puticr/download/bedops24/bin/update-sort-bed-starch-slurm-float128', 
        'puticr/download/bedops24/bin/update-sort-bed-starch-slurm-megarow', 
        'puticr/download/bedops24/bin/update-sort-bed-starch-slurm-typical', 
        'puticr/download/bedops24/bin/vcf2bed', 
        'puticr/download/bedops24/bin/vcf2bed-float128', 
        'puticr/download/bedops24/bin/vcf2bed-megarow', 
        'puticr/download/bedops24/bin/vcf2bed-typical', 
        'puticr/download/bedops24/bin/vcf2starch', 
        'puticr/download/bedops24/bin/vcf2starch-float128', 
        'puticr/download/bedops24/bin/vcf2starch-megarow', 
        'puticr/download/bedops24/bin/vcf2starch-typical', 
        'puticr/download/bedops24/bin/wig2bed', 
        'puticr/download/bedops24/bin/wig2bed-float128', 
        'puticr/download/bedops24/bin/wig2bed-megarow', 
        'puticr/download/bedops24/bin/wig2bed-typical', 
        'puticr/download/bedops24/bin/wig2starch', 
        'puticr/download/bedops24/bin/wig2starch-float128', 
        'puticr/download/bedops24/bin/wig2starch-megarow', 
        'puticr/download/bedops24/bin/wig2starch-typical',
        'puticr/download/bedops24/bin/bam2bed', 
        'puticr/download/bedops24/bin/bam2bed-float128', 
        'puticr/download/bedops24/bin/bam2bed_gnuParallel', 
        'puticr/download/bedops24/bin/bam2bed_gnuParallel-float128', 
        'puticr/download/bedops24/bin/bam2bed_gnuParallel-megarow', 
        'puticr/download/bedops24/bin/bam2bed_gnuParallel-typical', 
        'puticr/download/bedops24/bin/bam2bed-megarow', 
        'puticr/download/bedops24/bin/bam2bed_sge', 
        'puticr/download/bedops24/bin/bam2bed_sge-float128', 
        'puticr/download/bedops24/bin/bam2bed_sge-megarow', 
        'puticr/download/bedops24/bin/bam2bed_sge-typical', 
        'puticr/download/bedops24/bin/bam2bed_slurm', 
        'puticr/download/bedops24/bin/bam2bed_slurm-float128', 
        'puticr/download/bedops24/bin/bam2bed_slurm-megarow', 
        'puticr/download/bedops24/bin/bam2bed_slurm-typical', 
        'puticr/download/bedops24/bin/bam2bed-typical', 
        'puticr/download/bedops24/bin/bam2starch', 
        'puticr/download/bedops24/bin/bam2starch-float128', 
        'puticr/download/bedops24/bin/bam2starch_gnuParallel', 
        'puticr/download/bedops24/bin/bam2starch_gnuParallel-float128', 
        'puticr/download/bedops24/bin/bam2starch_gnuParallel-megarow', 
        'puticr/download/bedops24/bin/bam2starch_gnuParallel-typical', 
        'puticr/download/bedops24/bin/bam2starch-megarow', 
        'puticr/download/bedops24/bin/bam2starch_sge', 
        'puticr/download/bedops24/bin/bam2starch_sge-float128', 
        'puticr/download/bedops24/bin/bam2starch_sge-megarow', 
        'puticr/download/bedops24/bin/bam2starch_sge-typical', 
        'puticr/download/bedops24/bin/bam2starch_slurm', 
        'puticr/download/bedops24/bin/bam2starch_slurm-float128', 
        'puticr/download/bedops24/bin/bam2starch_slurm-megarow', 
        'puticr/download/bedops24/bin/bam2starch_slurm-typical', 
        'puticr/download/bedops24/bin/bam2starch-typical',
        'puticr/download/bedops24/bin/bedextract', 
        'puticr/download/bedops24/bin/bedextract-float128', 
        'puticr/download/bedops24/bin/bedextract-megarow', 
        'puticr/download/bedops24/bin/bedextract-typical', 
        'puticr/download/bedops24/bin/bedmap', 
        'puticr/download/bedops24/bin/bedmap-float128', 
        'puticr/download/bedops24/bin/bedmap-megarow', 
        'puticr/download/bedops24/bin/bedmap-typical', 
        'puticr/download/bedops24/bin/bedops', 
        'puticr/download/bedops24/bin/bedops-float128', 
        'puticr/download/bedops24/bin/bedops-megarow', 
        'puticr/download/bedops24/bin/bedops-typical',
        'puticr/download/bedops24/bin/closest-features', 
        'puticr/download/bedops24/bin/closest-features-float128', 
        'puticr/download/bedops24/bin/closest-features-megarow', 
        'puticr/download/bedops24/bin/closest-features-typical', 
        'puticr/download/bedops24/bin/convert2bed', 
        'puticr/download/bedops24/bin/convert2bed-float128', 
        'puticr/download/bedops24/bin/convert2bed-megarow', 
        'puticr/download/bedops24/bin/convert2bed-typical',
        'puticr/download/bedops24/bin/gff2bed', 
        'puticr/download/bedops24/bin/gff2bed-float128', 
        'puticr/download/bedops24/bin/gff2bed-megarow', 
        'puticr/download/bedops24/bin/gff2bed-typical', 
        'puticr/download/bedops24/bin/gff2starch', 
        'puticr/download/bedops24/bin/gff2starch-float128', 
        'puticr/download/bedops24/bin/gff2starch-megarow', 
        'puticr/download/bedops24/bin/gff2starch-typical', 
        'puticr/download/bedops24/bin/gtf2bed', 
        'puticr/download/bedops24/bin/gtf2bed-float128', 
        'puticr/download/bedops24/bin/gtf2bed-megarow', 
        'puticr/download/bedops24/bin/gtf2bed-typical', 
        'puticr/download/bedops24/bin/gtf2starch', 
        'puticr/download/bedops24/bin/gtf2starch-float128', 
        'puticr/download/bedops24/bin/gtf2starch-megarow', 
        'puticr/download/bedops24/bin/gtf2starch-typical', 
        'puticr/download/bedops24/bin/gvf2bed', 
        'puticr/download/bedops24/bin/gvf2bed-float128', 
        'puticr/download/bedops24/bin/gvf2bed-megarow', 
        'puticr/download/bedops24/bin/gvf2bed-typical', 
        'puticr/download/bedops24/bin/gvf2starch', 
        'puticr/download/bedops24/bin/gvf2starch-float128', 
        'puticr/download/bedops24/bin/gvf2starch-megarow', 
        'puticr/download/bedops24/bin/gvf2starch-typical',
        'puticr/download/bedops24/bin/sort-bed',
        'puticr/download/bedops24/bin/sort-bed-float128',
        'puticr/download/bedops24/bin/sort-bed-megarow',
        'puticr/download/bedops24/bin/sort-bed-typical',
        ],
    package_data = {
        'puticr': ['files/*'],
    },
)
# def runTasks():
#     """ Run paver taks
#     """
#     cmd = "paver install"/data1/jimaprogramming/python/puticr/puticr/bin
#     return subprocess.Popen(cmd, shell=True).communicate()
def main():
     #setup(**setup_dict)
     try:
         import paver.tasks
     except ImportError:
         if os.path.exists("paver-minilib.zip"):
             sys.path.insert(0, "paver-minilib.zip")
         else:
             raise ValueError("No paver in the path")
         import paver.tasks
     paver.tasks.main()
     #runTasks()
if __name__ == '__main__':
     main()

