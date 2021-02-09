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
db_download_url = 'http://vm-devnginxsw/api/ddoi/getDefs?'


class UploadFailed(UserWarning): pass


def check_ping(address='vm-webtools.keck.hawaii.edu', wait=2):
    '''This can be removed once the DB is available outside of keck.  It is
    here just to prevent failures when testing.
    '''
    import subprocess
    import platform
    import os
    try:
        ping = subprocess.check_output(['which', 'ping'])
        ping = ping.decode()
        ping_cmd = [ping.strip()]
    except subprocess.CalledProcessError as e:
        warn("Ping command not available")
        ping_cmd = None
        return None
    os = platform.system()
    os = os.lower()
    # Ping once, wait up to 2 seconds for a response.
    if os == 'linux':
        ping_cmd.extend(['-c', '1', '-w', 'wait'])
    elif os == 'darwin':
        ping_cmd.extend(['-c', '1', '-W', 'wait000'])
    else:
        # Don't understand how ping works on this platform.
        ping_cmd = None
        return None

    ping_cmd = [x.replace('wait', f'{int(wait)}') for x in ping_cmd]
    ping_cmd.append(address)
    output = subprocess.run(ping_cmd,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    if output.returncode != 0:
        return False
    else:
        return True


##-------------------------------------------------------------------------
## upload_to_DB
##-------------------------------------------------------------------------
def upload_to_DB(input_list):
    '''Upload objects to the database at Keck
    '''
    if check_ping() in [False, None]:
        print('Unable to connect to Keck DB')
        return None

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
## download_from_DB
##-------------------------------------------------------------------------
def download_from_DB(col='Target', name=None):
    if check_ping(address='vm-devnginxsw') in [False, None]:
        print('Unable to connect to Keck DB')
        return None
    query_url = f'{db_download_url}col={col}'
    if name is not None:
        query_url += f'&name={name}'
    r = requests.get(query_url)
    if r.status_code != requests.codes.ok:
        warn('Download failed', category=UploadFailed)
        return None
    contents = yaml.safe_load(r.text)
    return parse_yaml([contents])


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
                dc = getattr(importlib.import_module(f'odl.{instname.lower()}'),
                             f'{instname}{detectorname}DetectorConfig')(**dc_dict)
                dcs.append(dc)

        # Read InstrumentConfigs
        if 'InstrumentConfigs' in entry.keys():
            for ic_dict in entry['InstrumentConfigs']:
                instname = ic_dict.pop('instrument')
                ic = getattr(importlib.import_module(f'odl.{instname.lower()}'),
                             f'{instname}Config')(**ic_dict)
                ics.append(ic)

    return tl, ops, dcs, ics


