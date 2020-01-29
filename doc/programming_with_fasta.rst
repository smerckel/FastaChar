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
   # example script reads a fasta file, and divides all the species in a
   # two sets, one that with species names that match a regular
   # expression, and a set with sequences that does not match the regular
   # expression. Then, for set A, the differences within this set as well
   # as its unique characters are computed. Finally, the results are
   # reported and dumped on the terminal.

   import fastachar


   filename = "../data/COI_sequences_MUSCLE.fas"

   alignment = fastachar.fasta_io.Alignment()
   # The sequences in this alignemnt typically look like this:
   # >WBET001_Nototeredo_norvagica_Ms_TK

   # that is, an ID, followed by an underscore and a species name. In
   # order to parse this sequence header correctly, we must tell the
   # alignment reader how this header is constructed.
   # See http://www.rexegg.com/regex-quickstart.html for a reference table.
   alignment.set_fasta_hdr_fmt(header_format='{ID}_{SPECIES}',
   IDregex = '[A-Z0-9]+',
   SPECIESregex = '[A-Z][a-z_]+')

   errno, errmesg = alignment.load(filename)
   if errno: # we have a non-zero error, so something went wrong. Print
   # the corresponding message to give us a clue
   print(errmesg)
   else:
   # all well.
   species = alignment.get_species_list()
   print("Species in this file:")
   for s in species:
   print("{:30s}".format(s))
   print()

   # Divide all the species in two groups, set A that matches the regex,
   # and set B that does not. Notice we can use regular expressions here too.
   set_A, set_B = alignment.select_two_sequence_sets("Lyrodus.pedicellatus.*[mM][Ss]")

   # We could also use other methods to extract specific sequences.
   # Let's investigate Lyrodus pedicellatus. We suspect that the
   # sequences found in Turkey, they end with TK might be different
   # from those found in France (ending in Fr). So we select all
   # Lyrodus species, but exclude those ending in TK, for set_A, and
   # do the same for set_B, but invert the selection.
   
   set_A = alignment.select_sequences(regex='Lyrodus[_ ]pedicellatus.*',
                                      invert=False, exclude='.*[Tt][Kk]')
   set_B = alignment.select_sequences(regex='Lyrodus[_ ]pedicellatus.*',
                                      invert=True, exclude='.*[Tt][Kk]')

   S = fastachar.fasta_logic.SequenceLogic() 
   # Compute the differences within set A
   differences_set_A = S.differences_within_set(set_A)

   # Compute the unique characters in A with respect to B
   unique_characters_A = S.compare_sets(set_A, set_B)

   # Report the results to the terminal.
   report = fastachar.fasta_io.Report(filename)
   report.report_header(set_A, set_B)
   report.report_uniq_characters("Set A", set_A, set_B, unique_characters_A)


The advantage of using scripts such as the one above, is that it is
easier to redo an analysis, modify an existing one, or batch analyses
a number of fasta files.

The API for the class SequenceData can be consulted :ref:`modindex`.
