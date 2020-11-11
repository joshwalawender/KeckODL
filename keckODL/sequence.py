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
        return {'shutter open time': len(self.pattern) * self.detconfig.exptime * self.repeat,
                  'wall clock time': len(self.pattern) * self.detconfig.exptime * self.repeat,
                }


    def __str__(self):
        return f'{str(self.pattern):19s}|{self.repeat:6d} |{str(self.detconfig):29s}|{str(self.instconfig):45s}'


    def __repr__(self):
        return f'{str(self.pattern):19s}|{self.repeat:6d} |{str(self.detconfig):29s}|{str(self.instconfig):45s}'


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
        estimate = {'shutter open time': 0, 'wall clock time': 0}
        for s in self.data:
            estimate['shutter open time'] += s.estimate_time()['shutter open time']
            estimate['wall clock time'] += s.estimate_time()['wall clock time']
        print(f"Shutter Open Time: {estimate['shutter open time']} s "
              f"({estimate['shutter open time']/3600:.1f} hrs)")
        print(f"Wall Clock Time: {estimate['wall clock time']} s "
              f"({estimate['wall clock time']/3600:.1f} hrs)")


    def __str__(self):
        output = [f'{"Pattern":19s}|{"repeat":7s}|{"DetectorConfig":29s}|{"InstrumentConfig":45s}',
                  f'{"-"*19:19s}|{"-"*7:7s}|{"-"*29:29s}|{"-"*45:45s}',]
        for item in self.data:
            output.append(item.__str__())
        return "\n".join(output)


    def __repr__(self):
        output = [f'{"Pattern":19s}|{"repeat":7s}|{"DetectorConfig":29s}|{"InstrumentConfig":45s}',
                  f'{"-"*19:19s}|{"-"*7:7s}|{"-"*29:29s}|{"-"*45:45s}',]
        for item in self.data:
            output.append(item.__str__())
        return "\n".join(output)
