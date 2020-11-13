#!python3

## Import General Tools
from astropy import units as u
from collections import UserList

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
    coordinates as determined by the INSTXOFF, INSTXYOFF, and INSTANGL DCS
    keywords.  This class is intended to be subclassed to make it specific
    to each instrument focal plane.
    '''
    def __init__(self, name='InstrumentFrame', scale=1*u.arcsec/u.pixel,
                 offsetangle=0*u.deg):
        super().__init__(name=name)
        self.scale = scale
        self.offsetangle = offsetangle
        if ktl is not None:
            self.xkw = ktl.cache(keyword='INSTXOFF', service='DCS')
            self.ykw = ktl.cache(keyword='INSTXYOFF', service='DCS')
        else:
            self.xkw = 'INSTXOFF'
            self.ykw = 'INSTXYOFF'


##-------------------------------------------------------------------------
## TelescopeOffset
##-------------------------------------------------------------------------
class TelescopeOffset():
    '''Describes a telescope offset for the purposes of including it in an
    observing sequence.
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


    def execute(self):
        '''This is a dummy method for now to print actions to screen.
        
        This does not handle the offsetangle value for InstrumentFrame yet.
        '''
        rel2curr = {True: 't', False: 'f'}[self.relative]
        rel2base = {True: 'f', False: 't'}[self.relative]
        print(f'{repr(self.frame.xkw)}.write({self.dx}, rel2curr={rel2curr}, rel2base={rel2base})')
        print(f'{repr(self.frame.ykw)}.write({self.dy}, rel2curr={rel2curr}, rel2base={rel2base})')


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
        return f'{self.dx:+6.1f}|{self.dy:+6.1f}|{self.dr:+8.1f}|{self.posname:>8s}|{str(self.guide):>6s}'


    def __repr__(self):
        return f'{self.dx:+6.1f}|{self.dy:+6.1f}|{self.dr:+8.1f}|{self.posname:>8s}|{str(self.guide):>6s}'


##-------------------------------------------------------------------------
## OffsetPattern
##-------------------------------------------------------------------------
class OffsetPattern(UserList):
    '''Describes a telescope offset for the purposes of including it in an
    observing sequence.
    '''
    def __init__(self, name=''):
        super().__init__()
        self.name = name


    def verify(self):
        oframe = self.data[0].frame
        for item in self.data:
            if item.frame != oframe:
                raise OffsetError(f'Not all offsets in the pattern have the same frame')


    def __str__(self):
        return self.name


    def __repr__(self):
        output = [f'Frame: {self.data[0].frame}',
                  f' dx(")| dy(")| dr(deg)|    name|guide?',
                  f'{"-"*6:6s}|{"-"*6:6s}|{"-"*8:8s}|{"-"*8:8s}|{"-"*6:6s}',]
        for item in self.data:
            output.append(item.__str__())
        return "\n".join(output)


##-------------------------------------------------------------------------
## Per-Defined Patterns
##-------------------------------------------------------------------------
class Stare(OffsetPattern):
    def __init__(self):
        super().__init__()
        self.name = 'Stare'
        self.frame = SkyFrame()
        self.data = [TelescopeOffset(dx=0, dy=0, posname='base', frame=SkyFrame())]


class StarSkyStar(OffsetPattern):
    def __init__(self, dx=0, dy=0, guide=True, guideatsky=False):
        super().__init__()
        self.name = f'StarSkyStar ({dx:.0f} {dy:.0f})'
        self.frame = SkyFrame()
        self.data = [TelescopeOffset(dx=0, dy=0, posname='star', frame=SkyFrame(), guide=guide),
                     TelescopeOffset(dx=dx, dy=dy, posname='sky', frame=SkyFrame(), guide=guideatsky),
                     TelescopeOffset(dx=0, dy=0, posname='star', frame=SkyFrame(), guide=guide),
                     ]
