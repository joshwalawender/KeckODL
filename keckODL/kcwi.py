#!python3

## Import General Tools
from pathlib import Path
import re
from warnings import warn
from copy import deepcopy
import yaml
from astropy import units as u


from .detector_config import VisibleDetectorConfig
from .instrument_config import InstrumentConfig
from .offset import SkyFrame, InstrumentFrame, TelescopeOffset, OffsetPattern
from .offset import Stare
from .block import ObservingBlock, ObservingBlockList
from .target import Target, DomeFlats


##-------------------------------------------------------------------------
## Constants for the Instrument
##-------------------------------------------------------------------------
lamp_exptimes = {'FEAR': 30, 'THAR': 45, 'CONT': 6}


##-------------------------------------------------------------------------
## KCWI Frames
##-------------------------------------------------------------------------
bluedetector = InstrumentFrame(name='Blue Detector',
                               scale=0.1798*u.arcsec/u.pixel)
smallslicer = InstrumentFrame(name='SmallSlicer',
                              scale=0.35*u.arcsec/u.pixel)
mediumslicer = InstrumentFrame(name='MediumSlicer',
                               scale=0.70*u.arcsec/u.pixel)
largeslicer = InstrumentFrame(name='LargeSlicer',
                              scale=1.35*u.arcsec/u.pixel)


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
        self.bluepwave = bluecwave-300 if bluepwave is None else bluepwave
        self.bluenandsmask = bluenandsmask
        self.bluefocus = bluefocus

        # Red Components
        self.redgrating = redgrating
        self.redfilter = redfilter
        self.redcwave = redcwave
        self.redpwave = redcwave-300 if redpwave is None else redpwave
        self.rednandsmask = rednandsmask
        self.redfocus = redfocus

        # Calibration Components
        self.calmirror = calmirror
        self.calobj = calobj
        self.arclamp = arclamp
        self.domeflatlamp = domeflatlamp

        # Set config name
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
        output['InstrumentConfigs'][0]['slicer'] = self.slicer
        output['InstrumentConfigs'][0]['bluegrating'] = self.bluegrating
        output['InstrumentConfigs'][0]['bluefilter'] = self.bluefilter
        output['InstrumentConfigs'][0]['bluenandsmask'] = self.bluenandsmask
        output['InstrumentConfigs'][0]['bluefocus'] = self.bluefocus
        output['InstrumentConfigs'][0]['bluecwave'] = self.bluecwave
        output['InstrumentConfigs'][0]['bluepwave'] = self.bluepwave
        output['InstrumentConfigs'][0]['redgrating'] = self.redgrating
        output['InstrumentConfigs'][0]['redfilter'] = self.redfilter
        output['InstrumentConfigs'][0]['rednandsmask'] = self.rednandsmask
        output['InstrumentConfigs'][0]['redfocus'] = self.redfocus
        output['InstrumentConfigs'][0]['redcwave'] = self.redcwave
        output['InstrumentConfigs'][0]['redpwave'] = self.redpwave
        output['InstrumentConfigs'][0]['calmirror'] = self.calmirror
        output['InstrumentConfigs'][0]['calobj'] = self.calobj
        output['InstrumentConfigs'][0]['polarizer'] = self.polarizer
        output['InstrumentConfigs'][0]['arclamp'] = self.arclamp
        output['InstrumentConfigs'][0]['domeflatlamp'] = self.domeflatlamp
        
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
        contbars = ObservingBlock(target=None,
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
        arcs = ObservingBlock(target=None,
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
        domeflats = ObservingBlock(target=DomeFlats(),
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
        bias = ObservingBlock(target=None,
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


