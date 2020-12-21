from astropy import units as u

from ..offset import InstrumentFrame

from .config import KCWIConfig
from .detector import KCWIblueDetectorConfig, KCWIredDetectorConfig


##-------------------------------------------------------------------------
## KCWI Offset Frames
##-------------------------------------------------------------------------
bluedetector = InstrumentFrame(name='Blue Detector',
                               scale=0.1798*u.arcsec/u.pixel)
smallslicer = InstrumentFrame(name='SmallSlicer',
                              scale=0.35*u.arcsec/u.pixel)
mediumslicer = InstrumentFrame(name='MediumSlicer',
                               scale=0.70*u.arcsec/u.pixel)
largeslicer = InstrumentFrame(name='LargeSlicer',
                              scale=1.35*u.arcsec/u.pixel)

