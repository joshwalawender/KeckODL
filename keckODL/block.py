#!python3

## Import General Tools
from collections import UserList


##-------------------------------------------------------------------------
## ObservingBlock
##-------------------------------------------------------------------------
class ObservingBlock(UserList):
    '''An ordered list of (Target, Sequence) pairs
    
    Upon entering each element in the list, the Target defines what type of
    acquisition to perform
    '''
    def validate(self):
        pass


    def __str__(self):
        output = [f'{"Pattern":19s} {"DetectorConfig":29s} {"InstrumentConfig":29s}',
                  '-'*86]
        for item in self.data:
            output.append(item.__str__())
        return "\n".join(output)


    def __repr__(self):
        output = [f'{"Pattern":19s} {"DetectorConfig":29s} {"InstrumentConfig":29s} {"repeat":6s}',
                  '-'*86]
        for item in self.data:
            output.append(item.__str__())
        return "\n".join(output)
