###############################################################################################################
#                                                                                                             #
#  Perform a backup of sourceDir to destDir                                                                   #
#                                                                                                             #
#  The backup is a mirrored backup, that is after the process destDir will be a perfect mirror of sourceDir.  #
#                                                                                                             #
#  Usage: pyBackup [--help --test --license --version] -s sourceDir -d destDir                                #
#                                                                                                             #
#  October 2019                Kevin Scott                                                                    #
#                                                                                                             #
#                                                                                                             #
#   V1.01   17 Oct.2019     Will copy files that are not in the destination.                                  #
#   V1.02   20 Oct.2019     Added copy of file size and date change.  Added reverse scan.                     #
#                                                                                                             #
###############################################################################################################
#    Copyright (C) <2019>  <Kevin Scott>                                                                      #
#                                                                                                             #
#    This program is free software: you can redistribute it and/or modify it under the terms of the           #
#    GNU General Public License as published by the Free Software Foundation, either version 3 of the         #`
#    License, or (at your option) any later version.                                                          #
#                                                                                                             #
#    This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without        #
#    even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
#    GNU General Public License for more details.                                                             #
#                                                                                                             #
#    You should have received a copy of the GNU General Public License along with this program.               #
#    If not, see <http://www.gnu.org/licenses/>.                                                              #
#                                                                                                             #
###############################################################################################################


import os
import time
import shutil
import textwrap
import datetime
import argparse
from _version import __version__


############################################################################################## copyFiles ######

class Results():
    """  A simple class that holds the total number and size of files copied.
         Save on global variables.
    """   
    def __init__(self):
        self.copySize     = 0
        self.copyNumber   = 0
        self.sizeSize     = 0
        self.sizeNumber   = 0
        self.dateSize     = 0
        self.dateNumber   = 0
        self.deleteSize   = 0
        self.deleteNumber = 0
        self.emptyDirs    = 0

############################################################################################## copyFiles ######

def copyFiles(sourceFileName, destFileName, mode, test):
    """  If file does not exist in the destination directory, then copy the file.
         If the destination path does not exit, the directory path is created.

         Will only copy is test is set to false.
    """
    destDir = os.path.split(destFileName)[0]
    if not os.path.exists(destDir):
        try:
            if not test: os.makedirs(destDir)        #   use instead of mkdir, will recursively create directory path.
            print("created {}".format(destDir))
        except (IOError, os.error) as error:
            sys.stderr.write(dstDir + " : does not exist, or could not be created {0}".format(error))
            return

    try:
        print("Copying {} :: {}".format(mode, sourceFileName))
        if not test: shutil.copy(sourceFileName, destFileName)
    except (IOError, os.error) as error:
        print("ERROR :: {0} : could not copy {1}".format(sourceFileName, error))

#################################################################################### comparForwardFiles ######

def compareForwardFiles(sourceFileName, destFileName, test):
    """  Called when forward checking the original source against the original destination.
    
         Compares two files, one in the source directory and the second in the destination directory.
         Then copies the files depending upon the result.  
         Will only copy the file is it does not exist in the destination or has been altered,
         or that the file size is different in source and destination,
         or that the file date is later in source then destination.
    """
    if not os.path.exists(destFileName): 
        mode = "file does not exist in destination"
        copyFiles(sourceFileName, destFileName, mode, test)
        CopyResults.copyNumber += 1
        CopyResults.copySize   += os.path.getsize(sourceFileName)

    elif (os.path.getsize(sourceFileName) != os.path.getsize(destFileName)):
        mode = "file size has changed."
        copyFiles(sourceFileName, destFileName, mode, test)
        CopyResults.sizeNumber += 1
        CopyResults.sizeSize   += os.path.getsize(sourceFileName)

    elif (os.path.getmtime(sourceFileName) > os.path.getmtime(destFileName)):
        mode = "file date has changed."
        copyFiles(sourceFileName, destFileName, mode, test)
        CopyResults.dateNumber += 1
        CopyResults.dateSize   += os.path.getsize(sourceFileName)

################################################################################## compareReverseFiles ######

def compareReverseFiles(sourceFileName, destFileName, test, root):
    """  Called when reverse checking the original destination against the original source.
    
         Compares two files, one in the source directory and the second in the destination directory.
         Then deletes the files if in the source directory and not in the destination.  

         will only copy is test is set to false.
    """
    if not os.path.exists(destFileName): 
        mode = "file does not exist in Source"
        CopyResults.deleteNumber += 1
        CopyResults.deleteSize   += os.path.getsize(sourceFileName)

        try:
            print("Deleting {} :: {}".format(mode, sourceFileName))
            if not test: os.remove(sourceFileName)
        except (IOError, os.error) as error:
            print("ERROR :: {0} : could not delete {1}".format(destFileName, error))

############################################################################################## removeDir ######
def removeDir(path):
    """  removes a empty directory.
    """

    print("removing empty directory {}".format(path))
    try:
        os.rmdir(path)
        CopyResults.emptyDirs += 1
    except (IOError, os.error) as error:
        print("ERROR :: {0} : could not delete {1}".format(path, error))

################################################################################################# backup ######

def backup(sourceDir, destDir, direction, test):
    """  Performs a file walk of the source directory, then passes each filename for further processing.
    """
    for root, dirs, files in os.walk(sourceDir):    #  walk source directory
        for name in files:
            sourceFileName = os.path.join(root, name)

            newRoot = root.replace(sourceDir, destDir)
            destFileName   = os.path.join(newRoot, name)

            if direction == "forward":
                compareForwardFiles(sourceFileName, destFileName, test)   #   original.source -> original.destination
            else:
                compareReverseFiles(sourceFileName, destFileName, test, root)   #   original.destination -> original.source

        if not os.listdir(root): removeDir(root)

########################################################################################### printResults ######

def printResults():
    """  Print out the results of the backup.
    """
    print()
    print("Copied {0} file[s] not in destination [Copied], {1}".format(CopyResults.copyNumber,   GetHumanReadable(CopyResults.copySize)))
    print("Copied {0} file[s] that size has changed      , {1}".format(CopyResults.sizeNumber,   GetHumanReadable(CopyResults.sizeSize)))
    print("Copied {0} file[s] that date has changed      , {1}".format(CopyResults.dateNumber,   GetHumanReadable(CopyResults.dateSize)))
    print("Copied {0} file[s] not in source [deleted]    , {1}".format(CopyResults.deleteNumber, GetHumanReadable(CopyResults.deleteSize)))
    print("Empty directories deleted                    , {0}".format(CopyResults.emptyDirs))

####################################################################################### GetHumanReadable ######
def GetHumanReadable(size,precision=2):
    """  Returns the number of bytes in a more readable form.
         Nicked from the internet.
    """
    suffixes=['B','KB','MB','GB','TB']
    suffixIndex = 0
    while size > 1024:
        suffixIndex += 1        #  increment the index of the suffix
        size = size/1024.0      #  apply the division
    return "%.*f %s"%(precision,size,suffixes[suffixIndex])

########################################################################################### printSortLicense ######
def printShortLicense():
    print("""
PyBackup {}   Copyright (C) 2019  Kevin Scott
This program comes with ABSOLUTELY NO WARRANTY; for details type `pyBackup -l'.
This is free software, and you are welcome to redistribute it under certain conditions.
    """.format(__version__))

########################################################################################### printLongLicense ######
def printLongLicense():
    print("""
    Copyright (C) 2019  kevin Scott

    This program is free software: you can redistribute it and/or modify it 
    under the terms of the GNU General Public License as published by   
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
    """, end="")

############################################################################################## parseArgs ######
def parseArgs():
    """  Process the command line arguments.
    """
    parser = argparse.ArgumentParser(
        formatter_class = argparse.RawTextHelpFormatter,
        description=textwrap.dedent("""\
        A Python backup script.
        -----------------------
        The backup is a mirrored backup, that is after
        the process destDir will be a perfect mirror of sourceDir."""),
        epilog = " Kevin Scott (C) 2019")

    #  Add a Positional Argument.
    #  a optional argument would be --source or -s
    parser.add_argument("-s", "--sourceDir", action="store", default="", help="Name of the Source directory to backed up [mirrored].")
    parser.add_argument("-d", "--destDir",   action="store", default="", help="Name of the Destination directory.")
    parser.add_argument("-t", "--test",      action="store_true", help="run a test backup, nothing is changes only reported on.")
    parser.add_argument("-l", "--license",   action="store_true", help="Print the Software License.")
    parser.add_argument("-v", "--version",   action="version", version="%(prog)s 1.0.2")

    args   = parser.parse_args()

    if args.license:
        printLongLicense()
        exit(0)

    printShortLicense()

    if (args.sourceDir == "") or (args.destDir == ""):
        print()
        print("Run build.py --help for usage")
        exit(2)

    return (args.sourceDir, args.destDir, args.test)

############################################################################################### __main__ ######

CopyResults = Results()     #   Creates the results class.

if __name__ == "__main__":
    start_time = time.time()

    sourceDir, destDir, test = parseArgs()

    if os.path.isdir(sourceDir):
        if test:
            print("Backing up {0} -> {1} n test mode".format(sourceDir, destDir))
        else:
            print("Backing up {0} -> {1} ".format(sourceDir, destDir))

        backup(sourceDir, destDir, "forward", test)
        print("-----------------------------------------------------------------")
        print("Reverse Scan :: {1} -> {0}".format(sourceDir, destDir))
        print("-----------------------------------------------------------------")
        backup(destDir, sourceDir, "reverse", test)
        printResults()
    else:
        print("Source Directory not found")
        print("Run build.py --help for usage")
        exit(2)

    print()
    elapsed_time_secs = time.time() - start_time
    print("Completed {}".format(datetime.timedelta(seconds = elapsed_time_secs)))
    print()
