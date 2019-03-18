====================
Running the Pipeline
====================

.. _activate:

Activating the Pipeline
=======================

You must always ensure that the virtualenv that you installed into during the
:doc:`installation` is activated prior to running any portion of the pipeline.

You only have to do this if you have closed your terminal since the last time your
activated.

You need to specify the full path to the activate script such as

.. code-block:: bash

    $> . /path/to/puticr/puticr/bin/activate


You can read more about what virtualenv is `here <https://virtualenv.pypa.io/en/latest/>`_

To get help
===========

.. code-block:: bash

    puticr_cli -h 

If your fastq file has a `.fq.gz` extension, make sure to rename to `tissueName.*.fastq.gz` extension and it should be gzipped. 
The name of the fastq file does matter. For example, Brain.21423B_S1_R1_001.fastq.gz, Liver.21423L_S3_R1_001.fastq.gz, oocyte.5423B_S1_R1_001.fastq.gz, 
Brain.21424B_S5_R1_001.fastq.gz

General pipeline flowchart
==========================

.. image:: _static/images/flowchart.png
   :width: 600

Usage Examples
==============

You must use  `TissueName`.*.fastq.gz``

Typical Usage with germ cell tissues such as kidney, liver, brain ...
---------------------------------------------------------------------

In this case, the goal is to find a region where the genome is methylated 50%. We will use the lower methylation cutoff of 0.3 and the upper cutoff 0.7.
Don't forget to store the `tissueName.*.fastq.gz` file under any directory name and pass to -f option. I suggest to store the raw data into separate folders.
One for somatic tissue fastq.gz  files and the other for gamet cells (oocyte and sperm). The pipleline only  support single end reads. 

.. code-block:: bash

    puticr_cli  -o outputDir1 -f testData/raw  -l 6 -c 12  -L 0.3 -U 0.7  --indexed=no --refGenome=hs_chr6.fa --refGenomeDir=testData/genome2/

Gamet cells (oocyte and sperm)
------------------------------

The goal is to find a region where the genome is methylated 100%

   .. code-block:: bash
           
       puticr_cli  -o outputDir2 -f testData/raw  -l 6 -c 12  -L 0.8 -U 1.0 --indexed=no --refGenome=hs_chr6.fa --refGenomeDir=testData/genome2/


To index your own genome and run the pipeline 
---------------------------------------------

Assuming you downlaoded and saved `hs38.fa` under `mygenome/genome3/`, you will turn on `indexed=yes`. Indexing a genome is a slower process, be petient. 

.. code-block:: bash

       puticr_cli  -o outputDir1 -f testData/raw  -l 6 -c 12  -L 0.3 -U 0.7  --indexed=yes --refGenome=hs38.fa --refGenomeDir=mygenome/genome3/


Then, the next time you run a different data or the same data. You don't need to re-index. This is a one time process unless you used different version of the genome.

Don't forget to change `--indexed=no`.

.. code-block:: bash
       
    puticr_cli  -o outputDir2 -f testData/raw  -l 6 -c 12  -L 0.8 -U 1.0 --indexed=no --refGenome=hs38.fa --refGenomeDir=mygenome/genome3/


Checking error logs
===================

If it fails then an error is reported that generally suggest where it failed by
checking the key files created at each stage. Most likely, the error occurs on the 
suggested stage or the stage before it. You will likely have to check the log files
to get an idea what went wrong and go from there.

