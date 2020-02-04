import sys

sys.path.insert(0,'.')

import fastachar.fasta_io as io


alignment = io.Alignment()

alignment.set_fasta_hdr_fmt("{SPECIES}")

alignment.load("data/COI_sequences_MUSCLE.fas")

s = alignment.sequences[0]
