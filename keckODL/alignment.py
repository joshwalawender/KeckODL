#!python3

## Import General Tools
from pathlib import Path
import re
from warnings import warn
import yaml


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


    def to_dict(self):
        return {'Alignments': [{'name': self.name,
                                }]}


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

    Attributes
    ----------
    slew : boolean
        Slew the telescope?  If True, then this is a normal blind acquisition.
        If False, this implies that the telescope is already aligned and should
        not be moved.
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
    bright : boolean
        If False, then the OA may need to increase guider exposure time to see
        the target (or offset star if offset is also True) in order to align
        it on the guider.
    '''
    def __init__(self, bright=True):
        name = 'Guider Align'
        if bright is False:
            name += ', faint'
        super().__init__(name=name)


##-------------------------------------------------------------------------
## MaskAlignment
##-------------------------------------------------------------------------
class MaskAlign(Alignment):
    '''An object to hold information about a how to align a mask or long slit
    which does not use a slit viewing camera.

    Attributes
    ----------
    '''
    def __init__(self, bright=False, detconfig=None, filter=None,
                 takesky=False):
        name = 'Mask Align'
        if bright is True:
            name += ', bright'
        super().__init__(name=name)
        self.bright = bright
        self.detconfig = detconfig
        self.takesky = takesky
        self.filter = filter

    def to_dict(self):
        return {'Alignments': [{'name': self.name,
                                'bright': self.bright,
                                'takesky': self.takesky,
                                'filter': self.filter,
                                }]}
