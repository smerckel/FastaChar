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
        ''' Sets the regular expressions used to parse the fasta headers

        Parameters
        ----------
        
        header_format : string
            regular expression and containing the strings {ID} and {SPECIES}
        IDregex : string
            regular expression matching IDs and lab codes
        SPECIESregex : string
            regular expression matchin species names.

        .. Note:
           
           If it cannot get to work to parse the header strings correctly, a workaround 
           can be to specify the header_format as '{SPECIES}', and let the SPECIESregex
           capture anything by setting it to '.+'
        '''
        self.pattern_dict, self.regex_dict = self.generate_regex_dict(header_format, IDregex, SPECIESregex)
        

    def generate_regex_dict(self, header_format, IDregex, SPECIESregex):
        if "{ID}" not in header_format:
            header_format+="{ID}"
            IDregex=''
        pattern_dict = dict(ID=IDregex, SPECIES=SPECIESregex, HEADER=header_format,
                            SEP=header_format.replace("{ID}","").replace("{SPECIES}",""))

        regex_dict=dict(header=re.compile(header_format.format(**pattern_dict)),
                        ID_first=header_format.index("ID")<header_format.index("SPECIES"))
        return pattern_dict, regex_dict
    
    def load(self, fn):
        ''' Load sequence data from filename *fn* 

        Parameters
        ----------
        
        fn : string
            filename of file to open
        
        Returns
        -------
        errorcode : int
            errocode indicating what went wrong if something did go wrong
            Returns 0 if OK, otherwise see error codes above.
        arg : string
            Error message
        '''
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
                        arg = "Error: %s\nOffending line: %d\n"%(e.args[0], cnt-1)
                        break
                    except KeyError as e:
                        error = ERROR_FILE_NOT_FOUND
                        arg = "Error: Invalid character encountered ('%s')\nOffending line :%d\n"%(e.args[0], cnt)
                        break
        if not error and not self.are_sequences_of_equal_lengths(sequences):
            error = ERROR_UNEQUAL_SEQS
        self.sequences = sequences
        return error, arg
                
    
    def parse_hdr(self, hdr, **kwds):
        ''' Parse the header string of the sequence 

        Parameters
        ----------
        
        hdr : string
             fasta header to parse
        
        **kwds :
            if available, pattern_dict and regex_dict are extracted from the parameter list

        Returns
        -------
        IDstring : string
            a string representation of the ID or lab code
        species : string
            the name of the species

        This method tries to parse the header of a sequence as read from a fasta file.
        '''

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

        Parameters
        ----------
        sequences : list of strings
            contains a list of sequence characters.

        Returns
        -------
        boolean : True if all are equal length, False otherwise
        
        '''
        l = [len(s) for s in sequences]
        return len(set(l))==1


    def get_species_info(self):
        ''' get_species_info()

        Returns
        -------
        dictionary :
            keys: species
            values: IDs
        '''
        d = defaultdict(lambda : [])
        for s in self.sequences:
            d[s.species].append(s.ID)
        return d

    def get_species_list(self):
        ''' get_species_list()

        Returns
        -------
        list of sorted species names.
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

        Returns
        -------
        list
            List of sequences.



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

        Parameters
        ----------
        regex: string
            a regular expression or exact string

        Returns
        -------
        two lists of sequences : 
             one matching set and one not matching set.

        ..note :

        The union of the two sets is identical to the whole data set.
        '''
        set_A = self.select_sequences(regex, invert=False)
        set_B = self.select_sequences(regex, invert=True)
        return set_A, set_B

    def select_sequences_from_list(self, itemlist):
        ''' Selects sequence objects for a list of species names
        
        Parameters
        ----------
        itemlist : list of strings
            list of species names

        Returns
        -------
        list of sequence objects
        '''
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
        
    def report_mdcs(self, set_name, set_A, set_B, unique_characters_A):
        if 'A' in set_name:
            other_set_name = set_name.replace('A','B')
        else:
            other_set_name = set_name.replace('B','A')
        try:
            self.reportxls.report_mdcs(set_name, set_A, set_B, unique_characters_A)
        except AttributeError:
            pass
        potential_MDC_only = any([len(i[1])>=2 for i in unique_characters_A])

        if potential_MDC_only:
            modifier='potential '
        else:
            modifier=''
        w = self.output_filename
        if unique_characters_A:
            if potential_MDC_only: # we need to list ALL characters for each position in A, so we need to compute how much space to reserve.
                n_chars = len(unique_characters_A[0][1]._value)
                marker_position = max(24, 10 + 2*n_chars)
                filling = " "*(marker_position-23)
            else:
                filling = ""
            w.write("The species in {} have the following {}MDCs:\n\n".format(set_name, modifier))
            w.write("position: character(s) {}|  characters for species in {}\n".format(filling, other_set_name))
            if potential_MDC_only:
                s = " "*(8+2)
                s += " ".join(["%d"%((i+1)%10) for i in range(n_chars)])
                n_spaces_required = max(0,marker_position -len(s))
                s += " "*n_spaces_required
                w.write("{}|  ".format(s))
            else:
                w.write("                       {}|  ".format(filling))
            for i in range(len(set_B)):
                w.write("%d "%((i+1)%10))
            w.write("\n")
            w.write("-"*80+"\n")
            for (j, state_a, state_b) in unique_characters_A:
                if potential_MDC_only:
                    s = "%8d: %s"%(j+1, " ".join(state_a._value))
                    filling = " "*max(0, marker_position - len(s))
                    w.write("{}{}|  ".format(s,filling))
                else:
                    w.write("%8d: %s            |  "%(j+1, state_a._value[0]))
                w.write("%s\n"%(" ".join(state_b._value)))
            a = len(unique_characters_A)
            b = len(set_A[0].data)
            f = a/b*100
            if not potential_MDC_only:
                w.write("\n%d of %d characters are unique (%.1f%%)"%(a,b,f))
        else:
            w.write("{} has no MDCs\n".format(set_name))

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
            w.write("The sequences of species in {} have the following non-unique characters on\npositions:\n\n".format(set_name))
            w.write("position:  chars\n")
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
        self.sheet = self.book.add_sheet(sheet_name, cell_overwrite_ok=False)
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
    
    def report_mdcs(self, set_name, set_A, set_B, unique_characters_A):
        potential_MDC_only = any([len(i[1])>=2 for i in unique_characters_A])
        if potential_MDC_only:
            len_A = len(unique_characters_A[0][1]._value)
        else:
            len_A = 1
        n = self.__row +2
        self.sheet.write(n, 0, "Unique characters of {}:\n\n".format(set_name))
        n+=1
        self.sheet.write(n, 1, "Position")
        if potential_MDC_only:
            self.sheet.write(n, 2, "Potential MDCs")
            self.sheet.write(n, 2+len_A, "Characters different in other species")
        else:
            self.sheet.write(n, 2, "MDCs")
            self.sheet.write(n, 3, "Characters different in other species")
        n+=1
        if potential_MDC_only:
            for i, v in enumerate(set_A):
                formula = xlwt.Formula("A%d"%(4+i))
                self.sheet.write(n, 2+i, formula)
        else:
            self.sheet.write(n, 2, "List A")
        for i, v in enumerate(set_B):
            formula = xlwt.Formula("B%d"%(4+i))
            self.sheet.write(n, 2 + len_A+i, formula)
        n+=1
        for j, state_a, state_b in unique_characters_A:
            self.sheet.write(n, 1, "%d"%(j+1))
            if potential_MDC_only:
                for i, _state in enumerate(state_a._value):
                    self.sheet.write(n, 2+i, _state)
            else:
                self.sheet.write(n, 2, state_a._value[0])
            for i, _state in enumerate(state_b._value):
                self.sheet.write(n, 2+ len_A + i, _state)
            n+=1
        self.__row = n
        
    def report_differences_in_set(self, set_name, differences_set):
        n = self.__row +2
        self.sheet.write(n, 0, "The differences within {} are:".format(set_name))
        n+=1
        self.sheet.write(n, 1, "Position")
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

    
