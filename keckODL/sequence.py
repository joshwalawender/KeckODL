#!python3

## Import General Tools
from pathlib import Path
from astropy import units as u
from collections import UserList


class SequenceError(Exception):
    pass


class SequenceWarning(UserWarning):
    pass


##-------------------------------------------------------------------------
## SequenceElement
##-------------------------------------------------------------------------
class SequenceElement():
    '''One element of the sequence.
    
    Can be thought of as one line in a table of actions.
    '''
    def __init__(self, pattern=None, detconfig=None, instconfig=None, repeat=1):
        self.pattern = pattern
        self.detconfig = detconfig
        self.instconfig = instconfig
        self.repeat = repeat


    def validate(self):
        pass


    def estimate_time(self):
        '''Estimate the wall clock time to complete the sequence.
        '''
        raise NotImplementedError()


    def __str__(self):
        return f'{str(self.pattern):19s}|{str(self.detconfig):29s}|{str(self.instconfig):29s}|{self.repeat:6d}'


    def __repr__(self):
        return f'{str(self.pattern):19s}|{str(self.detconfig):29s}|{str(self.instconfig):29s}|{self.repeat:6d}'


##-------------------------------------------------------------------------
## Sequence
##-------------------------------------------------------------------------
class Sequence(UserList):
    '''An ordered list of SequenceElements
    '''
    def validate(self):
        for i,s in enumerate(self.data):
            if type(s) != SequenceElement:
                raise SequenceError(f'A Sequence must be made up of SequenceElements. '
                                    f'Element {i} is type {type(s)}.')
            s.validate()


    def estimate_time(self):
        '''Estimate the wall clock time to complete the sequence.
        '''
        raise NotImplementedError()


    def __str__(self):
        output = [f'{"Pattern":19s}|{"DetectorConfig":29s}|{"InstrumentConfig":29s}|{"repeat":6s}',
                  f'{"-"*19:19s}|{"-"*29:29s}|{"-"*29:29s}|{"-"*6:6s}',]
        for item in self.data:
            output.append(item.__str__())
        return "\n".join(output)


    def __repr__(self):
        output = [f'{"Pattern":19s}|{"DetectorConfig":29s}|{"InstrumentConfig":29s}|{"repeat":6s}',
                  f'{"-"*19:19s}|{"-"*29:29s}|{"-"*29:29s}|{"-"*6:6s}',]
        for item in self.data:
            output.append(item.__str__())
        return "\n".join(output)
