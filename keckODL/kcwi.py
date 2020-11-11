#!python3

## Import General Tools
from pathlib import Path
import re
from warnings import warn
import yaml
from astropy import units as u


from .detector_config import VisibleDetectorConfig
from .instrument_config import InstrumentConfig


##-------------------------------------------------------------------------
## KCWIblueDetectorConfig
##-------------------------------------------------------------------------
class KCWIblueDetectorConfig(VisibleDetectorConfig):
    '''An object to hold information about KCWI Blue detector configuration.
    '''
    def __init__(self, exptime=None, readoutmode=None, ampmode=10,
                 dark=False, binning='1x1', window=None):
        super().__init__(exptime=exptime, readoutmode=readoutmode,
                         ampmode=ampmode, dark=dark, binning=binning,
                         window=window)
        self.instrument = 'KCWIblue'
        self.set_name()


    ##-------------------------------------------------------------------------
    ## Validate
    def validate(self):
        '''Check values and verify that they meet assumptions.
        
        Check:
        
        Warn:
        '''
        pass


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


    def validate(self):
        '''Check values and verify that they meet assumptions.
        
        Check:
        
        Warn:
        '''
        pass


    def to_dict(self):
        output = super().to_dict()
        output['slicer'] = self.slicer
        output['grating'] = self.grating
        output['cwave'] = self.cwave
        output['pwave'] = self.pwave
        return output


    def __str__(self):
        self.name = f'{self.slicer} {self.grating} {self.cwave*u.A:.0f}'
        return f'{self.name}'


    def __repr__(self):
        self.name = f'{self.slicer} {self.grating} {self.cwave*u.A:.0f}'
        return f'{self.name}'


