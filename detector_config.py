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
        self.name = 'GenericDetectorConfig'
        self.exptime = exptime
        self.readoutmode = readoutmode


    def to_dict(self):
        return {'exptime': self.exptime, 'readoutmode': self.readoutmode}


    def __str__(self):
        return self.name


    def __repr__(self):
        return self.name


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
        self.instrument = 'GenericIR'
        self.set_name()


    def set_name(self):
        exptime = self.exptime if self.exptime is not None else -1
        self.name = f'{exptime:.1f}s ({self.readoutmode}, {self.coadds:d} coadds)'


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
        self.instrument = 'GenericVis'
        self.ampmode = ampmode
        self.dark = dark
        self.binning = binning
        self.window = window
        self.set_name()


    def set_name(self):
        exptime = self.exptime if self.exptime is not None else -1
        ampmode = self.ampmode if self.ampmode is not None else 'unknown'
        dark_string = {True: ', Dark', False: ''}[self.dark]
        self.name = f'{exptime:.1f}s ({ampmode}{dark_string})'


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
    def __init__(self, exptime=None, readoutmode='CDS', coadds=1):
        super().__init__(exptime=exptime, readoutmode=readoutmode, coadds=coadds)
        self.instrument = 'NIRES'
        self.set_name()


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
## MOSFIREDetectorConfig
##-------------------------------------------------------------------------
class MOSFIREDetectorConfig(IRDetectorConfig):
    '''An object to hold information about NIRES detector configuration.
    '''
    def __init__(self, exptime=None, readoutmode='CDS', coadds=1):
        super().__init__(exptime=exptime, readoutmode=readoutmode, coadds=coadds)
        self.instrument = 'MOSFIRE'
        self.set_name()


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
                                          f'(only 1-16 are supported)')


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
