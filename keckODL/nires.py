#!python3

## Import General Tools
from pathlib import Path
import re
from warnings import warn
import yaml


from .detector_config import IRDetectorConfig
from .instrument_config import InstrumentConfig


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


