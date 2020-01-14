from collections import UserList, defaultdict


class Char(set):
    IUPAC = {'A':'A', 'T':'T', 'C':'C', 'G':'G', 'Y':'CT', 'R':'AG', 'W':'AT',
             'S':'GC', 'K':'TG', 'M':'CA', 'D':'AGT', 'V':'AGC', 'H':'ACT', 'B':'CGT',
             'X':'ACTG', 'N':'ACTG', '-':'-'}

    def __init__(self, c):
        s = Char.IUPAC[c]
        super().__init__(s[0])
        for _s in s[1:]:
            self.add(_s)
        self._value = c
        
class State(set):

    def __init__(self, chars):
        super().__init__()
        self._value = []
        self._chars = []
        for _char in chars:
            self.update(_char)

    def update(self, s):
        self._value.append(s._value)
        self._chars.append(s)
        super().update(s)

    def intersection_of_subsets(self):
        return set.intersection(*self._chars)
    
    def __repr__(self):
        m = "{} ({})".format(super().__repr__(), "".join(self._value))
        return m


class Sequence(UserList):
    ''' A class to hold the information of a single sequence '''
    IDcounter = 0
    def __init__(self, ID, species, sequence_chars):
        super().__init__()
        self.ID, self.species = ID, species
        for s in sequence_chars:
            self.append(Char(s))

    def __repr__(self):
        return "Sequence {}({}) {}".format(self.species, self.ID, self.pretty_print(self, c=''))
    
    @staticmethod
    def pretty_print(m,c=" "):
        return c.join(_m._value for _m in m)
        

class SequenceLogic(object):

    
    def mark_unit_length_states_within_set(self, aset):
        ''' 
        '''
        selection = []
        for j, c in enumerate(zip(*aset)):
            s = State(c)
            condition =  len(s) == 1
            selection.append((condition, s))
        return selection
        
    def differences_within_set(self, aset):
        ''' differences_within_set(aset)

        aset: list of seqeunces

        returns a list of those columns for which are one or more differences found between the sequences
        of this aset
        '''
        r = self.mark_unit_length_states_within_set(aset)
        return [(j, s) for j, (c, s) in enumerate(r) if not c]

    def agreements_within_set(self, aset):
        ''' agreements_within_set(aset)

        aset: list of sequences

        returns a list of those columns for which all columns agree between the sequences 
        of this aset
        '''
        r = self.mark_unit_length_states_within_set(aset)
        return [(j, s) for j, (c, s) in enumerate(r) if c]

    
    def compare_sets(self, set_A, set_B, invert=False):
        '''Compares set A with set B and list 
            the differences  if not invert
            the agreements if invert
        '''
        selection = []
        potential_CAs = self.mark_unit_length_states_within_set(set_A)
        for j, ((is_unique, state_a), b) in enumerate(zip(potential_CAs, zip(*set_B))):
            if is_unique:
                state_b = State(b)
                if not state_a.intersection(state_b):
                    selection.append((j, state_a, state_b))
        return selection

