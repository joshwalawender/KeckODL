#!python3

## Import General Tools
import sys
from pathlib import Path
from astropy import units as u
from astropy.io import fits
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
    keywords.  Instantiate this class with a scale and offset angle to make it
    specific to a particular instrument's focal plane.

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

    Attributes
    ----------
    dx : float or `u.Quantity`
        The amount of the offset in the X direction.  If given as a
        `u.Quantity`, it should be angular units convertible to arcseconds.  If
        given as a float, units of arcseconds are assumed.

    dy : float or `u.Quantity`
        The amount of the offset in the Y direction.  If given as a
        `u.Quantity`, it should be angular units convertible to arcseconds.  If
        given as a float, units of arcseconds are assumed.

    dr : float or `u.Quantity`
        The amount of the offset in rotation.  If given as a `u.Quantity`, it
        should be angular units convertible to degrees.  If given as a float,
        units of degrees are assumed.

    frame : a subclass of `OffsetFrame`
        The frame in which the offset is made.

    relative : boolean
        A boolean value indicating whether the offset is to be made relative to
        the current position or is an absolute offset (relative to the original
        target position).

    posname : string
        A name for the position.

    guide : boolean
        A boolean value indicating whether to guide at that position.

    pmfm : int
        The pmfm value to be used.  Defaults to None which does not set it.
    '''
    def __init__(self, dx=0, dy=0, dr=0, relative=False, frame=SkyFrame(),
                 posname='', guide=True, pmfm=None):
        self.dx = dx
        self.dy = dy
        self.dr = dr
        self.frame = frame
        self.relative = relative
        self.posname = posname
        self.guide = guide
        self.pmfm = pmfm
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
        # set pmfm
        if self.pmfm is not None:
            print(f'Set pmfm value to {self.pmfm}')


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
    observing block.  The object contains a list of `TelescopeOffset`s and two
    additional properties: name and repeat.
    
    Attributes
    ----------
    name : str
        A human readable name for the pattern.
    
    repeat : int
        The number of times to repeat this pattern.
    '''
    def __init__(self, *args, name='', repeat=1):
        super().__init__(*args)
        self.name = f'{name} x{repeat}'
        self.repeat = repeat
        self.validate()


    def validate(self):
        if len(self.data) > 0:
            oframe = type(self.data[0].frame)
            for item in self.data:
                if isinstance(item.frame, oframe) is False:
                    raise OffsetError(f'All offsets must have the same frame')


    def to_dict(self):
        return {'name': self.name,
                'repeat': self.repeat,
                'offsets': [x.to_dict() for x in self.data]}


    def to_header(self):
        h = fits.Header()
        h['OPNAME'] = (self.name, 'Offset Pattern Name')
        h['OPREPEAT'] = (self.repeat, 'Offset Pattern Repeats')
        h['OPLENGTH'] = (len(self.data), 'Number of Offset Positions')
        for i, patt in enumerate(self.data):
            h[f'OP{i+1:02d}NAME'] = (patt.posname, f'Position {i+1:02d} Name')
            h[f'OP{i+1:02d}DX'] = (patt.dx.value, f'Position {i+1:02d} dX (arcsec)')
            h[f'OP{i+1:02d}DY'] = (patt.dy.value, f'Position {i+1:02d} dY (arcsec)')
            h[f'OP{i+1:02d}REL'] = (patt.relative, f'Position {i+1:02d} Relative?')
            h[f'OP{i+1:02d}FRM'] = (patt.frame.name, f'Position {i+1:02d} Frame')
            h[f'OP{i+1:02d}GUID'] = (patt.guide, f'Position {i+1:02d} Guide?')
        return h


    def to_yaml(self):
        return yaml.dump(self.to_dict())


    def to_DB(self):
        return {'OffsetPatterns': [self.to_dict()]}


    def write(self, file):
        '''Write the offset pattern to a yaml formatted file.
        '''
        self.validate()
        p = Path(file).expanduser().absolute()
        if p.exists(): p.unlink()
        with open(p, 'w') as FO:
            FO.write(yaml.dump([self.to_dict()]))


    def parse_yaml(self, contents):
        list_of_dicts = contents[0]['OffsetPatterns']

        for d in list_of_dicts:
            for offset in d['offsets']:
                print(offset)
                frame_name = offset.get('frame', 'SkyFrame')
                print(frame_name)
                frame_class = getattr(sys.modules[__name__], offset.get('frame', 'SkyFrame'))
                print(frame_class)
                frame_object = frame_class()
                print(frame_object)
                print()

            offsets = [TelescopeOffset(dx=d.get('dx', 0),
                                       dy=d.get('dy', 0),
                                       dr=d.get('dr', 0),
                                       relative=d.get('relative', False),
                                       frame=getattr(sys.modules[__name__], d.get('frame', 'SkyFrame'))(),
                                       posname=d.get('posname', ''),
                                       guide=d.get('guide', True))
                       for d['offsets'] in list_of_dicts]
        return OffsetPattern(offsets)


    def read(self, file):
        '''Read targets from a yaml formatted file.
        '''
        p = Path(file).expanduser().absolute()
        if p.exists() is False:
            raise FileNotFoundError
        with open(p, 'r') as FO:
            contents = yaml.safe_load(FO)
        return self.parse_yaml(contents)


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
def Stare(repeat=1, guide=True):
    '''Return a simple Stare pattern with the specified number of repeats.

    Attributes
    ----------
    repeat : int
        The number of times to repeat this pattern.
    '''
    offset1 = TelescopeOffset(dx=0, dy=0, posname='base', frame=SkyFrame(),
                              guide=guide)
    return OffsetPattern([offset1], name='Stare', repeat=repeat)


def StarSky(dx=10*u.arcsec, dy=10*u.arcsec, repeat=1):
    '''Return a two point pattern where the first point is at offset 0,0 and is
    named "star" and the second point is at the specified dx, dy offsets and is
    named "sky".

    Attributes
    ----------
    repeat : int
        The number of times to repeat this pattern.
    '''
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
    return OffsetPattern([o1, o2], repeat=repeat,
                         name=f'StarSky ({dx.value:.0f} {dy.value:.0f})')


def SkyStar(dx=10*u.arcsec, dy=10*u.arcsec, repeat=1):
    '''Return a two point pattern where the first point is at the specified 
    dx, dy offsets and is named "sky" and the second point is at offset 0,0 and
    is named "star".

    Attributes
    ----------
    repeat : int
        The number of times to repeat this pattern.
    '''
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
    return OffsetPattern([o2, o1], repeat=repeat,
                         name=f'SkyStar ({dx.value:.0f} {dy.value:.0f})')


def StarSkyStar(dx=10*u.arcsec, dy=10*u.arcsec, repeat=1):
    '''Return a three point pattern where the first point is at offset 0,0 and
    is named "star" and the second point is at the specified dx, dy offsets and
    is named "sky" and the third point is again at offset 0,0 and is named
    "star".

    Attributes
    ----------
    repeat : int
        The number of times to repeat this pattern.
    '''
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


def pmfm(value=350):
    '''A two "position" pattern which, rather than offsetting the telescope,
    sets the pmfm value to +value and -value.

    Attributes
    ----------
    value : int
        The pmfm value to set.
    '''
    o1 = TelescopeOffset(dx=0, dy=0, posname=f'+{value}', pmfm=value)
    o2 = TelescopeOffset(dx=0, dy=0, posname=f'-{value}', pmfm=-value)
    return OffsetPattern([o1, o2], name=f'PMFM +/-{value}')

