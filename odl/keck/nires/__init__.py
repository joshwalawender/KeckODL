from astropy import units as u

from odl.block import FocusBlock
from odl.offset import InstrumentFrame, TelescopeOffset, OffsetPattern, pmfm

from .config import NIRESConfig
from .detector import NIRESScamDetectorConfig, NIRESSpecDetectorConfig


##-------------------------------------------------------------------------
## NIRES Frames
##-------------------------------------------------------------------------
scam = InstrumentFrame(name='NIRES Scam Detector',
                       scale=0.123*u.arcsec/u.pixel)
slit = InstrumentFrame(name='NIRES Slit',
                       scale=0.15*u.arcsec/u.pixel,
                       offsetangle=0*u.deg) # Note this offset angle is wrong


##-------------------------------------------------------------------------
## Pre-Defined Patterns
##-------------------------------------------------------------------------
def ABBA(offset=1.25*u.arcsec, guide=True, repeat=1):
    o1 = TelescopeOffset(dx=0, dy=+offset, posname="A", guide=guide, frame=slit)
    o2 = TelescopeOffset(dx=0, dy=-offset, posname="B", guide=guide, frame=slit)
    o3 = TelescopeOffset(dx=0, dy=-offset, posname="B", guide=guide, frame=slit)
    o4 = TelescopeOffset(dx=0, dy=+offset, posname="A", guide=guide, frame=slit)
    return OffsetPattern([o1, o2, o3, o4], repeat=repeat,
                         name=f'ABBA ({offset:.2f})')


##-------------------------------------------------------------------------
## Standard Blocks
##-------------------------------------------------------------------------
def mira():
    return FocusBlock(target=None,
                      pattern=pmfm(),
                      instconfig=NIRESConfig(),
                      detconfig=NIRESScamDetectorConfig(exptime=2, coadds=5))
