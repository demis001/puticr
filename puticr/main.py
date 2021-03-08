#!/usr/bin/env python
# -*- coding: utf-8 -*-


"""Console script for puticr."""
import sys
import click
from ruffus import *
import yaml
import time
import os
import helpers
from helpers import runCommand, isGzip
from os.path import (
    join, expanduser, expandvars,
    splitext, basename, dirname, exists
)
# helpers.setup_shell_environment()
import tasks
from glob import glob
from termcolor import colored
import datetime
import warnings

if not sys.warnoptions:
    warnings.simplefilter("ignore")

is_64bits = sys.maxsize > 2**32
#import graphviz
if not is_64bits:
    print "Please upgrade your operating system to 64 bit, application such as diamond don't run on 32 bit"
    sys.exit(0)
options = helpers.get_options()
basedir = os.path.relpath('./')

projectDir = options.outdir  # set output dir
proDir = os.path.basename(projectDir)
click.echo(proDir)
# fastq dir
inputDir = options.fastq_file
inputDir = os.path.abspath(inputDir)
click.echo(inputDir)

cpuNum = options.cpuNum
click.echo(cpuNum)
lowerMeth = options.lMethLimit
upperMeth = options.uMethLimit

trimLeft = options.trim_left


logsDir = join(proDir, "logs")
resultDir = join(proDir, "result")
rawData = join(proDir, "result", "rawData")
proFastq = join(proDir, "result", "trimFastq")
tempDir = join(resultDir, "analysisDir")
genomeDir = options.refGenomeDir
fa_file = options.refGenome

print logsDir
print resultDir

# setup starting files
param = [
    #[inputFile, join(proDir, "input", inFile)],
    [inputDir, join(proDir, "result", "rawData")]

]
param2 = [
    [genomeDir, join(genomeDir, fa_file, "_bowtie2")]
]


@graphviz(height=1.6, width=2, label="Prepare\nanalysis")
@follows(mkdir(proDir, resultDir, proFastq, logsDir, tempDir))
@files(param)
def prepare_analysis(input, output):
    """Copy the inputfiles to analysis dir
        -`input`: input file to copy to the outdir
        -`outfile`: output file name
    """
    stage1 = "Stage1: Make fastq source symlink", input, " to ", output
    click.echo(colored(stage1, "green"))
    click.echo(output)
    result = tasks.creatSymLink(input, output)
    return result


@graphviz(height=1.6, width=2, label="Clean\nfastq files")
@follows(prepare_analysis)
@transform(join(rawData, "*.fastq.gz" or ".fq.gz"), suffix(".fastq.gz"), "_trimmed.fq.gz")
def cleanFastq(input_file, output_file):
    """docstring for cleanFast
    -`input_file`: A fastq gz file
    -`output_file`: A trimmed fastq.gz file using trim_galore
    """
    click.echo(colored("Stage 2: Creating DB file from probe file ...", "green"))
    click.echo(input_file)
    result = tasks.trimFastq(input_file, output_file, trimLeft, proFastq)
    return result


@graphviz(height=1.6, width=2, label="Index ref\ngenome")
@files(param2)
def indexGenome(input, output):
    """
    Index the genome,
    Input: fasta file and a dir where to store the indexed the genome
    """
    click.echo(colored(
        "Stage 0: Indexing the reference genome, take longer time be petient ....", "green"))
    if not os.path.exists(join(genomeDir, fa_file)):
        click.echo("Fasta file doesn't exist in {}, make sure the ref genome fasta file exist in the genomeDir path you provided".format(genomeDir))
        exit
    elif not os.path.exists(genomeDir):
        click.echo(
            "The reference genome dir doesn't exist, make sure the dir {} exists".format(genomeDir))
    else:
        result = tasks.bowtie2_genomeIndex(fa_file, genomeDir, cpuNum)
        return


@graphviz(height=1.6, width=2, label="Align\nsequence")
@follows(cleanFastq)
@transform(join(proFastq, "*_trimmed.fq.gz"), suffix("_trimmed.fq.gz"), "_trimmed.bam")
#@collate(join(proFastq, "*_trimmed.fq.gz"), regex(r"(.+)_.+_trimmed.fq.gz$"),  r'\1_trimmed.bam')
def bsAlign(input, output):
    """ Align the the sequence to reference genome
    input: trimmed fastq.gz file
    output: aligned bam file
    """
    click.echo(input)
    click.echo(
        colored("Stage 3: Align the BS sequence to the reference gneome ...", "green"))
    if not os.path.exists(genomeDir):
        click.echo("Please provide the genome index directory with / at the end")
    else:
        genomeFolder = genomeDir[:-1]  # trim "/" from dir path
        result = tasks.alignBsData(
            input, output, cpuNum, genomeFolder, fa_file)
        return


bamFiles = glob(join(proFastq, "*_trimmed.bam"))


@graphviz(height=1.6, width=2, label="Merge bam\n files")
#@follows(bsAlign)
#@collate(join(proFastq, "*_trimmed.bam"), regex(r"(.+)\..+_trimmed.bam$"),  r'\1.merged.bam')
@collate(join(proFastq, "*_trimmed.bam"), regex(r"(.+)_.+_trimmed.bam$"),  r'\1.merged.bam')
def mergeBamSameTissue(input, output):
    """ Sort and index bam file
    input: bam file
    output: Merged bam from the same tissue
    """
    # click.echo(input)
    click.echo(colored("Stage 4: merge bames from the same tissue ...", "green"))
    result = tasks.sameTissueBamMerge(input, output)
    return


@graphviz(height=1.6, width=2, label="Sort bam files")
@follows(mergeBamSameTissue)
@transform(join(proFastq, "*.merged.bam"), suffix(".bam"), ".sorted.bam")
def bamSort(input, output):
    """ Sort and index bam file
    input: bam file
    output: sorted and indexed bam file
    """
    click.echo(colored("Stage 5: Sort  bam files ...", "green"))
    result = tasks.sortBam(input, output, cpuNum)
    return


@graphviz(height=1.6, width=2, label="Index bam files")
@follows(bamSort)
@transform(join(proFastq, "*.sorted.bam"), suffix(".bam"), ".bam.bai")
def bamIndex(input, output):
    """ Sort and index bam file
    input: bam file
    output: sorted and indexed bam file
    """
    click.echo(colored("Stage 6: Index  bam files ...", "green"))
    result = tasks.indexBam(input, output, cpuNum)
    return


@graphviz(height=1.6, width=2, label="Convert bam\nto CGmap fromat")
@follows(bamIndex)
@transform(join(proFastq, "*.sorted.bam"), suffix(".sorted.bam"), ".sorted")
def createCGmap(input, output):
    """ Sort and index bam file
    input: sorted bam file
    output: CGmap format
    """
    click.echo(colored("Stage 7: Convert bam file to CGmap format ...", "green"))
    genomeFolder = genomeDir[:-1]
    faFile = join(genomeFolder, fa_file)
    result = tasks.bamToCGmap(input, output, faFile)
    return


@graphviz(height=1.6, width=2, label="Extract CG\n context")
@follows(createCGmap)
@transform(join(proFastq, "*.sorted.CGmap.gz"), suffix(".CGmap.gz"), "_CGcontext.CGmap")
def extractCG_Context(input, output):
    """ Sort and index bam file
    input: gzipped CGmap file
    output: Extracted CG context CGmap file
    """
    click.echo(
        colored("Stage 8: Extract CG context from the CGmap files ...", "green"))
    baseN = os.path.basename(output)
    out = tempDir + "/" + baseN
    result = tasks.extractCGcontext(input, out)
    return


@graphviz(height=1.6, width=2, label="Prepare\n CGmap file")
@follows(extractCG_Context)
@transform(join(tempDir, "*_CGcontext.CGmap"), suffix(".CGmap"), "_updated.CGmap")
def mergeConCGcall(input, output):
    """ Sort and index bam file
    input: gzipped CGmap file
    output: Extracted CG context CGmap file
    """
    click.echo(
        colored("Stage 9: Merge consecutive CG call in the CGmap file ...", "green"))
    result = tasks.mergeConsecutiveCGcall(input, output)
    return


@graphviz(height=1.6, width=2, label="Generate\nPutative ICRs")
@follows(mergeConCGcall)
@transform(join(tempDir, "*_CGcontext_updated.CGmap"), suffix("_updated.CGmap"), "_putative_icr.txt")
def icrHotSpot(input, output):
    """ Sort and index bam file
    input: updated CGmap file
    output: identified putative ICR as txt fromat
    """
    click.echo(colored(
        "Stage 10: Identify ICR hotspot from CG context CGmap file ...", "green"))
    result = tasks.identifyICRhotSpot(input, output, lowerMeth, upperMeth)
    return


@graphviz(height=1.6, width=2, label="Convert text\n to bed format")
@follows(icrHotSpot)
@transform(join(tempDir, "*_putative_icr.txt"), suffix(".txt"), ".bed")
def convertToBed(input, output):
    """ Sort and index bam file
    input: ICR text file
    output: ICR bed file
    """
    click.echo(colored(
        "Stage 11: Convert putative ICR to bed format to view in genome browser...", "green"))
    result = tasks.textToBed(input, output)
    return


@graphviz(height=1.6, width=2, label="Generate union\nof Bed files")
@follows(convertToBed)
# @transform(join(tempDir, "*_putative_icr.bed"), suffix(".bed"), "_union.bed")
@merge(convertToBed, tempDir + "/bed_union_bedfile.bed")
def unionBed(input, output):
    """ Create a union of bed files
    input: Bed files from different tissues
    output: Union bed files
    """
    click.echo(colored(
        "Stage 12: Create a union of bed files from multiple tissues...", "green"))
    result = tasks.createUnionBed(input, output)
    return


@graphviz(height=1.6, width=2, label="Merge bed\nfiles")
@follows(convertToBed)
# @transform(join(tempDir, "*_putative_icr.bed"), suffix(".bed"), "_union.bed")
@merge(convertToBed, tempDir + "/bed_merge_bedfile.bed")
def mergeBed(input, output):
    """ Create a merged of bed files
    input: Bed files from different tissues
    output: Merged bed files
    """
    click.echo(colored(
        "Stage 13: Create a merged of bed files from multiple tissues...", "green"))
    result = tasks.createMergedBed(input, output)
    return


@graphviz(height=1.6, width=2, label="Count overlaping\n ICRs regions")
@follows(unionBed, mergeBed)
@collate(join(tempDir, "*_bedfile.bed"), regex(r".+_.+_(bedfile).bed$"), tempDir +  "/" + r'\1_putative_ICR_AllTissues.bed')
def countICR(input, output):
    """ Create a merged of bed files
    input: union and merged bed files from multiple tissue
    output: A putative ICR region count based on the region count
    """
    click.echo(input)
    click.echo(colored(
        "Stage 14: Generate a count of overlaping regions across different tissues...", "green"))
    result = tasks.createCountICR(input, output)
    return


def main():
    if options.indexed == "yes":
        click.echo(
            "Indexing the reference genome {}, be patient, it takes longer time".format(genomeDir))
        pipeline_run(["indexGenome"], verbose=1, multiprocess=cpuNum)
        pipeline_run(["prepare_analysis", "cleanFastq", "bsAlign", "mergeBamSameTissue", "bamSort", "bamIndex", "createCGmap",
                      "extractCG_Context", "mergeConCGcall", "icrHotSpot", "convertToBed", "unionBed", "mergeBed", "countICR"], verbose=1, multiprocess=cpuNum)
        # Flowcharts can be printed in a large number of formats including jpg, svg, png and pdf
        pipeline_printout_graph("flowchart.pdf", "pdf", [countICR], user_colour_scheme={
                                "colour_scheme_index": 6}, pipeline_name="Putative ICR pipeline", no_key_legend=False)
    else:
        """Console script for puticr."""
        click.echo(tasks.comment())
        t0 = time.time()
        click.echo("Starting the process .....")
        #click.echo("Starting the pipeline, staring time ...{}".format(datetime.timedelta(seconds=t0)))
        #tasks_torun = [prepare_analysis, cleanFastq]
        # pipeline_run(["prepare_analysis", "cleanFastq", "bsAlign", "mergeBamSameTissue", "bamSort", "bamIndex", "createCGmap",
        #             "extractCG_Context", "mergeConCGcall", "icrHotSpot", "convertToBed", "unionBed", "mergeBed", "countICR"], verbose=1, multiprocess=cpuNum)

        pipeline_run(["mergeBamSameTissue", "bamSort", "bamIndex", "createCGmap",
                       "extractCG_Context", "mergeConCGcall", "icrHotSpot", "convertToBed", "unionBed", "mergeBed", "countICR"], verbose=1, multiprocess=cpuNum)
        #pipeline_run(["icrHotSpot", "convertToBed", "unionBed", "mergeBed", "countICR"], verbose=1, multiprocess=cpuNum)
        # Flowcharts can be printed in a large number of formats including jpg, svg, png and pdf
        pipeline_printout_graph("flowchart.pdf", "pdf", [countICR], user_colour_scheme={
                                "colour_scheme_index": 6}, pipeline_name="Putative ICR pipeline", no_key_legend=False)
        click.echo(".................. {}".format(resultDir))

        elapsedTime = int((time.time()) - t0)
        elapsedTime = str(datetime.timedelta(seconds=elapsedTime))
        click.echo("Time to complete the task .....{}".format(
            colored(elapsedTime, "red")))
        click.echo(tasks.comment())


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
