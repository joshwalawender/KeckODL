#!python3

## Import General Tools
from pathlib import Path
import re
from warnings import warn
import yaml
from astropy.io import fits


##-------------------------------------------------------------------------
## Alignment
##-------------------------------------------------------------------------
class Alignment():
    '''An object to hold information about a how to align on a target.  This
    is an abstract class which is intended to be subclassed.

    Needs to describe strategies such as:
        guider: bright,
        guider: faint
        guider: offset
        mask align
        mask align + offset
        mask align (bright)
        mask align (bright) + offset
        blind
        none

    Attributes
    ----------
    '''
    def __init__(self, name='GenericAlignment'):
        self.name = name


    def validate(self):
        pass


    def to_header(self):
        h = fits.Header()
        h['ALNAME'] = (self.name, 'Alignment Name')
        return h


    def to_dict(self):
        return {'name': self.name}


    def to_yaml(self):
        '''Return string corresponding to a Detector Config Description
        Language (DCDL) YAML entry.
        '''
        return yaml.dump(self.to_dict())


    def write(self, file):
        self.validate()
        p = Path(file).expanduser().absolute()
        if p.exists(): p.unlink()
        with open(p, 'w') as FO:
            FO.write(yaml.dump([self.to_dict()]))


    def __str__(self):
        return f'{self.name}'


    def __repr__(self):
        return f'{self.name}'


##-------------------------------------------------------------------------
## BlindAlignment
##-------------------------------------------------------------------------
class BlindAlign(Alignment):
    '''An object to hold information about a how to align on a target.  This is
    intended to be used for simple blind alignment strategies (no feedback).
    '''
    def __init__(self):
        name = 'Blind Align'
        super().__init__(name=name)


##-------------------------------------------------------------------------
## GuiderAlignment
##-------------------------------------------------------------------------
class GuiderAlign(Alignment):
    '''An object to hold information about a how to align on a target using
    the guider.  This in intended for use in instruments where there is a slit
    viewing guider.

    Attributes
    ----------
    faint : boolean
        If True, then the OA may need to increase guider exposure time to see
        the target (or offset star if offset is also True) in order to align
        it on the guider.  In the case of an IR slit viewing camera, this
        indicates that a sky subtraction is likely necessary to see the target.
    '''
    def __init__(self, faint=True):
        name = 'Guider Align'
        if faint is True:
            name += ', faint'
        self.faint = faint
        super().__init__(name=name)


    def to_dict(self):
        return {'name': self.name,
                'faint': self.faint,
                }


##-------------------------------------------------------------------------
## MaskAlignment
##-------------------------------------------------------------------------
class MaskAlign(Alignment):
    '''An object to hold information about a how to align a mask or long slit
    which does not use a slit viewing camera.

    Attributes
    ----------
    '''
    def __init__(self, detconfig=None, filter=None, takesky=False):
        name = f'Mask Align ({str(detconfig)})'
        if takesky is True:
            name += ' take sky'
        super().__init__(name=name)
        self.detconfig = detconfig
        self.takesky = takesky
        self.filter = filter

    def to_dict(self):
        return {'name': self.name,
                'takesky': self.takesky,
                'filter': self.filter,
                'detconfig': self.detconfig.to_dict(),
                }

