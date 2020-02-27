from setuptools import setup
import fastachar

long_description='''
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
'''

setup(name="fastachar",
      version=fastachar.__version__,
      packages = ['fastachar'],
      py_modules = [],
      entry_points = {'console_scripts':[],
                      'gui_scripts':['fastachar = fastachar.tkgui:main']
                      },
      install_requires = 'sphinx-rtd-theme xlwt'.split(),
      author="Lucas Merckelbach",
      author_email="lucas.merckelbach@hzg.de",
      description="A simple program with GUI to compare dna sequences",
      long_description=long_description,
      long_description_content_type='text/x-rst',
    url='http://cubic-l.science/fastachar.html',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: MacOS :: MacOS X',
                  'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Topic :: Scientific/Engineering',
    ])
