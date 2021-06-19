import os
import shutil
import sys
import time
from datetime import datetime

import win32file
from PIL import Image

PATH_TO_PHOTOS_DIRECTORY = "C:/Users/xxx/Pictures/Photos"  # CHANGE THIS TO YOUR FOLDER
PHOTO_DIRECTORY = "DCIM"  # SPECIFIES A FOLDER NAME, WHERE PHOTOS SHOULD BE FOUND
NEW_DIRECTORY_NAME_SHORT = "-n"
NEW_DIRECTORY_NAME = "-name"
DATE_SHORT = "-d"
DATE = "-date"
HELP_SHORT = "-h"
HELP = "-help"
INFO_SHORT = "-i"
INFO = "-info"
VERSION = "0.8"


# https://stackoverflow.com/questions/4273252/detect-inserted-usb-on-windows
def locateUsb():
    drive_list = []
    drivebits = win32file.GetLogicalDrives()
    for d in range(1, 26):
        mask = 1 << d
        if drivebits & mask:
            # here if the drive is at least there
            drname = '%c:\\' % chr(ord('A') + d)
            t = win32file.GetDriveType(drname)
            if t == win32file.DRIVE_REMOVABLE:
                drive_list.append(drname)
    return drive_list


def findDCIM():
    drive_list = locate_usb()
    if not drive_list:
        sys.exit("No external USB recognized.")
    else:
        print("Successfully found those external USB-s:", end=" ")
        print(", ".join(map(str, drive_list)))
    drives_with_dcim = []
    for path in drive_list:
        try:
            if PHOTO_DIRECTORY in os.listdir(path):
                drives_with_dcim.append(path)
        except PermissionError:
            continue
    if not drives_with_dcim:
        sys.exit("No suitable directory in USB-s:")
    else:
        print("Drives containing DCIM folder:", end=" ")
        print(", ".join(map(str, drives_with_dcim)))
        return drives_with_dcim


def specifyFolder(length):
    while True:
        try:
            num = int(input())
        except ValueError:
            print("Input must be a number. Try again: ", end="")
            continue
        if num >= length or num < 0:
            print("Unvalid input, try again: ", end="")
            continue
        else:
            return num


def findRAW():
    dcim_list = findDCIM()
    folders_with_raws = []
    for path in dcim_list:
        for subdir, dirs, files in os.walk(path):
            for filename in files:
                filepath = subdir + os.sep + filename
                if filepath.endswith(".CR2"):
                    folder_path = subdir + os.sep
                    if folder_path not in folders_with_raws:
                        folders_with_raws.append(folder_path)
    correct_folder_path = ""
    if len(folders_with_raws) == 0:
        sys.exit("No RAW found")
    elif len(folders_with_raws) == 1:
        correct_folder_path = folders_with_raws[0]
        print("RAW successfully found in: ", correct_folder_path)
    else:
        print("RAW successfully found in more than one directory: ")
        for i in range(0, len(folders_with_raws)):
            print("\t", i, ":", folders_with_raws[i])
        print("Please, choose directory inserting a number: ", end="")
        correct_folder_path = folders_with_raws[specifyFolder(len(folders_with_raws))]
        print("Choosed", correct_folder_path)
    return correct_folder_path


def findPhotos(dates):
    folder = findRAW()
    if folder == "":
        sys.exit("Unexpected error")
    photos_with_correct_time = []
    for entry in os.scandir(folder):
        if entry.path.endswith(".CR2") and entry.is_file():
            photo_time = datetime.fromtimestamp(os.path.getctime(entry.path))
            if not dates:
                if photo_time.date() == datetime.today().date():
                    photos_with_correct_time.append(entry.path)
            else:
                photo_date = str(photo_time.date().month) + "." + str(photo_time.date().day)
                if photo_date in dates:
                    photos_with_correct_time.append(entry.path)
    if not photos_with_correct_time:
        sys.exit("No photos with todays/given date found")
    print("Successfully found", len(photos_with_correct_time), " photos.")
    return photos_with_correct_time


def createFolder(name, date):
    print(date)
    path = PATH_TO_PHOTOS_DIRECTORY + "/" + date + " " + name
    try:
        os.mkdir(path)
    except OSError as exc:
        sys.exit("Creation of the directory %s failed due to %s" % (path, exc))
    else:
        print("Successfully created the directory %s " % path)
        return path


def copyFiles(photos, new_folder):
    length = len(photos)
    for i in range(0, length):
        shutil.copy2(photos[i], new_folder)
        print("Copied %s (%s/%s)" % (photos[i], i + 1, length))
    print("Everything is done! You can find your photos in Photos folder!\n -> %s" % PATH_TO_PHOTOS_DIRECTORY)
    return


def showHelp():
    print("### Welcome to Photo Extractor by Z3L0! ###\n")
    print("Version: %s" % VERSION)
    print("This script is used to extract photos from your removable disc (SD card, etc...)")
    print("It finds all discs with DCIM folder. If there is more than one, the script displays all of them.")
    print("!!! It extracts RAW photos into folder, that you specified directly in script !!!\n")
    print("Available switches:")
    print(" 1) -n, -name")
    print("\tSpecifies a name of a subfolder, which will be created in the default photo folder and where all photos "
          "will be stored. (eg. \"-n Jozef a Mirka\")")
    print("\tThis switch is mandatory!")
    print(" 2) -d, -date")
    print("\tSpecifies dates of photos, that should be extracted. In a format <month.day>! (eg. \"-d 6.15 6.16\")")
    print("\tThis switch is optional. If not set, photos with today's date will be extracted.")
    print(" 2) -h, -help")
    print("\tYou are here :-)")


def showInfo():
    print("Photos will be searched in all folders on a removable disc with name: %s" % PHOTO_DIRECTORY)
    print("Your photos will be stored into: %s" % PATH_TO_PHOTOS_DIRECTORY)
    print("!!! These values can be changed directly in the script source code !!!")


def main():
    args = sys.argv
    name_passed = False
    new_directory_name = ""
    dates = []

    for i in range(0, len(args)):
        # NAME
        if args[i] == NEW_DIRECTORY_NAME_SHORT or args[i] == NEW_DIRECTORY_NAME:
            if new_directory_name != "":
                sys.exit("You specified -name or -n more than one time!")
            if len(args) - 1 < i + 1 or '-' in args[i + 1]:
                sys.exit("You must specify a name after -n or -name!")
            for j in range(i + 1, len(args)):
                if '-' in args[j]:
                    break
                new_directory_name = new_directory_name + " " + args[j]
            name_passed = True

        # DATE
        if args[i] == DATE or args[i] == DATE_SHORT:
            if dates:
                sys.exit("You specified -date or -d more than one time!")
            if len(args) - 1 < i + 1 or '-' in args[i + 1]:
                sys.exit("You must specify a date after -d or -date!")
            for j in range(i + 1, len(args)):
                if '-' in args[j]:
                    break
                dates.append(args[j])

        # INFO
        if args[i] == INFO or args[i] == INFO_SHORT:
            if len(args) != 2:
                sys.exit("You cannot specify nothing else with -i or -info!")
            showInfo()
            return

        # HELP
        if args[i] == HELP or args[i] == HELP_SHORT:
            if len(args) != 2:
                sys.exit("You cannot specify nothing else with -h or -help!")
            showHelp()
            return

    if not name_passed:
        sys.exit("You must specify a name of a new folder to store photos with -n or -name.")
    photos = findPhotos(dates)
    date_of_photos = datetime.fromtimestamp(os.path.getctime(photos[0])).strftime("%Y.%m.%d")
    new_folder_path = createFolder(new_directory_name, date_of_photos)
    copyFiles(photos, new_folder_path)
    return


if __name__ == "__main__":
    main()
