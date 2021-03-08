import time
import datetime
import os
import sys
import subprocess
import yaml
import shutil
from helpers import get_options, make_logger, runCommand,which,run_cmd
import os.path
from pkg_resources import resource_filename, resource_stream
import click


def work_dir(dirname):
    """get the current working dir"""
    if not dirname:
        currpath =os.getcwd()
        dir_to_create = currpath + "/" + dirname
        print dir_to_create
        os.mkdir(dir_to_create, 0755)
        return

def rmdir(dirname):
    """remove dir"""
    if os.path.exists(dirname):
        shutil.rmtree(dirname)
        return

def mkdir(dirname):
    """make dir"""
    if not os.path.exists(dirname):
        os.mkdir(dirname)
        return
def creatSymLink(src, dist):
    os.symlink(src, dist)
    return

def trimFastq(input, output, trimLeft, proFastq):
    """Clean fastq file using trim_galore"""
    cmds = [
        'trim_galore', '-q', str(20),
        '--stringency', str(5),
        '--trim1',
        '--clip_R1', str(trimLeft),
        '--trim-n',
        '--phred33',
        '--gzip', '--illumina',
        input,
        '-o', proFastq,
    ]
    cmds ='  '.join(cmds)
    runCommand(cmds, True)
    return
def copyFileToAnaFolder(file_to_copy, file_copy):
    """copy the mapfile to analysis dir
    Arguments:
        - `file_to_copy`: The mapfile from
        - ` file_copy`: a copy of mapfile
    """
    shutil.copyfile(file_to_copy, file_copy)
    return
def bowtie2_genomeIndex(fa_file, genomeDir, thread):
    t = str(thread)
    thrd = "--bt2--threads=" + t
    cmds = ['bs_seeker2-build.py',
            '-f',  fa_file,
            '--aligner=bowtie2',
            thrd,
            '-d', genomeDir,
    ]
    cmds = '  '.join(cmds)
    runCommand(cmds, True)
    return
# '-i', input,
def alignBsData(input, output, thread, genomeDir, fa_file):
    click.echo(input)
    cmds = [
        'bs_seeker2-align.py',
        '-i', input,
        '-f','bam',
        '--bt2-p', str(thread),
        '-m', str(4),
        '--bt2-I', str(0),
        '--bt2-X', str(1000),
        '-d',genomeDir,
        '--aligner=bowtie2',
        '-g', fa_file,
        '--bt2--local',
    ]
    cmds = '  '.join(cmds)
    runCommand(cmds, True)
    return

def sortBam(input, output, thread):
    myDir, baseFile = os.path.split(input)
    tempFile = "temp_" + baseFile
    tempFile = myDir + "/" + tempFile
    cmds = [
        'samtools sort',
        '-@', str(thread),
        input,
        '-o', output,
        '-T', tempFile,
    ]
    cmds = ' '.join(cmds)
    runCommand(cmds, True)
    return

def indexBam(input, output, thread):
    click.echo(output)
    cmds = [
        'samtools index',
        '-b',
        input,
        '>', output,
    ]
    cmds = ' '.join(cmds)
    runCommand(cmds, True)
    return

def sameTissueBamMerge(input, output):
    if len(input) > 1:

        inFile = " ".join(input)
        myDir, baseFile = os.path.split(output)
        cmds = [
            'samtools merge',
            baseFile,
            inFile,

        ]
        cmds = ' '.join(cmds)
        runCommand(cmds, True)
        cmds2 = [
            'mv',
            baseFile,
            myDir,
        ]
        cmds2 = ' '.join(cmds2)
        runCommand(cmds2, True)
        return
    else:
        inFile = " ".join(input)
        cmds = [
            'cp ', inFile,
            output,
        ]
        cmds = ' '.join(cmds)
        runCommand(cmds, True)
        return


def bamToCGmap(input, output,faFile):

    cmds = [
        'cgmaptools convert  bam2cgmap',
        '-b',input,
        '-g', faFile,
        '-o', output,
    ]
    cmds = ' '.join(cmds)
    runCommand(cmds, True)
    return
def extractCGcontext(input, output):

    cmds = [
        'zcat',
        input,
        '| grep "CG" >',
        output,
    ]
    cmds = ' '.join(cmds)
    runCommand(cmds, True)
    return

def mergeConsecutiveCGcall(input, output):

    cmds = [
        'update_CGmap2.py',
        '-f', input,
        '>',
        output,
    ]
    cmds = ' '.join(cmds)
    runCommand(cmds, True)
    return
def identifyICRhotSpot(input, output, lowerMeth, upperMeth):

    cmds = [
        'identify_hotspot_V2.py',
        '-f', input,
        '-l', str(lowerMeth),
        '-u',  str(upperMeth),
        '>',
        output,
    ]
    cmds = ' '.join(cmds)
    runCommand(cmds, True)
    return

def textToBed(input, output):

    cmds = [
        'grep -v "start"', input,
        '| awk',
        '\'{print "chr"$1"\t"$2"\t"$3"\t"$4"\t"$5"\t"$6"\t"$7"\t"$8}\' >',output,
    ]
    cmds = ' '.join(cmds)
    runCommand(cmds, True)
    return

def createUnionBed(input, output):
    myinput = "  ".join(input)
    cmds = [
        'awk',
        '\'{ print $1"\t"$2"\t"$3"\t"FILENAME }\'', myinput,
        '| sort-bed - >',
        output,
    ]
    cmds = ' '.join(cmds)
    runCommand(cmds, True)
    return

def createMergedBed(input, output):
    myinput = "  ".join(input)
    cmds = [
        'bedops -m ',myinput,
        '>',
        output,
    ]
    cmds = ' '.join(cmds)
    runCommand(cmds, True)
    return

def createCountICR(input, output):
    myinput = "  ".join(input)
    cmds = [
        'bedmap --echo --echo-map-id-uniq --bp-ovr 10 --delim "\t"',myinput,
        '| awk \'{ print $1"\t"$2"\t"$3"\t"split($4, a, ";"); }\' >',
        output,
    ]
    cmds = ' '.join(cmds)
    runCommand(cmds, True)
    return

def createQuality(input, output):
    """Check quality of the fastqfile

    Arguments:
        -`input`: The input fastq file
        -`output`: The output folder for the analysis
    """
    cmds = [
        'fastqc',
        input,
        '-o', output,
     ]
    cmds = '  '.join(cmds)
    cmds += " 2>&1 | tee -a  " + output + "/analysis_quality.log"
    runCommand(cmds, True)
    return

def convertSamToBam(samfile, bamfileout):
    """Convert sam file to bam file"""
    cmds = "samtools view -b -S %s > %s"%(samfile, bamfileout)
    runCommand(cmds, True)

def sortBamFile(bamfile, outSuffix):
    """docstring for sortBamFile"""
    cmds = "samtools  sort -m 1000000000  %s  %s" %(bamfile, outSuffix)
    runCommand(cmds, True)

def index_bam_file(bamfile):
    """Index bam files"""
    cmds = "samtools index %s" %(bamfile)
    runCommand(cmds, True)


def comment():
    return "*" * 80
