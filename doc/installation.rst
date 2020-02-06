Installation
============

**Fastachar** is written in Python3 and should run on all major
platforms, including linux and windows. In order to run **Fastachar** a
working copy of the python3 interpreter is required (including the
tkinter windowing toolkit).

Linux
~~~~~
As of the beginning of 2020, support for python2 is officially
dropped. This means that most likely python points to python
version 3. In the documentation below, python3 is used explicitly, but
on recent linux distributions, the '3' can probably be left out.

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
line:::
  
  $ pip3 install fastachar
  
or from a tar-gzipped file downloaded from `FastaChar github repository <http://github.com/smerckel/fastachar>`_. After extracting
the .tgz file and cd-ing into the newly created directory, you run::
  
  $ python3 setup.py build && sudo python3 setup.py install && sudo python3 setup.py clean

Either installation method for **Fastachar** should take care of
installing the dependencies (xlwt) correctly.


Windows
~~~~~~~
Usually python is not installed by default on a Windows computer and
needs to be installed by the user. In this readme the official python
distribution will be used, but other python packages exist and may
work equally well, too.

To install Python3, visit https://www.python.org/downloads/windows/
and select the (latest) python3 version. (Do not select Python2 as
this is not supported by **Fastachar**.) When downloading the Python3
distribution, make sure you select the proper verion for your computer
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
  
which should also install the dependency xlwt.

Alternatively, **Fastachar** can be installed using an MSI file, which
can be downloaded from http://cubic-l.science/fastachar.html.
