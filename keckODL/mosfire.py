#!python3

## Import General Tools
from pathlib import Path
import re
from warnings import warn
import yaml
from copy import deepcopy
from astropy import units as u


from .detector_config import IRDetectorConfig
from .instrument_config import InstrumentConfig
from .sequence import SequenceElement, Sequence
from .offset import SkyFrame, InstrumentFrame, TelescopeOffset, OffsetPattern
from .offset import Stare
from .block import ObservingBlock, ObservingBlockList
from .target import Target, DomeFlats


##-------------------------------------------------------------------------
## MOSFIRE Frames
##-------------------------------------------------------------------------
detector = InstrumentFrame(name='MOSFIRE Detector',
                           scale=0.1798*u.arcsec/u.pixel)
slit = InstrumentFrame(name='MOSFIRE Slit',
                       scale=0.1798*u.arcsec/u.pixel,
                       offsetangle=0*u.deg) # Note this offset angle is wrong


##-------------------------------------------------------------------------
## MOSFIREDetectorConfig
##-------------------------------------------------------------------------
class MOSFIREDetectorConfig(IRDetectorConfig):
    '''An object to hold information about NIRES detector configuration.
    '''
    def __init__(self, exptime=None, readoutmode='CDS', coadds=1):
        super().__init__(instrument='MOSFIRE', exptime=exptime,
                         readoutmode=readoutmode, coadds=coadds)


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
                                          f'(only 1-16 are supported)')


##-------------------------------------------------------------------------
## MOSFIREInstrumentConfig
##-------------------------------------------------------------------------
class MOSFIREConfig(InstrumentConfig):
    '''An object to hold information about MOSFIRE configuration.
    '''
    def __init__(self, mode='spectroscopy', filter='Y', mask='longslit_46x0.7'):
        super().__init__()
        self.instrument = 'MOSFIRE'
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
        output['filter'] = self.filter
        output['mode'] = self.mode
        output['mask'] = self.mask
        output['arclamp'] = self.arclamp
        output['domeflatlamp'] = self.domeflatlamp
        return output


    def arcs(self, lampname):
        '''
        '''
        arcs = deepcopy(self)
        arcs.arclamp = lampname
        arcs.name += f' arclamp={arcs.arclamp}'
        return arcs


    def domeflats(self, off=False):
        '''
        '''
        domeflats = deepcopy(self)
        domeflats.domeflatlamp = not off
        domeflats.name += f' domeflatlamp={domeflats.domeflatlamp}'
        return domeflats


    def cals(self):
        '''
        '''
        mosfire_1s = MOSFIREDetectorConfig(exptime=1, readoutmode='CDS')
        mosfire_11s = MOSFIREDetectorConfig(exptime=11, readoutmode='CDS')

        cals = ObservingBlockList()
        cals.append(ObservingBlock(target=DomeFlats(),
                                   pattern=Stare(),
                                   detconfig=mosfire_11s,
                                   instconfig=self.domeflats(),
                                   repeat=7))
        if self.filter == 'K':
            cals.append(ObservingBlock(target=DomeFlats(),
                                       pattern=Stare(),
                                       detconfig=mosfire_11s,
                                       instconfig=self.domeflats(off=True),
                                       repeat=7))
            cals.append(ObservingBlock(target=None,
                                       pattern=Stare(),
                                       detconfig=mosfire_1s,
                                       instconfig=self.arcs('Ne'),
                                       repeat=2))
            cals.append(ObservingBlock(target=None,
                                       pattern=Stare(),
                                       detconfig=mosfire_1s,
                                       instconfig=self.arcs('Ar'),
                                       repeat=2))
        return cals


    def seq_cals(self):
        '''
        '''
        mosfire_1s = MOSFIREDetectorConfig(exptime=1, readoutmode='CDS')
        mosfire_11s = MOSFIREDetectorConfig(exptime=11, readoutmode='CDS')

        cals = Sequence()
        cals.append(SequenceElement(pattern=Stare(),
                                    detconfig=mosfire_11s,
                                    instconfig=self.domeflats(),
                                    repeat=7))
        if self.filter == 'K':
            cals.append(SequenceElement(pattern=Stare(),
                                        detconfig=mosfire_11s,
                                        instconfig=self.domeflats(off=True),
                                        repeat=7))
            cals.append(SequenceElement(pattern=Stare(),
                                        detconfig=mosfire_1s,
                                        instconfig=self.arcs('Ne'),
                                        repeat=2))
            cals.append(SequenceElement(pattern=Stare(),
                                        detconfig=mosfire_1s,
                                        instconfig=self.arcs('Ar'),
                                        repeat=2))
        return cals


##-------------------------------------------------------------------------
## Pre-Defined Patterns
##-------------------------------------------------------------------------
def ABBA(offset=1.25*u.arcsec, guide=True):
    o1 = TelescopeOffset(dx=0, dy=+offset, posname="A", guide=guide, frame=slit)
    o2 = TelescopeOffset(dx=0, dy=-offset, posname="B", guide=guide, frame=slit)
    o3 = TelescopeOffset(dx=0, dy=-offset, posname="B", guide=guide, frame=slit)
    o4 = TelescopeOffset(dx=0, dy=+offset, posname="A", guide=guide, frame=slit)
    return OffsetPattern([o1, o2, o3, o4], name=f'ABBA ({offset:.2f})')


def long2pos(guide=True):
    o1 = TelescopeOffset(dx=+45*u.arcsec, dy=-23*u.arcsec, posname="A",
                         guide=guide, frame=detector)
    o2 = TelescopeOffset(dx=+45*u.arcsec, dy=-9*u.arcsec, posname="B",
                         guide=guide, frame=detector)
    o3 = TelescopeOffset(dx=-45*u.arcsec, dy=+9*u.arcsec, posname="A",
                         guide=guide, frame=detector)
    o4 = TelescopeOffset(dx=-45*u.arcsec, dy=+23*u.arcsec, posname="B",
                         guide=guide, frame=detector)
    return OffsetPattern([o1, o2, o3, o4], name=f'long2pos')

