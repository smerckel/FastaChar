What is Fastachar for and how to use it?
========================================

*Fastachar* is a graphical user interface to the *fasta* python module
that allows a user to compare pre-aligned DNA sequences. A typical
application is to distinguish one species from a set of different,
but closely related other species, based on DNA sequences.

Example
-------

Let's assume we collected specimens of a species that is hypothesised
to be a new species. From each specimen, material is extracted from
which a DNA sequences is produced. In order to determine whether or
not these particular specimens are a new species, the DNA sequences
are compared with sequences of identified specimens of closely related
species. To do so, we would like to know whether the sequences of the
unidentified specimens are all identical, and if not, in which
positions of the DNA there are differences. Ideally all sequences are
identical. We put these sequences in a set A. The sequences of
related specimens are collected in set B. Then, to determine whether
the particular type of DNA sequence, or marker, discriminates the
sequences in set A from those in set B, the positions of all the
DNA sequences in set B are compared with the corresponding position
of the sequence in set A, and listed if the base pair character is
different in *all* sequences of set B in comparison to the
corresponding position of the sequences in set A, yielding the
unique characters of the sequences in set A.

Preparation
-----------
The input for *Fastachar* is a list of DNA sequences, formatted in the
fasta format (see also
https://en.wikipedia.org/wiki/FASTA_format). The program assumes that
the DNA sequences that are going to be compared are:

* already aligned, and
* written into a single file using the fasta format.

Tools exist that can assist in aligning DNA sequences.

Running *Fastachar*
-------------------

On Windows, *Fastachar* is run by executing the fastachar.exe, and on
Linux, it is run be executing fastachar from the terminal
console. Once started, a new window appears with three empty text
boxes, labelled "Species", "Set A" and "Set B",
respectively. Below, there is a set of radio buttons to selection the
comparison operation, a button to execute the comparison ("Process")
and a button ("Clear output") to clear the output that is generated
and shown in the bottom text box, see the Figure.

.. figure:: _static/main_window.png
   :align: center
      
   Opening window of *Fastachar*

   
Opening a fasta file
~~~~~~~~~~~~~~~~~~~~

To start working, a fasta file is opened using::
  
  File
   └── Open fasta file

and select a fasta file from the dialogue offered. If a valid fasta
file is read, the text box *Species* is populated with the names of
the species found.

Selecting species for set  A and B
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Select a species name by left-clicking. A multiple selection can be
made by clicking again with *ctrl* pressed, which also selects the
item clicked. If instead of *ctrl* the *shift* key is pressed, all the
items in between are selected as well.

In order to move them into either set A or set B, drag the
selected items from the *Species* text box to the target text box
whilst holding the right-mouse button pressed.

Selecting the operation
~~~~~~~~~~~~~~~~~~~~~~~
Once the selection is made, the comparison operation is to be
selected. Two operations are implemented:

* show unique characters of one set
* show differences within a single set.

Either operation can be applied to set A or B.

After selecting the operation, the comparison can be executed by
clicking the *Process* button, and a report appears in the lower text
box.

Case files
~~~~~~~~~~
At this stage a case file can be written, which stores:

* the fasta file read
* the selection made
* the operation selected.

To save a case file select from the menu: ::

  File
   └── Save case file

To load a previously saved case file: ::
 
  File
   └── load case file

Output
~~~~~~

Multiple operations as well species selections can be processed and
the output will be appended to the lowest text box. The output can be
cleared using the *Clear output* button.

To save the output to file, select from the menu: ::

  Output
   └── Save report (txt)

to write the output as show in a text file, or ::
  
  Output
   └── Save report (xls)

to write the output in an excel file, with a tab for each processing
operation.


Help
~~~~

The user interface also provides help and information on the licensing
from the menu entry::

  Output
   └── Help
  
and ::

  Output
   └── About

respectively.




