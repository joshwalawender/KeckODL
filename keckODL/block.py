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
    
    Can be thought of as one line in a table of actions.
    '''
    def __init__(self, target=None, pattern=None, instconfig=None,
                 detconfig=None):
        self.target = target
        self.pattern = pattern
        self.instconfig = instconfig
        self.detconfig = detconfig if type(detconfig) in [list, tuple]\
                         else [detconfig]


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
        return self.instconfig.cals()


    def __str__(self):
        return (f'{str(self.target):15s}|{str(self.pattern):22s}|'
                f'{str(self.instconfig):45s}|'
                f'{str(self.detconfig):36s}')


    def __repr__(self):
        return (f'{str(self.target):15s}|{str(self.pattern):22s}|'
                f'{str(self.instconfig):45s}|'
                f'{str(self.detconfig):36s}')


##-------------------------------------------------------------------------
## SecondaryBlock
##-------------------------------------------------------------------------
class SecondaryBlock():
    '''Object describing a secondary observing block.
    '''
    def __init__(self, instconfig=None, linkedto=None):
        self.instconfig = instconfig
        self.linkedto = linkedto


    def validate(self):
        pass


    def estimate_time(self):
        '''Estimate the wall clock time to complete this block.
        '''
        inst_time = self.instconfig.estimate_time()
        return {'shutter open time': self.linkedto.pattern.repeat * len(self.linkedto.pattern) *\
                                     inst_time['shutter open time'],
                'wall clock time': self.linkedto.pattern.repeat * len(self.linkedto.pattern) *\
                                   inst_time['wall clock time']}


    def cals(self):
        return self.instconfig.cals()


    def __str__(self):
        return (f'{"( linked)":15s}|{"( linked)":22s}|'
                f'{str(self.instconfig):45s}|'
                f'{str(self.instconfig.detconfig):36s}')


    def __repr__(self):
        return (f'{"( linked)":15s}|{"( linked)":22s}|'
                f'{str(self.instconfig):45s}|'
                f'{str(self.instconfig.detconfig):36s}')


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
        for instconfig in set([OB.instconfig for OB in self.data]):
            calblocklist.extend( instconfig.cals() )
        return calblocklist


    def __str__(self):
        output = [(f'{"Target":15s}|{"Pattern":22s}|'
                   f'{"InstrumentConfig":45s}|{"DetectorConfig":36s}'),
                  (f'{"-"*15:15s}|{"-"*22:22}|{"-"*45:45}|'
                   f'{"-"*36:36s}')]
        for item in self.data:
            output.append(item.__str__())
        return "\n".join(output)


    def __repr__(self):
        output = [(f'{"Target":15s}|{"Pattern":22s}|'
                   f'{"InstrumentConfig":45s}|{"DetectorConfig":36s}'),
                  (f'{"-"*15:15s}|{"-"*22:22}|{"-"*45:45}|'
                   f'{"-"*36:36s}')]
        for item in self.data:
            output.append(item.__str__())
        return "\n".join(output)
