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
from .sequence import Sequence, SequenceElement


##-------------------------------------------------------------------------
## KCWI Frames
##-------------------------------------------------------------------------
bluedetector = InstrumentFrame(name='Blue Detector',
                               scale=0.1798*u.arcsec/u.pixel,
                               offsetangle=+0.22*u.deg)
SmallSlicer_Frame = InstrumentFrame(name='SmallSlicer',
                                    scale=0.35*u.arcsec/u.pixel)
MediumSlicer_Frame = InstrumentFrame(name='MediumSlicer',
                                     scale=0.70*u.arcsec/u.pixel)
LargeSlicer_Frame = InstrumentFrame(name='LargeSlicer',
                                    scale=1.35*u.arcsec/u.pixel)


##-------------------------------------------------------------------------
## KCWIblueDetectorConfig
##-------------------------------------------------------------------------
class KCWIblueDetectorConfig(VisibleDetectorConfig):
    '''An object to hold information about KCWI Blue detector configuration.
    '''
    def __init__(self, exptime=None, readoutmode=None, ampmode=9,
                 dark=False, binning='1x1', window=None, gain=10, ccdmode=1):
        super().__init__(instrument='KCWIblue', exptime=exptime,
                         readoutmode=readoutmode, ampmode=ampmode, dark=dark,
                         binning=binning, window=window)
        self.gain = gain
        self.ccdmode = ccdmode


    ##-------------------------------------------------------------------------
    ## Validate
    def validate(self):
        '''Check values and verify that they meet assumptions.
        
        Check:
        - exptime is in range 1-3600
        - readoutmode is in range ??
        - ampmode is in range ??
        - dark is bookean
        - binning is one of 1x1, 2x2
        - gain is in range ??
        - ccdmode is one of ??

        Warn:
        - Window is not used
        '''
        pass


##-------------------------------------------------------------------------
## KCWIblueConfig
##-------------------------------------------------------------------------
class KCWIblueConfig(InstrumentConfig):
    '''An object to hold information about KCWI Blue configuration.
    '''
    def __init__(self, slicer='medium', grating='BH3', filter='KBlue',
                 cwave=4800, pwave=None, nandsmask=False, focus=None,
                 calmirror='Sky', calobj='Dark', arclamp=None,
                 domeflatlamp=None, polarizer='Sky'):
        super().__init__()
        self.instrument = 'KCWIblue'
        self.slicer = slicer
        self.grating = grating
        self.filter = filter
        self.nandsmask = nandsmask
        self.focus = focus
        self.calmirror = calmirror
        self.calobj = calobj
        self.arclamp = arclamp
        self.domeflatlamp = domeflatlamp
        self.polarizer = polarizer
        self.cwave = cwave
        self.pwave = cwave-300 if pwave is None else pwave
        self.name = f'{self.slicer} {self.grating} {self.cwave*u.A:.0f}'
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
        output['grating'] = self.grating
        output['filter'] = self.filter
        output['nandsmask'] = self.nandsmask
        output['focus'] = self.focus
        output['calmirror'] = self.calmirror
        output['calobj'] = self.calobj
        output['polarizer'] = self.polarizer
        output['cwave'] = self.cwave
        output['pwave'] = self.pwave
        return output


    def arcs(self, lampname):
        '''
        '''
        arcs = deepcopy(self)
        arcs.arclamp = lampname
        arcs.calobj = 'FlatA'
        arcs.name += f' arclamp={arcs.arclamp}'
        arcs.name += f' calobj={arcs.calobj}'
        return arcs


    def contbars(self):
        '''
        '''
        contbars = deepcopy(self)
        contbars.calobj = 'MedBarsA'
        contbars.arclamp = 'CONT'
        contbars.name += f' arclamp={contbars.arclamp}'
        contbars.name += f' calobj={contbars.calobj}'
        return contbars


    def domeflats(self, off=False):
        '''
        '''
        domeflats = deepcopy(self)
        domeflats.domeflatlamp = not off
        domeflats.name += f' domeflatlamp={domeflats.domeflatlamp}'
        return domeflats


    def cals(self, internal=True, domeflats=True):
        '''
        '''
        kcwib_0s_dark = KCWIblueDetectorConfig(exptime=0, dark=True)
        kcwib_6s = KCWIblueDetectorConfig(exptime=6)
        kcwib_30s = KCWIblueDetectorConfig(exptime=30)
        kcwib_45s = KCWIblueDetectorConfig(exptime=45)
        kcwib_100s = KCWIblueDetectorConfig(exptime=100)

        cals = Sequence()
        if internal is True:
            cals.append(SequenceElement(pattern=Stare(),
                                        detconfig=kcwib_6s,
                                        instconfig=self.contbars(),
                                        repeat=1))
            cals.append(SequenceElement(pattern=Stare(),
                                        detconfig=kcwib_30s,
                                        instconfig=self.arcs('FEAR'),
                                        repeat=1))
            cals.append(SequenceElement(pattern=Stare(),
                                        detconfig=kcwib_45s,
                                        instconfig=self.arcs('THAR'),
                                        repeat=1))
            cals.append(SequenceElement(pattern=Stare(),
                                        detconfig=kcwib_6s,
                                        instconfig=self.arcs('CONT'),
                                        repeat=6))
            cals.append(SequenceElement(pattern=Stare(),
                                        detconfig=kcwib_0s_dark,
                                        instconfig=self,
                                        repeat=7))
        if domeflats is True:
            cals.append(SequenceElement(pattern=Stare(),
                                        detconfig=kcwib_100s,
                                        instconfig=self.domeflats(),
                                        repeat=3))
        return cals


    def __str__(self):
        return f'{self.name}'


    def __repr__(self):
        return f'{self.name}'


