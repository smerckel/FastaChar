from collections import defaultdict
from itertools import zip_longest
import os
import re
import sys

import xlwt

from .fasta_logic import Sequence, State


OK = 0b0000
ERROR_FILE_NOT_FOUND = 0b0001
ERROR_FILE_INVALID = 0b0010
ERROR_IO           = 0b0011
ERROR_NO_CASE_DATA = 0b0100
ERROR_UNEQUAL_SEQS = 0b0101
ERROR_CASE         = 0b0111
ERROR_UNKNOWN      = 0b1111


class Alignment(object):
    ''' Class to hold sequences '''
    def __init__(self):
        self.sequences = []
        self.set_fasta_hdr_fmt()
        
    def set_fasta_hdr_fmt(self,header_format = "{ID}[_ ]{SPECIES}",
                          IDregex = "[A-Za-z0-9_]+[0-9\.]+[A-Za-z0-9]*",
                          SPECIESregex="[A-Za-z_]+"):
        self.pattern_dict, self.regex_dict = self.generate_regex_dict(header_format, IDregex, SPECIESregex)
        

    def generate_regex_dict(self, header_format, IDregex, SPECIESregex):
        pattern_dict = dict(ID=IDregex, SPECIES=SPECIESregex, HEADER=header_format,
                            SEP=header_format.replace("{ID}","").replace("{SPECIES}",""))

        regex_dict=dict(header=re.compile(header_format.format(**pattern_dict)),
                        ID_first=header_format.index("ID")<header_format.index("SPECIES"))
        return pattern_dict, regex_dict
    
    def load(self, fn):
        ''' Load sequence data from filename *fn* '''
        sequences=[]
        error = OK
        arg = ''
        if not os.path.exists(fn):
            error = ERROR_FILE_NOT_FOUND
            arg = fn
            return error, arg
        # File can be opened...
        cnt = 0
        with open(fn) as f:
            while True:
                hdr = f.readline()
                if not hdr:
                    break
                cnt+=1
                try:
                    data = f.readline().strip()
                except:
                    error = ERROR_IO
                    arg = hdr
                else:
                    cnt+=1
                    try:
                        sequences.append(Sequence(*self.parse_hdr(hdr), data))
                    except ValueError as e:
                        error = ERROR_FILE_INVALID
                        arg = "Error: %s\nOffending line: %d\n"%(e.args[0], cnt+1)
                        break
        if not error and not self.are_sequences_of_equal_lengths(sequences):
            error = ERROR_UNEQUAL_SEQS
        self.sequences = sequences
        return error, arg
                
    
    def parse_hdr(self, hdr, **kwds):
        ''' Parse the header string of the sequence '''

        pattern_dict = kwds.get('pattern_dict', self.pattern_dict)
        regex_dict = kwds.get('regex_dict', self.regex_dict)
            
        #>WBET042_Lyrodus_pedicellatus_Brittany_France
        if hdr[0] != ">" or len(hdr)==1:
            raise ValueError("Invalid header/file.")
        s = hdr[1:].strip()
        # Test whether we have a header with an ID. If not, create one of the form ID001. If yes, strip it from the species name.
        if regex_dict['header'].match(s) is None:
            raise ValueError("Parsing error of header.\nHeader: {header}\nFormat: {hformat}\nPattern: {pattern}\n".format(header=hdr.strip(),
                                                                                                                          hformat=pattern_dict['HEADER'],
                                                                                                                          pattern=regex_dict['header'].pattern))
        if regex_dict['ID_first']:
            regex = re.match("{ID}{SEP}".format(**pattern_dict), s)
        else:
            regex = re.search("{SEP}{ID}".format(**pattern_dict), s)
        regexSep = re.search("{SEP}".format(**pattern_dict), s)
        if not regexSep:
            raise ValueError("Unexpected header.\nHeader: {header}\nPattern: {pattern}".format(header=hdr, pattern=self.regex.pattern))

        if not regex: # Fallback method.
            IDstring, species = s.split(regexSep.group())
            if not regex_dict['ID_first']: # swap the values
                IDstring, species = species, ID            
        else:
            species = s.replace(regex.group(),'')
            IDstring = regex.group().replace(regexSep.group(),'')
        return IDstring, species
        
    def are_sequences_of_equal_lengths(self, sequences):
        ''' Check whether all sequences are equally long.

        Raises ValueError if not all sequences are equally long.
        '''
        l = [len(s) for s in sequences]
        return len(set(l))==1


    def get_species_info(self):
        ''' get_species_info()

        returns a dictionary with
            keys: species
            values: IDs
        '''
        d = defaultdict(lambda : [])
        for s in self.sequences:
            d[s.species].append(s.ID)
        return d

    def get_species_list(self):
        ''' get_species_list()

        returns list of sorted species names.
        '''
        d = self.get_species_info()
        k = list(d.keys())
        k.sort()
        return k

    def select_sequences(self, regex, invert = False, exclude=None):
        '''select_sequences using regular expressions

        Parameters
        ----------

        regex: string
            a regular expression or exact string to match the species names
        
        invert: bool
            if True, the inverted selection is returned (not matching species)

        exclude: None or a regular expression
            exclude the matches that are included by the regex parameter.

        RETURNS
        -------

        The methode returns a list with selected sequences.

        This method can be used to select a set of species using
        regular expressions. All species are returned that match the
        spefified regex, or all except these if invert is set to
        True. An optional exlude regex can be given to filter the list
        further. This will affect the behaviour of the invert option,
        see the note below.

        Note :: If an expression is given for the exlude parameter and
        invert==True, then those sequences that match the regex
        selection AND the exclude selection is returned.
        '''
        c = re.compile(regex)
        if not exclude:
            if invert:
                group = [i for i in self.sequences if not c.match(i.species)]
            else:
                group = [i for i in self.sequences if c.match(i.species)]
        else:
            x = re.compile(exclude)
            if invert:
                group = [i for i in self.sequences if c.match(i.species) and x.match(i.species)]
            else:
                group = [i for i in self.sequences if c.match(i.species) and not x.match(i.species)]
            
        return group

    def select_two_sequence_sets(self, regex):
        ''' select_two_sequence_sets(regex)
        regex: a regular expression or exact string

        returns two sets of sequences: one matching set and one not matching set.
        The union fo the two sets is identical to the whole data set.
        '''
        set_A = self.select_sequences(regex, invert=False)
        set_B = self.select_sequences(regex, invert=True)
        return set_A, set_B

    def select_sequences_from_list(self, itemlist):
        group = [i for i in self.sequences if i.species in itemlist]
        return group


class Report(object):
    def __init__(self, filename=None, output_filename=None, reportxls = None):
        self.filename = filename or "noname"
        self.output_filename = output_filename or sys.stdout
        self.reportxls = reportxls
        try:
            self.reportxls.filename = self.filename
        except AttributeError:
            pass
            
    def report_unique_characters(self, set_A, set_B, differences_set_A, unique_characters_A):
        Q # obsolete???
        try:
            self.reportxls.report_unique_characters(set_A, set_B, differences_set_A, unique_characters_A)
        except AttributeError:
            pass
        w = self.output_filename
        w.write("Filename : {}\n".format(self.filename))
        w.write("-"*80+"\n")
        w.write("List A:\n")
        for i,s in enumerate(set_A):
            w.write("%2d %s (%s)\n"%(i+1, s.species, s.ID))
        w.write("\n")
        w.write("List B:\n")
        for i,s in enumerate(set_B):
            w.write("%2d %s (%s)\n"%(i+1, s.species, s.ID))
        w.write("-"*80+"\n")
        w.write("\n\n")
        if differences_set_A:
            w.write("The sequences of species in list A have the following non-unique characters on\n columns:\n\n")
            w.write("column: Characters\n")
            for (j, state) in differences_set_A:
                w.write("%6d  %s\n"%(j+1, " ".join(state._value)))
            w.write("\n")
        if unique_characters_A:
            w.write("The sequences of species in list A have the following molecular diagnostic characters:\n\n")
            w.write("column: chr|  characters different in other species\n")
            w.write("           |  ")
            for i in range(len(set_B)):
                w.write("%d "%((i+1)%10))
            w.write("\n")
            w.write("-"*80+"\n")
            for (j, state_a, state_b) in unique_characters_A:
                w.write("%6d: %s  |  "%(j+1, state_a._value[0]))
                w.write("%s\n"%(" ".join(state_b._value)))
            w.write("-"*80+"\n")
            a = len(unique_characters_A)
            b = len(set_A[0])
            f = a/b*100
            w.write("%d of %d characters are unique (%.1f%%)"%(a,b,f))
        else:
            w.write("The sequences of the species in list A have no molecular diagnostic characters.\n")
        if not w == sys.stdout:
            w.close()
        else:
            w.write("\n")

    def report_header(self, set_A, set_B):
        try:
            self.reportxls.report_header(set_A, set_B)
        except AttributeError:
            pass
        w = self.output_filename
        w.write("Filename : {}\n".format(self.filename))
        w.write("-"*80+"\n")
        w.write("List A:\n")
        for i,s in enumerate(set_A):
            w.write("%2d %s (%s)\n"%(i+1, s.species, s.ID))
        w.write("\n")
        w.write("List B:\n")
        for i,s in enumerate(set_B):
            w.write("%2d %s (%s)\n"%(i+1, s.species, s.ID))
        w.write("-"*80+"\n")
        w.write("\n\n")

    def report_footer(self):
        try:
            self.reportxls.report_footer()
        except AttributeError:
            pass
        w = self.output_filename
        w.write("\n")
        w.write("="*80)
        w.write("\n\n")
        
    def report_uniq_characters(self, set_name, set_A, set_B, unique_characters_A):
        if 'A' in set_name:
            other_set_name = set_name.replace('A','B')
        else:
            other_set_name = set_name.replace('B','A')
        try:
            self.reportxls.report_uniq_characters(set_name, set_A, set_B, unique_characters_A)
        except AttributeError:
            pass
        w = self.output_filename
        if unique_characters_A:
            w.write("The species in {} have the following MCDs:\n\n".format(set_name))
            w.write("column: chr|  characters for species in {}\n".format(other_set_name))
            w.write("           |  ")
            for i in range(len(set_B)):
                w.write("%d "%((i+1)%10))
            w.write("\n")
            w.write("-"*80+"\n")
            for (j, state_a, state_b) in unique_characters_A:
                w.write("%6d: %s  |  "%(j+1, state_a._value[0]))
                w.write("%s\n"%(" ".join(state_b._value)))
            a = len(unique_characters_A)
            b = len(set_A[0].data)
            f = a/b*100
            w.write("\n%d of %d characters are unique (%.1f%%)"%(a,b,f))
        else:
            w.write("{} has no MCDs\n".format(set_name))

    def report_differences_in_set(self, set_name, set_A, differences_set):
        try:
            self.reportxls.report_differences_in_set(set_name, differences_set)
        except IOError:
            pass
        except AttributeError:
            pass
        w = self.output_filename
        if differences_set:
            count=0
            w.write("The sequences of species in {} have the following non-unique characters on\ncolumns:\n\n".format(set_name))
            w.write("column:  chars\n")
            w.write("-"*80)
            w.write("\n")
            for j, state_a in differences_set:
                if len(state_a.intersection_of_subsets())==1:
                    prefix='*'
                    count+=1
                else:
                    prefix=' '
                w.write("%s%5d %s\n"%(prefix,j+1, " ".join(state_a._value)))
            w.write("\n")
            a = len(differences_set)
            b = len(set_A[0].data)
            f = (b-a)/b*100
            w.write("\nSummary:")
            w.write("\n\t- %d of %d characters are different (%.1f%% identical)."%(a,b,f))
            if count:
                w.write("\n\n\t - A number of %d instances (marked by *) were found \n\t  that *could* be potential unique.\n"%(count))

        else:
            w.write("All sequences within {} are identical.\n".format(set_name))
            

class MyWorkbook(xlwt.Workbook):
    def __init__(self, *p, **kw):
        super().__init__(*p, *kw)

    def remove_all_sheets(self):
        self._Workbook__worksheet_idx_from_name.clear()
        self._Workbook__worksheets.clear()
        
            
class ReportXLS(object):
    def __init__(self):
        self.book = MyWorkbook()
        self.sheet_idx = 0
        self.__row = 0
        self.styles = self.define_styles()
        
    def define_styles(self):
        default = xlwt.Style.easyxf()
        alert = xlwt.Style.easyxf()
        alert.pattern.pattern=alert.pattern.SOLID_PATTERN
        alert.pattern.pattern_fore_colour = xlwt.Style.colour_map['yellow']
        s = dict(default=default, alert=alert)
        return s
    
    def __create_sheet(self):
        sheet_name = "worksheet%02d"%(self.sheet_idx)
        self.sheet = self.book.add_sheet(sheet_name)
        self.sheet_idx+=1
        
    def clear(self):
        self.book.remove_all_sheets()
        self.sheet_idx = 0
        
    def save(self, fn):
        try:
            self.book.save(fn)
        except IndexError:
            pass # try to save an empty workbook ignore.
        
    def report_header(self, set_A, set_B):
        self.__create_sheet()
        n = 0
        self.sheet.write(n, 0, "Filename:")
        self.sheet.write(n, 1, self.filename)
        n+=2
        self.sheet.write(n, 0, "List A")
        self.sheet.write(n, 1, "List B")
        n+=1
        for a, b in zip_longest(set_A, set_B):
            if a:
                self.sheet.write(n, 0, "%s (%s)"%(a.species, a.ID))
            if b:
                self.sheet.write(n, 1 ,"%s (%s)"%(b.species, b.ID))
            n+=1
        self.__row = n

    def report_footer(self):
        pass
    
    def report_uniq_characters(self, set_name, set_A, set_B, unique_characters_A):
        n = self.__row +2
        self.sheet.write(n, 0, "Unique characters of {}:\n\n".format(set_name))
        n+=1
        self.sheet.write(n, 1, "Column")
        self.sheet.write(n, 2, "Character")
        self.sheet.write(n, 3, "Characters different in other species")
        n+=1
        self.sheet.write(n, 2, set_name)
        for i, v in enumerate(set_B):
            self.sheet.write(n, 3+i, "%d"%(i+1))
        n+=1
        for j, state_a, state_b in unique_characters_A:
            self.sheet.write(n, 1, "%d"%(j+1))
            self.sheet.write(n, 2, state_a._value[0])
            for i, _state in enumerate(state_b._value):
                self.sheet.write(n, 3+i, _state)
            n+=1
        self.__row = n
        
    def report_differences_in_set(self, set_name, differences_set):
        n = self.__row +2
        self.sheet.write(n, 0, "The differences within {} are:".format(set_name))
        n+=1
        self.sheet.write(n, 1, "Column")
        self.sheet.write(n, 2, "Chars")
        n+=1
        for (j, state) in differences_set:
            if len(state)==0 or len(state.intersection_of_subsets())==0:
                style = self.styles['default']
            else:
                style = self.styles['alert']
            self.sheet.write(n, 1, "%d"%(j+1), style)
            for i, s in enumerate(state._value):
                self.sheet.write(n, 2+i, s, style)
            n+=1

    
