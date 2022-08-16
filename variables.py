# User defined variables for deluge-to-transmission
# See README.md for documentation

from pathlib import Path

deluge_vars = {'url': 'http://x.x.x.x:xxxx',
               'password': 'password',
               'file_path': Path('/path/to/deluge/torrent/data'),
               'config_path': Path('/path/to/deluge/config')}

transmission_vars = {'url': 'http://x.x.x.x:xxxx',
                     'auth': 'username:password',
                     'file_path': Path('/path/to/transmission/torrent/data'),
                     'config_path': Path('/path/to/transmission/config')}
