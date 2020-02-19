# Example script how to do an analysis of a fasta file accessing the
# fasta module directly, and not using a graphical interface. The
# example script reads a fasta file, and divides all the species in a
# two sets, one that with species names that match a regular
# expression, and a set with sequences that does not match the regular
# expression. Then, for set A, the differences within this set as well
# as its unique characters are computed. Finally, the results are
# reported and dumped on the terminal.
import sys
sys.path.insert(0, '..')
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
    lst_A, lst_B = alignment.select_two_sequence_sets("Lyrodus.pedicellatus.*[mM][Ss]")

    # We could also use other methods to extract specific sequences.
    # Let's investigate Lyrodus pedicellatus. We suspect that the
    # sequences found in Turkey, they end with TK might be different
    # from those found in France (ending in Fr). So we select all
    # Lyrodus species, but exclude those ending in TK, for lst_A, and
    # do the same for lst_B, but invert the selection.
    
    lst_A = alignment.select_sequences(regex='Lyrodus[_ ]pedicellatus.*',
                                      invert=False,
                                      exclude='.*[Tt][Kk]')
    lst_B = alignment.select_sequences(regex='Lyrodus[_ ]pedicellatus.*',
                                      invert=True,
                                      exclude='.*[Tt][Kk]')
    

    S = fastachar.fasta_logic.SequenceLogic() 

    # Compute the unique characters in A with respect to B
    method = "MDC"
    
    mcds = S.compute_mdcs(lst_A, lst_B, method)

    # Report the results to the terminal.
    reportxls = fastachar.fasta_io.ReportXLS()
    report = fastachar.fasta_io.Report(filename, reportxls = reportxls)
    report.report_header(lst_A, lst_B, method)
    report.report_mdcs("List A", lst_A, lst_B, mcds, method)

    # compute non unique charachters in B
    nucs = S.list_non_unique_characters_in_set(lst_B)

    report.report_header(lst_A, lst_B, method='nucs')
    report.report_nucs("List B", lst_B, nucs)

    #reportxls.save('test.xls')



    
