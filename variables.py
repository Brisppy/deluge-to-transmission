# User defined variables for deluge-to-transmission

from pathlib import Path

"""
!!IMPORTANT!!

Windows paths need TWO backslashes.

Do not end paths with a back or forward slash.

A note about the file_path variables:
  These must point to the EXACT same BASE location.

  e.g If you are moving from say a Windows machine to a Linux one, the base path structure can differ.
      Say your torrents base path is W:\\torrents on Windows, and /mnt/media/torrents on Linux, these
      are the paths you must supply to the below variables.
      The actual torrents themselves may be in a subdirectory such as W:\\torrents\\movies which would match with
      /mnt/media/torrents/movies, but the base path is what should be supplied (W:\\torrents, /mnt/media/torrents).

In summary, the base path can differ between the source and destination clients, but the subfolders MUST MATCH
between the instances.
"""

deluge_vars = {'url': 'http://x.x.x.x:xxxx',
               'password': 'password',
               'file_path': Path('/path/to/deluge/torrent/data'),
               'config_path': Path('/path/to/deluge/config')}

transmission_vars = {'url': 'http://x.x.x.x:xxxx',
                     'auth': 'username:password',
                     'file_path': Path('/path/to/transmission/torrent/data'),
                     'config_path': Path('/path/to/transmission/config')}
