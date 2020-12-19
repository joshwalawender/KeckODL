import importlib
import requests
import yaml
from warnings import warn
import importlib
from astropy import units as u

from .target import Target, TargetList
from .offset import OffsetPattern, TelescopeOffset
from .instrument_config import InstrumentConfig
from .detector_config import DetectorConfig
from . import offset


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
        if 'Targets' in entry.keys():
            for td in entry['Targets']:
                tl.append(Target(name=td.get('name', None),
                                 RA=td.get('RA', None),
                                 Dec=td.get('Dec', None),
                                 equinox=td.get('equinox', None),
                                 rotmode=td.get('rotmode', None),
                                 PA=td.get('PA', None),
                                 RAOffset=td.get('RAOffset', None),
                                 DecOffset=td.get('DecOffset', None),
                                 objecttype=td.get('objecttype', None),
                                 acquisition=td.get('acquisition', None),
                                 frame=td.get('frame', None),
                                 PMRA=td.get('PMRA', 0),
                                 PMDec=td.get('PMDec', 0),
                                 epoch=td.get('epoch', None),
                                 obstime=td.get('obstime', None),
                                 mag=td.get('mag', {}),
                                 comment=td.get('comment', None) ) )
        # Read OffsetPatterns
        if 'OffsetPatterns' in entry.keys():
            for op in entry['OffsetPatterns']:
                offset_list = [TelescopeOffset(dx=o.get('dx', 0*u.arcsec),
                                               dy=o.get('dy', 0*u.arcsec),
                                               dr=o.get('dr', 0*u.arcsec),
                                               relative=o.get('relative', False),
                                               frame=getattr(offset,
                                                             o.get('frame', 'SkyFrame'))(),
                                               posname=o.get('posname', ''),
                                               guide=o.get('guide', True))
                                               for o in op['offsets']]
                ops.append(OffsetPattern(offset_list,
                                         name=op.get('name', ''),
                                         repeat=op.get('repeat', 1)))

        # Read DetectorConfigs
        if 'DetectorConfigs' in entry.keys():
            for dc_dict in entry['DetectorConfigs']:
                instname = dc_dict.pop('instrument')
                detectorname = dc_dict.pop('detector')
                dc = getattr(importlib.import_module(f'keckODL.{instname.lower()}'),
                             f'{instname}{detectorname}DetectorConfig')(**dc_dict)
                dcs.append(dc)

        # Read InstrumentConfigs
        if 'InstrumentConfigs' in entry.keys():
            for ic_dict in entry['InstrumentConfigs']:
                instname = ic_dict.pop('instrument')
                ic = getattr(importlib.import_module(f'keckODL.{instname.lower()}'),
                             f'{instname}Config')(**ic_dict)
                ics.append(ic)

    return tl, ops, dcs, ics


