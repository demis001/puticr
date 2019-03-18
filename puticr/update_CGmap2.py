#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2018 ddjima <ddjima@jimaTox>
#
# Distributed under terms of the MIT license.

"""
 Restrict to CG methylation context only
 zcat full.21421L_S4_R1_001_sorted.CGmap.gz  | grep "CG" > full.21421L_S4_R1_001_sorted_CGcontext.CGmap
 This script update the CpG map, it combine the two lines if the lines are consequetive CpG lines
 1       C       1677434 CG      CG      1.00    3       3
 1       G       1677435 CG      CG      1.00    4       4

python update_CGmap2.py -f test.txt > outfile
python update_CGmap2.py  -f full.21421L_S4_R1_001_sorted_CGcontext.CGmap > full21421L_S4_R1_001_sorted_CGcontext_updated.CGmap
"""
from __future__ import division
import os
import re
import itertools
import sys
def skip_after(mylist):
    i = iter(mylist)
    for x in i:
        yield x
        while x == 'a':
            x = i.next()
myline = []
def filter(previous_line, current_line):
 #print "--------------"
 #print previous_line
 ch1,genome1,loc1,CpG1,cont1,metp1,metcount1, totalCount1=previous_line.split()
 #print current_line
 ch2,genome2,loc2,CpG2,cont2,metp2,metcount2, totalCount2=current_line.split()
 genome1 = genome1.strip()
 genome2 = genome2.strip()
 loc1 = loc1.strip()
 loc2 = loc2.strip()
 loc3 = int(loc2) - 1
 #print genome1
 #print genome2
 #print loc1
 #print loc2
 #myline = []
 #myprev = []
 if genome1 == "C" and genome2 == "G" and int(loc1) == int(loc3):
     #print genome1
     #print genome2
     #print loc1
     #print loc2
     ch =ch1
     genome = genome1
     loc = loc1
     CpG = CpG1
     cont = cont1
     metp=round((int(metcount1) + int(metcount2))/(int(totalCount1) + int(totalCount2)), 2)
     metcount = int(metcount1) + int(metcount2)
     totalCount = int(totalCount1) + int(totalCount2)
     line = "AAA"+ ch + "\t" + genome + "\t" + loc + "\t" + CpG + "\t" + cont + "\t" + str(metp) +  "\t" +      str(metcount) + "\t" + str(totalCount) + "\n"
     #print line
     myline.append(line)
 else:
     myline.append(previous_line)
 return myline


import argparse
sys.tracebacklimit = 0 # stop trace error
parser = argparse.ArgumentParser()

parser.add_argument("--file", "-f", type=str, required=True)
args = parser.parse_args()

my_file = open(args.file, 'r')

if my_file:
 current_line = my_file.readline()

for line in my_file:

     previous_line = current_line
     current_line = line

     filter(previous_line, current_line)
#print myline
myiter=iter(myline)
for line2 in myiter:
    if "AAA" in line2:
        line = re.sub('[AAA]', '', line2)
        print line,
        k = next(myiter)
    else:
        print line2,


