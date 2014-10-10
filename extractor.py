#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.


import sys,os,struct,glob

# print command line syntax
def Usage():
	print "Usage:"
	print "extractor.py isofile"
	print ""
	print "isofile - .iso file with firmaware package , "
	print "          which can be obtained from www.seagate.com"



def Error(mess):
	print "x",mess
	sys.exit(1)

def Progress(mess):
	print "*",mess

def Warning(mess):
	print "!",mess


def Run(cmd, out=False):
    out = os.popen(cmd)
    while True:
        line = out.readline()
        if line == "":
            break
        if out==True:
            sys.stdout.write(line)
    return out.close()    


def DissectLOD(lodfile):

	LOD_HEADER_SIZE = 0x40
	muted = False;


	Progress("")
	Progress("Dissecting: %s  " % (os.path.basename(lodfile)))

	f = open(lodfile, "rb")
	try:
 	 os.mkdir(os.path.basename(lodfile))
	except:
	  Warning("Cannot create output directory for this LOD, files won't be created.")
	  muted = True

	list = open(os.path.basename(lodfile)+"\\list.txt","w")

	list.write("*=====*======*=============*============*============*============*\n")
        list.write("| idx | type | start offs. | end offs.  | size(hex)  | size(dec)  |\n")
	list.write("*=====*======*=============*============*============*============*\n")
	idx=0

	while True:
	  try:
	    offset = f.tell()
	    data = f.read(LOD_HEADER_SIZE)
	    size = int(struct.unpack("<I",data[0x10:0x14])[0])
	    blob = f.read(size)


	    list.write("| %02d  |  %02x  | 0x%08x  | 0x%08x | 0x%08x | %10d |\n" % (idx, ord(data[0xe]), offset, offset+size-1, size,size))

	    if muted==False:
  	      lf = open(os.path.basename(lodfile) + "\\%02d.bin" % (idx),"wb")
	      lf.write(blob)
	      lf.close()

 	    idx+=1
          except:
	    break
	list.write("*=====*======*=============*============*============*============*\n")
	list.close()

	Progress("Found [%d] chunks in [%s]" % (idx, os.path.basename(lodfile)))
	f.close()



#-----------------------------  MAIN CODE ------------------------------------
print "Seagate firmware extractor 1.0 Copyright (C) 2014 THiNK (think@hron.eu)"
print ""



if len(sys.argv)<2:
	Usage()
	sys.exit(1)

# check that file exists
isofile = sys.argv[1]
if os.path.isfile(isofile)==False:
	Error("Not found or is not a file [%s]." % (isofile))

# check that 7z is in place
zipcmd = "bin\\7z.exe"
if os.path.isfile(zipcmd)==False:
	Error("7Zip not found, check [bin] directory." )

Progress("Trying to find floppy image inside [%s]...." %(os.path.basename(isofile)))
Run("bin\\7z.exe x -y -otmp %s *.ima *.zip" %(isofile))
floppy =  glob.glob('tmp\\*.ima')

if (len(floppy)==0):
	Error("Can't find any floppy image file inside [%s]" %(os.path.basename(isofile)))

Progress("Found [%d] match(es)." % (len(floppy)))

for flp in floppy:
	Progress("Trying to find *.zip files inside floppy image [%s]" % (flp))
	Run("bin\\7z.exe x -y -otmp %s *.zip *.lod" % (flp))

	zipfiles =  glob.glob('tmp\\*.zip')
	if (len(zipfiles)==0):
	    Error("Can't find any *.zip file inside [%s]" %(flp))

	Progress("Found [%d] match(es)." % (len(zipfiles)))

	
	for zipfile in zipfiles:
		Progress("Trying to find *.lod files inside [%s]" %(zipfile))
		Run("bin\\7z.exe x -y -otmp %s *.lod" % (zipfile))

	lods =  glob.glob('tmp\\*.lod')	
	if (len(lods)==0):
	    Error("Can't find any *.lod, nothing to do")
	Progress("")
	Progress("Found [%d] match(es)." % (len(lods)))

	for lod in lods:
		DissectLOD(lod)

files = glob.glob("tmp\*.*")	
for f in files:
  if os.path.isfile(f):
    os.remove(f)

os.rmdir("tmp")

sys.exit(1)



