from collections import UserList, defaultdict
import re

class Char(set):
    ''' A character object representation a nucleotide in a sequence

    The object is initialised with a character from the IUPAC list. Ambiguous characters, 
    such as Y and W are expanded into their base nucleotides.

    Parameters
    ----------
    c : str 
         IUPAC character
    subst_c : str
         IUPAC character substitute for logical operations.

    Attributes
    ----------
    _value : str
        (non-expanded) character representation of nucleotide character.
 
    Notes
    -----
    
    The (IUPAC) characters supported are::

        A
        T
        C
        G
        - (gap)

    The ambiguous characters and their expansions::

        Y -> C and T
        R -> A and G
        W -> A and T
        S -> G and C
        K -> T and G
        M -> C and A

        D -> A, G and T
        V -> A, G and C
        H -> A, C and T
        B -> C, G and T

    The masking characters X and N expand to A, G, T and G.
    '''
    IUPAC = {'A':'A', 'T':'T', 'C':'C', 'G':'G', 'Y':'CT', 'R':'AG', 'W':'AT',
             'S':'GC', 'K':'TG', 'M':'CA', 'D':'AGT', 'V':'AGC', 'H':'ACT', 'B':'CGT',
             'X':'ACTG', 'N':'ACTG', '-':'-'}

    def __init__(self, c, masked):
        s = Char.IUPAC[c]
        super().__init__(s[0])
        for _s in s[1:]:
            self.add(_s)
        self._value = c
        self._masked = masked

    @property
    def is_masked(self):
        ''' Evaluates to True if this character is a masked character.'''
        return self._masked
    
class State(set):
    ''' The class' purpose is to hold a number of Char objects
        and treat these as a set.

    Parameters
    ----------
    chars : iterable of :obj: Char

    Attributes
    ----------
    _value : list of str
        ascii representation of characters.
    '''
    def __init__(self, chars):
        super().__init__()
        self._value = []
        self._chars = []
        for _char in chars:
            if not _char.is_masked:
                self.update(_char)
                self._value.append(_char._value)
            else:
                self._value.append(' ')

    def update(self, s):
        ''' update the set with a new element

        Parameters
        ----------
        s : instance of a Char object

        '''
        self._chars.append(s)
        super().update(s)

    def intersection_of_subsets(self):
        return set.intersection(*self._chars)
    
    def __repr__(self):
        m = "{} ({})".format(super().__repr__(), "".join(self._value))
        return m


class Sequence(UserList):
    ''' A class to hold the information of a single sequence 
    
    Parameters
    ----------
    ID : str
        ID or lab code
    species : str
        species name
    sequences_chars : str
        ascii representation of the sequence

    '''
    PATTERNS = (re.compile('^[N]+'), re.compile('[N]+$'),
                re.compile('^[X]+'), re.compile('[X]+$'),
                re.compile('^[-]+'), re.compile('[-]+$'))
    
    def __init__(self, ID, species, sequence_chars):
        super().__init__()
        self.ID, self.species = ID, species
        self.sequence_chars = sequence_chars
        self.masked_positions = self.get_masked_positions(sequence_chars)
        for s, m in zip(sequence_chars, self.masked_positions):
            self.append(Char(s, m))


    def __repr__(self):
        return "Sequence {}({}) {}".format(self.species, self.ID, self.sequence_chars)

    def get_masked_positions(self, sequence_chars):
        ''' Get masked positions

        Returns the positions where this sequences has a continuous block of N, X or - characters,
        either leading, or trailing.

        Parameters
        ----------
        sequence_chars : str
            string of sequence characters
        
        Returns
        -------
        m : list of int
            True where masked N appears.
        '''
        m = [False]*len(sequence_chars)
        for p in Sequence.PATTERNS:
            match = p.search(sequence_chars)
            if match:
                for i in range(*match.span()):
                    m[i]=True
        return m
        
        

class SequenceLogic(object):
    ''' Class for state comparison
    '''
    
    def mark_unit_length_states_within_set(self, aset):
        ''' marks for each position whether this position has a unique character
        
        Parameters
        ----------
        aset : list of :obj: Char

        Returns
        -------
        list of tuple of (bool, :class:`State`)
            a list of tuples with first element True for unique character, and 
            second element the character(s) on this position of :class:`State`.
        '''
        selection = []
        for j, c in enumerate(zip(*aset)):
            s = State(c)
            condition =  len(s) == 1
            selection.append((condition, s))
        return selection
        
    def list_non_unique_characters_in_set(self, aset):
        ''' 
        list non-unique characters in set.

        Parameters
        ----------
        aset: list of :class:`Char`
            list of sequences

        Returns
        -------
        list of tuple of (int, :class:`State`)
            Returns list of tuples of position and characters, for which more 
            than one different characters were found.
        '''
        r = self.mark_unit_length_states_within_set(aset)
        return [(j, s) for j, (c, s) in enumerate(r) if not c]

    def list_unique_characters_in_set(self, aset):
        ''' list where aset has unique characters

        Parameters
        ----------
        aset: list of :class:`Char`
            list of sequences

        Returns
        -------
        list of tuple of (int, :class:`State`)
            Returns list of tuples of position and characters, for which only 
            one characeter was found.
        '''
        r = self.mark_unit_length_states_within_set(aset)
        return [(j, s) for j, (c, s) in enumerate(r) if c]

    
    def compute_mdcs(self, set_A, set_B, method = "MDC"):
        '''Computes molecular diagnostic characters
        
        Parameters
        ----------
        set_A: list of :class:`Char`
            list of sequences in list A
        set_B: list of :class:`Char`
            list of sequence in list B
        
        method: {"MDC", "potential_MDC_only"}
            method of comparison.


        Returns
        -------
        list of tuples of (int, :class:`State`, :class:`State`)
            Each tuple contains the position, its state for list A, and its state for list B
            sequences.

        
        This method computes molecular diagnostic characters by comparing the sequences in list 
        set_A and set_B. Two different criteria for comparison can be selected: return molecular 
        diagnostic characters, or only the potential modlecular diagnostic characters.

        Method determining the comparison method:
             * "MDC" returns Molecular Diagnostic Characters only
                conditions 1 and 2 are honoured
             * "potential_MDC_only" return MDCs only
                condition 2 is honoured, condition 1 is violated. 
        '''
        if method not in "MDC potential_MDC_only".split():
            raise ValueError('Invalid method specified. Use either MDC or potential_MDC_only.')
        
        selection = []
        potential_CAs = self.mark_unit_length_states_within_set(set_A)
        
        for j, ((is_unique, state_a), b) in enumerate(zip(potential_CAs, zip(*set_B))):
            if (method=="MDC" and is_unique) or (method=="potential_MDC_only" and not is_unique):
                state_b = State(b)
                if not state_a or not state_b: # if either set is empty, there cannot be a MDC. 
                    continue
                if not state_a.intersection(state_b):
                    selection.append((j, state_a, state_b))
        return selection

