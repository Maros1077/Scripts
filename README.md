# Scripts
Little scripts to help with basic things

## Photo Extractor
Version: 0.8

This script is used to extract photos from your removable disc (SD card, etc...).
It finds all discs with DCIM folder. If there is more than one, the script displays all of them.
It extracts RAW photos into folder that you specified directly in the script's source code.

Available switches:
 1) -n, -name<br/>
	Specifies a name of a subfolder, which will be created in the default photo folder and where all photos will be stored. (eg. "-n Jozef a Mirka")
	This switch is mandatory!
  
 2) -d, -date<br/>
	Specifies dates of photos, that should be extracted. In a format <month.day>! (eg. "-d 6.15 6.16")
	This switch is optional. If not set, photos with today's date will be extracted.
  
 3) -i, -info<br/>
	Shows information about specified folders.
  
 4) -h, -help<br/>
	Shows help
