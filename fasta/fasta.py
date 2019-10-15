from collections import defaultdict
from itertools import zip_longest
import os
import re
import sys

import numpy as np
import xlwt

OK = 0b0000
ERROR_FILE_NOT_FOUND = 0b0001
ERROR_FILE_INVALID = 0b0010
ERROR_IO           = 0b0011
ERROR_NO_CASE_DATA = 0b0100
ERROR_UNEQUAL_SEQS = 0b0101
ERROR_CASE         = 0b0111
ERROR_UNKNOWN      = 0b1111


class Seq(object):
    ''' A class to hold the information of a single sequence '''
    S = "-?"+"".join([chr(i+65) for i in range(26)])
    ID = 0
    
    def __init__(self, hdr, data):
        self.ID, self.species = self.parse_hdr(hdr)
        self.data = data
        self.seq = self.parse_data(data)
        self.length = len(self.seq)

    def parse_data(self,data):
        ''' Parse the data string of the sequence '''
        seq=np.array([Seq.S.index(i) for i in data.strip()], dtype=int)
        return seq
    
    def parse_hdr(self, hdr):
        ''' Parse the header string of the sequence '''
        #>WBET042_Lyrodus_pedicellatus_Brittany_France
        if hdr[0] != ">":
            raise ValueError("Invalid header/file.")
        Seq.ID += 1
        species = hdr[1:].strip()
        return Seq.ID, species

    def __repr__(self):
        return "Seq object ({}, {})".format(self.ID, self.species)
    
    @staticmethod
    def pretty_print(m,c=" "):
        return c.join(Seq.S[_m] for _m in m)
        
        

class SequenceData(object):
    ''' Class to hold sequences '''
    def __init__(self):
        self.sequences = []

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
                    data = f.readline()
                except:
                    error = ERROR_IO
                    arg = hdr
                else:
                    cnt+=1
                    try:
                        sequences.append(Seq(hdr, data))
                    except ValueError:
                        error = ERROR_FILE_INVALID
                        arg = "Offending line: %d"%(cnt+1)
                        break
        if not error and not self.are_sequences_of_equal_lengths(sequences):
            error = ERROR_UNEQUAL_SEQS
        self.sequences = sequences
        return error, arg
                
        
    def are_sequences_of_equal_lengths(self, sequences):
        ''' Check whether all sequences are equally long.

        Raises ValueError if not all sequences are equally long.
        '''
        l = [s.length for s in sequences]
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


    def select_sequences_from_list(self, itemlist):
        group = [i for i in self.sequences if i.species in itemlist]
        return group
    
    def select_sequences(self, regex, invert = False, exclude=None):
        ''' select_sequences(regex, invert):

        regex: a regular expression or exact string
        invert: if True, the inverted selection is returned (not matching species)
        exclude: None or a regular expression to exclude these.

        returns a list with selected sequences.
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
                group = [i for i in self.sequences if not c.match(i.species) or x.match(i.species)]
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
    
    def make_matrix(self, aset):
        # returns a matrix with sequence info.
        # ther returned shape seqeunce_length x number_of_seqs
        #
        return np.array([i.seq for i in aset]).T
    
    def comparison_within_set(self, aset, invert=False):
        ''' show_differences_within_set(aset)
        shows the columns within a set that are not identical, if any
        
        returns a list of tuples, of which each tuple is the column number, and the the column data.
        '''
        matrix = self.make_matrix(aset)
        return self.__compare_matrix(matrix, invert)
    
    def __compare_matrix(self, matrix, invert):
        sel = []
        for i, row in enumerate(matrix):
            if invert:
                if np.all(row==row[0]):
                    sel.append((i, row))
            else:
                if not np.all(row==row[0]):
                    sel.append((i, row))
        return sel

    def find_columns_matching_char_list(self, aset, char_list):
        n_list = [Seq.S.index(i) for i in char_list]
        m = self.make_matrix(aset)
        cols = [i for i,_m in enumerate(m) if any(any(_m==c) for c in n_list)]        
        return cols
        
    def differences_within_set(self, aset):
        ''' differences_within_set(aset)

        aset: list of seqeunces

        returns a list of those columns for which are one or more differences found between the sequences
        of this aset
        '''
        return self.comparison_within_set(aset, invert=False)

    def agreements_within_set(self, aset):
        ''' agreements_within_set(aset)

        aset: list of sequences

        returns a list of those columns for which all columns agree between the sequences 
        of this aset
        '''
        return self.comparison_within_set(aset, invert=True)
    
    def compare_sets(self, set_A, set_B, invert=False,
                       excluded_character_list_set_A='- ?'.split()):
        '''Compares set A with set B and list 
            the differences  if not invert
            the agreements if invert
        
        all columns that have coding letters that appear in
        excluded_characeter_list_set_A are excluded from comparison,
        as well ass all column for which set A is not consistent.
        '''
        
        # is set A composed of identical sequences?
        delta_A = self.differences_within_set(set_A)
        if delta_A:
            # columns that are different and should be excluded from comparison are
            cols_excl = [i[0] for i in delta_A]
        else:
            cols_excl = []
        cols_excl += self.find_columns_matching_char_list(set_A, excluded_character_list_set_A)
        matrix_A = self.make_matrix(set_A)[:,0]
        matrix_B = self.make_matrix(set_B)

        sel = []
        for i, (a, b) in enumerate(zip(matrix_A, matrix_B)):
            if i in cols_excl:
                continue
            if invert==False:
                if np.all(a!=b):
                    sel.append((i, a, b))
            else:
                if not np.all(a!=b):
                    sel.append((i, a, b))
        return sel


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
        try:
            self.reportxls.report_unique_characters(set_A, set_B, differences_set_A, unique_characters_A)
        except AttributeError:
            pass
        w = self.output_filename
        w.write("Filename : {}\n".format(self.filename))
        w.write("-"*80+"\n")
        w.write("Set A:\n")
        for i,s in enumerate(set_A):
            w.write("%2d %d %s\n"%(i+1, s.ID, s.species))
        w.write("\n")
        w.write("Set B:\n")
        for i,s in enumerate(set_B):
            w.write("%2d %d %s\n"%(i+1, s.ID, s.species))
        w.write("-"*80+"\n")
        w.write("\n\n")
        if differences_set_A:
            w.write("The differences WITHIN the set A are:\n\n")
            w.write("column: chars\n")
            for _d in differences_set_A:
                w.write("%6d %s\n"%(_d[0]+1, Seq.pretty_print(_d[1])))
            w.write("\n")
        if unique_characters_A:
            w.write("Unique characters of set A:\n\n")
            w.write("column: chr|  characters different in other species\n")
            w.write("           |  ")
            for i in range(len(set_B)):
                w.write("%d "%((i+1)%10))
            w.write("\n")
            w.write("-"*80+"\n")
            for _d in unique_characters_A:
                w.write("%6d: %s  |  "%(_d[0]+1, Seq.pretty_print([_d[1]])))
                w.write("%s\n"%(Seq.pretty_print(_d[2])))
            w.write("-"*80+"\n")
            a = len(unique_characters_A)
            b = len(set_A)
            f = a/b*100
            w.write("%d of %d characters are unique (%.1f%%)"%(a,b,f))
        else:
            w.write("Set A has no unique characters\n")
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
        w.write("Set A:\n")
        for i,s in enumerate(set_A):
            w.write("%2d %d %s\n"%(i+1, s.ID, s.species))
        w.write("\n")
        w.write("Set B:\n")
        for i,s in enumerate(set_B):
            w.write("%2d %d %s\n"%(i+1, s.ID, s.species))
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
        try:
            self.reportxls.report_uniq_characters(set_name, set_A, set_B, unique_characters_A)
        except AttributeError:
            pass
        w = self.output_filename
        if unique_characters_A:
            w.write("Characters unique in set {}, but different in other species set:\n\n".format(set_name))
            w.write("column: chr|  characters different in other species\n")
            w.write("           |  ")
            for i in range(len(set_B)):
                w.write("%d "%((i+1)%10))
            w.write("\n")
            w.write("-"*80+"\n")
            for _d in unique_characters_A:
                w.write("%6d: %s  |  "%(_d[0]+1, Seq.pretty_print([_d[1]])))
                w.write("%s\n"%(Seq.pretty_print(_d[2])))
            a = len(unique_characters_A)
            b = len(set_A[0].data)
            f = a/b*100
            w.write("\n%d of %d characters are unique (%.1f%%)"%(a,b,f))
        else:
            w.write("{} has no unique characters\n".format(set_name))

    def report_differences_in_set(self, set_name, set_A, differences_set):
        try:
            self.reportxls.report_differences_in_set(set_name, differences_set)
        except IOError:
            pass
        w = self.output_filename
        if differences_set:
            w.write("The differences within {} are:\n\n".format(set_name))
            w.write("column: chars\n")
            w.write("-"*80)
            w.write("\n")
            for _d in differences_set:
                w.write("%6d %s\n"%(_d[0]+1, Seq.pretty_print(_d[1])))
            w.write("\n")
            a = len(differences_set)
            b = len(set_A[0].data)
            f = (b-a)/b*100
            w.write("\n%d of %d characters are different (%.1f%% identical)"%(a,b,f))

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
        self.sheet.write(n, 0, "Set A")
        self.sheet.write(n, 1, "Set B")
        n+=1
        for a, b in zip_longest(set_A, set_B):
            if a:
                self.sheet.write(n, 0, "%s (%d)"%(a.species, a.ID))
            if b:
                self.sheet.write(n, 1 ,"%s (%d)"%(b.species, b.ID))
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
        self.sheet.write(n, 3, "Characters in different in other species")
        n+=1
        for i, v in enumerate(set_B):
            self.sheet.write(n, 3+i, "%d"%(i+1))
        n+=1
        for _d in unique_characters_A:
            self.sheet.write(n, 1, "%d"%(_d[0]+1))
            self.sheet.write(n, 2, Seq.pretty_print([_d[1]]))
            for i, _dd in enumerate(_d[2]):
                self.sheet.write(n, 3+i, Seq.pretty_print([_dd]))
            n+=1
        self.__row = n
        
    def report_differences_in_set(self, set_name, differences_set):
        n = self.__row +2
        self.sheet.write(n, 0, "The differences within {} are:".format(set_name))
        n+=1
        self.sheet.write(n, 1, "Column")
        self.sheet.write(n, 2, "Chars")
        n+=1
        for _d in differences_set:
            self.sheet.write(n, 1, "%d"%(_d[0]+1))
            for i, _dd in enumerate(_d[1]):
                self.sheet.write(n, 2+i, Seq.pretty_print([_dd]))
            n+=1


