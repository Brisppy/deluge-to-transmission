#!/usr/bin/env python

import sys
import json
import requests
from variables import *
from pathlib import Path, PureWindowsPath, PurePosixPath
from base64 import b64encode


class Deluge:
    def __init__(self, url, password, file_path, config_path):
        """Fetch data from Deluge.
        Manual: https://deluge.readthedocs.io/en/latest/reference/api.html#

        :param url: url of Deluge
        :param password: password for Deluge
        :param file_path: torrent download directory
        :param config_path: Deluge config folder
        """
        self.cookies = []
        self.url = url
        self.password = password
        self.file_path = file_path
        self.config_path = config_path
        # Perform auth
        self.auth_api()

    def put_api(self, method, params=None):
        """Sends a given request to the Deluge API

        :param method: api function to call
        :param params: parameters to pass to function
        :return: response from deluge api
        """
        if params is None:
            params = []
        b = {'method': method, 'params': params, 'id': 1}
        h = {'Content-Type': "application/json", 'Accept': "application/json"}
        r = requests.post(url=self.url + '/json', data=json.dumps(b), headers=h, cookies=self.cookies, verify=False)
        if r.status_code != 200:
            sys.exit('ERROR: Deluge request failed.')

        if json.loads(r.text)['error']:
            if json.loads(r.text)['error']['message'] == 'Not authenticated':
                self.auth_api()
                # Retry request
                self.put_api(method, params)

        return r

    def auth_api(self):
        r = self.put_api('auth.login', [self.password])
        if json.loads(r.text)['result']:
            self.cookies = dict(_session_id=r.cookies['_session_id'])

        else:
            sys.exit('ERROR: Deluge authentication failed.')


class Transmission:
    def __init__(self, url, auth, file_path, config_path):
        """Fetch data from Transmission.
        Manual: https://github.com/transmission/transmission/blob/main/extras/rpc-spec.txt

        :param url: url of Transmission
        :param auth: username:password used for api access
        :param file_path: torrent download directory
        :param config_path: Transmission config folder
        """
        self.url = url + '/transmission/rpc'
        self.auth = auth
        self.file_path = file_path
        self.config_path = config_path
        self.sid = ''
        # Perform auth
        self.put_api()

    def put_api(self, method='', arguments=None):
        """Sends a request to Transmission API.

        :param method: api function to call
        :param arguments: Arguments to pass to specified function
        :return: API response
        """
        if arguments is None:
            arguments = []
        b = {'method': method, 'arguments': arguments}
        h = {'Content-Type': "application/json", 'Accept': "application/json", 'X-Transmission-Session-Id': self.sid}
        _r = requests.post(url=self.url, data=json.dumps(b), headers=h, verify=False)
        if _r.status_code == 409:
            # Initialize session header
            self.sid = _r.headers['X-Transmission-Session-Id']
            # Retry the request again
            _r = self.put_api(method=method, arguments=arguments)

        if _r.status_code != 200:
            print('error', _r.text)
            sys.exit('ERROR: Transmission request failed.')

        return _r

    # Adds specified torrent to transmission
    def add_torrent(self, torrent_base64, torrent_data):
        """Adds a given torrent to Transmission.

        :param torrent_base64: base64 hash of torrent file
        :param torrent_data: dict of torrent information
        :return: non-zero if added successfully
        """
        if not torrent_base64:
            return

        try:
            # Send base64 encoded torrent to transmission along with the generated directory, adding in a paused state
            _t = self.put_api('torrent-add', {'metainfo': torrent_base64,
                                              'download-dir': str(torrent_data['save_path']), 'paused': True})
            return json.loads(_t.text)['arguments']['torrent-added']['hashString']

        except BaseException as e:
            print('ERROR: Failed to add torrent to Transmission.', str(torrent_data))
            print('ERROR:', str(_t.text), str(e))
            return


def get_torrent_base64(deluge_config_path, torrent_hash):
    """Converts a given torrent files to base64

    :param deluge_config_path: path to deluge config folder
    :param torrent_hash: hash of torrent to encode
    :return: base64 encoding of torrent file, or nothing on error
    """
    try:
        return b64encode(open(
            Path(deluge_config_path, 'state', torrent_hash + '.torrent'), 'rb').read()).decode('ascii')

    except FileNotFoundError:
        return


def generate_file_path(save_path, deluge_file_path, transmission_file_path):
    """Converts torrent file paths from of Deluge instance to where Transmission expects

    :param save_path: torrent data folder
    :param deluge_file_path: base directory of deluge torrent data
    :param transmission_file_path: base directory of transmission torrent data
    :return: corrected save path
    """
    # First we compare the length of the separated file_path and save_path
    ld = len(save_path.parts) - len(deluge_file_path.parts)
    if ld:
        # Add subdirectories from save_path to the transmission file_path
        save_path = Path.joinpath(transmission_file_path, *list(save_path.parts[len(deluge_file_path.parts):]))
        return save_path

    else:
        # No additions needed, paths already match
        return save_path


def get_os(deluge_file_path, transmission_file_path):
    """Corrects paths if Deluge and Transmission are located on different OS's.

    :param deluge_file_path: directory of deluge torrent data
    :param transmission_file_path: directory of transmission torrent data
    :return: corrected deluge file path, corrected transmission file path
    """
    if '\\' in str(deluge_file_path):
        print('INFO: Deluge is on a windows system.')
        deluge_file_path = PureWindowsPath(deluge_file_path)

    elif '/' in str(deluge_file_path):
        print('INFO: Deluge is on a linux or mac system.')
        deluge_file_path = PurePosixPath(deluge_file_path)

    else:
        sys.exit('ERROR: Deluge OS is not recognized.')

    if '\\' in str(transmission_file_path):
        print('INFO: Transmission is on a windows system.')
        transmission_file_path = PureWindowsPath(transmission_file_path)

    elif '/' in str(transmission_file_path):
        print('INFO: Transmission is on a linux or mac system.')
        transmission_file_path = PurePosixPath(transmission_file_path)

    else:
        sys.exit('ERROR: Transmission OS is not recognized.')

    return deluge_file_path, transmission_file_path


# Main processing
def main():
    # First we must retrieve all torrents from deluge
    # Authenticate and store session cookies for both applications
    print('INFO: Authenticating against clients.')
    deluge = Deluge(**deluge_vars)
    transmission = Transmission(**transmission_vars)
    # Retrieve os information to correctly modify file paths
    deluge_file_path, transmission_file_path = get_os(deluge_vars['file_path'], transmission_vars['file_path'])
    # Get list of COMPLETED torrents, retrieving their hash, save path and name.
    # Possible filters can be found here: https://libtorrent.org/reference-Torrent_Status.html
    print('INFO: Fetching torrents from Deluge.')
    deluge_torrents = json.loads(deluge.put_api(
        'core.get_torrents_status',
        [{'progress': [100]}, ["save_path", "torrent_file", "name", "info_hashes", "peers"]]).text)['result']

    if not deluge_torrents:
        sys.exit('ERROR: No torrents returned by Deluge.')

    # Convert save_path strings into correct Path objects depending on os
    if isinstance(deluge_file_path, PurePosixPath):
        for torrent_hash in deluge_torrents:
            deluge_torrents[torrent_hash]['save_path'] = PurePosixPath(deluge_torrents[torrent_hash]['save_path'])

    elif isinstance(deluge_file_path, PureWindowsPath):
        for torrent_hash in deluge_torrents:
            deluge_torrents[torrent_hash]['save_path'] = PureWindowsPath(deluge_torrents[torrent_hash]['save_path'])

    # Process torrents one-by-one into transmission
    for torrent_hash, torrent_data in deluge_torrents.items():
        # Skip if any active peers present
        if torrent_data['peers']:
            continue

        # Check if torrent is already present in transmission
        if json.loads((transmission.put_api('torrent-get', {'fields': ['name'], 'ids': [torrent_hash]})).text
                      )['arguments']['torrents']:
            print('INFO: Torrent "' + torrent_data['name'] + '" already present.')
            continue

        # Now we rebuild the file paths for transmission
        torrent_data['save_path'] = generate_file_path(torrent_data['save_path'],
                                                       deluge_file_path, transmission_file_path)
        # Optionally pause torrent in deluge before adding
        deluge.put_api('core.pause_torrent', [torrent_hash])
        # Add torrent to transmission
        if transmission.add_torrent(get_torrent_base64(deluge_vars['config_path'], torrent_hash), torrent_data):
            # Remove torrent from deluge if it was successfully added
            print('INFO: Torrent ' + torrent_data['name'] + ' successfully added to Transmission.')
            deluge.put_api('core.remove_torrent', [torrent_hash, False])

    print('INFO: Finished adding torrents to Transmission.')


if __name__ == '__main__':
    main()
