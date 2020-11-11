#!python3

## Import General Tools
from pathlib import Path
from astropy import units as u
import yaml
from copy import deepcopy

from .sequence import SequenceElement, Sequence
from .offset import Stare
from .detector_config import MOSFIREDetectorConfig, KCWIblueDetectorConfig

class InstrumentConfigError(Exception): pass


class InstrumentConfigWarning(UserWarning): pass


##-------------------------------------------------------------------------
## InstrumentConfig
##-------------------------------------------------------------------------
class InstrumentConfig():
    '''An object to hold information about an instrument configuration.
    '''
    def __init__(self, name='GenericInstrumentConfig'):
        self.name = name
        self.instrument = 'unknown'


    def validate(self):
        pass


    def to_dict(self):
        return {'name': self.name,
                'instrument': self.instrument}


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


    def __str__(self):
        return f'{self.name}'


    def __repr__(self):
        return f'{self.name}'


##-------------------------------------------------------------------------
## KCWIblueConfig
##-------------------------------------------------------------------------
class KCWIblueConfig(InstrumentConfig):
    '''An object to hold information about KCWI Blue configuration.
    '''
    def __init__(self, slicer='medium', grating='BH3', cwave=4800, pwave=None):
        super().__init__()
        self.instrument = 'KCWIblue'
        self.slicer = slicer
        self.grating = grating
        self.cwave = cwave
        self.pwave = cwave-300 if pwave is None else pwave


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
        output['cwave'] = self.cwave
        output['pwave'] = self.pwave
        return output


    def __str__(self):
        self.name = f'{self.slicer} {self.grating} {self.cwave*u.A:.0f}'
        return f'{self.name}'


    def __repr__(self):
        self.name = f'{self.slicer} {self.grating} {self.cwave*u.A:.0f}'
        return f'{self.name}'


##-------------------------------------------------------------------------
## NIRESConfig
##-------------------------------------------------------------------------
class NIRESConfig(InstrumentConfig):
    '''An object to hold information about NIRES configuration.
    '''
    def __init__(self):
        super().__init__()
        self.instrument = 'NIRES'

    ##-------------------------------------------------------------------------
    ## Validate
    def validate(self):
        '''Check values and verify that they meet assumptions.
        
        Check:
        
        Warn:
        '''
        pass


##-------------------------------------------------------------------------
## MOSFIREConfig
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
