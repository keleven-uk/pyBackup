About pyBackup

A attempt to write a backup script in Python.

Written in Python 3.7.


The backup is a mirrored backup, that is after the process destDir will be a perfect mirror of sourceDir.

usage: pyBackup.py [-h] [-s SOURCEDIR] [-d DESTDIR] [-t] [-l] [-v]

A Python backup script.
-----------------------
The backup is a mirrored backup, that is after
the process destDir will be a perfect mirror of sourceDir.

optional arguments:
  -h, --help            show this help message and exit
  -s SOURCEDIR, --sourceDir SOURCEDIR
                        Name of the Source directory to backed up [mirrored].
  -d DESTDIR, --destDir DESTDIR
                        Name of the Destination directory.
  -t, --test            run a test backup, nothing is changes only reported on.
  -l, --license         Print the Software License.
  -v, --version         show program's version number and exit

 Kevin Scott (C) 2019 - 2020

