#!python3

## Import General Tools
from pathlib import Path
from astropy import units as u
from .offset import OffsetFrame, TelescopeOffset


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
    def __init__(self, offset=None, config=None):
        self.offset = offset
        self.config = config


##-------------------------------------------------------------------------
## Sequence
##-------------------------------------------------------------------------
class Sequence(UserList):
    '''An ordered list of SequenceElements
    '''
    def validate(self):
        for t in self.data:
            t.validate()
