#!python3

## Import General Tools
import re
from warnings import warn
from copy import deepcopy

from ..detector_config import IRDetectorConfig


##-------------------------------------------------------------------------
## MOSFIREDetectorConfig
##-------------------------------------------------------------------------
class MOSFIREDetectorConfig(IRDetectorConfig):
    '''An object to hold information about MOSFIRE detector configuration.
    '''
    def __init__(self, exptime=None, readoutmode='CDS', coadds=1):
        super().__init__(instrument='MOSFIRE', exptime=exptime,
                         readoutmode=readoutmode, coadds=coadds)


    ##-------------------------------------------------------------------------
    ## Validate
    def validate(self):
        '''Check values and verify that they meet assumptions.
        
        Check:
        - readoutmode is either CDS or MCDSn where n is 1-16.
        
        Warn:
        '''
        parse_readoutmode = re.match('(M?)CDS(\d*)', self.readoutmode)
        if parse_readoutmode is None:
            raise DetectorConfigError(f'Readout Mode "{self.readoutmode}" '
                                      f'is not CDS or MCDSn')
        else:
            nreads = int(parse_readoutmode.group(2))
            if nreads > 16:
                raise DetectorConfigError(f'MCDS{nreads} not supported '
                                          f'(only 1-16 are supported)')


##-------------------------------------------------------------------------
## Pre-Defined Values
##-------------------------------------------------------------------------
default_acq = MOSFIREDetectorConfig(exptime=7, coadds=3, readoutmode='CDS')
bright_acq = MOSFIREDetectorConfig(exptime=2, coadds=5, readoutmode='CDS')
