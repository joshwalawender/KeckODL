#!python3

## Import General Tools
import re
from pathlib import Path
from astropy import units as u
from astropy.io import fits
import yaml


class InstrumentConfigError(Exception): pass


class InstrumentConfigWarning(UserWarning): pass


##-------------------------------------------------------------------------
## InstrumentConfig
##-------------------------------------------------------------------------
class InstrumentConfig():
    '''An object to hold information about an instrument configuration.  This
    is an abstract class which is intended to be subclassed for each instrument.

    Attributes
    ----------
    name : string
        A string with a human readable name for this configuration.

    Note that some features of the reader for this class require a particular
    naming convention for the implementation of the sub-class.  The sub-class
    should be in a package `odl.[instrument]` where `[instrument]` is the
    name of the instrument in lower case.  In addition, the name of the
    sub-class itself must be of the form `[Instrument]Config` where
    `[Instrument]` is the name of the instrument (in the instrument's chosen
    case).  For example: `odl.kcwi.KCWIConfig` or
    `odl.mosfire.MOSFIREConfig`.
    '''
    def __init__(self, instrument='GenericInstrument',
                 name='GenericInstrumentConfig', obswl=0.5*u.micron):
        self.name = name
        # Determine instrument from class name.  This is needed so the class
        # name and the instrument property have a predictable relationship
        self.instrument = instrument
        self.name = name
        self.obswl = obswl


    def validate(self):
        pass


    def to_header(self):
        h = fits.Header()
        h['ICNAME'] = (self.name, 'Instrument Config Name')
        h['ICPKG'] = (self.package, 'Instrument Config Package Name')
        h['ICINST'] = (self.instrument, 'Instrument Config Instrument Name')
        h['ICOBSWL'] = (self.obswl.to(u.micron).value, 'Instrument Config Wavelength (micron)')
        return h

    def to_dict(self):
        return {'name': self.name,
                'instrument': self.instrument,
                'obswl': self.obswl.to(u.micron).value,
                }


    def to_yaml(self):
        '''Return string corresponding to a Detector Config Description
        Language (DCDL) yaml entry.
        '''
        return yaml.dump(self.to_dict())


    def to_DB(self):
        return {'InstrumentConfigs': [self.to_dict()]}


    def write(self, file):
        self.validate()
        p = Path(file).expanduser().absolute()
        if p.exists(): p.unlink()
        with open(p, 'w') as FO:
            FO.write(yaml.dump([self.to_dict()]))


    def arcs(self, lampname):
        '''This method should be overridden on each instrument to be the arcs
        configuration for the science config described.
        '''
        pass


    def domeflats(self, off=False):
        '''This method should be overridden on each instrument to be the dome
        flat configuration for the science config described.
        '''
        pass


    def __str__(self):
        return f'{self.name}'


    def __repr__(self):
        return f'{self.name}'


