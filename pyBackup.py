###############################################################################################################
#                                                                                                             #
#  Perform a backup of sourceDir to destDir                                                                   #
#                                                                                                             #
#  The backup is a mirrored backup, that is after the process destDir will be a perfect mirror of sourceDir.  #
#                                                                                                             #
#  Usage: pyBackup [--help] sourceDir destDir                                                                 #
#                                                                                                             #
#  October 2019                Kevin Scott                                                                    #
#                                                                                                             #
#                                                                                                             #
#   V1.00   17 Oct.2019     Will copy files that are not in the destination.                                  #
#                                                                                                             #
###############################################################################################################
#   This program is free software; you can redistribute it and/or modify it under the terms of                #
#   the GNU General Public License as published by the Free Software Foundation; either version               #
#   2 of the License, or (at your option) any later version.                                                  #
#                                                                                                             #
#   This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;                 #
#   without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.                 #
#   See the GNU General Public License for more details.                                                      #
#                                                                                                             #
#   You should have received a copy of the GNU General Public License long with this program;                 #
#   if not, write to the Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor,                     #
#   Boston, MA 02110-1301, USA.                                                                               #
###############################################################################################################


import os
import time
import shutil
import datetime
import argparse


############################################################################################## copyFiles ######

class Results():
    """  A simple class that holds the total number and size of files copied.
         Save on global variables.
    """   
    def __init__(self):
        self.copySize   = 0
        self.copyNumber = 0

############################################################################################## copyFiles ######

def copyFiles(sourceFileName, destFileName):
    """  If file does not exist in the destination directory, then copy the file.
         If the path does not exits, the directory path is created.
    """
    destDir = os.path.split(destFileName)[0]
    if not os.path.exists(destDir):
        try:
            os.makedirs(destDir)        #   use instead of mkdir, will recursively create directory path.
            print("created %s" % destDir)
        except (IOError, os.error) as error:
            sys.stderr.write(dstDir + " : does not exist, or could not be created {0}".format(error))
            return

    try:
        print("Copying %s" % sourceFileName)
        shutil.copy(sourceFileName, destFileName)
    except (IOError, os.error) as error:
        sys.stderr.write(sourceFileName + " : could not copy {0}".format(error))

########################################################################################### compareFiles ######

def compareFiles(sourceFileName, destFileName):
    """  Compares two files, one in the source directory and the second in the destination directory.
         Then copies the files depending upon the result.  Will only copy the file is it does not
         exist in the destination or has been altered.
    """
    if not os.path.exists(destFileName): 
        copyFiles(sourceFileName, destFileName)
        CopyResults.copyNumber += 1
        CopyResults.copySize   += os.path.getsize(sourceFileName)

################################################################################################# backup ######

def backup(sourceDir, destDir):
    """  Performs a file walk of the source directory, then passes each filename for further processing.
    """
    for root, dirs, files in os.walk(sourceDir):    #  walk source directory
        for name in files:
            sourceFileName = os.path.join(root, name)

            newRoot = root.replace(sourceDir, destDir)
            destFileName   = os.path.join(newRoot, name)

            compareFiles(sourceFileName, destFileName)

########################################################################################### printResults ######

def printResults():
    """  Print out the results of the backup.
    """
    print()
    print("Copied %s file[s], %s bytes" % (CopyResults.copyNumber, CopyResults.copySize))

############################################################################################### __main__ ######

CopyResults = Results()     #   Creates the results class.

if __name__ == "__main__":
    start_time = time.time()

    parser = argparse.ArgumentParser(
        description="""
            A Python backup script.
            -----------------------
           The backup is a mirrored backup, 
           that is after the process destDir will be a 
           perfect mirror of sourceDir.""",

        formatter_class = argparse.ArgumentDefaultsHelpFormatter,
        epilog = " Kevin Scott (C) 2019")

    #  Add a Positional Argument.
    #  a optional argument would be --source or -s
    parser.add_argument("sourceDir", type=str, help="Name of the Source directory to backed up [mirrored].")
    parser.add_argument("destDir",   type=str, help="Name of the Destination directory.")

    args   = parser.parse_args()

    sourceDir = args.sourceDir
    destDir   = args.destDir

    if os.path.isdir(sourceDir):
        print("Backing up %s to %s " % (sourceDir, destDir))
        backup(sourceDir, destDir)
        printResults()
    else:
        print("Source Directory not found")
        print("Run build.py --help for usage")
        exit(2)

    print()
    elapsed_time_secs = time.time() - start_time
    print("Completed %s" % datetime.timedelta(seconds = elapsed_time_secs))
    print()
