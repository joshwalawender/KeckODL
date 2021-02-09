#!python3

## Import General Tools
from pathlib import Path
import re
from warnings import warn
from copy import deepcopy
import yaml
from astropy import units as u

from ..instrument_config import InstrumentConfig
from ..offset import Stare
from ..block import ObservingBlockList, CalibrationBlock
from ..target import DomeFlats
from .detector import KCWIblueDetectorConfig, KCWIredDetectorConfig


##-------------------------------------------------------------------------
## Constants for the Instrument
##-------------------------------------------------------------------------
lamp_exptimes = {'FEAR': 30, 'THAR': 45, 'CONT': 6}


##-------------------------------------------------------------------------
## KCWIConfig
##-------------------------------------------------------------------------
class KCWIConfig(InstrumentConfig):
    '''An object to hold information about KCWI Blue+Red configuration.
    '''
    def __init__(self, name=None, slicer='medium', 
                 bluegrating='BH3', bluefilter='KBlue',
                 bluecwave=4800, bluepwave=None,
                 bluenandsmask=False, bluefocus=None,
                 redgrating='BH3', redfilter='KRed',
                 redcwave=4800, redpwave=None,
                 rednandsmask=False, redfocus=None,
                 calmirror='Sky', calobj='Dark', arclamp=None,
                 domeflatlamp=None, polarizer='Sky'):
        super().__init__(name=name)
        self.slicer = slicer
        self.polarizer = polarizer

        # Blue Components
        self.bluegrating = bluegrating
        self.bluefilter = bluefilter
        self.bluecwave = bluecwave
        self.bluepwave = bluepwave
        self.bluenandsmask = bluenandsmask
        self.bluefocus = bluefocus

        # Red Components
        self.redgrating = redgrating
        self.redfilter = redfilter
        self.redcwave = redcwave
        self.redpwave = redpwave
        self.rednandsmask = rednandsmask
        self.redfocus = redfocus

        # Calibration Components
        self.calmirror = calmirror
        self.calobj = calobj
        self.arclamp = arclamp
        self.domeflatlamp = domeflatlamp

        # Set config name
        if self.slicer == 'FPC':
            self.name = 'FPC'
        else:
            self.name = f'{self.slicer} {self.bluegrating} {self.bluecwave*u.A:.0f}'
        if self.calobj != 'Dark':
            self.name += f' calobj={self.calobj}'
        if self.arclamp is not None:
            self.name += f' arclamp={self.arclamp}'
        if self.domeflatlamp is not None:
            self.name += f' domeflatlamp={self.domeflatlamp}'


    def validate(self):
        '''Check values and verify that they meet assumptions.
        
        Check:
        
        Warn:
        '''
        pass


    def to_dict(self):
        output = super().to_dict()
        output['slicer'] = self.slicer
        output['bluegrating'] = self.bluegrating
        output['bluefilter'] = self.bluefilter
        output['bluenandsmask'] = self.bluenandsmask
        output['bluefocus'] = self.bluefocus
        output['bluecwave'] = self.bluecwave
        output['bluepwave'] = self.bluepwave
        output['redgrating'] = self.redgrating
        output['redfilter'] = self.redfilter
        output['rednandsmask'] = self.rednandsmask
        output['redfocus'] = self.redfocus
        output['redcwave'] = self.redcwave
        output['redpwave'] = self.redpwave
        output['calmirror'] = self.calmirror
        output['calobj'] = self.calobj
        output['polarizer'] = self.polarizer
        output['arclamp'] = self.arclamp
        output['domeflatlamp'] = self.domeflatlamp
        
        return output


#     def from_dict(self, input):
#         pass
#         return self
# 
# 
    def contbars(self):
        '''
        '''
        ic_for_contbars = deepcopy(self)
        ic_for_contbars.calobj = 'MedBarsA'
        ic_for_contbars.arclamp = 'CONT'
        ic_for_contbars.name += f' arclamp={ic_for_contbars.arclamp}'
        ic_for_contbars.name += f' calobj={ic_for_contbars.calobj}'
        exptime = lamp_exptimes[ic_for_contbars.arclamp]
        dc_for_contbars = KCWIblueDetectorConfig(exptime=exptime)
        contbars = CalibrationBlock(target=None,
                                  pattern=Stare(repeat=1),
                                  instconfig=ic_for_contbars,
                                  detconfig=dc_for_contbars,
                                  )
        return contbars


    def arcs(self, lampname):
        '''
        '''
        ic_for_arcs = deepcopy(self)
        ic_for_arcs.arclamp = lampname
        ic_for_arcs.calobj = 'FlatA'
        ic_for_arcs.name += f' arclamp={ic_for_arcs.arclamp}'
        ic_for_arcs.name += f' calobj={ic_for_arcs.calobj}'
        dc_for_arcs = KCWIblueDetectorConfig(exptime=lamp_exptimes[lampname])
        arcs = CalibrationBlock(target=None,
                              pattern=Stare(repeat=1),
                              instconfig=ic_for_arcs,
                              detconfig=dc_for_arcs,
                              )
        return arcs


    def domeflats(self, off=False):
        '''
        '''
        ic_for_domeflats = deepcopy(self)
        ic_for_domeflats.domeflatlamp = not off
        ic_for_domeflats.name += f' domeflatlamp={not off}'
        dc_for_domeflats = KCWIblueDetectorConfig(exptime=100)
        domeflats = CalibrationBlock(target=DomeFlats(),
                                   pattern=Stare(repeat=3),
                                   instconfig=ic_for_domeflats,
                                   detconfig=dc_for_domeflats,
                                   )
        return domeflats


    def bias(self):
        '''
        '''
        ic_for_bias = deepcopy(self)
        ic_for_bias.name += f' bias'
        dc_for_bias = KCWIblueDetectorConfig(exptime=0, dark=True)
        bias = CalibrationBlock(target=None,
                              pattern=Stare(repeat=7),
                              instconfig=ic_for_bias,
                              detconfig=dc_for_bias,
                              )
        return bias


    def cals(self, internal=True, domeflats=True):
        '''
        '''
        cals = ObservingBlockList()
        if internal is True:
            cals.append(self.contbars())
            cals.append(self.arcs('FEAR'))
            cals.append(self.arcs('THAR'))
            cals.append(self.arcs('CONT'))
            cals.append(self.bias())
        if domeflats is True:
            cals.append(self.domeflats())
        return cals


    def __str__(self):
        return f'{self.name}'


    def __repr__(self):
        return f'{self.name}'
