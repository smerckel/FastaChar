Fastachar
=========

**Fastachar** is a graphical user interface that allows a simple
comparison of two sets of DNA sequences. A typical working example
is to have a selection of DNA sequences of different, but related
species. These sequences are divided in a set A, which are thought
to be a single taxon (species) and a set B, which is a collection of
different taxa. Using the program, it can be established easily whether:

* the DNA sequences in set A are all identical, and if not, list the
  differences for those positions in the DNA sequences.

* set B has positions in the DNA that are different from those in
  set A,  across **all** species in set B.

**Fastachar** takes as input the alignments stored in a single file of
the fasta format. **Fastachar** is not a tool to align sequences. It is
assumed that the sequences were previously aligned with different algorithms 
(e.g. MUSCLE) and the most reliable alignment was chosen.


Installation
------------

**Fastachar** is written in Python3 and should run on all major
platforms, including linux and windows. In order to run **Fastachar** a
working copy of the python3 interpreter is required (including the
tkinter windowing toolkit).

Linux
~~~~~
Usually python3 is included in most linux distributions. A simple test
is to open a terminal and try to run python by::

  $ python3
  
which should give you the python interpreter (including its version
number). If it is verified that this works, test for the presence of
the tkinter windowing toolkit::

  >>> import tkinter

If this does not raise an exception, then you are all good and you can
exit the interpreter (ctl-D). Otherwise
you will need to install tkinter yourself, which is probably best done
via your distribution's package manager.

**Fastachar** can be installed from pypi, using pip from the command
line::
  
  $ pip3 install fastachar
  
or from a tar-gzipped file downloaded from github `FastaChar github repository <http://github.com/smerckel/fastachar>`. After extracting
the .tgz file and cd-ing into the newly created directory, you run::
  
  $ python3 setup.py build && sudo python3 setup.py install && sudo python3 setup.py clean

Either installation method for *Fastachar* should take care of
installing the dependencies (numpy and xlwt) correctly.

.. note::
  Although setuptools will resolve the dependency on numpy correctly,
  it is not capable of installing numpy as a wheel, but rather
  compiles it. This may take a long time, and possibly not be
  successful because of other dependencies that are not met. Therefore
  it is recommended to install numpy either via the distribution's
  package manager, or using pip::

    $ pip3 install numpy

  which *does* install numpy's wheel version.

Windows
~~~~~~~
Usually python is not installed by default on a Windows computer and
needs to be installed by the user. In this readme the official python
distribution will be used, but other python packages exist and may
work equally well, too.

To install Python3, visit https://www.python.org/downloads/windows/
and select the (latest) python3 version. (Do not select Python2 as
this is not supported by **Fastachar**.) When downloading the Python3
distribution, make sure you select the proper version for your computer
hardware:

* Download Windows x86 executable installer for a 32 bit system

* Download Windows x86-64 executable installer for a 64 bit system.

You can check from the **control panel/system** which version your
computer is running on, when in doubt.

When, the file is downloaded, run it and follow the default
installation (which includes pip and tkinter, which are both
needed for successful operation of **Fastachar**). It is recommend
however to check the box to add Python3 to the PATH environment variable.

Once Python3 is installed, **Fastachar** can be installed using
pip. This requires a dos prompt (go to **Start/search for programs** and
enter **cmd**, which should give an entry to the dos-command line. Type
in the dos-prompt::
  
  pip3 install fastachar
  
or::
  
  py -3 pip -m install fastachar
  
which should also install the dependencies numpy and xlwt.

Alternatively, **Fastachar** can be installed using an MSI file, which
can be downloaded from http://cubic-l.science/fastachar.html.



Authors
~~~~~~~

* Lucas Merckelbach (lucas.merckelbach at hzg.de)

* Luisa Borges (info at cubic-l.science or luisaborges2000 at yahoo.co.uk)

The software is released under the GPLv3 licence.
