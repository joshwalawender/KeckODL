import requests
import yaml
from warnings import warn

from .target import Target, TargetList
from .offset import OffsetPattern
from .instrument_config import InstrumentConfig
from .detector_config import DetectorConfig

db_upload_url = 'http://vm-webtools.keck.hawaii.edu:59999/'


class UploadFailed(UserWarning): pass


##-------------------------------------------------------------------------
## upload_to_DB
##-------------------------------------------------------------------------
def upload_to_DB(input_list):
    '''Upload objects to the database at Keck
    '''
    output = []

    if type(input_list) in [TargetList, Target, OffsetPattern]:
        output.append(input_list.to_dict())
    elif type(input_list) is list:
        for item in input_list:
            output.append(item.to_dict())

    yaml_output = yaml.dump(output)
    files = [('yaml_cfg', yaml_output)]
    r = requests.post(db_upload_url, files=files)
    if r.status_code == requests.codes.ok:
        return True
    else:
        warn('Upload failed', category=UploadFailed)
        return False


##-------------------------------------------------------------------------
## parse_yaml
##-------------------------------------------------------------------------
def parse_yaml(contents):
    '''Parse YAML from a file or from the Keck database
    '''
    tl = TargetList([]) # Output Target List
    ops = [] # List of output OffsetPatterns
    ics = [] # List of output InstrumentConfigs
    dcs = [] # List of output DetectorConfigs
    for entry in contents:
        # Read Targets
        if len(entry['Targets']) > 0:
            targets = [Target(name=d.get('name', None),
                              RA=d.get('RA', None),
                              Dec=d.get('Dec', None),
                              equinox=d.get('equinox', None),
                              rotmode=d.get('rotmode', None),
                              PA=d.get('PA', None),
                              RAOffset=d.get('RAOffset', None),
                              DecOffset=d.get('DecOffset', None),
                              objecttype=d.get('objecttype', None),
                              acquisition=d.get('acquisition', None),
                              frame=d.get('frame', None),
                              PMRA=d.get('PMRA', 0),
                              PMDec=d.get('PMDec', 0),
                              epoch=d.get('epoch', None),
                              obstime=d.get('obstime', None),
                              mag = d.get('mag', {}),
                              comment=d.get('comment', None),)\
                       for d in entry['Targets']]
            tl.append(targets)
        # Read OffsetPatterns
        if len(entry['OffsetPatterns']) > 0:
            offsets = [TelescopeOffset(dx=d.get('dx', 0),
                                       dy=d.get('dy', 0),
                                       dr=d.get('dr', 0),
                                       relative=d.get('relative', False),
                                       frame=getattr(sys.modules[__name__],
                                                     d.get('frame', 'SkyFrame'))(),
                                       posname=d.get('posname', ''),
                                       guide=d.get('guide', True))
                       for d['offsets'] in entry['OffsetPatterns']]
            ops.append(OffsetPattern(offsets,
                           name=entry['OffsetPatterns'].get('name', ''),
                           repeat=entry['OffsetPatterns'].get('repeat', 1)))
    return tl, op, ics, dcs

