# -*- coding: utf-8 -*-
from __future__ import print_function
from paver.setuputils import install_distutils_tasks
from paver.easy import options, task, needs, consume_args
import os
import sys
import time
import subprocess
from paver.easy import *
from os.path import islink, isfile, join, basename, dirname, exists, relpath, abspath
from paver.setuputils import setup
from sys import platform
try:
    from paver.virtual import bootstrap, virtualenv
except ImportError, e:
    info(
        "VirtualEnv must be installed to enable 'paver bootstrap'. If you need this command, run: pip install virtualenv"
    )
from setup import setup_dict, get_project_files, print_success_message, print_failure_message, _lint, _test, _test_all, CODE_DIRECTORY, DOCS_DIRECTORY, TESTS_DIRECTORY, PYTEST_FLAGS
# Import parameters from the setup file.
sys.path.append('.')


options(setup=setup_dict,
        star=Bunch(
            sdir=path('puticr/download'),
            bindir=path('puticr/bin')
        ),
        FastQC=Bunch(
            url='http://www.bioinformatics.babraham.ac.uk/projects/fastqc/fastqc_v0.11.2.zip',
            downloads=path('puticr/download'),
            installdir=join(sys.prefix, 'lib')
        ),
        cgmaptools=Bunch(
            url='https://github.com/guoweilong/cgmaptools/archive/v0.1.2.tar.gz',
            downloads=path('puticr/download'),
            installdir=join(sys.prefix, 'download',
                            'cgmaptools-0.1.2', 'cgmaptools')

        ),

        trimg=Bunch(
            url='https://github.com/FelixKrueger/TrimGalore/archive/0.5.0.tar.gz',
            downloads=path('puticr/download')

        ),
        settings=Bunch(
            shell_file=path('puticr/files/settings.sh'),
            binDir=path("puticr/bin")
        ),
        bsseeker2=Bunch(
            url="https://github.com/BSSeeker/BSseeker2/archive/BSseeker2-v2.1.8.tar.gz",
            downloads=path('puticr/download'),
            binDir=path("puticr/bin")

        ),
        bedops=Bunch(
            url="https://github.com/bedops/bedops/releases/download/v2.4.35/bedops_linux_x86_64-v2.4.35.tar.bz2",
            downloads=path('puticr/download'),
            binDir=path("puticr/bin"),
            installdir=join(sys.prefix, 'download','bedops24')

        ),
        samtools=Bunch(
            sdir=path('puticr/download'),
            bindir=path('puticr/bin')
        ),
        bowtie2=Bunch(
             url =path('https://github.com/BenLangmead/bowtie2/releases/download/v2.3.4.3/bowtie2-2.3.4.3-linux-x86_64.zip'),
             downloads=path('puticr/download'),
             olink =path('puticr/bin')
 
         ),
        # environ=Bunch(
        # installdir=path('puticr/lib')

        # ),
        # settings=Bunch(
        # shell_file=path('puticr/files/settings.sh')
        # ),
        # samtools=Bunch(
        # sdir=path('puticr/download'),
        # bindir=path('puticr/bin')
        # ),
        # help2man=Bunch(
        # sdir=path('puticr/download'),
        # url='http://ftp.gnu.org/gnu/help2man/help2man-1.43.3.tar.gz',
        # ),
        libtool=Bunch(
            sdir=path('puticr/download'),
            url='https://ftp.gnu.org/gnu/libtool/libtool-2.4.tar.gz'
        ),
        textinfo=Bunch(
            sdir=path('puticr/download'),
            url='http://ftp.gnu.org/gnu/texinfo/texinfo-6.1.tar.gz'
        ),
        graphviz=Bunch(
            sdir=path('puticr/download'),
            url='https://github.com/ellson/graphviz/releases/download/Nightly/graphviz-2.41.20170103.1755.tar.gz'
        ),
        virtualenv=Bunch(
            packages_to_install=[],
            no_site_packages=True)
        )
INSTRUICTIONS = """
Run
    $ source puticr/bin/activate
to enter the virtual environment and
    $ deactivate
to exit the environment.
 #sudo yum  install lzma-devel.x86_64 xz-devel.x86_64 pyliblzma.x86_64
"""
install_distutils_tasks()

# Miscellaneous helper functions


@task
def bootstrap(options):
    """Create virtualenv in ./bootstrap"""
    try:
        import virtualenv
    except ImportError, e:
        raise RuntimeError("Virtualenv is needed for bootstrap")
    options.virtualenv.no_site_packages = False
    options.bootstrap.no_site_packages = False
    call_task("paver.virtualenv.boostrap")


@task
def make_download_dir(options):
    currwd = os.getcwd()
    sdir = path(currwd) / options.star.sdir
    sh('mkdir -p %s' % (sdir))


@task
def download_compile_star(options):
    """installs the current package"""
    starbin = join(sys.prefix, 'bin', 'STAR')
    if not exists(starbin):
        info("Compiling STAR...")
        currwd = os.getcwd()
        sdir = path(currwd) / options.star.sdir
        bdir = path(currwd) / options.star.bindir
        dist = join(sys.prefix, 'bin', 'STAR')
        if not islink(dist):
            sh('(cd %s; wget https://github.com/alexdobin/STAR/archive/2.5.2b.tar.gz -O- | tar xzf -; cd STAR-2.5.2b; make; ln -s source/STAR %s; cd %s)' % (sdir, bdir, sdir))


@task
def download_compile_seqtk(options):
    """Download and compile seqtk"""
    appbin = join(sys.prefix, 'bin', 'seqtk')
    srcdir = join(options.seqtk.downloads, "seqtk")
    if not exists(appbin):
        if exists(srcdir):
            lbcmd = 'cd %s && cd seqtk && make' % (options.seqtk.downloads)
            sh(lbcmd)
        else:
            lbcmd = 'cd %s && git clone %s  && cd seqtk && make' % (
                options.seqtk.downloads, options.seqtk.url)
            sh(lbcmd)


@task
def download_compile_samtools(options):
    """installs the current package"""
    samtoolsbin = join(sys.prefix, 'bin', 'samtools')
    if not exists(samtoolsbin):
        info("Compiling samtools....")
        currwd = os.getcwd()
        sdir = path(currwd) / options.samtools.sdir
        sh('(cd %s; wget https://github.com/samtools/htslib/releases/download/1.8/htslib-1.8.tar.bz2 -O- | tar xjf -; mv htslib-* htslib;wget https://github.com/samtools/samtools/releases/download/1.8/samtools-1.8.tar.bz2 -O- | tar xjf -; mv samtools-* samtools; cd samtools;make; cd %s)' % (sdir, sdir))


@task
def install_fastax_lib(options):
    """Install lib required for fastx"""
    info("Installing lib required for fastx ...")
    installdir = abspath(options.fastx_lib.installdir)
    if not exists(installdir):
        lbcmd = 'cd %s   && wget %s && tar -xvf libgtextutils-0.7.tar.gz  && cd libgtextutils-0.7 && ./configure --prefix=%s && make &&  make install' % (
            options.fastx_lib.downloads, options.fastx_lib.url, installdir)
        sh(lbcmd)


@task
def install_trimg(options):
    """Install trim_glore toolkit ..."""
    info("Installing trim_glore toolkit ...")
    installdir = join(sys.prefix, 'download',
                      'TrimGalore-0.5.0', 'trim_galore')
    if not exists(installdir):
        cmd = 'cd %s && wget %s && tar -xvf 0.5.0.tar.gz' % (
            options.trimg.downloads, options.trimg.url)
        sh(cmd)


@task
def install_bsseeker2(options):
    """Install bsseeker2 from github repo ..."""
    info("Installing bsseeker2 from github ...")
    srcDir = abspath(options.bsseeker2.downloads)
    bsfile = join(sys.prefix, 'bin',  'bs_seeker2-align.py')
    if not exists(bsfile):
        cmds = 'cd %s && wget %s && tar -xzvf BSseeker2-v2.1.8.tar.gz && cd %s && mv BSseeker2-BSseeker2-v2.1.8 BSseeker2' % (
            srcDir, options.bsseeker2.url, srcDir)
        sh(cmds)
        bindir = join('puticr', 'bin')
        bsfile2 = join(sys.prefix, 'download', 'BSseeker2/')
@task
def install_bowtie2():
    info("Checking  bowtie2 aligner if exist")
    url = options.bowtie2.url
    bindir = options.bowtie2.olink
    downloadDir = options.bowtie2.downloads
    bowtie_bin = join(sys.prefix, 'bin', 'bowtie2')
    if not exists(bowtie_bin):
        info("Installing bowtie2 aligner ...")
        cmds = 'cd %s && wget %s  && unzip bowtie2-2.3.4.3-linux-x86_64.zip'%(downloadDir, url)
        sh(cmds)

@task
def download_compile_samtools(options):
    """installs the current package"""
    samtoolsbin=join(sys.prefix,'bin','samtools')
    if not exists(samtoolsbin):
        info("Compiling samtools....")
        currwd = os.getcwd()
        sdir = path(currwd) / options.samtools.sdir
        sh('(cd %s; wget https://github.com/samtools/htslib/archive/1.1.tar.gz -O- | tar xzf -; mv htslib-* htslib; \
        wget https://github.com/samtools/samtools/archive/1.1.tar.gz -O- | tar xzf -; mv samtools-* samtools; \
        cd samtools;make; cd %s)' % (sdir, sdir))



@task
def install_cgmaptools(options):
    """Install cgmaptools ..."""
    info("Installing cgmaptools ...")
    installdir = abspath(options.cgmaptools.installdir)
    srcdir = abspath(options.cgmaptools.installdir)
    if not exists(installdir):
        lbcmd = 'cd %s && wget %s && tar -xvf v0.1.2.tar.gz && cd cgmaptools-0.1.2 && ./install.sh' % (
            options.cgmaptools.downloads, options.cgmaptools.url)
        sh(lbcmd)

@task
def set_ld_path(options):
    """Create setting.sh file and source it"""
    srcdir = abspath(options.cgmaptools.installdir)
    cgmap = join(srcdir, "cgmaptools-0.1.2")
    src = options.settings.shell_file
    binDir = options.settings.binDir
    with open(src, 'w') as myfile:
        installdir = sys.prefix
        rldpath = os.path.join(installdir, binDir)
        sep = "$"
        ldpath = "export PATH=%s:%s:%sPATH\n" % (cgmap, rldpath, sep)
        myfile.write(ldpath)
    info(src)
    #sh('source %s' %(src))

@task
def installBedOps(options):
    if platform == "linux" or platform == "linux2":
       # linux
       
        info("Installing bedops ...")
        installdir = options.bedops.installdir
        if not exists(installdir):
            lbcmd = 'cd %s ;mkdir -p bedops24 ;cd bedops24 && wget %s  -O- |  tar -xjvf -' % (options.bedops.downloads, options.bedops.url)
            sh(lbcmd)
    elif platform == "darwin":
        # OS X
        pass 
    else:
        info("This operating system isn't supported ...")

@task
def download_compile_textinfo(options):
    """installs the textinfo, required by graphviz"""
    makeinfobin = join(sys.prefix, 'bin', 'makeinfo')
    srcfile = join(sys.prefix, "download", 'texinfo-6.1.tar.gz')
    if not exists(makeinfobin) and not exists(srcfile):
        info("Installing textinfo...")
        currwd = os.getcwd()
        sdir = path(currwd) / options.textinfo.sdir
        url = options.textinfo.url
        info(sdir)
        sh('(cd %s; wget %s; tar -xzvf texinfo-6.1.tar.gz;cd texinfo-6.1;./configure --prefix=%s/texinfo-6.1;make;make install)' % (sdir, url, sdir))


@task
def download_compile_help2man(options):
    """installs the help2man, required by graphviz"""
    help2manbin = join(sys.prefix, 'bin', 'help2man')
    info(help2manbin)
    srcfile = join(sys.prefix, "download", 'help2man-1.43.3.tar.gz')
    if not exists(help2manbin) and not exists(srcfile):
        info("Installing help2man...")
        currwd = os.getcwd()
        sdir = path(currwd) / options.help2man.sdir
        url = options.help2man.url
        src = join(sys.prefix, "download", 'help2man-1.43.3')
        info(sdir)
        sh('cd %s; wget %s;tar -xzvf help2man-1.43.3.tar.gz; cd help2man-1.43.3; ./configure CC="cc" --prefix=%s;make;make install' % (sdir, url, src))


@task
# @needs('download_compile_help2man', 'download_compile_textinfo')
def download_compile_libtool(options):
    """installs libtool, needed by graphviz ... """
    libtoolbin = join(sys.prefix, 'bin', 'libtool')
    srcfile = join(sys.prefix, "download", 'libtool-2.4.tar.gz')
    if not exists(libtoolbin) and not exists(srcfile):
        info("Installing libtool, needed by graphviz ...")
        currwd = os.getcwd()
        sdir = path(currwd) / options.libtool.sdir
        url = options.libtool.url
        info(sdir)
        sh('(cd %s; wget %s; tar -xzvf libtool-2.4.tar.gz;cd libtool-2.4;./configure CC="cc" --prefix=%s/libtool-2.4;make;make install)' % (sdir, url, sdir))


@task
@needs('download_compile_libtool')
def download_compile_graphviz(options):
    """installs the current package"""
    graphvizbin = join(sys.prefix, 'bin', 'dot')
    currwd = os.getcwd()
    ssdir = path(currwd) / options.graphviz.sdir / \
        "graphviz-2.41.20170103.1755"
    info(graphvizbin)
    if not exists(graphvizbin):
        info("Installing graphviz...")
        #sdir =path(currwd) / options.graphviz.sdir
        info(ssdir)
        sh('(cd %s;rm -rf %s; wget %s -O- | tar xzf -;cd  graphviz-2.41.20170103.1755;./configure --prefix=%s;make;make install)' %
           (options.graphviz.sdir, ssdir, options.graphviz.url, ssdir))


@task
def download_install_fastqc(options):
    import zipfile
    from glob import glob
    dlpath = join(options.FastQC.downloads, 'fastqc_v*.zip')
    fastqczip = glob(dlpath)
    # No need to redownload
    if not len(fastqczip):
        info("Downloading FastQC from %s" % options.FastQC.url)
        dlcmd = 'cd %s && [ ! -e fastqc*.zip ] && wget %s' % (
            options.FastQC.downloads, options.FastQC.url)
        sh(dlcmd)
    else:
        info("FastQC Already downloaded")
    fastqczip = glob(dlpath)
    fqcdir = join(options.FastQC.installdir, 'FastQC')
    # Check to see if it is extracted already
    if not exists(fqcdir):
        info("Unpacking FastQC")
        zfh = zipfile.ZipFile(fastqczip[-1])
        zfh.extractall(options.FastQC.installdir)
        zfh.close()
    else:
        info("FastQC already unpacked")
    # Make symlink to bin
    src = relpath(join(fqcdir, 'fastqc'), join(sys.prefix, 'bin'))
    dst = join(sys.prefix, 'bin', 'fastqc')
    if not exists(dst):
        info("Installing fastqc symlink")
        os.symlink(src, dst)
        os.chmod(dst, 0755)
    else:
        info("fastqc symlink already exists")


def is_tool(name):
    """Install R if not already installed.
    :return True

    """
    import subprocess
    import os
    try:
        devnull = open(os.devnull)
        subprocess.Popen([name], stdout=devnull, stderr=devnull).communicate()
    except OSError as e:
        if e.errno == os.errno.ENOENT:
            return False
    return True


@task
def install_R(options):
    """TODO: Docstring for function.

    :arg1: TODO
    :returns: TODO

    """
    if is_tool("R") == False:
        info("R doesn't exist, installing")
    else:
        pass


def print_passed():
    # generated on http://patorjk.com/software/taag/#p=display&f=Small&t=PASSED
    print_success_message(r'''  ___  _   ___ ___ ___ ___
 | _ \/_\ / __/ __| __|   \
 |  _/ _ \\__ \__ \ _|| |) |
 |_|/_/ \_\___/___/___|___/
''')


def print_failed():
    # generated on http://patorjk.com/software/taag/#p=display&f=Small&t=FAILED
    print_failure_message(r'''  ___ _   ___ _    ___ ___
 | __/_\ |_ _| |  | __|   \
 | _/ _ \ | || |__| _|| |) |
 |_/_/ \_\___|____|___|___/
''')


class cwd(object):
    """Class used for temporarily changing directories. Can be though of
    as a `pushd /my/dir' then a `popd' at the end.
    """

    def __init__(self, newcwd):
        """:param newcwd: directory to make the cwd
        :type newcwd: :class:`str`
        """
        self.newcwd = newcwd

    def __enter__(self):
        self.oldcwd = os.getcwd()
        os.chdir(self.newcwd)
        return os.getcwd()

    def __exit__(self, type_, value, traceback):
        # This acts like a `finally' clause: it will always be executed.
        os.chdir(self.oldcwd)


# Task-related functions

def _doc_make(*make_args):
    """Run make in sphinx' docs directory.

    :return: exit code
    """
    if sys.platform == 'win32':
        # Windows
        make_cmd = ['make.bat']
    else:
        # Linux, Mac OS X, and others
        make_cmd = ['make']
    make_cmd.extend(make_args)

    # Account for a stupid Python "bug" on Windows:
    # <http://bugs.python.org/issue15533>
    with cwd(DOCS_DIRECTORY):
        retcode = subprocess.call(make_cmd)
    return retcode


# Tasks


@task
def init():
    """Initializing everything so you can start working"""
    info("virtual environment successfully bootstrapped.")
    info(INSTRUICTIONS)


@task
@needs('install_python_dependencies', 'install_other_dependencies')
def install_dependencies():
    pass


@task
# @needs('download_compile_star', 'download_install_fastqc', 'download_compile_seqtk','download_compile_samtools','install_fastax_lib', 'install_fastx', 'in)
@needs('install_cgmaptools', 'install_bsseeker2', 'install_trimg', 'install_bowtie2', 'download_compile_samtools', 'set_ld_path', 'installBedOps')
def install_other_dependencies():
    pass


@task
def install_python_dependencies():
    import pip
    if pip.__version__ > 6.0:
        sh('pip install -r requirements_dev.txt')

    else:
        sh('pip install -r requirements_dev.txt  --cache-dir puticr/download/.pip_cache')

@task
@needs('install_dependencies', 'setuptools.command.install')
def install():
    pass


@task
@needs('install')
def develop():
    pass


@task
@needs('prepare', 'doc_html', 'setuptools.command.sdist')
def sdist():
    """Build the HTML docs and the tarball."""
    pass


@task
def test():
    """Run the unit tests."""
    raise SystemExit(_test())


@task
def lint():
    # This refuses to format properly when running `paver help' unless
    # this ugliness is used.
    ('Perform PEP8 style check, run PyFlakes, and run McCabe complexity '
     'metrics on the code.')
    raise SystemExit(_lint())


@task
def test_all():
    """Perform a style check and run all unit tests."""
    retcode = _test_all()
    if retcode == 0:
        print_passed()
    else:
        print_failed()
    raise SystemExit(retcode)


@task
@consume_args
def run(args):
    """Run the package's main script. All arguments are passed to it."""
    # The main script expects to get the called executable's name as
    # argv[0]. However, paver doesn't provide that in args. Even if it did (or
    # we dove into sys.argv), it wouldn't be useful because it would be paver's
    # executable. So we just pass the package name in as the executable name,
    # since it's close enough. This should never be seen by an end user
    # installing through Setuptools anyway.
    from puticr.main import main
    raise SystemExit(main([CODE_DIRECTORY] + args))


@task
def commit():
    """Commit only if all the tests pass."""
    if _test_all() == 0:
        subprocess.check_call(['git', 'commit'])
    else:
        print_failure_message('\nTests failed, not committing.')


@task
def coverage():
    """Run tests and show test coverage report."""
    try:
        import pytest_cov  # NOQA
    except ImportError:
        print_failure_message(
            'Install the pytest coverage plugin to use this task, '
            "i.e., `pip install pytest-cov'.")
        raise SystemExit(1)
    import pytest
    pytest.main(PYTEST_FLAGS + [
        '--cov', CODE_DIRECTORY,
        '--cov-report', 'term-missing',
        TESTS_DIRECTORY])


@task  # NOQA
def doc_watch():
    """Watch for changes in the docs and rebuild HTML docs when changed."""
    try:
        from watchdog.events import FileSystemEventHandler
        from watchdog.observers import Observer
    except ImportError:
        print_failure_message('Install the watchdog package to use this task, '
                              "i.e., `pip install watchdog'.")
        raise SystemExit(1)

    class RebuildDocsEventHandler(FileSystemEventHandler):
        def __init__(self, base_paths):
            self.base_paths = base_paths

        def dispatch(self, event):
            """Dispatches events to the appropriate methods.
            :param event: The event object representing the file system event.
            :type event: :class:`watchdog.events.FileSystemEvent`
            """
            for base_path in self.base_paths:
                if event.src_path.endswith(base_path):
                    super(RebuildDocsEventHandler, self).dispatch(event)
                    # We found one that matches. We're done.
                    return

        def on_modified(self, event):
            print_failure_message('Modification detected. Rebuilding docs.')
            # # Strip off the path prefix.
            # import os
            # if event.src_path[len(os.getcwd()) + 1:].startswith(
            #         CODE_DIRECTORY):
            #     # sphinx-build doesn't always pick up changes on code files,
            #     # even though they are used to generate the documentation. As
            #     # a workaround, just clean before building.
            doc_html()
            print_success_message('Docs have been rebuilt.')

    print_success_message(
        'Watching for changes in project files, press Ctrl-C to cancel...')
    handler = RebuildDocsEventHandler(get_project_files())
    observer = Observer()
    observer.schedule(handler, path='.', recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        observer.join()


@task
@needs('doc_html')
def doc_open():
    """Build the HTML docs and open them in a web browser."""
    doc_index = os.path.join(DOCS_DIRECTORY, 'build', 'html', 'index.html')
    if sys.platform == 'darwin':
        # Mac OS X
        subprocess.check_call(['open', doc_index])
    elif sys.platform == 'win32':
        # Windows
        subprocess.check_call(['start', doc_index], shell=True)
    elif sys.platform == 'linux2':
        # All freedesktop-compatible desktops
        subprocess.check_call(['xdg-open', doc_index])
    else:
        print_failure_message(
            "Unsupported platform. Please open `{0}' manually.".format(
                doc_index))


@task
def get_tasks():
    """Get all paver-defined tasks."""
    from paver.tasks import environment
    for task in environment.get_tasks():
        print(task.shortname)


@task
def doc_html():
    """Build the HTML docs."""
    retcode = _doc_make('html')

    if retcode:
        raise SystemExit(retcode)


@task
def doc_clean():
    """Clean (delete) the built docs."""
    retcode = _doc_make('clean')

    if retcode:
        raise SystemExit(retcode)
