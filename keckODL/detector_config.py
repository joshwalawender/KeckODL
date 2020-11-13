#!python3

## Import General Tools
from pathlib import Path
import re
from warnings import warn
import yaml


class DetectorConfigError(Exception): pass


class DetectorConfigWarning(UserWarning): pass


##-------------------------------------------------------------------------
## DetectorConfig
##-------------------------------------------------------------------------
class DetectorConfig():
    '''An object to hold information about a detector configuration.  This is
    an abstract class which we expect to be subclassed.

    Attributes
    ----------
    exptime : float
        The exposure time in units of seconds (per coadd if applicable).
    
    readoutmode : str
        The readout mode.  Must be one of a set of approved values depending
        on the instrument.
    
    Methods
    -------
    validate
    to_dict
    to_YAML
    write
    '''
    def __init__(self, instrument='GenericDetector', exptime=None, readoutmode=None):
        self.instrument = instrument
        self.name = 'GenericDetectorConfig'
        self.exptime = exptime
        self.readoutmode = readoutmode


    def validate(self):
        pass


    def to_dict(self):
        return {'name': self.name,
                'instrument': self.instrument,
                'exptime': self.exptime,
                'readoutmode': self.readoutmode}


    def to_YAML(self):
        '''Return string corresponding to a Detector Config Description
        Language (DCDL) YAML entry.
        '''
        return yaml.dump(self.to_dict())


    def write(self, file):
        self.validate()
        p = Path(file).expanduser().absolute()
        if p.exists(): p.unlink()
        with open(p, 'w') as FO:
            FO.write(yaml.dump(self.to_dict()))


    def __str__(self):
        return self.name


    def __repr__(self):
        return self.name


##-------------------------------------------------------------------------
## IRDetectorConfig
##-------------------------------------------------------------------------
class IRDetectorConfig(DetectorConfig):
    '''An object to hold information about an IR detector configuration.  This
    is an abstract class which we expect to be subclassed to a particular
    instrument/detector.

    Attributes
    ----------
    coadds : int
        The number of coadds (if applicable)
    '''
    def __init__(self, instrument='GenericIR', exptime=None, readoutmode='CDS',
                 coadds=1):
        super().__init__(instrument=instrument, exptime=exptime,
                         readoutmode=readoutmode)
        self.coadds = coadds
        self.set_name()


    def set_name(self):
        exptime = self.exptime if self.exptime is not None else -1
        self.name = f'{self.instrument} {exptime:.1f}s ({self.readoutmode}, {self.coadds:d} coadds)'


    def to_dict(self):
        output = super().to_dict()
        output['coadds'] = self.coadds
        return output


##-------------------------------------------------------------------------
## VisibleDetectorConfig
##-------------------------------------------------------------------------
class VisibleDetectorConfig(DetectorConfig):
    '''An object to hold information about a visible light detector
    configuration.  This is an abstract class which we expect to be subclassed
    to a particular instrument/detector.

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
    def __init__(self, instrument='GenericVis', exptime=None, readoutmode=None,
                 ampmode=None, dark=False, binning='1x1', window=None):
        super().__init__(instrument=instrument, exptime=exptime,
                         readoutmode=readoutmode)
        self.ampmode = ampmode
        self.dark = dark
        self.binning = binning
        self.window = window
        self.set_name()


    def set_name(self):
        exptime = self.exptime if self.exptime is not None else -1
        ampmode = self.ampmode if self.ampmode is not None else 'unknown'
        dark_string = {True: ', Dark', False: ''}[self.dark]
        self.name = f'{self.instrument} {exptime:.1f}s ({ampmode}{dark_string})'


    def to_dict(self):
        output = super().to_dict()
        output['ampmode'] = self.ampmode
        output['dark'] = self.dark
        output['binning'] = self.binning
        output['window'] = self.window
        return output


