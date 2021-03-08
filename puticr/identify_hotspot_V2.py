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
		ch3,genome3,start3,CpG3,cont3,metp3,metcount3,totalCount3, metstatus3=firstLine.split()
		endLine = mylist[-1]
		ch4,genome4,end4,CpG4,cont4,metp4,metcount4,totalCount4, metstatus4=endLine.split()
                getcontext().prec =2
                length = int(end4) - int(start3)
                length = str(length)
                #mPercent = Decimal("0.00")
                #tMcount = Decimal("0.0")
                totalReads = [] # to report the values at max count
                totalCpG = 0
                totalCpGSite= len(mylist)
                #print mylist
                for l in mylist:
                    # Initially intended to report average across all CpGs, but decided to report methylation percent, total methylated reads, and total reads at max read count from the list.
                    ch5,genome5,start5,CpG5,cont5,metp5,metcount5,totalCount5, metstatus5=l.split()
                    metP = Decimal(metp5)
                    #print type(mPercent)
                    #print type(metP)
                    #mPercent += metP
                    #tMcount += int(metcount5)
                    totalReads.append(int(totalCount5))
                # report the index of maxTotalReadCount
                max_value = max(totalReads)
                max_index = totalReads.index(max_value)
                my_max_line = mylist[max_index]
                ch6,genome6,start6,CpG6,cont6,metp6,metcount6,totalCount6, metstatus6=my_max_line.split()
                    #totalCpG += int(metstatus5)
                #aveMetPerc = mPercent/Decimal(totalCpGSite)
                #aveMetPerc = str(aveMetPerc)
                #aveTotalMetCount = Decimal(tMcount)/Decimal(totalCpGSite)
                #aveTotalMetCount = str(aveTotalMetCount)
                #aveTotalReads =Decimal(totalReads)/Decimal(totalCpGSite)
                #aveTotalReads = str(aveTotalReads)
                metPerc=str(metp6)
                totalMetCount=str(metcount6)
                totalReads=str(totalCount6)

                totalCpG = str(totalCpGSite)
		icr = [ch3, start3, end4, length, metPerc, totalMetCount, totalReads, totalCpG]
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
