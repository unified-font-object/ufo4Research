# UFO 4 Research

UFO 4 *research* is being conducted here. None of this is official or an example implementation.

## File Structure Tests

Possible file structures are currently being researched. At the moment, the following are being considered:

1. Zipped version of the current UFO 3 file structure 
2. Single XML file.
3. Package file structure similar to the UFO 3 file structure but with the glyph sub-directories flattened into single XML files.
4. Zipped version of 3.
5. Package file structure similar to the UFO 3 file structure but with the glyphs in the glyph sub-directories grouped into chunks rather than one file per glyph.
6. Zipped version of 5.
7. A very simple SQLite database. The intial idea is to use the existing UFO 3 strcture, but instead of writing to paths, the files would be stored in something like a key value with the relative paths indicating the file location in the UFO 3 package structe as the keys and the current XML formats as the values. Additionally, modification times for each of these could be stored.

### Some research links:
- [SQLite as file format.](https://www.sqlite.org/appfileformat.html)
- [Some notes on SQLite corruption](https://www.sqlite.org/howtocorrupt.html)
- [SQlite databases under git](http://ongardie.net/blog/sqlite-in-git/)
- Fontlab have introduced an `.ufoz` format (that basically is 1. in the list above) as mentioned in this [blogpost](http://blog.fontlab.com/font-utility/vfb2ufo/)

### Test Implementation

The tests are likely going to be structured as a common UFO reader/writer that works with an abstract "file system" API. Basically, this API will enable the reader/writer to interact with the various file structure proposals without knowing the internal details of the file structures. Each test will be implemented as one of these file structures following the abstract API. Given that the "file systems" will be the only part of the code that varies from test to test, this should give us a very clear picture of the read/write effeciency and ease of implementation of the various proposals.

The current effort is going into building a file system wrapper that works with the existing UFO 3 file structure.

The UFO reader/writer and GLIF interpretation were initially forked from RoboFab's UFO 3 version of ufoLib. These have been greatly simplified for these tests. Validation of the data has been eliminated to reduce the number of moving parts. Therefore, all incoming data must be perfectly compliant with the UFO 3 specification. The XML parsing, both GLIF and plist, is now handled exclusively by the Python Standard Library's version of cElementTree.
