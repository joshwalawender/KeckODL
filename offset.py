#!python3

## Import General Tools
from astropy import units as u


class OffsetError(Exception):
    pass


class OffsetWarning(UserWarning):
    pass



##-------------------------------------------------------------------------
## OffsetFrame
##-------------------------------------------------------------------------
class OffsetFrame():
    '''An OffsetFrame is the coordinate frame in which the offset is done.  It
    usually corresponds to a focal plane.  An OffsetFrame consists of a pixel
    scale and an orientation.
    
    Examples: Sky, Detector, Slit, Guider
    '''
    def __init__(self, pixelscale=1*u.arcsec/u.pixel, PA='ROTPPOSN'):
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


##-------------------------------------------------------------------------
## Some actual frames with values
##-------------------------------------------------------------------------
KCWI_SmallSlicer_Frame = OffsetFrame(pixelscale=0.35*U.arcsec/u.pixel, PA='ROTPPOSN')
KCWI_MediumSlicer_Frame = OffsetFrame(pixelscale=0.70*U.arcsec/u.pixel, PA='ROTPPOSN')
KCWI_LargeSlicer_Frame = OffsetFrame(pixelscale=1.35*U.arcsec/u.pixel, PA='ROTPPOSN')


##-------------------------------------------------------------------------
## TelescopeOffset
##-------------------------------------------------------------------------
class TelescopeOffset():
    '''Describes a telescope offset for the purposes of including it in an
    observing sequence.
    '''
    def __init__(self, frame=None, dx=0, dy=0, dr=0, relative=False):
        self.frame = frame
        self.dx = dx
        self.dy = dy
        self.dr = dr
        self.relative = relative


    def validate(self):
        '''Validate the offset.
        
        Check that a known frame was used.
        '''
        # Is the given frame a known OffsetFrame
        if issubclass(self.frame, OffsetFrame) is False:
            raise OffsetError(f'"{self.frame}" is not a known OffsetFrame')
        # Are the offset values valid
        if type(self.dx) not in [float, int, u.Quantity]:
            raise OffsetError(f'Value for dx "{self.frame}" is not valid type')
        if type(self.dy) not in [float, int, u.Quantity]:
            raise OffsetError(f'Value for dy "{self.frame}" is not valid type')


