import requests
import yaml
from warnings import warn

from .target import Target, TargetList
from .offset import OffsetPattern
from .instrument_config import InstrumentConfig
from .detector_config import DetectorConfig

db_upload_url = 'http://vm-webtools.keck.hawaii.edu:59999/'


class UploadFailed(UserWarning): pass


def upload_to_DB(input_list):

    output = []

    if type(input_list) in [TargetList, Target, OffsetPattern]:
        output.append(input_list.to_dict())
    elif type(input_list) is list:
        for item in input_list:
            output.append(item.to_dict())

    yaml_output = yaml.dump(output)
    files = [('yaml_cfg', yaml_output)]
    return yaml_output
#     r = requests.post(db_upload_url, files=files)
#     if r.status_code == requests.codes.ok:
#         return True
#     else:
#         warn('Upload failed', category=UploadFailed)
#         return False
