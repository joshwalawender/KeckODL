#!python3

## Import General Tools
from pathlib import Path
import re
from warnings import warn


class DetectorConfigError(Exception):
    pass


class DetectorConfigWarning(UserWarning):
    pass


##-------------------------------------------------------------------------
## DetectorConfig
##-------------------------------------------------------------------------
class DetectorConfig():
    '''An object to hold information about a detector configuration.

    Attributes
    ----------
    exptime : float
        The exposure time in units of seconds (per coadd if applicable).
    
    readoutmode : str
        The readout mode.  Must be one of a set of approved values depending
        on the instrument.
    '''
    def __init__(self, exptime=None, readoutmode=None):
        self.instrument = None
        self.exptime = exptime
        self.readoutmode = readoutmode

    def to_dict(self):
        return {'exptime': self.exptime, 'readoutmode': self.readoutmode}



##-------------------------------------------------------------------------
## IRDetectorConfig
##-------------------------------------------------------------------------
class IRDetectorConfig(DetectorConfig):
    '''An object to hold information about an IR detector configuration.

    Attributes
    ----------
    coadds : int
        The number of coadds (if applicable)
    '''
    def __init__(self, exptime=None, readoutmode='CDS', coadds=1):
        super().__init__(exptime=exptime, readoutmode=readoutmode)
        self.coadds = coadds


    def to_dict(self):
        output = super().to_dict()
        output['coadds'] = self.coadds
        return output


##-------------------------------------------------------------------------
## VisibleDetectorConfig
##-------------------------------------------------------------------------
class VisibleDetectorConfig(DetectorConfig):
    '''An object to hold information about a visible light detector configuration.

    Attributes
    ----------
    ampmode : str
        The amplifier mode.  Must be one of a set of approved values depending
        on the instrument.
    
    dark : bool
        If True, will not open shutter during exposure.
    
    binning : str
        The binning, parsed as (nrows)x(ncolumns)
    
    window : str
        The window, parsed as x1:x2,y1:y2
    '''
    def __init__(self, exptime=None, readoutmode=None, ampmode=None,
                 dark=False, binning='1x1', window=None):
        super().__init__(exptime=exptime, readoutmode=readoutmode)
        self.ampmode = ampmode
        self.dark = dark
        self.binning = binning
        self.window = window


    def to_dict(self):
        output = super().to_dict()
        output['ampmode'] = self.ampmode
        output['dark'] = self.dark
        output['binning'] = self.binning
        output['window'] = self.window
        return output


##-------------------------------------------------------------------------
## NIRESDetectorConfig
##-------------------------------------------------------------------------
class NIRESDetectorConfig(IRDetectorConfig):
    '''An object to hold information about NIRES detector configuration.
    '''
    def __init__(self):
        self.instrument = 'NIRES'


    ##-------------------------------------------------------------------------
    ## Validate
    def validate(self):
        '''Check values and verify that they meet assumptions.
        
        Check:
        - readoutmode is either CDS or MCDSn where n is 1-32.
        
        Warn:
        '''
        parse_readoutmode = re.match('(M?)CDS(\d*)', self.readoutmode)
        if parse_readoutmode is None:
            raise DetectorConfigError(f'Readout Mode "{self.readoutmode}" '
                                      f'is not CDS or MCDSn')
        else:
            nreads = int(parse_readoutmode.group(2))
            if nreads > 32:
                raise DetectorConfigError(f'MCDS{nreads} not supported '
                                          f'(only 1-32 are supported)')


##-------------------------------------------------------------------------
## KCWIbDetectorConfig
##-------------------------------------------------------------------------
class KCWIbDetectorConfig(VisibleDetectorConfig):
    '''An object to hold information about KCWI Blue detector configuration.
    '''
    def __init__(self):
        self.instrument = 'KCWIblue'

    ##-------------------------------------------------------------------------
    ## Validate
    def validate(self):
        '''Check values and verify that they meet assumptions.
        
        Check:
        
        Warn:
        '''
        pass
