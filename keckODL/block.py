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
    def __init__(self, target=None, pattern=None, instconfig=None):
        self.target = target
        self.pattern = pattern
        self.instconfig = instconfig


    def validate(self):
        pass


    def estimate_time(self):
        '''Estimate the wall clock time to complete this block.
        '''
        inst_time = self.instconfig.estimate_time()
        return {'shutter open time': self.pattern.repeat * len(self.pattern) *\
                                     inst_time['shutter open time'],
                'wall clock time': self.pattern.repeat * len(self.pattern) *\
                                   inst_time['wall clock time']}


    def cals(self):
        return self.instconfig.cals()


    def __str__(self):
        return (f'{str(self.target):15s}|{str(self.pattern):22s}|'
                f'{str(self.instconfig):45s}|'
                f'{str(self.instconfig.detconfig):36s}')


    def __repr__(self):
        return (f'{str(self.target):15s}|{str(self.pattern):22s}|'
                f'{str(self.instconfig):45s}|'
                f'{str(self.instconfig.detconfig):36s}')


##-------------------------------------------------------------------------
## ObservingBlockList
##-------------------------------------------------------------------------
class ObservingBlockList(UserList):
    '''An ordered list of SequenceElements
    '''
    def validate(self):
        for i,s in enumerate(self.data):
            if type(s) != ObservingBlock:
                raise SequenceError(f'An ObservingBlockList must be made up of '
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
