#!python3

## Import General Tools
from pathlib import Path
from astropy import units as u
from collections import UserList
from warnings import warn
import yaml

try:
    import ktl
except ModuleNotFoundError:
    ktl = None


class OffsetError(Exception): pass


class OffsetWarning(UserWarning): pass



##-------------------------------------------------------------------------
## OffsetFrame
##-------------------------------------------------------------------------
class OffsetFrame():
    '''An OffsetFrame is the coordinate frame in which the offset is done.  It
    usually corresponds to a focal plane.  This class is abstract and is meant
    to be subclassed.
    
    Attributes
    ----------
    xkw : str or ktl.Keyword instance
        The DCS keyword corresponding to the X coordinate of the move.

    ykw : str or ktl.Keyword instance
        The DCS keyword corresponding to the Y coordinate of the move.
    '''
    def __init__(self, name='GenericFrame'):
        self.name = name
        self.xkw = '?'
        self.ykw = '?'


    def __str__(self):
        return f'{self.name} ({self.xkw} {self.ykw})'


    def __repr__(self):
        return f'{self.name} ({self.xkw} {self.ykw})'


class SkyFrame(OffsetFrame):
    '''A SkyOffset is an offset frame which takes place in sky coordinates
    (North-South and East-West).  It uses the RAOFF and DECOFF DCS keywords.

    Attributes
    ----------
    scale : astropy.units.Quantity
        An angle per unit length or pixel value.
    '''
    def __init__(self, name='SkyFrame', scale=1.3751*u.arcsec/u.mm):
        super().__init__(name=name)
        self.scale = scale
        if ktl is not None:
            self.xkw = ktl.cache(keyword='RAOFF', service='DCS')
            self.ykw = ktl.cache(keyword='DECOFF', service='DCS')
        else:
            self.xkw = 'RAOFF'
            self.ykw = 'DECOFF'



class InstrumentFrame(OffsetFrame):
    '''An InstrumentFrame is an offset frame which takes place in instrument
    coordinates as determined by the INSTXOFF, INSTYOFF, and INSTANGL DCS
    keywords.  This class is intended to be subclassed to make it specific
    to each instrument focal plane.

    Attributes
    ----------
    scale : astropy.units.Quantity
        An angle per unit length or pixel value.

    offsetangle : float or astropy.units.Quantity or astropy.units.Angle
        The angular offset between the INST(XY)OFF keyword coordinate system
        (defined by INSTANGL) and the desired frame.  For example, a
        spectrograph slit which is not aligned to the pixels of the detector
        (assuming the INST(XY)OFF keywords move in pixel space) would need to
        define the offsetangle.
    '''
    def __init__(self, name='InstrumentFrame', scale=1*u.arcsec/u.pixel,
                 offsetangle=0*u.deg):
        super().__init__(name=name)
        self.scale = scale
        self.offsetangle = offsetangle
        if ktl is not None:
            self.xkw = ktl.cache(keyword='INSTXOFF', service='DCS')
            self.ykw = ktl.cache(keyword='INSTYOFF', service='DCS')
        else:
            self.xkw = 'INSTXOFF'
            self.ykw = 'INSTYOFF'
        self.validate()


    def validate(self):
        if self.offsetangle != 0*u.deg:
            raise NotImplementedError('offsetangle is not yet supported')


##-------------------------------------------------------------------------
## TelescopeOffset
##-------------------------------------------------------------------------
class TelescopeOffset():
    '''Describes a telescope offset for the purposes of including it in an
    OffsetPattern.
    '''
    def __init__(self, dx=0, dy=0, dr=0, relative=False, frame=SkyFrame(),
                 posname='', guide=True):
        self.dx = dx
        self.dy = dy
        self.dr = dr
        self.frame = frame
        self.relative = relative
        self.posname = posname
        self.guide = guide
        self.standardize_units()
        self.validate()


    def execute(self):
        '''This is a dummy method for now to print actions to screen.
        
        This does not handle the offsetangle value for InstrumentFrame yet.
        '''
        self.standardize_units()
        rel2what = {True: 'rel2curr=t', False: 'rel2base=t'}[self.relative]
        print(f'{repr(self.frame.xkw)}.write({self.dx.value}, {rel2what})')
        print(f'{repr(self.frame.ykw)}.write({self.dy.value}, {rel2what})')


    def validate(self):
        '''Validate the offset.
        
        Check that a known frame was used.
        '''
        # Is the given frame a known OffsetFrame
        if isinstance(self.frame, OffsetFrame) is False:
            raise OffsetError(f'"{self.frame}" is not a known OffsetFrame')



    def standardize_units(self):
        if type(self.dx) in [float, int]:
            if abs(self.dx) > 1e-6:
                warn('No offset unit given for dx, assuming arcseconds',
                              category=OffsetWarning)
            self.dx *= u.arcsec
        if type(self.dy) in [float, int]:
            if abs(self.dy) > 1e-6:
                warn('No offset unit given for dy, assuming arcseconds',
                              category=OffsetWarning)
            self.dy *= u.arcsec
        if type(self.dr) in [float, int]:
            if abs(self.dr) > 1e-1:
                warn('No offset unit given for dr, assuming degrees',
                              category=OffsetWarning)
            self.dr *= u.degree
        self.dx = self.dx.to(u.arcsec)
        self.dy = self.dy.to(u.arcsec)
        self.dr = self.dr.to(u.degree)


    def to_dict(self):
        self.standardize_units()
        self.validate()
        return {'dx': float(self.dx.value),
                'dy': float(self.dy.value),
                'dr': float(self.dr.value),
                'frame': str(self.frame.name),
                'relative': self.relative,
                'posname': self.posname,
                'guide': self.guide,
                }


    def __str__(self):
        dx = self.dx if isinstance(self.dx, u.Quantity) is False\
             else self.dx.to(u.arcsec).value
        dy = self.dy if isinstance(self.dy, u.Quantity) is False\
             else self.dy.to(u.arcsec).value
        dr = self.dr if isinstance(self.dr, u.Quantity) is False\
             else self.dr.to(u.degree).value
        return (f'{dx:+6.1f}|{dy:+6.1f}|{dr:+8.1f}|{self.posname:>8s}|'
                f'{str(self.guide):>6s}')


    def __repr__(self):
        dx = self.dx if isinstance(self.dx, u.Quantity) is False\
             else self.dx.to(u.arcsec).value
        dy = self.dy if isinstance(self.dy, u.Quantity) is False\
             else self.dy.to(u.arcsec).value
        return (f'{dx:+6.1f}|{dy:+6.1f}|{self.dr:+8.1f}|{self.posname:>8s}|'
                f'{str(self.guide):>6s}')


##-------------------------------------------------------------------------
## OffsetPattern
##-------------------------------------------------------------------------
class OffsetPattern(UserList):
    '''Describes a telescope offset for the purposes of including it in an
    observing block.
    '''
    def __init__(self, liste, name='', repeat=1):
        super().__init__(liste)
        self.name = f'{name} x{repeat}'
        self.repeat = repeat
        self.validate()


    def validate(self):
        oframe = type(self.data[0].frame)
        for item in self.data:
            if isinstance(item.frame, oframe) is False:
                raise OffsetError(f'All offsets must have the same frame')


    def to_YAML(self):
        offsets = [item.to_dict() for item in self.data]
        outputdict = {'name': self.name,
                      'repeat': self.repeat,
                      'offsets': offsets}
        return yaml.dump(outputdict)


    def write(self, file):
        '''Write the offset pattern to a YAML formatted file.
        '''
        self.validate()
        p = Path(file).expanduser().absolute()
        if p.exists(): p.unlink()
        with open(p, 'w') as FO:
            FO.write(self.to_YAML())


    def __str__(self):
        return self.name


    def __repr__(self):
        output = [f'Frame: {self.data[0].frame}',
                  f'Repeats: {self.repeat}',
                  f' dx(")| dy(")| dr(deg)|    name|guide?',
                  f'{"-"*6:6s}|{"-"*6:6s}|{"-"*8:8s}|{"-"*8:8s}|{"-"*6:6s}',]
        for item in self.data:
            output.append(item.__str__())
        return "\n".join(output)


##-------------------------------------------------------------------------
## Pre-Defined Patterns
##-------------------------------------------------------------------------
def Stare(repeat=1):
    offset1 = TelescopeOffset(dx=0, dy=0, posname='base', frame=SkyFrame())
    return OffsetPattern([offset1], name='Stare', repeat=repeat)


def StarSkyStar(dx=0, dy=0, repeat=1):
    if type(dx) in [float, int]:
        if abs(dx) > 1e-6:
            warn('No offset unit given for dx, assuming arcseconds',
                          category=OffsetWarning)
        dx *= u.arcsec
    if type(dy) in [float, int]:
        if abs(dy) > 1e-6:
            warn('No offset unit given for dy, assuming arcseconds',
                          category=OffsetWarning)
        dy *= u.arcsec
    dx = dx.to(u.arcsec)
    dy = dy.to(u.arcsec)

    o1 = TelescopeOffset(dx=0, dy=0, posname='star',
                         frame=SkyFrame(), guide=True)
    o2 = TelescopeOffset(dx=dx, dy=dy, posname='sky',
                         frame=SkyFrame(), guide=False)
    o3 = TelescopeOffset(dx=0, dy=0, posname='star',
                         frame=SkyFrame(), guide=True)
    return OffsetPattern([o1, o2, o3], repeat=repeat,
                         name=f'StarSkyStar ({dx.value:.0f} {dy.value:.0f})')
