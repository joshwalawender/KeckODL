from astropy import units as u

from ..offset import InstrumentFrame, TelescopeOffset, OffsetPattern

from .config import MOSFIREConfig
from .detector import MOSFIREDetectorConfig


##-------------------------------------------------------------------------
## MOSFIRE Frames
##-------------------------------------------------------------------------
detector = InstrumentFrame(name='MOSFIRE Detector',
                           scale=0.1798*u.arcsec/u.pixel)
slit = InstrumentFrame(name='MOSFIRE Slit',
                       scale=0.1798*u.arcsec/u.pixel,
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


def long2pos(guide=True, repeat=1):
    o1 = TelescopeOffset(dx=+45*u.arcsec, dy=-23*u.arcsec, posname="A",
                         guide=guide, frame=detector)
    o2 = TelescopeOffset(dx=+45*u.arcsec, dy=-9*u.arcsec, posname="B",
                         guide=guide, frame=detector)
    o3 = TelescopeOffset(dx=-45*u.arcsec, dy=+9*u.arcsec, posname="A",
                         guide=guide, frame=detector)
    o4 = TelescopeOffset(dx=-45*u.arcsec, dy=+23*u.arcsec, posname="B",
                         guide=guide, frame=detector)
    return OffsetPattern([o1, o2, o3, o4], name=f'long2pos', repeat=repeat)

