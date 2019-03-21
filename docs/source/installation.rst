.. highlight:: shell

============
Installation
============


Stable release
--------------

System dependancies:

1. Python >= 2.7 <- usally exist in all linux system, check the version
2. graphviz <- install this as a root user

To install graphviz follow package manager on your unix/linux system. 

In Ubuntu, do this on a linux terminal as root user, if you are not super user, ask your system admin to install it.

.. code-block:: console

     sudo apt-get install graphviz

In Red Hat flavor linux such as CentOs: 

.. code-block:: console

     sudo yum install graphviz

Note: Make sure the pip and virtualenv packages are  installed on your system.

.. code-block:: console 
     
    which pip 
    which virtualenv


If not installed, 

.. code-block:: console

    curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
    python get-pip.py  --user

Then, if there is no virtualenv package

.. code-block:: console
 
     pip install virtualenv

To install puticr, run this command in your terminal:

.. code-block:: console

    git clone https://github.com/demis001/puticr.git ; cd puticr ; make install

This is the preferred method to install puticr, as it will always install the most recent stable release.

Download test data from this site https://www.ddjima.com/software/  and extract the result in the same directory. The directory contains an example fastq files and indexed genome and test data. 

.. code-block:: console
    
    wget https://ddjima.com/wp-content/uploads/2019/02/testData.zip 

To extract ... 

.. code-block:: console

    unzip testData.zip


Run the test data
-----------------

The application has to run in Python virtual envirnoment. First,  activate the virtual environment to use the application after installation. 

.. code-block:: console

    source   puticr/bin/activate

Then, run the following line to test the application ...
This is also the way to run germ layer tissue samples (50% methylation)

.. code-block:: console

    puticr_cli  -o outdir2 -f testData/raw  -l 6 -c 12  -L 0.3 -U 0.7  --indexed=no --refGenome=hs_chr6.fa --refGenomeDir=testData/genome2/

To index your own reference genome and run your own data, create  the directory to hold the reference genome, merge all chromosome and store your genome as a single fasta  file. Example, mm10.fa, hs.fa etc. 

Then do this, `indexed=yes` telling the application to index before it uses it. Assumming you saved mm10.fa genome under mm10ref directory... 

.. code-block:: console

    puticr_cli  -o outdir2 -f testData/raw -l 6 -c 12  -L 0.3 -U 0.7  --indexed=yes --refGenome=mm10.fa --refGenomeDir=YOURPATH/mm10ref/


To run gamet cells samples (oocytes and sperm) that expected (100% methylation call). We haven't provided the oocytes and sperm test data. The file is similar to the test data. 
Please rename the file as oocyte_*.fastq.gz and sperm_*.fastq.gz in its separate directory. 

.. code-block:: console

    puticr_cli  -o outdir2 -f testData/raw  -l 6 -c 12  -L 0.8 -U 1.0  --indexed=no --refGenome=hs_chr6.fa --refGenomeDir=testData/genome2/


Note: The Germ layer tisse samples and the gamet cells samples must be called separetlly. 

.. _Github repo: https://github.com/demis001/puticr
.. _testData: https://www.ddjima.com/software/ 


Once  you have installed the document, don't forget to activate before each use.

.. code-block:: console

    source   puticr/bin/activate

To deactivate virtual envirnoment. Type the following command on Linux commmand line

.. code-block:: console

    deactivate

This will exit the virtual envirnoment
