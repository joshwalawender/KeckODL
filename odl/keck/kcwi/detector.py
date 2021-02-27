#!python3

## Import General Tools
import re
from warnings import warn
from copy import deepcopy

from odl.detector_config import VisibleDetectorConfig


##-------------------------------------------------------------------------
## KCWIblueDetectorConfig
##-------------------------------------------------------------------------
class KCWIblueDetectorConfig(VisibleDetectorConfig):
    '''An object to hold information about KCWI Blue detector configuration.
    
    readoutmode corresponds to the KCWI config keyword ccdmodeb
    
    kbds keywords:
    CCDMODE      CCD mode (0 slow/1 fast)

    For ampmode
    '''
    def __init__(self, name=None, exptime=None, nexp=1, readoutmode=0,
                 ampmode=9, dark=False, binning='1x1', window=None, gain=10):
        super().__init__(name=name, instrument='KCWI', detector='blue', 
                         exptime=exptime, nexp=nexp, readoutmode=readoutmode,
                         ampmode=ampmode, dark=dark, binning=binning,
                         window=window)
        self.gain = gain


    ##-------------------------------------------------------------------------
    ## Validate
    def validate(self):
        '''Check values and verify that they meet assumptions.
        
        Check:
        - exptime is in range 1-3600
        - readoutmode is in range ??
        - ampmode is in range ??
        - dark is boolean
        - binning is one of 1x1, 2x2
        - gain is in range ??

        Warn:
        - Window is not used
        '''
        pass


    def erase_time(self):
        return 0


    def readout_time(self):
        '''
        Single amp slow read, 1x1 [2x2] 337 [106] s
        Dual amp slow read, 1x1 [2x2]   170 [53] s
        Quad amp slow read, 1x1 [2x2]   85 [27] s  DO NOT USE!
        Single amp fast read, 1x1 [2x2] 75 [25] s
        Dual amp fast read,1x1 [2x2]    38 [13] s
        Quad amp fast read, 1x1 [2x2]   19 [7] s   NOT RECOMMENDED
        '''
        rspeed = {0: 'slow', 1: 'fast'}[self.readoutmode]
        namps_full = {0 : 'quad (ALL)', 1 : 'single C', 2 : 'single E',
                      3 : 'single D', 4 : 'single F', 5 : 'single B',
                      6 : 'single G', 7 : 'single A', 8 : 'single H',
                      9 : 'dual (A&B)', 10 : 'dual (C&D)'}[self.ampmode]
        namps_str = namps_full.split()[0]
        read_times = {'slow':{'single': {'1x1': 337, '2x2': 106},
                              'dual': {'1x1': 170, '2x2': 53},
                              'quad': {'1x1': 85, '2x2': 27} },
                      'fast':{'single': {'1x1': 75, '2x2': 25},
                              'dual': {'1x1': 38, '2x2': 13},
                              'quad': {'1x1': 19, '2x2': 7} } }
        return read_times[rspeed][namps_str][self.binning]


    def other_overhead(self):
        return 0


##-------------------------------------------------------------------------
## KCWIredDetectorConfig
##-------------------------------------------------------------------------
class KCWIredDetectorConfig(VisibleDetectorConfig):
    '''An object to hold information about KCWI Red detector configuration.
    
    readoutmode corresponds to the KCWI config keyword ccdmoder
    '''
    def __init__(self, name=None, exptime=None, nexp=1, readoutmode=0,
                 ampmode=9, dark=False, binning='1x1', window=None, gain=10):
        super().__init__(name=name, instrument='KCWI', detector='red', 
                         exptime=exptime, nexp=nexp, readoutmode=readoutmode,
                         ampmode=ampmode, dark=dark, binning=binning,
                         window=window)
        self.gain = gain


    ##-------------------------------------------------------------------------
    ## Validate
    def validate(self):
        '''Check values and verify that they meet assumptions.
        
        Check:
        - exptime is in range 1-3600
        - readoutmode is in range ??
        - ampmode is in range ??
        - dark is boolean
        - binning is one of 1x1, 2x2
        - gain is in range ??

        Warn:
        - Window is not used
        '''
        pass


##-------------------------------------------------------------------------
## KCWIFPCDetectorConfig
##-------------------------------------------------------------------------
class KCWIFPCDetectorConfig(VisibleDetectorConfig):
    '''An object to hold information about KCWI FPC detector configuration.
    
    readoutmode corresponds to the KCWI config keyword ccdmoder
    '''
    def __init__(self, name=None, exptime=None, nexp=1, readoutmode=0,
                 ampmode=9, dark=False, binning='1x1', window=None, gain=10):
        super().__init__(name=name, instrument='KCWI', detector='FPC', 
                         exptime=exptime, nexp=nexp, readoutmode=readoutmode,
                         ampmode=ampmode, dark=dark, binning=binning,
                         window=window)
        self.gain = gain


    ##-------------------------------------------------------------------------
    ## Validate
    def validate(self):
        '''Check values and verify that they meet assumptions.
        
        Check:
        - exptime is in range 1-3600
        - readoutmode is in range ??
        - ampmode is in range ??
        - dark is boolean
        - binning is one of 1x1, 2x2
        - gain is in range ??

        Warn:
        - Window is not used
        '''
        pass


