###############################################################################################################
#                                                                                                             #
#  Perform a backup of sourceDir to destDir                                                                   #
#                                                                                                             #
#  The backup is a mirrored backup, that is after the process destDir will be a perfect mirror of sourceDir.  #
#                                                                                                             #
#        usage: pyBackup.py [-h] [-s SOURCEDIR] [-d DESTDIR] [-t] [-l] [-v]                                   #
#                                                                                                             #
#       Kevin Scott     2019 - 2020                                                                           #
#                                                                                                             #
#                                                                                                             #
#   For changes see history.txt                                                                               #
#                                                                                                             #
###############################################################################################################
#    Copyright (C) <2019 - 2020>  <Kevin Scott>                                                                      #
#                                                                                                             #
#    This program is free software: you can redistribute it and/or modify it under the terms of the           #
#    GNU General Public License as published by the Free Software Foundation, either version 3 of the         #
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
import glob
import shutil
import pathlib
import textwrap
import datetime
import argparse
import colorama
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
    dir = destFileName.parent
    
    if not os.path.exists(dir):
        try:
            if not test: os.makedirs(dir)        #   use instead of mkdir, will recursively create directory path.
            print(f"Created {dir}")
        except (IOError, os.error) as error:
            sys.stderr.write(f"{dir} : does not exist, or could not be created {error}")
            return
    
    try:
        print(f"Copying : {mode} :: {sourceFileName.name}")
        if not test: shutil.copy(sourceFileName, destFileName)
    except (IOError, os.error) as error:
        print(f"ERROR :: { error} : could not copy {sourceFileName.name}")

#################################################################################### comparForwardFiles ######

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
    elif os.path.getsize(sourceFileName) != os.path.getsize(destFileName):
        mode = "file size has changed."
    elif (os.path.getmtime(sourceFileName) > os.path.getmtime(destFileName)):
        mode = "file date has changed."

    copyFiles(sourceFileName, destFileName, mode, test)
    CopyResults.copyNumber += 1
    CopyResults.copySize   += os.path.getsize(sourceFileName)
################################################################################## compareReverseFiles ######

def compareReverseFiles(sourceFileName, destFileName, test):
    """  Called when reverse checking the original destination against the original source.
    
         Compares two files, one in the source directory and the second in the destination directory.
         Then deletes the files if in the source directory and not in the destination.  

         will only copy is test is set to false.
    """
    if not destFileName.exists(): 
        mode = "file does not exist in Source"
        CopyResults.deleteNumber += 1
        CopyResults.deleteSize   += os.path.getsize(sourceFileName)

        try:
            print(f"Deleting {mode} :: {sourceFileName.name}")
            if not test: os.remove(sourceFileName)
        except (IOError, os.error) as error:
            print(f"ERROR :: {error} : could not delete {destFileName.name}")

############################################################################################## removeDir ######
def removeEmptyDir(path):
    """  removes all empty directory's in path.
    """

    subfolders = [ f.path for f in os.scandir(destDir) if f.is_dir() ]  # A quick list of all subfolders.
    
    for folder in subfolders: 
        if os.path.getsize(folder) == 0:
            
            print(f"Removing empty directory {path}")
            try:
                os.rmdir(path)
                CopyResults.emptyDirs += 1
            except (IOError, os.error) as error:
                print(f"ERROR :: {error} : could not delete {path}")

################################################################################################# backup ######

def backup(sourceDir, destDir, direction, test):
    """  Performs a file walk of the source directory, then passes each filename for further processing.
    
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
    
    for sourceFileName in sourceDir.glob('**/*.*'):     # Recursively find all files in sourceDir.
        fn = list(sourceFileName.parts)                 # A list of all the component parts on the source filename.
        dn = list(destDir.parts)                        # A list of all the component parts of the destination path.
        d = len(dn)                                     # Length of destination path

        p1 = "\\".join(dn)                              # A string of the destination path
        p2 = "\\".join(fn[d:])                          # A string of the source path, that needs to be added to the destination.
        p  = p1 + "\\" + p2                             # A complete string of the destination path
        
        destFileName   = pathlib.Path(p)                # Change the string path to a pathlib.Path

        if direction == "forward":
            compareForwardFiles(sourceFileName, destFileName, test)   #   original.source -> original.destination
        else:
            compareReverseFiles(sourceFileName, destFileName, test)   #   original.destination -> original.source

    # A quick check of destDir for empty directories.
    removeEmptyDir(destDir)

########################################################################################### printResults ######

def printResults():
    """  Print out the results of the backup.
    """
    print()
    print(f"Copied {CopyResults.copyNumber} file[s] not in destination [Copied], {GetHumanReadable(CopyResults.copySize)}")
    print(f"Copied {CopyResults.sizeNumber} file[s] that size has changed      , {GetHumanReadable(CopyResults.sizeSize)}")
    print(f"Copied {CopyResults.dateNumber} file[s] that date has changed      , {GetHumanReadable(CopyResults.dateSize)}")
    print(f"Copied {CopyResults.deleteNumber} file[s] not in source [deleted]  , {GetHumanReadable(CopyResults.deleteSize)}")
    print(f"Empty directories deleted                                          , {CopyResults.emptyDirs}")

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
PyBackup {}   Copyright (C) 2019 - 2020  Kevin Scott
This program comes with ABSOLUTELY NO WARRANTY; for details type `pyBackup -l'.
This is free software, and you are welcome to redistribute it under certain conditions.
    """.format(__version__), flush=True)

########################################################################################### printLongLicense ######
def printLongLicense():
    print("""
    Copyright (C) 2019 - 2020  Kevin Scott

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
        The backup is a mirrored backup, that is after
        the process destDir will be a perfect mirror of sourceDir."""),
        epilog = f" Kevin Scott (C) 2019 - 2020 :: %(prog)s V{__version__}")

    #  Add a Positional Argument.
    #  a optional argument would be --source or -s
    parser.add_argument("-s", "--sourceDir", type=pathlib.Path, action="store", default=False, help="Name of the Source directory to backed up [mirrored].")
    parser.add_argument("-d", "--destDir",   type=pathlib.Path, action="store", default=False, help="Name of the Destination directory.")
    parser.add_argument("-t", "--test",      action="store_true", help="run a test backup, nothing is changes only reported on.")
    parser.add_argument("-l", "--license",   action="store_true", help="Print the Software License.")
    parser.add_argument("-v", "--version",   action="version", version=f"%(prog)s {__version__}")

    args   = parser.parse_args()

    if args.license:
        printLongLicense()
        exit(0)

    printShortLicense()

    if not args.sourceDir:
        print(f"{colorama.Fore.RED}No Source Directory Supplied {colorama.Fore.RESET}")
        parser.print_help()
        exit(1)

    if not args.destDir:
        print(f"{colorama.Fore.RED}No Destination Directory Supplied {colorama.Fore.RESET}")
        parser.print_help()
        exit(2)

    if args.sourceDir == args.destDir:
        print(f"{colorama.Fore.RED}Source and Destination are the same {colorama.Fore.RESET}")
        parser.print_help()
        exit(3)
        
    if not os.path.isdir(args.sourceDir):
        print(f"{colorama.Fore.RED}Source Directory not found {colorama.Fore.RESET}")
        parser.print_help()
        exit(4)
        
    return (args.sourceDir, args.destDir, args.test)

############################################################################################### __main__ ######

CopyResults = Results()     #   Creates the results class.

if __name__ == "__main__":
    start_time = time.time()

    sourceDir, destDir, test = parseArgs()

    
    if test:
        print(f"Backing up {sourceDir} -> {destDir} in test mode", flush=True)
    else:
        print(f"Backing up {sourceDir} -> {destDir} ", flush=True)

    backup(sourceDir, destDir, "forward", test)
    print("-----------------------------------------------------------------")
    if test:
        print(f"Reverse Scan :: {destDir} -> {sourceDir} in test mode", flush=True)
    else:
        print(f"Reverse Scan :: {destDir} -> {sourceDir} ", flush=True)
    backup(destDir, sourceDir, "reverse", test)
    
    if CopyResults.copyNumber or CopyResults.deleteNumber:
        printResults()



    print()
    elapsed_time_secs = time.time() - start_time
    print(f"Completed {datetime.timedelta(seconds = elapsed_time_secs)}")
    print()
