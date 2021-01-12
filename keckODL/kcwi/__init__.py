from astropy import units as u

from ..offset import InstrumentFrame, pmfm

from .config import KCWIConfig
from .detector import (KCWIblueDetectorConfig, KCWIredDetectorConfig,
                       KCWIFPCDetectorConfig)


##-------------------------------------------------------------------------
## KCWI Offset Frames
##-------------------------------------------------------------------------
bluedetector = InstrumentFrame(name='Blue Detector',
                               scale=0.147*u.arcsec/u.pixel)
smallslicer = InstrumentFrame(name='SmallSlicer',
                              scale=0.35*u.arcsec/u.pixel)
mediumslicer = InstrumentFrame(name='MediumSlicer',
                               scale=0.70*u.arcsec/u.pixel)
largeslicer = InstrumentFrame(name='LargeSlicer',
                              scale=1.35*u.arcsec/u.pixel)


##-------------------------------------------------------------------------
## Standard Blocks
##-------------------------------------------------------------------------
def mira():
    # Build instrument config which only specifies critical changes for Mira
    ic = KCWIConfig(slicer='FPC', name='Mira', bluegrating=None,
                    bluefilter=None, 
                    bluecwave=None, bluepwave=None,
                    bluenandsmask=None, bluefocus=None,
                    redgrating=None, redfilter=None,
                    redcwave=None, redpwave=None,
                    rednandsmask=False, redfocus=None,
                    calmirror='Sky', calobj='Dark', arclamp=None,
                    domeflatlamp=None, polarizer=None)
    return ObservingBlock(target=None,
                          pattern=pmfm(),
                          instconfig=ic,
                          detconfig=KCWIFPCDetectorConfig(exptime=5))


def autofoc():
    return ObservingBlock(target=None,
                          pattern=None,
                          instconfig=None,
                          detconfig=None)
