from setuptools import setup

setup(name="fastachar",
      version="0.0.1",
      packages = ['fasta'],
      py_modules = ['fastachar'],
      entry_points = {'console_scripts':[],#['fastachar_gui = fastachar_gui:main'],
                      'gui_scripts':['fastachar = fastachar:main']
                      },
      install_requires = 'numpy xlwt'.split(),
      author="Lucas Merckelbach",
      author_email="lucas.merckelbach@hzg.de",
      description="A simple program with GUI to compare dna sequences",
      long_description="""A simple python module with graphical user interface
that allows to compare a group of aligned DNA sequences with another group of
aligned DNA sequences. Different operations can be specified such as find
differences or correspondences.""",
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
