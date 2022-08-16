```
deluge-to-transmission - version 1.0
  A Python script for flushing completed torrents from Deluge to Transmission.
  Torrent clients can reside on separate computers and even operating systems
  as long as the file structure remains the same past the provided base path.

Processing:

  1.       First we find any matching torrents
   1.1      Generate list of dicts containing completed torrents from deluge
            via API
    1.1.1    Dict contains: 
                 {"torrentHash": 
                    {"name": "torrentName", "save_path": "torrentFilePath", 
                     "torrentId": "torrentId"}}
   1.2      Convert the deluge save_path to one for the destination
            transmission instance
  2.       Now we add them all to transmission
   2.1      Loop through each torrent, adding them to transmission one-by-one
    2.1.1    Pause torrent in Deluge
    2.1.2    Convert torrent to a base64 string
    2.1.3    Send base64 string to transmission
    2.1.4    Now remove torrent from deluge if successfully added

Configuration:
  Variables are set in 'variables.py'.
  
  Most fields are self-explanatory, make sure to leave 'Path' and enclosing
  brackets '()' around the variables containing file paths.

  **IMPORTANT**
    Windows paths need TWO backslashes.
    Do not end paths with a back or forward slash.
  
  A note about the file_path variables:
    These must point to the EXACT same BASE location.
  
    e.g If you are moving from say a Windows machine to a Linux one, the base
        path structure can differ. Say your torrents base path is W:\\torrents
        on Windows, and /mnt/media/torrents on Linux, these are the paths you
        must supply to the variables in 'variables.py'. The actual torrents
        themselves may be in a subdirectory such as  W:\\torrents\\movies
        which would match with /mnt/media/torrents/movies, but the base path
        is what should be supplied (W:\\torrents, /mnt/media/torrents).
    
  In summary, the base path can differ between the source and destination
  clients, but the subfolders MUST MATCH between the instances.
```