#!python3

## Import General Tools
from pathlib import Path
from astropy import units as u
from collections import UserList


class BlockError(Exception):
    pass


class BlockWarning(UserWarning):
    pass


##-------------------------------------------------------------------------
## ObservingBlock
##-------------------------------------------------------------------------
class ObservingBlock():
    '''Object describing an observing block.
    
    Attributes
    ----------
    target : a `Target` instance or None
        The target this block will be used to observe.  None indicates that
        either the target has already been acquired in a previous block and no
        other actions are needed or that the target is not specified (for
        example, no target is needed for a set of arc lamp spectra).

    pattern : an `OffsetPattern` instance
        The offset pattern to use for this observing block.

    instconfig : an instance of `InstrumentConfig` or one if its subclasses
        The instrument config to use for this observing block.

    detconfig : an instance of `DetectorConfig` or one if its subclasses
        The detector config to use for this observing block.

    align : an `Alignment` instance
        The alignment strategy to use for this observing block.

    blocktype : str

    associatedblocks : list

    guidestar : an `astropy.coordinates.SkyCoord` instance

    drp_args : a dict containing arguments for the data reduction pipeline

    ql_args : a dict containing arguments for the quick look pipeline
    '''
    def __init__(self, target=None, pattern=None, instconfig=None,
                 detconfig=None, align=None, blocktype=None,
                 associatedblocks=None, guidestar=None,
                 drp_args=None, ql_args=None,
                 ):
        self.target = target
        self.pattern = pattern
        self.instconfig = instconfig
        self.detconfig = detconfig if type(detconfig) in [list, tuple]\
                         else [detconfig]
        self.align = align
        self.blocktype = blocktype
        self.associatedblocks = associatedblocks
        self.guidestar = guidestar
        self.drp_args = drp_args
        self.ql_args = ql_args


    def validate(self):
        pass


    def estimate_time(self):
        '''Estimate the wall clock time to complete this block.
        '''
        if type(self.detconfig) in [list, tuple]:
            t = [dc.estimate_clock_time() for dc in self.detconfig]
            detector_time = max(t)
            e = [dc.exptime*dc.nexp for dc in self.detconfig]
            exposure_time = max(e)
        else:
            detector_time = self.detconfig.estimate_clock_time()
            exposure_time = self.detconfig.exptime
        return {'shutter open time': self.pattern.repeat * len(self.pattern) *\
                                     exposure_time,
                'wall clock time': self.pattern.repeat * len(self.pattern) *\
                                   detector_time}


    def cals(self):
        if isinstance(self, CalibrationBlock):
            return None
        elif isinstance(self, FocusBlock):
            return None
        else:
            return self.instconfig.cals()


    def __str__(self):
        return (f'{str(self.target):15s}|{str(self.pattern):22s}|'
                f'{str(self.instconfig):45s}|{str(self.detconfig):36s}|'
                f'{str(self.align):20s}')


    def __repr__(self):
        return (f'{str(self.target):15s}|{str(self.pattern):22s}|'
                f'{str(self.instconfig):45s}|{str(self.detconfig):36s}|'
                f'{str(self.align):20s}')


##-------------------------------------------------------------------------
## ScienceBlock
##-------------------------------------------------------------------------
class ScienceBlock(ObservingBlock):
    '''An observing block describing a science observation.
    '''
    def __init__(self, target=None, pattern=None, instconfig=None,
                 detconfig=None, align=None, blocktype='science'):
        super().__init__(target=target, pattern=pattern, instconfig=instconfig,
                         detconfig=detconfig, align=align, blocktype=blocktype)


##-------------------------------------------------------------------------
## TelluricBlock
##-------------------------------------------------------------------------
class TelluricBlock(ObservingBlock):
    '''An observing block describing a telluric standard observation.
    '''
    def __init__(self, target=None, pattern=None, instconfig=None,
                 detconfig=None, align=None, blocktype='telluric'):
        super().__init__(target=target, pattern=pattern, instconfig=instconfig,
                         detconfig=detconfig, align=align, blocktype=blocktype)


##-------------------------------------------------------------------------
## StandardStarBlock
##-------------------------------------------------------------------------
class StandardStarBlock(ObservingBlock):
    '''An observing block describing a standard star observation.
    '''
    def __init__(self, target=None, pattern=None, instconfig=None,
                 detconfig=None, align=None, blocktype='standard'):
        super().__init__(target=target, pattern=pattern, instconfig=instconfig,
                         detconfig=detconfig, align=align, blocktype=blocktype)


##-------------------------------------------------------------------------
## CalibrationBlock
##-------------------------------------------------------------------------
class CalibrationBlock(ObservingBlock):
    '''An observing block describing a calibration observation.
    '''
    def __init__(self, target=None, pattern=None, instconfig=None,
                 detconfig=None, align=None, blocktype='calibration'):
        super().__init__(target=target, pattern=pattern, instconfig=instconfig,
                         detconfig=detconfig, align=align, blocktype=blocktype)


##-------------------------------------------------------------------------
## FocusBlock
##-------------------------------------------------------------------------
class FocusBlock(ObservingBlock):
    '''An observing block describing a calibration observation.
    '''
    def __init__(self, target=None, pattern=None, instconfig=None,
                 detconfig=None, align=None, blocktype='focus'):
        super().__init__(target=target, pattern=pattern, instconfig=instconfig,
                         detconfig=detconfig, align=align, blocktype=blocktype)


##-------------------------------------------------------------------------
## ObservingBlockList
##-------------------------------------------------------------------------
class ObservingBlockList(UserList):
    '''An ordered list of ObservingBlocks
    '''
    def validate(self):
        for i,s in enumerate(self.data):
            if type(s) != ObservingBlock:
                raise BlockError(f'An ObservingBlockList must be made up of '
                                 f'ObservingBlocks. Element {i} is {type(s)}.')
            s.validate()


    def estimate_time(self):
        '''Estimate the wall clock time to complete the blocks.
        '''
        estimate = {'shutter open time': 0, 'wall clock time': 0}
        for s in self.data:
            estimate['shutter open time'] += s.estimate_time()['shutter open time']
            estimate['wall clock time'] += s.estimate_time()['wall clock time']
        print(f"Shutter Open Time: {estimate['shutter open time']} s "
              f"({estimate['shutter open time']/3600:.1f} hrs)")
        print(f"Wall Clock Time: {estimate['wall clock time']} s "
              f"({estimate['wall clock time']/3600:.1f} hrs)")


    def cals(self):
        calblocklist = ObservingBlockList()
        ics = [OB.instconfig for OB in self.data\
               if not isinstance(OB, CalibrationBlock)\
               and not isinstance(OB, FocusBlock)]
        for instconfig in set(ics):
            calblocklist.extend( instconfig.cals() )
        return calblocklist


    def __str__(self):
        output = [(f'{"Target":15s}|{"Pattern":22s}|'
                   f'{"InstrumentConfig":45s}|{"DetectorConfig":36s}|'
                   f'{"AlignmentMethod":20s}'),
                  (f'{"-"*15:15s}|{"-"*22:22}|{"-"*45:45}|'
                   f'{"-"*36:36s}|{"-"*20:20s}')]
        for item in self.data:
            output.append(item.__str__())
        return "\n".join(output)


    def __repr__(self):
        output = [(f'{"Target":15s}|{"Pattern":22s}|'
                   f'{"InstrumentConfig":45s}|{"DetectorConfig":36s}|'
                   f'{"AlignmentMethod":20s}'),
                  (f'{"-"*15:15s}|{"-"*22:22}|{"-"*45:45}|'
                   f'{"-"*36:36s}|{"-"*20:20s}')]
        for item in self.data:
            output.append(item.__str__())
        return "\n".join(output)

