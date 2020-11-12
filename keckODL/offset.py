#!python3

## Import General Tools
from astropy import units as u
from collections import UserList


class OffsetError(Exception): pass


class OffsetWarning(UserWarning): pass



##-------------------------------------------------------------------------
## OffsetFrame
##-------------------------------------------------------------------------
class OffsetFrame():
    '''An OffsetFrame is the coordinate frame in which the offset is done.  It
    usually corresponds to a focal plane.  An OffsetFrame consists of a pixel
    scale and an orientation.
    
    Examples: Sky, Detector, Slit, Guider
    '''
    def __init__(self, name='GenericFrame', pixelscale=1*u.arcsec/u.pixel, PA=0):
        self.name = name
        self.pixelscale = pixelscale
        self._PA = PA
        if isinstance(self.PA, u.Quantity):
            # If the PA is given as a constant, no need to refresh the value
            self._refresh = False
        elif type(self.PA) in [float, int]:
            # If the PA is given as a constant, no need to refresh the value
            self._refresh = False
            # Assume degrees are the units
            self._PA *= u.deg
        else:
            # Assume PA is a keyword and must be refreshed each time it is used
            self._refresh = True


    def PA(self):
        '''
        '''
        if self._refresh is True:
            raise NotImplementedError
        else:
            return self._PA


    def __str__(self):
        return self.name


    def __repr__(self):
        return self.name


##-------------------------------------------------------------------------
## Some actual frames with values
##-------------------------------------------------------------------------
SkyFrame = OffsetFrame(name='SkyFrame')


##-------------------------------------------------------------------------
## TelescopeOffset
##-------------------------------------------------------------------------
class TelescopeOffset():
    '''Describes a telescope offset for the purposes of including it in an
    observing sequence.
    '''
    def __init__(self, dx=0, dy=0, dr=0, relative=False, name=''):
        self.dx = dx
        self.dy = dy
        self.dr = dr
        self.relative = relative
        self.name = name


    def validate(self):
        '''Validate the offset.
        
        Check that a known frame was used.
        '''
        # Is the given frame a known OffsetFrame
        if issubclass(self.frame, OffsetFrame) is False:
            raise OffsetError(f'"{self.frame}" is not a known OffsetFrame')
        # Are the offset values valid
        if type(self.dx) in [float, int]:
            warn('No offset unit given, assuming arcseconds',
                          category=OffsetWarning)
            self.dx *= u.arcsec
        elif type(self.dx) in [u.Quantity]:
            try:
                self.dx.to(u.arcsec)
            except:
                raise OffsetError(f'dx offset {self.dx} could not be converted to arcsec')
        else:
            raise OffsetError(f'dx offset {self.dx} could not be parsed')
        if type(self.dy) in [float, int]:
            warn('No offset unit given, assuming arcseconds',
                          category=OffsetWarning)
            self.dy *= u.arcsec
        elif type(self.dy) in [u.Quantity]:
            try:
                self.dy.to(u.arcsec)
            except:
                raise OffsetError(f'dy offset {self.dy} could not be converted to arcsec')
        else:
            raise OffsetError(f'dy offset {self.dy} could not be parsed')


    def __str__(self):
        return f'{self.dx:+6.1f}|{self.dy:+6.1f}|{self.dr:+8.1f}|{self.name:>8s}'


    def __repr__(self):
        return f'{self.dx:+6.1f}|{self.dy:+6.1f}|{self.dr:+8.1f}|{self.name:>8s}'


##-------------------------------------------------------------------------
## OffsetPattern
##-------------------------------------------------------------------------
class OffsetPattern(UserList):
    '''Describes a telescope offset for the purposes of including it in an
    observing sequence.
    '''
    def __init__(self, frame=None, name=''):
        super().__init__()
        self.name = name
        self.frame = frame


    def __str__(self):
        return self.name


    def __repr__(self):
        output = [f'Frame: {self.frame}',
                  f' dx(")| dy(")| dr(deg)|    name',
                  f'{"-"*6:6s}|{"-"*6:6s}|{"-"*8:8s}|{"-"*8:8s}',]
        for item in self.data:
            output.append(item.__str__())
        return "\n".join(output)


##-------------------------------------------------------------------------
## Per-Defined Patterns
##-------------------------------------------------------------------------
class ABBA(OffsetPattern):
    def __init__(self, offset=2):
        super().__init__()
        self.name = f'ABBA ({offset:.1f})'
        self.frame = SkyFrame
        self.data = [TelescopeOffset(dx=0, dy=+offset, name="A"),
                     TelescopeOffset(dx=0, dy=-offset, name="B"),
                     TelescopeOffset(dx=0, dy=-offset, name="B"),
                     TelescopeOffset(dx=0, dy=+offset, name="A"),
                     ]


class Stare(OffsetPattern):
    def __init__(self):
        super().__init__()
        self.name = 'Stare'
        self.frame = SkyFrame
        self.data = [TelescopeOffset(dx=0, dy=0, name='base')]


class StarSkyStar(OffsetPattern):
    def __init__(self, dx=0, dy=0):
        super().__init__()
        self.name = f'StarSkyStar ({dx:.0f} {dy:.0f})'
        self.frame = SkyFrame
        self.data = [TelescopeOffset(dx=0, dy=0, name='star'),
                     TelescopeOffset(dx=dx, dy=dy, name='sky'),
                     TelescopeOffset(dx=0, dy=0, name='star'),
                     ]


class Long2pos(OffsetPattern):
    '''Note that the offset values here are not correct.
    '''
    def __init__(self):
        super().__init__()
        self.name = f'long2pos'
        self.frame = MOSFIRE
        self.data = [TelescopeOffset(dx=+45, dy=-23, name="A"),
                     TelescopeOffset(dx=+45, dy=-9, name="B"),
                     TelescopeOffset(dx=-45, dy=+9, name="A"),
                     TelescopeOffset(dx=-45, dy=+23, name="B"),
                     ]
