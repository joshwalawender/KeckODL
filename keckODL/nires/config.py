#!python3

## Import General Tools
from pathlib import Path
import re
from warnings import warn
from copy import deepcopy
from astropy import units as u


from ..instrument_config import InstrumentConfig
from ..offset import Stare
from ..block import ObservingBlock, ObservingBlockList
from ..target import DomeFlats
from .detector import NIRESScamDetectorConfig, NIRESSpecDetectorConfig


##-------------------------------------------------------------------------
## Constants for the Instrument
##-------------------------------------------------------------------------
lamp_exptimes = {'arcs': 120, 'domeflats': 100}


##-------------------------------------------------------------------------
## NIRESConfig
##-------------------------------------------------------------------------
class NIRESConfig(InstrumentConfig):
    '''An object to hold information about NIRES configuration.
    '''
    def __init__(self, detconfig=None):
        super().__init__()
        self.name = 'NIRES Instrument Config'

    ##-------------------------------------------------------------------------
    ## Validate
    def validate(self):
        '''Check values and verify that they meet assumptions.
        
        Check:
        
        Warn:
        '''
        pass


    def arcs(self):
        '''
        '''
        ic_for_arcs = deepcopy(self)
        ic_for_arcs.domeflatlamp = 'niresarcs'
        ic_for_arcs.name += f' arclamp'
        exptime = lamp_exptimes['arcs']
        dc_for_arcs = NIRESSpecDetectorConfig(exptime=exptime,
                                              readoutmode='CDS')
        arcs = ObservingBlock(target=None,
                              pattern=Stare(repeat=3),
                              instconfig=ic_for_arcs,
                              detconfig=dc_for_arcs,
                              )
        return arcs


    def domeflats(self, off=False):
        '''
        '''
        ic_for_domeflats = deepcopy(self)
        ic_for_domeflats.domeflatlamp = not off
        lamp_str = {False: 'on', True: 'off'}[off]
        ic_for_domeflats.name += f' domelamp={lamp_str}'
        dc_for_domeflats = NIRESSpecDetectorConfig(exptime=100, 
                                           readoutmode='CDS')
        domeflats = ObservingBlock(target=DomeFlats(),
                                   pattern=Stare(repeat=9),
                                   instconfig=ic_for_domeflats,
                                   detconfig=dc_for_domeflats,
                                   )
        return domeflats


    def cals(self):
        '''
        '''
        cals = ObservingBlockList()
        cals.append(self.arcs())
        cals.append(self.domeflats())
        return cals


