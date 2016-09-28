========================
Cytometry ratio analysis
========================

Python program using Scikit-image (optionally, OpenCV) to analyze images

Prereqs
=======
You can install prereqs using ``conda`` (for x86 systems) or ``apt-get install`` (ARM systems like Beaglebone or Raspberry Pi etc.)

Using Conda
--------------
Using Miniconda, to run `cclskim.py`::

    conda install --file requirements.txt 


apt-get install
---------------
If you don't have/want ``conda`` then on Debian or Ubuntu the prereqs may be installed::

    sudo apt-get install python-numpy python-matplotlib python-skimage python-opencv


Run program
===========
assuming your *.png images are in a directory `../data`::
    
    ./cclskim.py ../data

You can also specify a single file

    ./cclskim.py ../data/mypic0.png


-e  suffix of filenames to look for [default .png]
-o  write all plots to a directory instead of showing on screen
