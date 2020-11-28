#!python3

## Import General Tools
from pathlib import Path
from astropy import units as u
import yaml


class InstrumentConfigError(Exception): pass


class InstrumentConfigWarning(UserWarning): pass


##-------------------------------------------------------------------------
## InstrumentConfig
##-------------------------------------------------------------------------
class InstrumentConfig():
    '''An object to hold information about an instrument configuration.
    '''
    def __init__(self, name='GenericInstrumentConfig', detconfig=None):
        self.name = name
        self.instrument = 'unknown'
        if type(detconfig) not in [list, tuple]:
            self.detconfig = [detconfig]
        else:
            self.detconfig = list(detconfig)


    def validate(self):
        pass


    def to_dict(self):
        return {'name': self.name,
                'instrument': self.instrument,
                'detconfig': [dc.name for dc in self.detconfig]}


    def to_YAML(self):
        '''Return string corresponding to a Detector Config Description
        Language (DCDL) YAML entry.
        '''
        return yaml.dump(self.to_dict())


    def write(self, file):
        self.validate()
        p = Path(file).expanduser().absolute()
        if p.exists(): p.unlink()
        with open(p, 'w') as FO:
            FO.write(yaml.dump(self.to_dict()))


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


    def estimate_time(self):
        '''Estimate the wall clock time to complete the sequence.
        '''
        if type(self.detconfig) in [list, tuple]:
            t = [dc.estimate_clock_time() for dc in self.detconfig]
            detector_time = max(t)
            e = [dc.exptime*dc.nexp for dc in self.detconfig]
            exposure_time = max(e)
        else:
            detector_time = self.detconfig.estimate_clock_time()
            exposure_time = self.detconfig.exptime

        return {'shutter open time': exposure_time,
                'wall clock time': detector_time}

    def __str__(self):
        return f'{self.name}'


    def __repr__(self):
        return f'{self.name}'


