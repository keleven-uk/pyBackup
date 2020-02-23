###############################################################################################################
#                                                                                                             #
#  Perform a backup of sourceDir to destDir                                                                   #
#                                                                                                             #
#  Two Directories are compared and the destination directory is made a mirror of the source directory.       #
#  That is, all files missing the the destination are copied across and all file that only exist in the       #
#  destination are deleted.  Also, all empty directories in the destination are removed [but not in source].  #
#                                                                                                             #
#        usage: pyBackup.py [-h] [-s SOURCEDIR] [-d DESTDIR] [-t] [-l] [-v]                                   #
#                                                                                                             #
#       Kevin Scott     2019 - 2020                                                                           #
#                                                                                                             #
#   TODO                                                                                                      #
#       Seems to ignore empty directories in source - maybe this is what we want.                             #
#                                                                                                             #
#   For changes see history.txt                                                                               #
#                                                                                                             #
###############################################################################################################
#    Copyright (C) <2019 - 2020>  <Kevin Scott>                                                               #
#                                                                                                             #
#    This program is free software: you can redistribute it and/or modify it under the terms of the           #
#    GNU General Public License as published by the Free Software Foundation, either myVERSION 3 of the       #
#    License, or (at your option) any later myVERSION.                                                        #
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
import pathlib
import textwrap
import datetime
import argparse
import colorama
import myLogger
from _version import myVERSION, myNAME


################################################################################################## Results ######

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
    dir = destFileName.parent

    if not os.path.exists(dir):
        try:
            if not test: os.makedirs(dir)        #   use instead of mkdir, will recursively create directory path.
            print(f"Created {dir}")
        except (IOError, os.error) as error:
            log.error(f"ERROR :: {dir} : does not exist, or could not be created {error}", exc_info=True)
            print(f"ERROR :: {dir} : does not exist, or could not be created {error}")
            return

    if sourceFileName.is_file():
        try:
            print(f"Copying : {mode} :: {sourceFileName.name}")
            # Use copy2 instead of copy, copies the file metadata with the file.
            if not test: shutil.copy2(sourceFileName, destFileName)
            CopyResults.copyNumber += 1
            CopyResults.copySize   += os.path.getsize(destFileName)
        except (IOError, os.error, shutil.Error) as error:
            log.error(f"ERROR :: { error} : could not copy {sourceFileName.name}", exc_info=True)
            print(f"ERROR :: { error} : could not copy {sourceFileName.name}")

#################################################################################### compareForwardFiles ######

def compareForwardFiles(sourceFileName, destFileName, test):
    """  Called when forward checking the original source against the original destination.

         Compares two files, one in the source directory and the second in the destination directory.
         Then copies the files depending upon the result.
         Will only copy the file is it does not exist in the destination or has been altered,
         or that the file size is different in source and destination,
         or that the file date is later in source then destination.
    """
    if not destFileName.exists():
        mode = "file does not exist in destination"
        copyFiles(sourceFileName, destFileName, mode, test)
    elif os.path.getsize(sourceFileName) != os.path.getsize(destFileName):
        mode = "file size has changed."
        copyFiles(sourceFileName, destFileName, mode, test)
    elif (os.path.getmtime(sourceFileName) > os.path.getmtime(destFileName)):
        mode = "file date has changed."
        copyFiles(sourceFileName, destFileName, mode, test)

    if sourceFileName.parent == "D:\scans":
        print(f"{sourceFileName} in copyFiles")

    if not destFileName.exists():
        log.debug(f"{sourceFileName} has no mode set")
################################################################################## compareReverseFiles ######

def compareReverseFiles(sourceFileName, destFileName, test):
    """  Called when reverse checking the original destination against the original source.

         Compares two files, one in the source directory and the second in the destination directory.
         Then deletes the files if in the source directory and not in the destination.

         will only copy is test is set to false.
    """
    if not destFileName.exists():
        try:
            if sourceFileName.is_file():
                print(f"Deleting : file does not exist in Source :: {sourceFileName.name}")
                CopyResults.deleteNumber += 1
                CopyResults.deleteSize   += os.path.getsize(sourceFileName)
                if not test: os.remove(sourceFileName)
        except (IOError, os.error) as error:
            log.error(f"ERROR :: {error} : could not delete {destFileName.name}", exc_info=True)
            print(f"ERROR :: {error} : could not delete {destFileName.name}")

######################################################################################### removeEmptyDir ######
def removeEmptyDir(destDir):
    """  removes all empty directory's in path.

         shutil.rmtree not deleting the whole directory tree.
         Each run will remove the lowest level of the directory tree.

         Only len(os.listdir(f)) gave a true zero value for empty directories.
         Also, tried f.stat().st_size, os.stat(f)[6] & os.path.getsize(f)
    """
    for f in destDir.glob("**/*"):
        if f.is_dir():
            if len(os.listdir(f)) == 0:
                assert os.path.getsize != 0, f"{f} :: os.path.getsize not zero"
                print(f"Removing empty directory {f}")
                try:
                    if not test: shutil.rmtree(f, ignore_errors=True, onerror=None)
                    CopyResults.emptyDirs += 1
                except (IOError, os.error) as error:
                    log.error(f"ERROR :: {error} : could not delete {f}", exc_info=True)
                    print(f"ERROR :: {error} : could not delete {f}")

 ################################################################################################# backup ######

def backup(sourceDir, destDir, direction, test):
    """  Performs a file walk of the source directory, then passes each filemyNAME for further processing.

    i.e. backing up the directory d:\one to d:\four.  [probably an easier way]
        sourceDir = d:\one\two\three.txt
        distDir   = d:\four
        fn        = ["d:\\", "one", "two", "three.txt"]
        dn        = ["d:\\", "four"]
        d         = 2

        p1 = "D:\\four"
        p2 = "two\\three.txt"
        p  = d:\\four\\two\\three.txt"
    """

    #for sourceFileName in sourceDir.glob("**/*.*"):    # Seems to miss files with no extension.
    for sourceFileName in sourceDir.glob("**/*"):       # Recursively find all files in sourceDir.
        fn = list(sourceFileName.parts)                 # A list of all the component parts on the source filemyNAME.
        dn = list(destDir.parts)                        # A list of all the component parts of the destination path.
        d = len(dn)                                     # Length of destination path

        p1 = "\\".join(dn)                              # A string of the destination path
        p2 = "\\".join(fn[d:])                          # A string of the source path, that needs to be added to the destination.
        p  = p1 + "\\" + p2                             # A complete string of the destination path

        destFileName = pathlib.Path(p)                  # Change the string path to a pathlib.Path

        if direction == "forward":
            compareForwardFiles(sourceFileName, destFileName, test)   #   original.source -> original.destination
        else:
            compareReverseFiles(sourceFileName, destFileName, test)   #   original.destination -> original.source

########################################################################################### printResults ######

def printResults():
    """  Print out the results of the backup.
    """
    print()
    print(f"Copied {CopyResults.copyNumber:6} file[s] not in destination [Copied], {getHumanReadable(CopyResults.copySize)}")
    print(f"Copied {CopyResults.sizeNumber:6} file[s] that size has changed      , {getHumanReadable(CopyResults.sizeSize)}")
    print(f"Copied {CopyResults.dateNumber:6} file[s] that date has changed      , {getHumanReadable(CopyResults.dateSize)}")
    print(f"Copied {CopyResults.deleteNumber:6}   file[s] not in source [deleted]  , {getHumanReadable(CopyResults.deleteSize)}")
    print(f"Empty directories deleted                        , {CopyResults.emptyDirs}")

####################################################################################### GetHumanReadable ######
def getHumanReadable(bytes, suffix="B"):
    """  Returns the number of bytes in a more readable form.
         Nicked from the internet.

         1253656 => "1.20MB"
         1253656678 => "1.17GB"
    """
    factor = 1024
    for unit in ["", "K", "M", "G", "T", "P"]:
        if bytes < factor:
            return f"{bytes:.2f}{unit}{suffix}"
        bytes /= factor

########################################################################################### printSortLicense ######
def printShortLicense():
    print(f"""
{myNAME} V{myVERSION}   Copyright (C) 2019 - 2020  Kevin Scott
This program comes with ABSOLUTELY NO WARRANTY; for details type `pyBackup -l'.
This is free software, and you are welcome to redistribute it under certain conditions.
    """, flush=True)

########################################################################################### printLongLicense ######
def printLongLicense():
    print(f"""
    {myNAME} V{myVERSION}   Copyright (C) 2019 - 2020  Kevin Scott

    This program is free software: you can redistribute it and/or modify it
    under the terms of the GNU General Public License as published by
    the Free Software Foundation, either myVERSION 3 of the License, or
    (at your option) any later myVERSION.

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

         Checks the arguments and will exit if not valid.

         Exit code 0 - program has exited normally, after print licence or help.
         Exit code 1 - No source directory supplied.
         Exit code 2 - No destination directory supplied.
         Exit code 3 - Source and destination directors are the same.
         Exit code 4 - Source directory not found.
    """
    parser = argparse.ArgumentParser(
        formatter_class = argparse.RawTextHelpFormatter,
        description=textwrap.dedent("""\
        A Python backup script.
        -----------------------
        Two Directories are compared and the destination directory is made a mirror of the source directory.
        That is, all files missing the the destination are copied across and all file that only exist in the
        destination are deleted.  Also, all empty directories in the destination are removed [but not in source]."""),
        epilog = f" Kevin Scott (C) 2019 - 2020 :: {myNAME} V{myVERSION}")

    #  Add a Positional Argument.
    #  a optional argument would be --source or -s
    parser.add_argument("-s", "--sourceDir", type=pathlib.Path, action="store", default=False, help="myNAME of the Source directory to backed up [mirrored].")
    parser.add_argument("-d", "--destDir",   type=pathlib.Path, action="store", default=False, help="myNAME of the Destination directory.")
    parser.add_argument("-t", "--test",      action="store_true", help="run a test backup, nothing is changes only reported on.")
    parser.add_argument("-l", "--license",   action="store_true", help="Print the Software License.")
    parser.add_argument("-v", "--version",   action="version", version=f"{myNAME} V{myVERSION}")

    args   = parser.parse_args()

    if args.license:
        printLongLicense()
        exit(0)

    printShortLicense()

    if not args.sourceDir:
        log.error("No Source Directory Supplied.")
        print(f"{colorama.Fore.RED}No Source Directory Supplied. {colorama.Fore.RESET}")
        parser.print_help()
        exit(1)

    if not args.destDir:
        log.error("No Destination Directory Supplied.")
        print(f"{colorama.Fore.RED}No Destination Directory Supplied. {colorama.Fore.RESET}")
        parser.print_help()
        exit(2)

    if args.sourceDir == args.destDir:
        log.error("Source and Destination are the same.")
        print(f"{colorama.Fore.RED}Source and Destination are the same. {colorama.Fore.RESET}")
        parser.print_help()
        exit(3)

    if not os.path.isdir(args.sourceDir):
        log.error("Source Directory not found.")
        print(f"{colorama.Fore.RED}Source Directory not found. {colorama.Fore.RESET}")
        parser.print_help()
        exit(4)

    return (args.sourceDir, args.destDir, args.test)

############################################################################################### __main__ ######

CopyResults = Results()     #   Creates the results class.

if __name__ == "__main__":

    log = myLogger.get_logger(myNAME)
    log.info("-------------------------------------------------------------")
    log.info(f"Start of {myNAME} V{myVERSION}")

    startTime = time.time()

    sourceDir, destDir, test = parseArgs()
    print("===================================")

    if sourceDir.parts == ():               # if sourceDir is "." then backup Current Working Directory
        destDir = pathlib.Path.cwd()

    if destDir.parts == ():                 # if destDir is "." then dump to Current Working Directory
        destDir = pathlib.Path.cwd()

    if test:
        print(f"Backing up {sourceDir} -> {destDir} in test mode", flush=True)
    else:
        print(f"Backing up {sourceDir} -> {destDir} ", flush=True)

    backup(sourceDir, destDir, "forward", test)
    forwardTime = time.time()
    print("-----------------------------------------------------------------")
    reverseStartTime = time.time()
    if test:
        print(f"Reverse Scan :: {destDir} -> {sourceDir} in test mode", flush=True)
    else:
        print(f"Reverse Scan :: {destDir} -> {sourceDir} ", flush=True)
    backup(destDir, sourceDir, "reverse", test)
    reverseTime = time.time()

    # A quick check of destDir for empty directories.
    emptyDirStartTime = time.time()
    removeEmptyDir(destDir)
    emptyDirTime = time.time()

    if CopyResults.copyNumber or CopyResults.deleteNumber or CopyResults.emptyDirs:
        printResults()

    print()
    elapsedTimeSecs  = time.time()  - startTime
    forwardTimeSecs  = forwardTime  - startTime
    reverseTimeSecs  = reverseTime  - reverseStartTime
    emptyDirTimeSecs = emptyDirTime - emptyDirStartTime
    print(f"{colorama.Fore.CYAN}Completed  :: {datetime.timedelta(seconds = elapsedTimeSecs)}   {colorama.Fore.RESET}")
    print(f"{colorama.Fore.CYAN}Forward    :: {datetime.timedelta(seconds = forwardTimeSecs)}   {colorama.Fore.RESET}")
    print(f"{colorama.Fore.CYAN}Reverse    :: {datetime.timedelta(seconds = reverseTimeSecs)}   {colorama.Fore.RESET}")
    print(f"{colorama.Fore.CYAN}Empty Dirs :: {datetime.timedelta(seconds = emptyDirTimeSecs)}  {colorama.Fore.RESET}")
    print()

    log.info(f"End of {myNAME} V{myVERSION}")