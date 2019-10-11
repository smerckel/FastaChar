ERRORS = {0b0001:'File not found.',
          0b0010:'Invalid or corrupt file.',
          0b0011:'Could not save file.',
          0b0100:'No case data.',
          0b0101:'Not all sequences are of equal length',
          0b0111:'Case file formatting error',
          0b1111:'Unkwown error.',
}



ABOUT_TEXT="""
ABOUT

FastaChar is a simple python program that reads a fasta file
with sequences for a number of different species. From the list
of species, the user can make a selection of two sets (A) and 
(B), which can be analysed. 

The available operations are
* Unique characters A: 
  lists the columns in the sequences of A for which holds that:
      - they are the same for all sequences in set A
      - all sequences in set B have a different nucleotide or amino 
        acid in this column.
* Differences within A:
  lists the columns of all sequences where the nucleotide or amino
  acid is not identical.

This software is licensed under GPLv3.

Authors:
    Lucas Merckelbach lucas.merckelbach@hzg.de
    Luisa Borges      luisaborges2000@yahoo.co.uk

April 2017
"""

DISCLAIMER="""
DISCLAIMER

This software is provided "as is" and any expressed or implied
warranties, including, but not limited to, the implied warranties of
merchantability and fitness for a particular purpose are
disclaimed. In no event shall the regents or contributors be liable
for any direct, indirect, incidental, special, exemplary, or
consequential damages (including, but not limited to, procurement of
substitute goods or services; loss of use, data, or profits; or
business interruption) however caused and on any theory of liability,
whether in contract, strict liability, or tort (including negligence
or otherwise) arising in any way out of the use of this software, even
if advised of the possibility of such damage.

"""

HELP_TEXT="""
HELP

FastaChar is a simple python program to compare aligned sequences of
different or (supposedly) the same species.

The sequences are assumed to be provided in the standard fasta file
format. See for example https://en.wikipedia.org/wiki/FASTA_format.

WORKFLOW
========

Before using the program the user needs to prepare a valid fasta file,
with sequences of one or more species. A given species may be 
represented by more than one sequence, each with its own ID.

To open a fasta file, select from the menu "File" and then "Open fasta
file". A dialogue window appears from which a fasta file can be
selected. The directory displayed is the working directory (home
directory if not previously specified). Prior to opening the fasta
file, it may be convenient to set the working directory path
first. The setting of the working directory is persistent (i.e., it
will be kept from one session to the next).


When the fasta file is opened, all species distinguished in the fasta
file will appear in the top left list box (species).

NOTES: 

   1) if a species has multiple sequences, it will still appear as one
      entry.  

   2) if a given species has multiple sequences, and the names are not
      exactly the same, then they will appear as two or more different 
      species.

From the pool of available species, the user can make two selections,
called set A and set B. Both sets should contain at least one
species. When species are selected, they are *moved* from their origin
(the box called "species" in this case) to their destination (set A for
example).

See below (MAKING A SELECTION) how to
make a selection of one or more species and drag them into a list box.

OPERATION
=========
The next step is to choose an operation. Two types of operations are
available:
    1) list unique characters of a set
    2) list the differences within a set.

Set A can be compared with set B, or vice versa, hence giving rise to
four operations in total.

Unique characters A operation 
-----------------------------
This operation compares the sequences
in set A with those in set B and lists all columns and base
characters (nucleotides or aminoacids) for which holds that for a given
column:
    - all base characters in set A are identical; and
    - all base characeters in set B are different from those in set A

Differences within A operation 
------------------------------
This operation lists all those columns for which the base characters
(nucleotides or amino acids) of the sequences in set A are *not* the same.

After choosing the operation, the "PROCESS" button can be hit, to make
the comparsion. The result report appears in the bottom window.

RESULT WINDOW
=============

The results are displayed in the following format. First the selected
fasta file is printed, followed by all the sequences (including ID) in
set A and set B. Then the actual result is printed. 

If set A is found not to have any unique characters then that will
be the result. Otherwise the result is printed as


Unique characters of set A:

column: chr|  characters different in other species
           |  1 2 3 4 5 6 7 8 
--------------------------------------------------------------------------------
    32: G  |  T T T T T T T T
   202: G  |  C C C C C C C C
   207: G  |  C C C C C C C C


which means that columns 32, 202 and 207 in *all* sequences of set A
are the same, and have the character G. Set B, having 8 sequences,
has sequences that are all different from G. Using the list of
sequences in set B printed above, the differences between the
sequences in this set can be attributed to different sequences.

If the operation chosen was "differences within a set", then result is similar.

The differences within set A are:

column: chars
    17 T T A A
    26 A A C C
   184 G G T T
   189 C C T T
   195 T T G G
   206 C C A A
   216 A A C C
   234 T T C C

which indicates the columns where the sequences in set A (in this case) differ.

Repeated processing will add the result to the result window, which
can be cleared using the "Clear output" button. The information in the
result window can be written to a text file via menu Output -> Save
report.

CASE FILES
==================

A given setting, defined by the selections made for species, set A,
set B and operation, can be saved to file for reanalysis later, or
as starting point for a similar, but not identical comparison. A case
file can be saved using the menu File -> Save case file, or loaded via
menu File -> Load case file.


MAKING A SELECTION 
==================

To make a selection, click with the mouse on a species name. To select
multiple species, click on another species name whilst pressing
"SHIFT"; this will select all the species in between as well. To add
more species to the selection, click on the species to select, whilst
pressing "CTRL". Use the right-hand button to drag the selection into
the listbox of choice.

This works identical for making a selection to move species from the
list "species" to set A, or back, or between set A and B.

"""
