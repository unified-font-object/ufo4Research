"""
UFO 3 sqlLite File System
-----------------

This implements an on-disk, compressed (sqlLite) package
structure.
"""

import os
import sqlite3

from core.fileSystem import BaseFileSystem

class SqliteFileSystem(BaseFileSystem):

    fileExtension = 'ufodb'

    def __init__(self, path):
        super(SqliteFileSystem, self).__init__()
        self.path = path
        # connect to a db
        self.db = sqlite3.connect(self.path)
        # create the base table if is doenst exists yet
        self.db.execute('CREATE TABLE IF NOT EXISTS data(location TEXT PRIMARY KEY, bytes TEXT)')
        
    def close(self):
        # commit all changes to the db
        self.db.commit()
        # close the db
        self.db.close()

    # ------------
    # File Support
    # ------------

    # locations

    def joinLocations(self, location1, *location2):
        return os.path.join(location1, *location2)

    def splitLocation(self, location):
        return os.path.split(location)

    # bytes <-> location

    def readBytesFromLocation(self, location):
        cursor = self.db.execute('SELECT bytes FROM data WHERE location=?', (location,))
        data = cursor.fetchone()
        if data:
            return data[0]
        return None
        
    def writeBytesToLocation(self, data, location):
        try:
            self.db.execute('INSERT INTO data VALUES (?, ?)', (location, data))
        except sqlite3.IntegrityError:
            self.db.execute('UPDATE data SET bytes=? WHERE location=?', (data, location))
        
            
        



if __name__ == "__main__":
    from core.fileSystem import debugWriteFont, debugReadFont
    debugWriteFont(SqliteFileSystem)
    font = debugReadFont(SqliteFileSystem)