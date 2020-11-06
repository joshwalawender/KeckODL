#!python3

## Import General Tools
from pathlib import Path
from astropy import units as u


class InstrumentConfigError(Exception):
    pass


class InstrumentConfigWarning(UserWarning):
    pass


##-------------------------------------------------------------------------
## InstrumentConfig
##-------------------------------------------------------------------------
class InstrumentConfig():
    '''An object to hold information about a detector configuration.
    '''
    def __init__(self):
        pass

