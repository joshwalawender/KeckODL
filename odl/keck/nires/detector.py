#!python3

## Import General Tools
import re
from warnings import warn
from copy import deepcopy

from odl.detector_config import IRDetectorConfig


##-------------------------------------------------------------------------
## NIRESDetectorConfig
##-------------------------------------------------------------------------
class NIRESSpecDetectorConfig(IRDetectorConfig):
    '''An object to hold information about NIRES detector configuration.
    '''
    def __init__(self, exptime=None, readoutmode='CDS', coadds=1, nexp=1):
        super().__init__(exptime=exptime, nexp=nexp, readoutmode=readoutmode,
                         coadds=coadds)
        self.instrument = 'NIRES Spec'
        self.set_name()


    ##-------------------------------------------------------------------------
    ## Validate
    def validate(self):
        '''Check values and verify that they meet assumptions.
        
        Check:
        - readoutmode is either CDS or MCDSn where n is 1-32.
        
        Warn:
        '''
        parse_readmode = re.match('(M?)CDS(\d*)', self.readoutmode)
        if parse_readmode is None:
            raise DetectorConfigError(f'Readout Mode "{self.readoutmode}" '
                                      f'is not CDS or MCDSn')
        else:
            nreads = int(parse_readmode.group(2))
            if nreads > 32:
                raise DetectorConfigError(f'MCDS{nreads} not supported '
                                          f'(only 1-32 are supported)')


class NIRESScamDetectorConfig(IRDetectorConfig):
    '''An object to hold information about NIRES detector configuration.
    '''
    def __init__(self, exptime=None, readoutmode='CDS', coadds=1, nexp=1):
        super().__init__(exptime=exptime, nexp=nexp, readoutmode=readoutmode,
                         coadds=coadds)
        self.instrument = 'NIRES SCAM'
        self.set_name()


    ##-------------------------------------------------------------------------
    ## Validate
    def validate(self):
        '''Check values and verify that they meet assumptions.
        
        Check:
        - readoutmode is either CDS or MCDSn where n is 1-32.
        
        Warn:
        '''
        parse_readmode = re.match('(M?)CDS(\d*)', self.readoutmode)
        if parse_readmode is None:
            raise DetectorConfigError(f'Readout Mode "{self.readoutmode}" '
                                      f'is not CDS or MCDSn')
        if parse_readmode.group(1) == '' and parse_readmode.group(2) == '':
            pass
        else:
            nreads = int(parse_readmode.group(2))
            if nreads > 32:
                raise DetectorConfigError(f'MCDS{nreads} not supported '
                                          f'(only 1-32 are supported)')

