"""
Test uploading all registerd fileSystem to your dropBox account

Required is the dropbox python API
see https://www.dropbox.com/developers/core/docs/python

and a auth token should be request first!
see https://www.dropbox.com/developers/core/start/python


result from Frederik (just in case you dont want to install everything)

----------------------
Upload font to dropBox
----------------------

file structure building test
----------------------------
Flat SQLite DB: 2.70396995544 (1 files)
Single XML: 1.93647909164 (1 files)
UFO 3: 443.017402172 (554 files)
UFO 3 Zipped: 1.76858496666 (1 files)

(result are very much depending on connection speed)
"""

try:
    # test if dropbox is installed
    import dropbox
    hasDropbox = True
except:
    hasDropbox = False

import tempfile
import time
import os
from core.fonts import compileFont
from core.fileSystem import _makeTestPath
from testAll import fileSystems, testFonts, setupFile, tearDownFile

def getAllFiles(fontFile):
    # get files recursively if 'fontFile' is a folder 
    paths = []
    if os.path.isdir(fontFile):
        for root, dirNames, fileNames in os.walk(fontFile):
            for fileName in fileNames:
                paths.append((root, fileName))
    else:
        root = os.path.dirname(fontFile)
        fileName = os.path.basename(fontFile)
        paths = [(root, fileName)]
    return paths


# the folder where to store the test files in your dropbox account
dropBoxRoot = "/ufoResearchTest"
# your auth token (see above to request one)
dropBoxAuthToken = "<your auth token, please change!>"


def execute():
    if not hasDropbox:
        print "dropbox python API is not installed."
        return

    # connect to your dropbox account
    client = dropbox.client.DropboxClient(dropBoxAuthToken)
    try:
        client.account_info()
    except:
        import traceback
        print traceback.format_exc(5)
        return
        

    testName = "Upload font to dropBox"
    print
    print "-" * len(testName)
    print testName
    print "-" * len(testName)
    print

    for fontName, description in sorted(testFonts):
        print fontName
        print "-" * len(fontName)
        font = compileFont(fontName)

        for fileSystemName, fileSystemClass in sorted(fileSystems.items()):
            tempRoot = tempfile.gettempdir()
            # provide a proper file name
            baseFileName = "ufo4-debug-%s.%s" % (fileSystemClass.__name__, fileSystemClass.fileExtension)
            path = os.path.join(tempRoot, baseFileName)
            # remove if the file already exists
            tearDownFile(path)
            # setup
            fs = fileSystemClass(path)
            setupFile(font, fs)
            # get all files
            paths = getAllFiles(path)

            start = time.time()

            try:
                for root, fileName in paths:
                    # set all the correct paths
                    filePath = os.path.join(root, fileName)
                    relativePath = os.path.relpath(filePath, tempRoot)
                    dropBoxPath = os.path.join(dropBoxRoot, relativePath)

                    # open the file
                    f = open(filePath)
                    # send the file to your dropbox client
                    response = client.put_file(dropBoxPath, f)
                    f.close()

                result = time.time() - start
                print "%s: %s (%s files)" % (fileSystemName, result, len(paths))
            except:
                import traceback
                print "%s: Oeps" % fileSystemName 
                print traceback.format_exc(5)
            finally:
                tearDownFile(path)

           



if __name__ == "__main__":
    execute()