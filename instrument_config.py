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
    '''An object to hold information about an instrument configuration.
    '''
    def __init__(self, name='GenericInstrumentConfig'):
        self.name = name
        self.instrument = 'unknown'


    def __str__(self):
        return f'{self.name}'


    def __repr__(self):
        return f'{self.name}'


##-------------------------------------------------------------------------
## KCWIblueConfig
##-------------------------------------------------------------------------
class KCWIblueConfig(InstrumentConfig):
    '''An object to hold information about KCWI Blue configuration.
    '''
    def __init__(self, slicer='medium', grating='BH3', cwave=4800, pwave=None):
        super().__init__()
        self.instrument = 'KCWIblue'
        self.slicer = slicer
        self.grating = grating
        self.cwave = cwave
        self.pwave = cwave-300 if pwave is None else pwave


    ##-------------------------------------------------------------------------
    ## Validate
    def validate(self):
        '''Check values and verify that they meet assumptions.
        
        Check:
        
        Warn:
        '''
        pass


    def __str__(self):
        self.name = f'{self.slicer} {self.grating} {self.cwave*u.A:.0f}'
        return f'{self.name}'


    def __repr__(self):
        self.name = f'{self.slicer} {self.grating} {self.cwave*u.A:.0f}'
        return f'{self.name}'


##-------------------------------------------------------------------------
## NIRESConfig
##-------------------------------------------------------------------------
class NIRESConfig(InstrumentConfig):
    '''An object to hold information about NIRES configuration.
    '''
    def __init__(self):
        super().__init__()
        self.instrument = 'NIRES'

    ##-------------------------------------------------------------------------
    ## Validate
    def validate(self):
        '''Check values and verify that they meet assumptions.
        
        Check:
        
        Warn:
        '''
        pass


##-------------------------------------------------------------------------
## MOSFIREConfig
##-------------------------------------------------------------------------
class MOSFIREConfig(InstrumentConfig):
    '''An object to hold information about MOSFIRE configuration.
    '''
    def __init__(self, mode='spectroscopy', filter='Y', mask='longslit_46x0.7'):
        super().__init__()
        self.instrument = 'MOSFIRE'
        self.mode = mode
        self.filter = filter
        self.mask = mask
        self.name = f'{self.mask} {self.filter}-{self.mode}'


    ##-------------------------------------------------------------------------
    ## Validate
    def validate(self):
        '''Check values and verify that they meet assumptions.
        
        Check:
        
        Warn:
        '''
        pass
