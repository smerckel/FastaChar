Programming with **fasta**
==========================


The graphical user interface is intended to provide easy access to the
functionality offered by the **fasta** module. Rather than using the
graphical interface, the user can also create her/his own python scripts.

Example script
--------------

::
   
   # Example script how to do an analysis of a fasta file accessing the
   # fasta module directly, and not using a graphical interface. The
   # example script reads a fasta file, and divides all the species in
   # two sets, one that with species names that match a regular
   # expression, and a set with sequences that does not match the regular
   # expression. Then, for set A, the differences within this set as well
   # as its unique characters are computed. Finally, the results are
   # reported and dumped on the terminal.
   
   from fasta import fasta


   filename = "../data/COI_sequences_MUSCLE.fas"

   S = fasta.SequenceData()

   S.load(filename)

   species = S.get_species_list()
   print("Species in this file:")
   for s in species:
       print("{:30s}".format(s))
   print()

   # Divide all the species in two groups, set A that matches the regex,
   # and set B that does not.
   set_A, set_B = S.select_two_sequence_sets("Lyrodus.pedicellatus.*[mM][Ss]")

   # Compute the differences within set A
   differences_set_A = S.differences_within_set(set_A)

   # Compute the unique characters in A with respect to B
   unique_characters_A = S.compare_sets(set_A, set_B)

   # Report the results to the terminal.
   report = fasta.Report(filename)
   report.report_unique_characters(set_A, set_B, differences_set_A, unique_characters_A)


The advantage of using scripts such as the one above, is that it is
easier to redo an analysis, modify an existing one, or batch analyses
a number of fasta files.

The API for the class SequenceData can be consulted :ref:`modindex`.
