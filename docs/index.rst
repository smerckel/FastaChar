 .. FastaChar documentation master file, created by
   sphinx-quickstart on Wed Jun 28 15:38:29 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

FastaChar's documentation
=========================

This manual covers the use of the program **Fastachar**.

FastaChar is a software developed to extract molecular diagnostic characters from
one or several taxonomically-informative DNA markers of a selected taxon
compared to those of other taxa (as many as required by the user) in a single step.
The input data consists of a single file with aligned sequences in the fasta format,
which can be created using alignment software such as MEGA or
GENEIOUS. The software is described by Merckelbach and Borges (2020) [Merckelbach2020]_.

The software was developed specifically to determine molecular
diagnostic characters for the description of Lyrodus mersinensis by
Borges and Merckelbach (2018) [BORGES2018]_, but it can be applied to
any taxon.  Since FastaChar is an intuitive and easy-to-use software, we
hope it helps to standardize the use of molecular data and stimulate
researchers to proceed to the final step of molecular taxonomy, that
is, describe the new species.

**Fastachar** is written in Python3, and is released as open source
software under the GPLv3 GNU Public License. The installation of the
program is (also) covered in the README.rst file, that comes with the source
code.

.. toctree::
   :maxdepth: 1
   :caption: Contents:
	     
   howto
   installation   
   programming_with_fasta
   regex

References to the fastachar source code
=======================================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

.. [Merckelbach2020]  Merckelbach,L.M., & Borges, L. M. S. (2020). Make every species count:
		      fastachar software for rapid determination of
		      molecular diagnostic haracters to describe
		      species.
		      Molecular Ecology Resources. 00:1–8.
		      https://doi.org/10.1111/1755-0998.13222. 

.. [BORGES2018]  Borges, L. M. S., & Merckelbach, L. M. (2018). Lyrodus mersinensis sp.
		 nov. (Bivalvia: Teredinidae) another cryptic species in the Lyrodus
		 pedicellatus (Quatrefages, 1849) complex. Zootaxa, 4442(3), 441–457.
		 https://doi.org/10.11646/zootaxa.4442.3.6

		 
