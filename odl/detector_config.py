#!python3

## Import General Tools
from pathlib import Path
import re
from warnings import warn
import yaml
from astropy.io import fits


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
    
    nexp : int
        The number of exposures.
    '''
    def __init__(self, instrument=None, detector='', exptime=None,
                 nexp=1, readoutmode=None):
        self.instrument = instrument
        self.detector = detector
        self.name = 'GenericDetectorConfig'
        self.exptime = exptime
        self.nexp = nexp
        self.readoutmode = readoutmode


    def validate(self):
        pass


    def to_header(self):
        h = fits.Header()
        h['DCNAME'] = (self.name, 'Detector Config Name')
        h['DCINSTR'] = (self.instrument, 'Detector Config Instrument Name')
        h['DCDET'] = (self.detector, 'Detector Config Detector Name')
        h['DCEXPT'] = (self.exptime, 'Detector Config Exptime (sec)')
        h['DCNEXP'] = (self.nexp, 'Detector Config Number of Exposures')
        h['DCRDMODE'] = (self.readoutmode, 'Detector Config Readout Mode')
        return h


    def to_dict(self):
        return {'name': self.name,
                'instrument': self.instrument,
                'detector': self.detector,
                'exptime': self.exptime,
                'nexp': self.nexp,
                'readoutmode': self.readoutmode}


    def to_yaml(self):
        '''Return string corresponding to a Detector Config Description
        Language (DCDL) yaml entry.
        '''
        return yaml.dump(self.to_dict())


    def to_DB(self):
        return {'DetectorConfigs': [self.to_dict()]}


    def write(self, file):
        self.validate()
        p = Path(file).expanduser().absolute()
        if p.exists(): p.unlink()
        with open(p, 'w') as FO:
            FO.write(yaml.dump([self.to_dict()]))


    def estimate_duration(self):
        return self.exptime


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
    def __init__(self, instrument='GenericIR', detector='',
                 exptime=None, nexp=1, readoutmode='CDS', coadds=1):
        super().__init__(instrument=instrument, detector=detector,
                         exptime=exptime, nexp=nexp, readoutmode=readoutmode)
        self.coadds = coadds
        if name is None:
            self.set_name()
        else:
            self.name = name


    def set_name(self):
        exptime = self.exptime if self.exptime is not None else -1
        self.name = (f'{self.instrument} {exptime:.0f}s ({self.readoutmode}, '
                     f'{self.coadds:d} coadds) x{self.nexp}')


    def to_dict(self):
        output = super().to_dict()
        output['coadds'] = self.coadds
        return output


##-------------------------------------------------------------------------
## CCDDetectorConfig
##-------------------------------------------------------------------------
class CCDDetectorConfig(DetectorConfig):
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
    def __init__(self, instrument='GenericCCD', detector='',
                 exptime=None, nexp=1, readoutmode=None, ampmode=None,
                 dark=False, binning='1x1', window=None):
        super().__init__(instrument=instrument, detector=detector,
                         exptime=exptime, nexp=nexp, readoutmode=readoutmode)
        self.ampmode = ampmode
        self.dark = dark
        self.binning = binning
        self.window = window
        if name is None:
            self.set_name()
        else:
            self.name = name


    def set_name(self):
        exptime = self.exptime if self.exptime is not None else -1
        ampmode = self.ampmode if self.ampmode is not None else 'unknown'
        dark_str = {True: ' (Dark)', False: ''}[self.dark]
        self.name = f'{self.instrument}{self.detector} {exptime:.0f}s{dark_str} x{self.nexp}'


    def to_dict(self):
        output = super().to_dict()
        output['ampmode'] = self.ampmode
        output['dark'] = self.dark
        output['binning'] = self.binning
        output['window'] = self.window
        return output


    def erase_time(self):
        return 0


    def readout_time(self):
        return 0


    def other_overhead(self):
        return 0


    def estimate_duration(self):
        total_time = self.erase_time()\
                   + self.exptime\
                   + self.readout_time()\
                   + self.other_overhead()
        return total_time*self.nexp


    def match_time(self, target):
        overhead_per_exp = self.other_overhead()\
                         + self.readout_time()\
                         + self.erase_time()
        self.exptime = target/self.nexp - overhead_per_exp
        self.set_name()


##-------------------------------------------------------------------------
## CMOSDetectorConfig
##-------------------------------------------------------------------------
class CMOSDetectorConfig(DetectorConfig):
    '''An object to hold information about a visible light detector
    configuration.  This is an abstract class which we expect to be subclassed
    to a particular instrument/detector.

    Attributes
    ----------
    readoutmode : str
        Either 'fast' or 'slow'

    gain : int
        The gain value.

    binning : str
        The binning, parsed as (nrows)x(ncolumns)

    window : str
        The window, parsed as x1:x2,y1:y2
    '''
    def __init__(self, instrument='GenericCMOS', detector='',
                 exptime=0, nexp=1, readoutmode='fast', gain=1, overhead=0,
                 binning='1x1', window=None):
        super().__init__(instrument=instrument, detector=detector,
                         exptime=exptime, nexp=nexp, readoutmode=readoutmode)
        self.binning = binning
        self.window = window
        self.gain = gain
        self.overhead = overhead
        self.set_name()


    def set_name(self):
        self.name = f'{self}{self.detector} {self.exptime:.0f}s (gain {self.gain}) x{self.nexp}'


    def to_header(self):
        h = fits.Header()
        h['DCNAME'] = (self.name, 'Detector Config Name')
        h['DCINSTR'] = (self.instrument, 'Detector Config Instrument Name')
        h['DCDET'] = (self.detector, 'Detector Config Detector Name')
        h['DCEXPT'] = (self.exptime, 'Detector Config Exptime (sec)')
        h['DCNEXP'] = (self.nexp, 'Detector Config Number of Exposures')
        h['DCRDMODE'] = (self.readoutmode, 'Detector Config Readout Mode')
        h['DCBIN'] = (self.binning, 'Detector Config Binning')
        h['DCWINDOW'] = (self.window, 'Detector Config Window')
        h['DCGAIN'] = (self.gain, 'Detector Config Gain')
        return h


    def to_dict(self):
        output = super().to_dict()
        output['gain'] = self.gain
        output['binning'] = self.binning
        output['window'] = self.window
        return output


    def estimate_duration(self):
        total_time = self.overhead + self.exptime
        return total_time*self.nexp


    def match_time(self, target):
        overhead_per_exp = self.other_overhead()\
                         + self.readout_time()\
                         + self.erase_time()
        self.exptime = target/self.nexp - overhead_per_exp
        self.set_name()


