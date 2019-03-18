Output
======

This shows the key intermediate and final files useful to understand.

Key output dir tree
===================

Here are the key files and directories in the output folder. The file structure is the same while running oocyte and sperm.

::

    outputDirName
    ├── logs
    ├── LICENCE.txt
    ├── result          
    │   ├── analysisDir: Final output directory
              ├── *.merged.sorted_CGcontext.CGmap: Output after restring extracting the CG context from CGmap file (*.merged.sorted.CGmap.gz)
              ├── *.merged.sorted_CGcontext_updated.CGmap: Output after merging the asymitrical CpG's from the CGmap file (*.merged.sorted_CGcontext.CGmap)
              ├── *.merged.sorted_CGcontext_updated.CGmap: Output after merging the asymitrical CpG's from the CGmap file (*.merged.sorted_CGcontext.CGmap)
              ├── *.merged.sorted_CGcontext_putative_icr.txt: Output after scanning ICR hotspot from the updated CGmap file (*.merged.sorted_CGcontext_updated.CGmap)
              ├── *.merged.sorted_CGcontext_putative_icr.bed: htospot Converted to bed format 
              ├── bed_merge_bedfile.bed: Merged all bed files from multiple tissue for downstream analysis
              ├── bed_union_bedfile.bed: Union of bed fils from multiple tissue 
              ├── bedfile_putative_ICR_AllTissues.bed: Final putative ICR files that will be used to intersect with oocyte and sperm calls. 
    │   └── bboxinout.py
    │   └── rawData: Symbolic link to your input directory
    │   └── trimFastq: Directory that contain intermediate quality trimmed files and alignment bam files
            │   └── *_trimmed.fq.gz: Quality trimmed input fastq files
            │   └── *.bam: intermediate bam files
            │   └── *.merged.sorted.ATCGmap.gz: Methylation ration call for the three context from cgmaptools 
            │   └── *.merged.sorted.CGmap.gz: Methylation ration call as CGmap format from cgmaptools

             
Output Examples
===============

Check the tutorial page from `cgmaptools <https://cgmaptools.github.io/cgmaptools_documentation/file-formats.html#cgmap-format>`_  to read the descrption of each column. 

CGmap file from cgmaptools
--------------------------

===     ===     =====     ====     =====     ====     ==     ==
chr     NUC     POS       CONT     DINUC     METH     MC     NC
===     ===     =====     ====     =====     ====     ==     ==
 6       C      60275     CHG      CT        0.00     0      1
 6       C      60280     CHH      CC        0.00     0      1
 6       C      60281     CHH      CT        0.00     0      1
 6       C      60284     CHH      CC        0.00     0      1
 6       C      60285     CHG      CT        0.00     0      1
 6       C      60293     CHH      CC        0.00     0      1
 6       C      60294     CHH      CC        0.00     0      1
 6       C      60295     CHH      CT        0.00     0      1
 6       G      60620     CHH      CT        0.00     0      1
 6       G      60623     CHG      CT        0.00     0      1
 6       G      60799     CG       CG        1.00     1      1
 6       C      66946     CG       CG        0.80     4      5
 6       G      66947     CG       CG        1.00     3      3
===     ===     =====     ====     =====     ====     ==     ==

Restrict to CG context
----------------------

===     ===     =====     ====     =====     ====     ==     ==
chr     NUC     POS       CONT     DINUC     METH     MC     NC
===     ===     =====     ====     =====     ====     ==     ==
 6       G      60799     CG       CG        1.00     1      1
 6       C      66946     CG       CG        0.80     4      5
 6       G      66947     CG       CG        1.00     3      3
===     ===     =====     ====     =====     ====     ==     ==

Merge symetrical CpG lines (updated CGmap file)
-----------------------------------------------

===     ===     =====     ====     =====     ====     ==     ==
chr     NUC     POS       CONT     DINUC     METH     MC     NC
===     ===     =====     ====     =====     ====     ==     ==
 6       G      60799     CG       CG        1.00     1      1
 6       C      66946     CG       CG        0.90     7      8
===     ===     =====     ====     =====     ====     ==     ==

Identify ICR hotspot from each tissue or gamet cells
----------------------------------------------------

This will be generated for all tissues and gamet cells (oocyte and sperm).
For germ cell tissues, we will merge the bed fils for each tissue (next step)

===   =======   =======   ======    ====   ===   ==   =========
chr   start     end       length    MP     TMR   TR   CpG_count
===   =======   =======   ======    ====   ===   ==   =========
6     142227    142313    86        0.53   3     6     6
6     7322171   7322364   193       0.53   2     3     7
===   =======   =======   ======    ====   ===   ==   =========


Merged bed file
---------------

====    ======  ======
Chr     start   end
====    ======  ======
chr6	135139	135605
chr6	139907	140060
chr6	142227	142313
chr6	146405	146477
====    ======  ======

Union bed file
--------------

====    ======  ======  =========================================================================
chr6	135139	135605	outdir/result/analysisDir/Liver.merged.sorted_CGcontext_putative_icr.bed
chr6	139907	140060	outdir/result/analysisDir/Brain.merged.sorted_CGcontext_putative_icr.bed
chr6	142227	142313	outdir/result/analysisDir/Kidney.merged.sorted_CGcontext_putative_icr.bed
chr6	146405	146477	outdir/result/analysisDir/Liver.merged.sorted_CGcontext_putative_icr.bed
chr6	188561	188610	outdir/result/analysisDir/Kidney.merged.sorted_CGcontext_putative_icr.bed
chr6	311402	311452	outdir/result/analysisDir/Kidney.merged.sorted_CGcontext_putative_icr.bed
chr6	348927	348958	outdir/result/analysisDir/Liver.merged.sorted_CGcontext_putative_icr.bed
chr6	359826	360962	outdir/result/analysisDir/Brain.merged.sorted_CGcontext_putative_icr.bed
====    ======  ======  =========================================================================

Count putative ICR in all tissue (Final file)
---------------------------------------------

The last column is a count in all tissue. This mean the ICR exist in 1 tissue only, in 2 tissues and 3 etc. 

====    =========   =========   =
chr6    118736283   118736335   1
chr6    118742075   118742229   1
chr6    119239091   119239173   2
chr6    119310973   119310996   3
chr6    119625970   119626080   1
chr6    120096163   120096207   2
chr6    120359520   120360857   1
====    =========   =========   =


At this point, we have generated three files of similar structures, one from germ layer tissues such as kidney, liver etc and two from Gamate cells (ocytes and sperm)

Before you instersect the three fiels and find bona fide ICR, it is advicable to pre-filter, the output file form the germ layer tissues. Based on the count column we may filter, 
the locus should exist at least 2/3 of the tissues. 

Example, if you did 3 tissues, we may restrict the locus should exist in at least 2 tissues. 


.. code-block:: bash

    awk  '$4 >= 2 {print $0}'  bedfile_putative_ICR_AllTissues.bed > bedfile_putative_ICR_AllTissues_2ORmore.bed


Then, this will be interesected with oocyte and sperm files to find the final list of bona fide ICRs. 

