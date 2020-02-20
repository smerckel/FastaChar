ERRORS = {0b0001:'File not found',
          0b0010:'Invalid or corrupt file',
          0b0011:'Could not save file',
          0b0100:'No case data',
          0b0101:'Not all sequences are of equal length',
          0b0111:'Case file formatting error',
          0b1000:'Regular expression formatting error',
          0b1111:'Unkwown error.',
}



ABOUT_TEXT="""
ABOUT

FastaChar V0.1.0 is a simple python program that reads a fasta file
with sequences for a number of different species. From the list
of species, the user can make a selection of two sets (A) and 
(B), which can be analysed. 

The available operations are
* Molecular diagnostic characters of the sequences in list A: 
  lists the positions of the sequences of A for which holds that:
      - they are the same for all sequences in list A
      - all sequences in list B have a different nucleotide on
        this position
* Potential molecular diagnostic characters
  lists the positions of all sequences of A for which holds that 
      - the nucleotides on in list A are different from those in
        list B, but,
      - the nucleotides in list A are not unique.

This software is licensed under GPLv3.

Authors:
    Lucas Merckelbach lucas.merckelbach@hzg.de
    Luisa Borges      luisaborges2000@yahoo.co.uk

Febuary 2020

Copyright 2017-2020
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

Fasta header parsing settings
-----------------------------
In a fasta file a sequence data entry consists of two lines. The
first line (starting with >), which we refer to as the sequence
header, contains then species name and usually an sequence ID. The
format of this header is not prescribed. FastaChar has a flexible
mechanism to interprete sequence header strings. The condition that
must be met, though, is that all sequences in a given fasta file
adhere to the same format. It may therefore be required to configure
FastaChar's sequence header parsing settings prior to open a fasta file
with aligned sequences. 

Sequence header parsing settings can be modified from selecting the
option "Header parsing settings" from the "File" menu. This presents a
new window with three entry fields for regular expressions. Regular
expressions are patterns that allows for searching text strings. using
a powerful wild-card system, see for example 
http://www.rexegg.com/

These entries could look like this:

+----------------+-------------------+
| Header format: | {ID}[_ ]{SPECIES} |
+----------------+-------------------+
| Regex ID:      | [A-Za-z0-9]+      |
+----------------+-------------------+
| Regex SPECIES: | [A-Z][a-z _]+      |
+----------------+-------------------+

The "Header format" describes the general layout of the header, where
the regular expressions for the ID and species are substituted for
{ID} and {SPECIES}, respectively. It is therefore mandatory that the
header format contains the strings {ID} and {SPECIES}.

In this example, the sequence headers is formed by some ID string,
separated by a space or an underscore, as indicated by "[ _]", from
the species string. The ID string is expected to be of the form of
alphanumeric characters, possibly captialised, and digits, and at
least one character long. The species strings is expected to start
with a capital, followed by non-capitalised alphanumeric characters,
and may include spaces and underscores.

Using the patterns is shown above, the following header will be
processed correctly:

WBET118 Lyrodus_pedicellatus_Tl_FR 

yielding the ID to be WBET118 and the species name to be
Lyrodus_pedicellatus_Tl_FR.

Any changes made, are accepted when clicking the button "OK", or
discarded when clicking the button "Cancel". The button "Help"
provides a new window with additional explanation.

Open a fasta file
-----------------

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
called list A and list B. Both lists should contain at least one
species. When species are selected, they are *moved* from their origin
(the box called "species" in this case) to their destination (list A for
example).

See below (MAKING A SELECTION) how to
make a selection of one or more species and drag them into a list box.

OPERATION
=========
The next step is to choose an operation. Two types of operations are
available:
    1) Molecular diagnostic characters in A
    2) Potential molecular diagnostic characters in A


Molecular diagnostic characters in A
------------------------------------
This operation compares the sequences
in list  A with those in list B and lists all positions and base
characters for which holds that for a given
position:
    - all base characters in list A are identical; and
    - all base characters in list B are different from those in list A

Potential molecular diagnostic characters in A
----------------------------------------------
This operation lists all those positions for which the base characters
in A are not unique, but different from those in list B.

After choosing the operation, the "PROCESS" button can be hit, to make
the comparsion. The result report appears in the bottom window.

RESULT WINDOW
=============

The results are displayed in the following format. First the selected
fasta file is printed, followed by all the sequences (including ID) in
list A and list B. Then the actual result is printed. 

If list A is found not to have any unique characters then that will
be the result. Otherwise the result is printed as

The species in List A have the following MCDs:

position: character(s) |  characters for species in List B
                       |  1 2 3 4 5 6 7 8 
--------------------------------------------------------------------------------
    32: G              |  T T T T T T T T
   202: G              |  C C C C C C C C
   207: G              |  C C C C C C C C


which means that positions 32, 202 and 207 in *all* sequences of list A
are the same, and have the character G. List B, having 8 sequences,
has sequences that are all different from G. Using the list of
sequences in list B printed above, the differences between the
sequences in this list can be attributed to different sequences.

When the operation for postenial MCDs is chosen, we might get a result such as:

The species in List A have the following potential MCDs:

position: character(s)  |  characters for species in List B
          1 2 3 4       |  1 2 3 4 5 6 7 8 
--------------------------------------------------------------------------------
      16: G K G G       |  A A A A A A A A


which indicates the positions where the sequences in list A differ from those 
in list B, but the characters in A are not unique. In this case, the second 
sequence has a K on position 16, which codes for either a G or T. Given the 
evidence of the other sequences, the user may conclude that the K most likely
represents a G, so that G is a potenial MCD on position 16.

Repeated processing will add the result to the result window, which
can be cleared using the "Clear output" button. The information in the
result window can be written to a text file via menu Output -> Save
report.

CASE FILES
==================

A given setting, defined by the selections made for species, list A,
list B and operation, can be saved to file for reanalysis later, or
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
list "species" to list A, or back, or between list A and B.


"""

REGEX_HELP_TEXT = """\

Regular expressions
-------------------

The sequence data in an aligned fasta file are assumed to be grouped
in two lines of data: a line indicative of the species and an
identifier, and a line containing the sequence characters. In the
fields below the format of the header can be precisely formatted. Note
that within a single alignment the header format should be consistent
for all entries.


Header format: This prescribes the global format of the header and
consists of the strings '{ID}' and '{SPECIES}', where {ID} and {SPECIES}
are placeholders for the identifier and species text strings,
respectively.

Example
-------

Suppose the header is given by 'WBT001 Lyrodus pediciliatus', then the
first word refers to an ID and the rest of the string refers to the
species. In this case the header format would be '{ID} {SPECIES}',
that is, the header consists of a ID string, and a species string
separated by a space. (Note the curly braces.)


The strings {ID} and {SPECIES} are subsitituted by regular
expressions. Sticking with the example above, IDs are given by
captialised letters and digits, and the species names consists of
letters and spaces. Then the regular exprresion for the ID becomes
'[A-Z0-9]+', and for the species names '[A-Z][a-z ]+'.

Common patterns
---------------

string: WBET001_Nototeredo_norvagica_Ms_TK
hdr_format : {ID}_{SPECIES}
regex ID: [A-Z0-9]+
regex SPECIES: [A-Za-z_]+

string: NR_042052.1_Streptococcus_equinus_ATCC_9812_16S_ribosomal_RNA_partial_sequence
hdr_format : {ID}_{SPECIES}
regex ID: NR_[0-9]+\.[0-9]+
regex SPECIES: [A-Za-z0-9_]+

string: Tongapyrgus_kohitateaSp2
hdr_format : {SPECIES}_{ID}
regex ID: [A-Za-z0-9]+
regex SPECIES: [A-Za-z]+

string: ZSM20100597 Pontohedyle wiggi
hdr_format : {ID} {SPECIES}
regex ID: [A-Z0-9]+
regex SPECIES: [A-Za-z ]+

string: CP036529.1 Streptococcus pneumoniae strain 521 chromosome complete genome
hdr_format : {ID}_{SPECIES}
regex ID: [A-Z0-9]+\.[0-9]+
regex SPECIES: [A-Za-z0-9_]+



Many websites provide further information on how to use regular
expressions. Try for example http://www.rexegg.com/.

"""
