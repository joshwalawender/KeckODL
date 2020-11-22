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
    def __init__(self, target=None, pattern=None, detconfig=None,
                 instconfig=None, repeat=1):
        self.target = target
        self.pattern = pattern
        self.detconfig = detconfig
        self.instconfig = instconfig
        self.repeat = repeat


    def validate(self):
        pass


    def estimate_time(self):
        '''Estimate the wall clock time to complete the sequence.
        '''
        return {'shutter open time': len(self.pattern) * self.detconfig.exptime\
                                     * self.repeat,
                  'wall clock time': len(self.pattern) * self.detconfig.exptime\
                                     * self.repeat}


    def cals(self):
        return self.instconfig.cals()


    def __str__(self):
        return (f'{str(self.target):15s}|{str(self.pattern):19s}|'
                f'{self.repeat:6d} |{str(self.detconfig):35s}|'
                f'{str(self.instconfig):45s}')


    def __repr__(self):
        return (f'{str(self.target):15s}|{str(self.pattern):19s}|'
                f'{self.repeat:6d} |{str(self.detconfig):35s}|'
                f'{str(self.instconfig):45s}')


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
        output = [(f'{"Target":15s}|{"Pattern":19s}|{"repeat":7s}|'
                   f'{"DetectorConfig":35s}|{"InstrumentConfig":45s}'),
                  (f'{"-"*15:15s}|{"-"*19:19s}|{"-"*7:7s}|{"-"*35:35s}|'
                   f'{"-"*45:45s}')]
        for item in self.data:
            output.append(item.__str__())
        return "\n".join(output)


    def __repr__(self):
        output = [(f'{"Target":15s}|{"Pattern":19s}|{"repeat":7s}|'
                   f'{"DetectorConfig":35s}|{"InstrumentConfig":45s}'),
                  (f'{"-"*15:15s}|{"-"*19:19s}|{"-"*7:7s}|{"-"*35:35s}|'
                   f'{"-"*45:45s}')]
        for item in self.data:
            output.append(item.__str__())
        return "\n".join(output)
