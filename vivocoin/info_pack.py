import os
import zipfile
import json

def find_filename(filename, info_list):
    for info in info_list:
        basename = os.path.basename(info.filename)
        if basename == filename:
            return info.filename
    return None

def read_auth_requestor_info(info_pack_filename):
    with zipfile.ZipFile(info_pack_filename, 'r') as thezip:
        info_list = thezip.infolist()
        auth_requestor_filename = find_filename('auth_requestor.json', info_list)
        if auth_requestor_filename:
            with thezip.open(auth_requestor_filename, 'r') as handle:
                return json.loads(handle.read())

    return None
