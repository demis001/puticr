#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2018 ddjima <ddjima@jimaTox>
#
# Distributed under terms of the MIT license.

"""
Identify hotspot in methylation data.
Rules:
    1. Mark site between 0.3 and 0.7 as 1 and the rest as 0
USAGE: ./identify_hotspot.py   -f full.21421L_S4_R1_001_sorted_CGcontext_updated.CGmap -l 0.3 -u 0.7 > full.21421L_S4_R1_001_putative_icr.txt
"""

import argparse
import os
import sys
from decimal import Decimal, getcontext
import itertools

def methStatus(fileName, lBound, uBound):
    with open(fileName, 'r') as f_in:
        mylist = []
        mylist2 =[]
        for line in f_in:
            metstatus = ''
            ch,genome,loc,CpG,cont,metp,metcount,totalCount=line.split()
            if Decimal(metp) >= Decimal(lBound) and Decimal(metp) <=  Decimal(uBound):
                metstatus = '1'
            else:
                metstatus = '0'
            mylist = [ch, genome, loc, CpG, cont, metp, metcount, totalCount, metstatus]
            line2 = "\t".join(mylist)
            #print line2
            mylist2.append(line2)
        return mylist2

def dmrHotSpot(mylist):
    """Identify DMR htospot by walking in the list."""
    myiter=iter(mylist) # convert list to iter object
    sublist = []
    print "chr\tstart\tend\tlength\tMethylation_Percent\tTotal_Methylated_Reads\t Total_reads\tCpG_count"
    for index, item in enumerate(myiter):
        #print str(index) + ":\t" + item
        ch,genome,loc,CpG,cont,metp,metcount,totalCount, metstatus=item.split()
        if int(metstatus) == 1 and int(metstatus) != 0:
                # check if the ICR cross different chromosome, it must be consecutive CpG on the same chr
                if len(sublist) == 0:
                    sublist.append(item)
                else:
                    # get the first entry in the growing list
                    firstE = sublist[0]
                    ch1,genome1,loc1,CpG1,cont1,metp1,metcount1,totalCount1, metstatus1=firstE.split()
                    ch2,genome2,loc2,CpG2,cont2,metp2,metcount2,totalCount2, metstatus2=item.split()
                    if str(ch1) == str(ch2):
                        sublist.append(item)
        else:
            if int(metstatus) == 0 and len(sublist)< 5:
                sublist = []
                item = item
            else:
                #print str(index) +  " ............................\n"
                mylist= sublist
                sublist = []
                #print mylist
                firstLine= mylist[0]
		ch,genome,start,CpG,cont,metp,metcount,totalCount, metstatus=firstLine.split()
		endLine = mylist[-1]
		ch,genome,end,CpG,cont,metp,metcount,totalCount, metstatus=endLine.split()
                getcontext().prec =2
                length = int(end) - int(start)
                length = str(length)
                mP = Decimal("0.00")
                tMc = 0
                totalReads = 0
                totalCpG = 0
                n= len(mylist)
                for l in mylist:
                    ch,genome,start2,CpG,cont,metp,metcount,totalCount, metstatus=l.split()
                    metp = Decimal(metp)
                    #print type(mP)
                    #print type(metp)
                    mP += metp
                    tMc += int(metcount)
                    totalReads += int(totalCount)
                    totalCpG += int(metstatus)
                mP = mP/Decimal(n)
                mP = str(mP)
                tMc = int(round(Decimal(tMc)/Decimal(n)))
                tMc = str(tMc)
                totalReads =int(round(Decimal(totalReads)/Decimal(n)))
                totalReads = str(totalReads)
                totalCpG = str(totalCpG)
		icr = [ch, start, end, length, mP, tMc,totalReads, totalCpG]
		icr2 = "\t".join(icr)
		print icr2

def main():
    import argparse
    sys.tracebacklimit = 0
    parser =argparse.ArgumentParser(description='Scan methylation hotspot from CGmap data.')
    parser.add_argument("--cgfile", "-f", type=str, required = True, help = "CGmap file name")
    parser.add_argument("--lMethLimit", "-l", type=float, required=False, default=0.3, help="Lower methylation ratio cutoff")
    parser.add_argument("--uMethLimit", "-u", type=float, required=False, default=0.7, help="Upper methylation cutoff")
    parser.add_argument("-v", "--verbose", action="store_true",help="increase output verbosity")
    if len(sys.argv)<=1:
        parser.print_help()
        sys.exit(1)
    else:
        args = parser.parse_args()

    fileName=args.cgfile
    lBound = args.lMethLimit
    uBound =args.uMethLimit

    mylist3 = methStatus(fileName, lBound, uBound)
    dmrHotSpot(mylist3)



if __name__ == "__main__":
        main()
