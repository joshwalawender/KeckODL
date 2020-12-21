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
from .detector import MOSFIREDetectorConfig


##-------------------------------------------------------------------------
## Constants for the Instrument
##-------------------------------------------------------------------------
exptime_for_domeflats = {'Y': 17, 'J': 11, 'H': 11, 'K': 11}



##-------------------------------------------------------------------------
## MOSFIREInstrumentConfig
##-------------------------------------------------------------------------
class MOSFIREConfig(InstrumentConfig):
    '''An object to hold information about MOSFIRE configuration.
    '''
    def __init__(self, mode='spectroscopy', filter='Y',
                 mask='longslit_46x0.7'):
        super().__init__()
        self.mode = mode
        self.filter = filter
        self.mask = mask
        self.arclamp = None
        self.domeflatlamp = None
        self.name = f'{self.mask} {self.filter}-{self.mode}'
        if self.arclamp is not None:
            self.name += f' arclamp={self.arclamp}'
        if self.domeflatlamp is not None:
            self.name += f' domeflatlamp={self.domeflatlamp}'


    ##-------------------------------------------------------------------------
    ## Validate
    def validate(self):
        '''Check values and verify that they meet assumptions.
        
        Check:
        
        Warn:
        '''
        pass


    def to_dict(self):
        output = super().to_dict()
        output['InstrumentConfigs'][0]['filter'] = self.filter
        output['InstrumentConfigs'][0]['mode'] = self.mode
        output['InstrumentConfigs'][0]['mask'] = self.mask
        output['InstrumentConfigs'][0]['arclamp'] = self.arclamp
        output['InstrumentConfigs'][0]['domeflatlamp'] = self.domeflatlamp
        return output


    def arcs(self, lampname):
        '''
        '''
        ic_for_arcs = deepcopy(self)
        ic_for_arcs.arclamp = lampname
        ic_for_arcs.name += f' arclamp={ic_for_arcs.arclamp}'
        dc_for_arcs = MOSFIREDetectorConfig(exptime=1, readoutmode='CDS')
        arcs = ObservingBlock(target=None,
                              pattern=Stare(repeat=2),
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
        exptime = exptime_for_domeflats[self.filter]
        dc_for_domeflats = MOSFIREDetectorConfig(exptime=exptime,
                                                 readoutmode='CDS')
        domeflats = ObservingBlock(target=DomeFlats(),
                                   pattern=Stare(repeat=7),
                                   instconfig=ic_for_domeflats,
                                   detconfig=dc_for_domeflats,
                                   )
        return domeflats


    def cals(self):
        '''
        '''
        cals = ObservingBlockList([self.domeflats()])
        if self.filter == 'K':
            cals.append(self.domeflats(off=True))
            cals.append(self.arcs('Ne'))
            cals.append(self.arcs('Ar'))
        return cals

